import re
from dataclasses import dataclass, field
from typing import List, Optional


# -----------------------------------------------------------
# Data Models
# -----------------------------------------------------------

@dataclass
class ToneDifference:
    source: str
    observation: str


@dataclass
class EmphasisDifference:
    source: str
    focus: str


@dataclass
class LanguageSignals:
    emotional_wording:   List[str] = field(default_factory=list)
    speculative_wording: List[str] = field(default_factory=list)


@dataclass
class FramingResult:
    """
    Structured output from the LLM response.
    Each field maps to one section of the FRAMING COMPARISON format.
    """
    overall_observation:        str                    = ""
    tone_differences:           List[ToneDifference]   = field(default_factory=list)
    emphasis_differences:       List[EmphasisDifference] = field(default_factory=list)
    language_signals:           LanguageSignals        = field(default_factory=LanguageSignals)
    reader_interpretation:      str                    = ""
    raw:                        str                    = ""      # always preserve the original


# -----------------------------------------------------------
# Output Parser
# -----------------------------------------------------------

class OutputParser:
    """
    Parses the LLM's raw text response into a FramingResult object.

    Expected LLM output format:
    ─────────────────────────────────────────
    FRAMING COMPARISON

    Overall Observation:
    <text>

    Tone Differences:
    - Source A: <text>
    - Source B: <text>

    Emphasis Differences:
    - Source A: <text>
    - Source B: <text>

    Language Signals:
    - Emotional wording: <text>
    - Speculative wording: <text>

    Reader Interpretation Impact:
    <text>
    ─────────────────────────────────────────
    """

    # Section header patterns
    _SECTION_PATTERNS = {
        "overall":       re.compile(r"Overall Observation\s*:\s*", re.IGNORECASE),
        "tone":          re.compile(r"Tone Differences\s*:\s*", re.IGNORECASE),
        "emphasis":      re.compile(r"Emphasis Differences\s*:\s*", re.IGNORECASE),
        "language":      re.compile(r"Language Signals\s*:\s*", re.IGNORECASE),
        "interpretation":re.compile(r"Reader Interpretation Impact\s*:\s*", re.IGNORECASE),
    }

    # Bullet line: "- Label: content"  or  "- content"
    _BULLET_LABELED = re.compile(r"^[-•]\s*(.+?)\s*:\s*(.+)$")
    _BULLET_PLAIN   = re.compile(r"^[-•]\s*(.+)$")

    def parse(self, raw_text: str) -> FramingResult:
        """
        Main method. Takes the raw LLM string and returns a FramingResult.
        Falls back gracefully if any section is missing.
        """
        result = FramingResult(raw=raw_text)

        sections = self._split_into_sections(raw_text)

        result.overall_observation   = self._extract_plain_text(sections.get("overall", ""))
        result.tone_differences      = self._extract_bullet_pairs(sections.get("tone", ""), ToneDifference, "source", "observation")
        result.emphasis_differences  = self._extract_bullet_pairs(sections.get("emphasis", ""), EmphasisDifference, "source", "focus")
        result.language_signals      = self._extract_language_signals(sections.get("language", ""))
        result.reader_interpretation = self._extract_plain_text(sections.get("interpretation", ""))

        return result

    # -----------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------

    def _split_into_sections(self, text: str) -> dict:
        """
        Splits the full LLM response into a dict of section_name -> raw_content.
        Uses the known section headers as delimiters.
        """
        # Build a combined pattern to find all headers and their positions
        header_map = {}   # position -> (section_key, match)
        for key, pattern in self._SECTION_PATTERNS.items():
            for m in pattern.finditer(text):
                header_map[m.end()] = (key, m)

        if not header_map:
            return {}

        sorted_positions = sorted(header_map.keys())
        sections = {}

        for i, start_pos in enumerate(sorted_positions):
            key, _ = header_map[start_pos]
            end_pos = sorted_positions[i + 1] - len(
                list(self._SECTION_PATTERNS.values())[0].pattern   # rough end boundary
            ) if i + 1 < len(sorted_positions) else len(text)

            # Slice content between this header and the next
            next_start = sorted_positions[i + 1] if i + 1 < len(sorted_positions) else len(text)
            # Walk back from next_start to exclude the next header text
            raw_section = text[start_pos:next_start]
            # Trim anything after the next section header keyword
            for other_key, other_pattern in self._SECTION_PATTERNS.items():
                if other_key == key:
                    continue
                m = other_pattern.search(raw_section)
                if m:
                    raw_section = raw_section[:m.start()]

            sections[key] = raw_section.strip()

        return sections

    def _extract_plain_text(self, section: str) -> str:
        """Returns cleaned plain text from a section (no bullets)."""
        lines = [l.strip() for l in section.splitlines() if l.strip()]
        # Drop lines that look like bullet points
        lines = [l for l in lines if not l.startswith("-") and not l.startswith("•")]
        return " ".join(lines).strip()

    def _extract_bullet_pairs(self, section: str, cls, key_field: str, value_field: str) -> list:
        """
        Parses bullet lines of the form '- Label: content'
        into a list of dataclass instances.
        """
        results = []
        for line in section.splitlines():
            line = line.strip()
            m = self._BULLET_LABELED.match(line)
            if m:
                results.append(cls(**{key_field: m.group(1).strip(), value_field: m.group(2).strip()}))
        return results

    def _extract_language_signals(self, section: str) -> LanguageSignals:
        """
        Parses the Language Signals section into emotional and speculative lists.
        Handles lines like:
          - Emotional wording: "surged", "crisis" (BBC)
          - Speculative wording: "could trigger" (Reuters)
        """
        signals = LanguageSignals()
        for line in section.splitlines():
            line = line.strip()
            m = self._BULLET_LABELED.match(line)
            if not m:
                continue
            label   = m.group(1).lower()
            content = m.group(2).strip()
            examples = [x.strip().strip('"') for x in content.split(",") if x.strip()]

            if "emotional" in label or "emotion" in label:
                signals.emotional_wording.extend(examples)
            elif "speculative" in label or "speculation" in label:
                signals.speculative_wording.extend(examples)

        return signals

    def to_dict(self, result: FramingResult) -> dict:
        """Serialises a FramingResult to a plain dict for JSON responses."""
        return {
            "overall_observation": result.overall_observation,
            "tone_differences": [
                {"source": t.source, "observation": t.observation}
                for t in result.tone_differences
            ],
            "emphasis_differences": [
                {"source": e.source, "focus": e.focus}
                for e in result.emphasis_differences
            ],
            "language_signals": {
                "emotional_wording":   result.language_signals.emotional_wording,
                "speculative_wording": result.language_signals.speculative_wording,
            },
            "reader_interpretation": result.reader_interpretation,
        }


# -----------------------------------------------------------
# Quick test
# -----------------------------------------------------------

if __name__ == "__main__":
    sample_llm_output = """
FRAMING COMPARISON

Overall Observation:
Coverage of the Fed rate hike varies notably in emotional register. One outlet adopts a measured, explanatory tone while the other leans on urgency and risk. Both report the same factual event but construct different reader experiences through word choice and emphasis.

Tone Differences:
- BBC News: Uses neutral, process-oriented language, describing the move as "cautious" and "measured," evoking stability rather than alarm.
- Fox Business: Employs anxiety-driven framing, with phrases like "braces for impact" and "raising fears" that foreground investor concern.

Emphasis Differences:
- BBC News: Focuses on the Fed's rationale and inflation management, framing the hike as a deliberate policy tool.
- Fox Business: Highlights potential economic downsides, centering the narrative on recession risk and investor sentiment.

Language Signals:
- Emotional wording: "braces for impact" (Fox Business), "aggressive tightening" (Fox Business), "cautious" (BBC News)
- Speculative wording: "could slow growth" (BBC News), "will tip the economy into recession" (Fox Business)

Reader Interpretation Impact:
Readers of BBC News may come away viewing the rate hike as a routine, carefully managed policy decision. Readers of Fox Business may perceive the same event as a more urgent economic threat, given the heavier use of risk-oriented and speculative language.
"""

    parser = OutputParser()
    result = parser.parse(sample_llm_output)

    print("=== PARSED FRAMING RESULT ===\n")
    print(f"Overall:\n  {result.overall_observation}\n")
    print("Tone Differences:")
    for t in result.tone_differences:
        print(f"  [{t.source}] {t.observation}")
    print("\nEmphasis Differences:")
    for e in result.emphasis_differences:
        print(f"  [{e.source}] {e.focus}")
    print("\nLanguage Signals:")
    print(f"  Emotional:   {result.language_signals.emotional_wording}")
    print(f"  Speculative: {result.language_signals.speculative_wording}")
    print(f"\nReader Interpretation:\n  {result.reader_interpretation}")

    print("\n=== AS DICT (for JSON response) ===")
    import json
    print(json.dumps(parser.to_dict(result), indent=2))
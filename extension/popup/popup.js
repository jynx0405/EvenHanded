// ─────────────────────────────────────────
// Even Handed – popup.js
// Calls the FastAPI backend and renders
// the structured framing comparison.
// ─────────────────────────────────────────

const API_URL = "http://localhost:8000/analyze";

// ── State management ──────────────────────

const states = ["idle", "loading", "error", "result"];

function showState(name) {
  states.forEach(s => {
    const el = document.getElementById(`state-${s}`);
    el.classList.toggle("active", s === name);
  });
}

// ── Render helpers ────────────────────────

function renderList(ulId, items, keyField, valueField) {
  const ul = document.getElementById(ulId);
  ul.innerHTML = "";
  items.forEach(item => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="source-name">${escHtml(item[keyField])}</span>
      <span class="source-text">${escHtml(item[valueField])}</span>
    `;
    ul.appendChild(li);
  });
}

function renderTags(containerId, words) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  if (!words || words.length === 0) {
    container.innerHTML = `<span class="tag" style="opacity:0.5">none detected</span>`;
    return;
  }
  words.forEach(word => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = word;
    container.appendChild(tag);
  });
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── Render full result ────────────────────

function renderResult(data) {
  // Overall observation
  document.getElementById("overall-observation").textContent =
    data.overall_observation || "No overview available.";

  // Tone differences
  renderList("tone-list", data.tone_differences || [], "source", "observation");

  // Emphasis differences
  renderList("emphasis-list", data.emphasis_differences || [], "source", "focus");

  // Language signals
  const signals = data.language_signals || {};
  renderTags("emotional-tags",   signals.emotional_wording   || []);
  renderTags("speculative-tags", signals.speculative_wording || []);

  // Reader interpretation
  document.getElementById("reader-interpretation").textContent =
    data.reader_interpretation || "No interpretation available.";

  showState("result");
}

// ── Fetch from backend ────────────────────

async function analyzeCurrentTab() {
  showState("loading");

  try {
    // Get the current tab URL to pass as context
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Build a minimal request payload.
    // In the full integration, the NLP pipeline will populate this.
    // For now we send the tab URL so the backend knows what's being analyzed.
    const payload = {
      event_description: tab.title || "Current news article",
      articles: [
        // Placeholder — replace with real NLP-enriched articles from your pipeline
        {
          source: "Source A",
          headline: tab.title || "Article headline",
          summary: "Summary pending NLP extraction.",
          features: {
            sentiment: "neutral",
            emotions: [],
            speculative_language: [],
            loaded_terms: [],
            key_entities: []
          }
        }
      ]
    };

    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${response.status}`);
    }

    const data = await response.json();

    // data.framing_comparison is the structured dict from OutputParser
    renderResult(data.framing_comparison);

  } catch (err) {
    document.getElementById("error-message").textContent =
      err.message || "Could not reach the analysis server.";
    showState("error");
  }
}

// ── Event listeners ───────────────────────

document.getElementById("btn-analyze").addEventListener("click", analyzeCurrentTab);

document.getElementById("btn-retry").addEventListener("click", analyzeCurrentTab);

document.getElementById("btn-reset").addEventListener("click", () => showState("idle"));
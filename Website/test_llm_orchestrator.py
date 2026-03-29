# test_llm_orchestrator.py
import json
from llm_orchestrator import generate_prompt, call_llm

def test_generate_prompt():
    print("=" * 50)
    print("TEST: generate_prompt")
    print("=" * 50)
    
    mock_articles = [
        {
            "source": "NewsNetwork A",
            "headline": "Historic Economic Policy Fails to Deliver",
            "summary": "The new policy announced by the government today disappointed markets.",
            "features": {
                "sentiment": -0.45,
                "emotion": "anger",
                "speculative_words": ["could", "appears"],
                "loaded_words": ["fails", "disappointed"],
                "entities": ["Government", "Markets"]
            }
        },
        {
            "source": "GlobalTimes B",
            "headline": "Bold New Policy Paves Way for Growth",
            "summary": "A comprehensive economic framework was unveiled, aiming at long-term stability.",
            "features": {
                "sentiment": 0.65,
                "emotion": "optimism",
                "speculative_words": ["aiming", "expected"],
                "loaded_words": ["bold", "comprehensive"],
                "entities": ["Government"]
            }
        }
    ]
    
    messages = generate_prompt("TOPIC_COMPARISON", "India Economic Policy", mock_articles)
    print("Generated Prompt Structure:")
    print(json.dumps(messages, indent=2))
    
    print("\n" + "=" * 50)
    print("TEST: call_llm (Gemini API)")
    print("=" * 50)
    print("Calling Gemini... (make sure GEMINI_API_KEY is set in your environment)")
    
    # This will use the GEMINI_API_KEY environment variable. 
    # Alternatively, you can pass it directly: call_llm(messages, api_key="YOUR_KEY")
    response = call_llm(messages)
    print("\n--- GEMINI RESPONSE ---")
    print(response)
    
if __name__ == "__main__":
    test_generate_prompt()

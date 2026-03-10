# Even Handed

A Chrome extension that helps readers understand how different news outlets
frame the same real-world event.

---

## Folder Structure

```
even-handed/
│
├── backend/                        # FastAPI server
│   ├── __init__.py
│   └── main.py                     # /analyze endpoint + LLM call
│
├── prompt/                         # LLM reasoning layer (Member 4)
│   ├── __init__.py
│   ├── system_prompt.py            # System instructions for the LLM
│   ├── input_builder.py            # Formats NLP data into prompt string
│   └── output_parser.py            # Parses LLM response into structured dict
│
├── extension/                      # Chrome extension frontend
│   ├── manifest.json               # Chrome extension config
│   ├── icons/                      # Extension icons (16, 48, 128px)
│   └── popup/
│       ├── popup.html              # Extension UI panel
│       ├── popup.js                # Calls backend, renders results
│       └── popup.css               # Styles
│
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_input_builder.py
│   ├── test_output_parser.py
│   └── test_prompt_engine.py
│
├── .env.example                    # Environment variable template
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Setup (Ubuntu)

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd even-handed

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy English model
python -m spacy download en_core_web_sm

# 5. Set your API key
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY

# 6. Run the server
uvicorn backend.main:app --reload
```

Server runs at: http://localhost:8000
API docs at:    http://localhost:8000/docs

---

## Running Tests

```bash
pytest tests/ -v
```
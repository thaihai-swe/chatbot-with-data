## Backend startup:

# 1. Activate the Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Start the backend server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

## Frontend startup:

# In a new terminal, from the root directory
cd frontend

# 1. Install Node dependencies
npm install

# 2. Start the dev server
npm run dev

## Testing Guide

| Test Goal | Question to Ask | Why it tests the mode |
|-----------|-----------------|----------------------|
| Keyword Test | "What should I do if I see ERR-999-X?" | Tests exact string matching for unique technical codes. |
| Semantic Test | "Tell me about using this device in dense air or deep underground." | Tests meaning-based retrieval (the file mentions "high-pressure" and "subterranean" but not "dense air"). |
| Hybrid Test | "Explain the low latency capabilities of the Nexus-7-Alpha." | Tests the combination of a specific product name (keyword) and a functional concept (semantic). |
| Settings Test | "What is the Shadow-Link protocol?" | Try asking this with alpha=0 (Keyword only) vs alpha=1 (Semantic only) to see how the ranking changes. |

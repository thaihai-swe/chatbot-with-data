- Backend startup:
# 1. Activate the Python virtual environment
source .venv/bin/activate

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Start the backend server
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Frontend startup:
# In a new terminal, from the root directory
cd frontend

# 1. Install Node dependencies
npm install

# 2. Start the dev server
npm run dev

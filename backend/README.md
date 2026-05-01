# Life Science Data Platform Backend

FastAPI backend for the Life Science Data Platform.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export DATABASE_URL=postgresql://localhost:5432/lifescience
   ```

4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API

- `GET /` - Returns API version info

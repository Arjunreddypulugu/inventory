# Inventory Backend (FastAPI + SQL Server)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables (Render dashboard or .env for local):
   - DB_USER
   - DB_PASSWORD
   - DB_SERVER
   - DB_NAME

3. Run locally:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoint
- `POST /inventory/add` — Add a new inventory item

## Deployment on Render
- Use a **Web Service**
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
- Set environment variables in Render dashboard 
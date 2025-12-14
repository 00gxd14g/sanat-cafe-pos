# ÖzlüceSanat SimplePOS Backend (FastAPI)

## Run (Windows / localhost)

```powershell
cd simplepos-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Frontend integration
Replace your mock ApiService with real calls (recommended):
- GET  /api/tables
- GET  /api/categories
- GET  /api/products?category_id=...
- POST /api/orders
- GET  /api/reports/daily/stats?date=YYYY-MM-DD
- GET  /api/reports/daily/sales?date=YYYY-MM-DD

## Printing
- By default it tries Windows RAW printing via pywin32 (if installed).
- If pywin32 isn't installed, it writes receipt bytes into `./print_spool/` (still OK for dev).

Set printer names in `.env` or via:
- GET/PUT `/api/settings/printers`

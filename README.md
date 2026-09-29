# PocketSmart AI

Complete FastAPI + Jinja2 + Gemini budget/recommendation assistant based on the supplied specification.

## Includes
- Home Interior Planner
- Party Budget Planner
- Jewelry Planner with optional image
- Gemini integration with fallback recommendations
- Register/Login/Logout
- JWT token endpoint
- Session information
- Recommendation history
- SQLite database
- Responsive frontend
- Upload validation
- API documentation

## Windows / VS Code

```powershell
cd $HOME\Downloads\PocketSmartAI
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your Gemini API key.

Run:
```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

Never put your API key in frontend code or commit `.env`.

# AI Product Requirement Generator

College GenAI project that turns a short product idea into a structured Product Requirements Document (PRD).

Phase 1: FastAPI backend foundation  
Phase 2: Gemini-backed PRD generation (this phase)

## Setup

### 1. Create a virtual environment and install dependencies

```powershell
cd C:\Shourya\ai-product-requirement-generator
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, skip it and use `.\.venv\Scripts\python.exe` and `.\.venv\Scripts\pip.exe` instead.

### 2. Create the `.env` file

Copy the example file, then edit the copy:

```powershell
copy .env.example .env
```

Open `.env` and set `GEMINI_API_KEY` to your real key from [Google AI Studio](https://aistudio.google.com/apikey).

Example:

```
APP_NAME=AI Product Requirement Generator
DEBUG=false
HOST=127.0.0.1
PORT=8000
GEMINI_API_KEY=your-real-key-here
GEMINI_MODEL=gemini-2.5-flash
```

Rules:

- Put the key **only** in `.env`, never in source code.
- `.env` is gitignored. Do not commit it.
- `GEMINI_MODEL` is optional. `gemini-2.5-flash` is the default.

### 3. Run the server

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API should be at `http://127.0.0.1:8000`.

### 4. Run tests

```powershell
pytest
```

Tests mock Gemini, so they do not need a real API key.

## How to test the API

### Health (Phase 1)

Browser: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Interactive docs

Browser: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

To try PRD generation:

1. Open `/docs`.
2. Find `POST /api/v1/prd/generate`.
3. Click **Try it out**.
4. Use a body like:

```json
{
  "product_idea": "I want to build an app where college students can find tutors."
}
```

5. Click **Execute**.
6. You should get structured JSON with PRD sections (not Markdown).

### PowerShell example

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/prd/generate -ContentType "application/json" -Body '{"product_idea":"I want to build an app where college students can find tutors."}'
```

Empty or missing `product_idea` should return HTTP 422.

# Ajaia Docs

A lightweight collaborative document editor: create and edit rich-text documents, import `.txt` / `.md` files, and share documents with other users.

**Live app:** https://ajaia-docs-rust-rho.vercel.app
**Live API:** https://ajaia-docs-api-ev2i.onrender.com (health check: `/health`)

> The API runs on Render's free plan, so the first request after a period of inactivity can take up to ~50 seconds while it wakes up.

## Test accounts

Authentication is mocked: pick a user from the **"Signed in as"** dropdown in the top-right corner. No password is needed.

| User | Email |
|---|---|
| Alice Owner | `alice@ajaia.test` |
| Bob Reviewer | `bob@ajaia.test` |
| Carol Editor | `carol@ajaia.test` |

**Quick demo:** sign in as Alice, create a document, share it with `bob@ajaia.test`, then switch to Bob. It appears under **Shared with me**. Carol cannot see it.

## Features

- Create, rename, edit and save documents
- Rich text: bold, italic, underline, H1/H2 headings, bulleted and numbered lists
- Documents persist in PostgreSQL and reopen with formatting intact
- Import `.txt` and `.md` files (max 1 MB) as new editable documents; Markdown headings and lists are preserved
- Sharing: only the owner can share; the dashboard separates **My documents** and **Shared with me**
- Validation and clear error messages (empty title, unsupported file type, unknown email, no access)
- Automated API tests (pytest)

## Tech stack

- **Frontend:** React 19 + Vite, TipTap editor (deployed on Vercel)
- **Backend:** Python, FastAPI, SQLAlchemy 2, Pydantic v2 (deployed on Render)
- **Database:** PostgreSQL on Neon (production), SQLite (local development and tests)

## Run locally

Requirements: Python 3.11+ and Node.js 18+.

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate      macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000 (interactive docs at http://localhost:8000/docs). With no `DATABASE_URL` set, it uses a local SQLite file and seeds the three demo users on startup.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend calls `http://localhost:8000` by default.

### Environment variables

| Where | Variable | Purpose |
|---|---|---|
| backend | `DATABASE_URL` | Postgres connection string (optional locally; defaults to SQLite) |
| backend | `CORS_ORIGINS` | Comma-separated allowed origins (default `*`) |
| frontend | `VITE_API_URL` | Backend URL (default `http://localhost:8000`) |

See `backend/.env.example` and `frontend/.env.example`. Real `.env` files are git-ignored.

## Run tests

```bash
cd backend
python -m pytest -q
```

Expected: `4 passed`. The tests cover sharing and access control, Markdown upload, rejection of unsupported file types, and user/title validation.

## Project structure

```
backend/
  app/
    main.py       # API routes, access control, file import
    models.py     # User, Document, DocumentShare tables
    schemas.py    # Request/response validation
    database.py   # DB connection (SQLite or Postgres)
  tests/test_api.py
frontend/
  src/
    App.jsx         # User picker + page switching
    Dashboard.jsx   # Document lists, create, import
    EditorPage.jsx  # TipTap editor, toolbar, save, share panel
    api.js          # API client
```

More detail: [ARCHITECTURE.md](ARCHITECTURE.md) · [AI_WORKFLOW.md](AI_WORKFLOW.md) · [SUBMISSION.md](SUBMISSION.md)

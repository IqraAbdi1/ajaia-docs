# Submission: Ajaia Docs

**Candidate:** Iqra Abdirizak Mohamed

| | Link |
|---|---|
| Live app | https://ajaia-docs-rust-rho.vercel.app |
| Live API (health check) | https://ajaia-docs-api-ev2i.onrender.com/health |
| Source code | https://github.com/IqraAbdi1/ajaia-docs |
| Walkthrough video | https://www.loom.com/share/fb28debcf60841408dbeed96cca815da |

> The API runs on Render's free plan, so the first request after inactivity can take up to ~50 seconds to wake up.

## Test accounts

Login is simulated: pick a user from the **"Signed in as"** dropdown (top right). No password needed.

| User | Email |
|---|---|
| Alice Owner | `alice@ajaia.test` |
| Bob Reviewer | `bob@ajaia.test` |
| Carol Editor | `carol@ajaia.test` |

**To test sharing:** sign in as Alice → create a document → share it with `bob@ajaia.test` → switch to Bob (it appears under **Shared with me**) → switch to Carol (she cannot see it).

## What's included

| Item | Location |
|---|---|
| Source code | `backend/`, `frontend/` |
| Setup and run instructions | `README.md` |
| Architecture note | `ARCHITECTURE.md` |
| AI workflow note | `AI_WORKFLOW.md` |
| Automated tests | `backend/tests/test_api.py` (4 tests) |
| Sample files for upload | `sample-files/plan.md`, `sample-files/meeting-notes.txt` |
| Walkthrough video link | `VIDEO_LINK.txt` |

## Run locally

Requirements: Python 3.11+ and Node.js 18+.

```bash
# Backend (http://localhost:8000)
cd backend
python -m venv venv
venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (http://localhost:5173), in a second terminal
cd frontend
npm install
npm run dev

# Tests
cd backend
python -m pytest -q             # expected: 4 passed
```

Locally the backend uses SQLite automatically and seeds the three demo users. No `.env` is needed.

## What works

- Create, rename, edit, save and reopen documents
- Rich text: bold, italic, underline, H1/H2 headings, bulleted and numbered lists
- Persistence in PostgreSQL (Neon); formatting preserved as HTML
- Import of `.txt` and `.md` files (max 1 MB) as new editable documents
- Owner-only sharing by email; separate **My documents** and **Shared with me** lists; users without access get "not found"
- Validation and clear error messages (empty title, wrong file type, unknown email)
- 4 passing automated API tests
- Live deployment: Vercel (frontend) + Render (API) + Neon (database), all free

## What's incomplete or simplified

- Authentication is simulated (user picker), as the brief allowed
- No real-time collaboration; the last save wins
- Shared users can edit; there are no viewer/editor roles and no way to remove access
- Only `.txt` and `.md` import; no `.docx` or export
- Manual save (button + Ctrl+S), no autosave

## Next 2–4 hours

1. Real authentication (sign-up/login with hashed passwords + JWT)
2. Viewer vs editor permissions, and removing someone's access
3. Autosave, so users don't lose work if they forget to click Save

## Note on timing

The assessment portal timed out on my first attempt to start (around 9:10 AM EAT). The timer started successfully at about 9:24 AM EAT.

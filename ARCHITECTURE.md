# Architecture Note

## Overview

```
React + TipTap (Vercel)  --HTTPS/JSON-->  FastAPI (Render)  --SQL-->  PostgreSQL (Neon)
```

The frontend is a single-page React app. The backend is a small REST API. Both are deployed separately and connected through the `VITE_API_URL` and `CORS_ORIGINS` settings.

## Key decisions

**1. Store documents as HTML.**
TipTap produces HTML, so documents are saved as an HTML string in one `content` column. Saving and reopening keeps all formatting with no conversion step. *Trade-off:* this is not ideal for real-time merging (a JSON/CRDT format would be better), but it is the simplest correct option for this scope.

**2. Three tables.**
- `users` (id, name, email)
- `documents` (title, content, owner_id, timestamps)
- `document_shares` (document_id, user_id), with a unique constraint so the same user cannot be shared twice

"Owned vs shared" comes straight from these tables: owned = `owner_id` is me; shared = a row in `document_shares` for me.

**3. Access control on the server.**
Every document request goes through one check: the user must be the owner or have a share row. Otherwise the API returns **404**, so users cannot discover documents they don't have access to. Only the owner can share (**403** otherwise). Shared users can view and edit.

**4. Mocked authentication.**
The brief allows simplified auth. Users are seeded on startup, and the frontend sends the selected user's id in an `X-User-Id` header. This kept the time on the core document and sharing features. *Not production-safe.* Real auth would replace this header with a verified session or JWT.

**5. File import: `.txt` and `.md` only.**
Uploads are converted on the server into a new document: Markdown is rendered to HTML, and plain text is HTML-escaped into paragraphs. There is a 1 MB limit, UTF-8 is required, and other types are rejected with a clear message. `.docx` was left out to save time.

**6. One codebase, two databases.**
SQLite is used locally and in tests (zero setup); Postgres on Neon is used in production (persistent; free hosting disks reset). `DATABASE_URL` switches between them.

## What I prioritised

Core editing → persistence → sharing with correct access rules → file import → validation and tests → deployment. Each step was working end-to-end before starting the next.

## Deliberately out of scope

- Real-time collaboration (multiple cursors, live sync)
- Comments, suggestions and version history
- Viewer vs editor roles (shared users can all edit)
- Real authentication
- `.docx` / PDF import and export
- Autosave (manual Save button + Ctrl+S, with an unsaved-changes indicator)

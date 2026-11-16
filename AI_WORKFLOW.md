# AI Workflow Note

## Tools used

- **Claude** (Anthropic): planning, generating the backend and frontend code, debugging, deployment guidance, and drafting documentation.

## How I worked with AI

I acted as the architect and reviewer, and used AI as a fast pair programmer. I chose the stack (Python/FastAPI, as Python is my strongest language), defined the scope, ran every command myself, tested the app in the browser, and made the deployment decisions.

## Where AI sped things up

- Scaffolding the FastAPI backend (models, validation, routes) and the React + TipTap editor in minutes instead of hours
- Writing the pytest tests for sharing, upload and validation
- Step-by-step deployment to Neon, Render and Vercel
- Drafting the README and notes

## Decisions I made (and AI suggestions I accepted or rejected)

- **Scope:** I rejected adding real-time collaboration, comments and real auth, to deliver a smaller app that works fully within the time limit.
- **Database:** I built with SQLite (simple, no setup), but free hosting wipes local files, so for the live version I chose Neon Postgres (free and permanent). The same code works with both.
- **Deployment:** I chose Vercel (frontend) + Render (backend) + Neon (database) because all three are free, so reviewers don't need to pay for anything.
- **Security:** I insisted on checking for secrets (`git status` + `git grep`) before pushing, and gave Vercel and Render access to this repo only, not my other private repositories.

## Issues found and fixed during the build

The AI's first version wasn't perfect. The automated tests and warnings caught these issues, and they were fixed:

- The email check rejected the demo emails (like `bob@ajaia.test`), so it was replaced with a simpler format check.
- An outdated FastAPI startup method (`on_event`) was replaced with the current `lifespan` approach.
- A duplicate editor plugin (Underline) that conflicted with the editor's built-in version was removed.

## How I verified the output

- Ran `pytest` locally: 4 tests passing
- Ran the app locally and tested every flow myself: create, format, save, refresh, share, switch users, import
- Checked that no secrets were committed (`git status` review and `git grep` for key patterns) before pushing
- Re-tested the full flow on the live deployment
- Noticed that a document I created locally didn't appear on the live site, and confirmed why: local uses a SQLite file and live uses the Neon database, so they are separate by design


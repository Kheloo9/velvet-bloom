# SETUP — Velvet Bloom local development

## 1. Assumptions
A machine with Python 3.12, a terminal, and a browser. Tested on this Linux VM with
Python 3.12.3. No Node, Docker, database server or API key is needed.

## 2. Get the project
Copy the `velvet-bloom/` folder to your machine. No repository URL is invented here —
if the folder came as a zip, unzip it and cd into it.

## 3. Install dependencies (verified)
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt   # Flask only
```
Note: system pip may refuse on externally-managed Python (PEP 668); the venv route
above is the verified path. Do not use --break-system-packages.

## 4. Environment file
No .env file is needed. Variables (placeholders only, never real values):
```
VELVET_SECRET_KEY=your-own-random-secret-here   # placeholder only, never a real value
VELVET_ADMIN_PASSWORD=your-own-private-admin-password-here   # placeholder only
```
If VELVET_SECRET_KEY is unset, the app generates a fresh random secret per process
— fine locally (sessions reset on restart); set the variable for persistent
sessions. There is no hardcoded fallback key. If VELVET_ADMIN_PASSWORD is unset,
no admin is seeded, and no admin password is hardcoded anywhere in the repo.

## 5. Required variables
VELVET_SECRET_KEY and VELVET_ADMIN_PASSWORD (optional locally, required before
shared use). No database, payment or LLM credentials are required for the MVP.
Never paste a secret into chat or git.

## 6. Database
None to install. On first run, app.py creates velvet.db (SQLite) and seeds 14 sample
perfumes and 8 sample reviews, plus an admin only if VELVET_ADMIN_PASSWORD
is set. To reset: delete velvet.db, restart.

## 7. Start / stop
```
sh run.sh
# or: .venv/bin/python app.py
```
Open http://127.0.0.1:5000. Stop with Ctrl+C (or kill the python process).

## 8. Tests, lint, build, format
- Tests: `.venv/bin/python tests/test_app.py` (17 checks after the 5-team round).
- Lint/type/build/format: none configured — deliberately, to keep the project light.
  Adding them is future work, not a hidden requirement.

## 9. Common errors
- 'No module named flask' -> you are not using .venv/bin/python; use run.sh.
- 'Address already in use' (port 5000) -> stop the old server first.
- 'Database is locked' -> only one app process should run at a time.
- Blank catalog -> delete velvet.db and restart to re-seed.

## 10. Health check
Open http://127.0.0.1:5000 (200, featured perfumes), /catalog (200, 14 perfumes),
/finder (submit fresh/university/4000 -> ranked results with reasons), /api/chat
(POST a question -> catalog answer). Commands marked above were run and verified
except the phone-width visual check, which is a manual gap (TESTING.md).

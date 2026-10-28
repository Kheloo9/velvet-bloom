# AGENTS — AI coding rules for Velvet Bloom

## 1. Read first
PRD.md, DESIGN.md, ARCHITECTURE.md, DATABASE.md, API.md, then app.py and data.py.
This project is a friend's FYP demo — never mix it with Quran Shazam code or data.

## 2. Stack and conventions
Python 3.12, Flask only (requirements.txt), SQLite, Jinja2 templates, no JS framework,
no build step. Files: app.py (routes), data.py (scoring/DNA/sentiment), templates/*,
static/style.css. Naming: snake_case Python, lowercase routes, Rs prices as integers.

## 3. Commands (verified, from this repo)
- Create/run: `sh run.sh`  (creates .venv, installs Flask, runs app.py on 127.0.0.1:5000)
- Or manually: `.venv/bin/python app.py`
- Tests: `.venv/bin/python tests/test_app.py`  (17 checks after the 5-team round; no pytest dependency needed)
- DB reset: delete velvet.db and restart — it re-seeds (demo data only).

## 4. Coding standards
Smallest coherent change; server-side validation for every input; Jinja autoescaping
kept on; never put a secret, price or role decision in frontend code; keep the demo
disclaimers (footer, checkout) intact.

## 5. Security rules
Never commit secrets; never weaken an auth check to make a test pass; validate on the
server; protect private data (there is no payment data — keep it that way); never
store a plaintext password (werkzeug generate_password_hash only).

## 6. Change rules
DB change: update init_db + DATABASE.md + seed. API change: update API.md + tests.
New dependency: justify it in ARCHITECTURE.md first; prefer none. Env vars: document
in SETUP.md with placeholder values only.

## 7. Workflow per task
Understand requirement -> inspect relevant code -> smallest change -> add/update a
test -> run tests -> review the diff -> summarise evidence (files + actual results).

## 8. Honesty rule
Never claim tests pass unless they were run and their output inspected. Never claim
the site is secure or production-ready — see AUTH.md residual risks.

## 9. Roles
Implementer: writes code + tests. Tester: runs tests, reports failures honestly.
Reviewer: checks auth, prices, and docs-vs-code consistency; does not blindly approve.

## 10. Ambiguity / broken builds / credentials
If a detail is unknown, make a sensible default and LABEL it as an assumption in the
docs (as this build does). If the build breaks, fix the code or the genuinely wrong
test with an explanation — never delete a test to go green. No external credentials
are needed for this MVP.

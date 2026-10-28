# Velvet Bloom — AI Perfume E-Commerce + Recommendation (DEMO)

## What it is and who it is for
A friend's FYP demo (NOT the user's Quran Shazam project): a perfume shop where buyers
browse a catalog and get AI-style help — a preference finder, a quiz, a DNA matcher,
a fragrance profile and a catalog-aware chatbot. The admin manages perfumes, stock
and demo orders. All products are fictional SAMPLE/DEMO data; no real brands,
testimonials or customer data are used.

## Status: implemented vs planned
Implemented: catalog/search/filters, product details, cart, Demo/COD checkout, orders,
wishlist, signup/login, admin CRUD + order status, AI finder, quiz, DNA matcher,
explainable recommendations, fragrance profile, rule-based chatbot, review sentiment.
Planned / NOT built: real payment, LLM chatbot (optional future step, MCP.md), image
discovery, behaviour-based recommendations, email, live weather.

## Stack and architecture
Python + Flask + SQLite + server-rendered HTML/CSS/JS. No JS framework, no build step.
See ARCHITECTURE.md. Only dependency: Flask.

## Prerequisites
Python 3.12 (tested with 3.12.3). No Node, no database server, no API keys.

## Local setup (verified)
```
sh run.sh
# or: .venv/bin/python app.py
```
Then open http://127.0.0.1:5000 — the DB (velvet.db) is created and seeded on first run.

## Environment variables (placeholders only, no real values)
- VELVET_SECRET_KEY — Flask session secret. Optional for local demo: if unset, the
  app generates a fresh random secret per process (sessions reset on restart).
  Set it for persistent sessions; there is NO hardcoded fallback key (see AUTH.md).

## Demo accounts (DEMO ONLY — never publish a real admin password)
- Admin: set privately with VELVET_ADMIN_PASSWORD before first run (placeholder
  only, never a real value in code or docs), then log in as admin@velvet.demo.
  With no VELVET_ADMIN_PASSWORD set, no admin is seeded.
- Customers: register a new account on /register (passwords are hashed).

## Commands
- Run: `sh run.sh` or `.venv/bin/python app.py`
- Tests: `.venv/bin/python tests/test_app.py` (17 real checks after the 5-team round — see TESTING.md)
- Reset demo data: delete velvet.db and restart the app.

## Directory overview
app.py (routes), data.py (sample data + scoring/DNA/sentiment), templates/ (18 pages),
static/style.css, tests/test_app.py, run.sh, requirements.txt, and the 15 workflow docs
(PRD, DESIGN, ARCHITECTURE, DATABASE, API, AGENTS, README, PLAN, SETUP, FEATURES,
AUTH, MCP, INTEGRATIONS, TESTING, DEBUGGING).

## Security notes and limitations
This is a LOCAL DEMO, not production-ready and not claimed secure. See AUTH.md for
residual risks (no HTTPS, no rate limiting, no CSRF tokens, no audit log).
No admin password is printed on the login page or committed in code. Do not put
real customer or payment data into it.

## Troubleshooting
- 'flask not found': use the project venv (.venv/bin/python) or run.sh, not system pip.
- Port 5000 busy: stop the other process, or edit the port in app.py (last lines).
- Empty catalog after edits: check velvet.db exists; delete it to re-seed demo data.

## Unverified details (labelled honestly)
- No formal WCAG contrast audit has been run. No performance/load test has been run.
- No real user testing has been done; all results are from the automated checks in
  TESTING.md plus a local smoke test.

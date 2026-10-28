# PLAN — Velvet Bloom phased roadmap

## Phase 1 — Repo and tooling (Done)
Task P1-01: venv + Flask install, folder layout, run.sh. Done: Flask 3.1.3 in .venv.
Acceptance: `sh run.sh` starts the app. Test: live smoke test (TESTING.md).

## Phase 2 — Design system and shared UI (Done)
Task P2-01: base.html + style.css with plum/gold/cream tokens, mobile-first.
Acceptance: home, catalog and admin render without horizontal scroll on a phone width.
Test: manual smoke test (not automated — gap noted in TESTING.md).

## Phase 3 — Database and data access (Done)
Task P3-01: init_db, 8 tables, 14 sample perfumes, 8 sample reviews, demo admin.
Acceptance: first run creates velvet.db and seeds only when empty.

## Phase 4 — Auth and authorisation (Done)
Task P4-01: register/login/logout, hashed passwords, login_required, admin_required.
Acceptance: /admin returns 403 without admin login (tested).

## Phase 5 — Core journeys and APIs (Done)
Task P5-01: catalog/product/cart/checkout/orders/wishlist. Task P5-02: /api/chat and
/api/recommend. Acceptance: checkout total is server-verified (tested).

## Phase 6 — AI features (Done)
Task P6-01: finder scoring + reasons. P6-02: quiz -> personality. P6-03: DNA matcher.
P6-04: profile. P6-05: rule-based chatbot. P6-06: review sentiment (rule-based).
Acceptance: each returns catalog-only results with reasons (tested for finder/chat/DNA).

## Phase 7 — Admin and hardening (Done, with documented limits)
Task P7-01: admin CRUD + order status. Hardening limits (AUTH.md): no HTTPS, no rate
limit, no CSRF tokens — acceptable for a local demo, must-fix before any real use.

## Phase 8 — Testing and debugging (Done)
Task P8-01: tests/test_app.py (17 checks after the 5-team round) + live smoke
test. Real bugs found and fixed in this phase (see DEBUGGING.md). Acceptance:
17/17 checks pass.

## Phase 9 — Deployment preparation (NOT DONE — deliberately)
No deployment is included. Post-launch monitoring, backups beyond copying velvet.db,
and a production checklist are future work and are listed as must-fix items in the
release review (DEBUGGING.md §Release review). Do not deploy this demo as-is.

## Traceability
Every must-have PRD requirement (FR-001..FR-014) maps to at least one task above;
TESTING.md is the honest record of which have dedicated automated tests and which
were verified by smoke/manual checks. First small task if starting again: P1-01
(venv + hello page).
Effort estimates are deliberately not given: the user asked for the build, not a quote,
and no deadline was set.

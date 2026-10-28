# TESTING — Velvet Bloom test strategy and ACTUAL results

## Strategy
- Unit-ish: scoring, DNA similarity and sentiment live in data.py and are exercised
  through the API/page tests below (no separate unit runner was added, to keep the
  project light — a gap, not a claim).
- Integration: DB + routes + auth via Flask test client (tests/test_app.py).
- End-to-end: local live-server smoke test (curl) over the main pages and APIs.
- Negative: admin 403, empty chat message 400, bad price/stock flash, out-of-stock
  checkout rollback (code path; the rollback branch is not separately automated).
- Security: admin bypass, generic login error, server-verified checkout price.
- Accessibility/responsive: NOT formally tested (gap); manual phone-width visual
  check is still open. No animations are used; forms are labelled.
- Test data: fictional sample perfumes/reviews only; no real customer or payment data.

## Commands
```
.venv/bin/python tests/test_app.py
```

## ACTUAL results (run 2026-10-28 during this build, Flask 3.1.3, Python 3.12.3)
```
PASS test_admin_blocked_without_login
PASS test_admin_login_and_crud
PASS test_chatbot_from_catalog
PASS test_dna_matcher
PASS test_pages_200
PASS test_recommendation_in_budget
PASS test_signup_login_and_server_price
7/7 passed
```
Note: the first run was 6/7 — test_signup_login_and_server_price failed on a real
bug (template `o.items` colliding with dict.items()). The bug was fixed in app.py /
orders.html (renamed to `line_items`), not by deleting or weakening the test, and
the suite was re-run to 7/7. See DEBUGGING.md.

Live smoke test (same day, server on 127.0.0.1:5000):
- / /catalog /finder /quiz /dna /chat /login all returned HTTP 200.
- POST /api/chat 'fresh perfume for university under 4000' returned Fresh Meadow
  (Rs 3,200), Pine Trail (Rs 3,400) and Ocean Breeze (Rs 3,500) with reasons.
- POST /api/recommend (fresh/university/4000) returned Fresh Meadow first, score 75,
  with reasons including 'Within budget (Rs 3,200)'.
- Server was stopped after the smoke test; no live deployment exists.

## Coverage gaps and known limitations
- No dedicated automated tests for wishlist toggle, quiz POST, profile save, gift
  chatbot branch, or checkout rollback on low stock (code paths exist, tests do not).
- No browser-automation, accessibility, performance or load tests.
- No CSRF, rate-limit or session-expiry tests (those features do not exist — AUTH.md).
- Release-blocking failures at build time: none remaining. The one failure found was
  fixed and re-verified (above).

## Traceability (requirement -> test)
FR-001/002 -> test_pages_200; FR-003 -> signup/login + admin 403 tests;
FR-004 -> checkout test; FR-007 -> recommendation test; FR-009 -> DNA test;
FR-011 -> chatbot test; FR-012 -> admin CRUD test. FR-005/006/008/010/013/014 have
partial or manual-only coverage — see gaps above.

## 5-team professional testing round (2026-10-28, post-build)
Five independent teams tested the SAME build in isolated temp copies (no edits to
the real folder during testing), each with a different focus. All findings were
checked by the coordinator against the actual code before any fix; non-issues and
already-disclosed demo limitations were left untouched (see DEBUGGING.md).

- Team 1 Functional (66 journey checks + 8 probes): all journeys passed; found
  negative price/stock acceptance, phantom cart/wishlist ids, silent admin no-ops.
- Team 2 Security: auth guards, isolation, SQLi/XSS all held; found session forgery
  via the published fallback secret (Critical if shared), negative-price checkout,
  confirmed CSRF/rate-limit gaps (already disclosed).
- Team 3 AI correctness: scoring/DNA/named-chatbot figures all matched the catalog;
  found nondeterministic quiz ties, PRD budget-ranking contradiction, false quiz
  label on empty answers, chatbot showing only the first reason, profile clobbering.
- Team 4 UI/UX/accessibility (HTML/CSS inspection — NO live browser, so phone
  visuals remain unverified): found unlabelled catalog filters, admin table with
  no phone layout, identical page titles, admin price formatting, out-of-stock
  add-to-cart, missing admin feedback, quiz Q3 label mismatch, profile free text.
- Team 5 Code/docs/edge cases: suite reproduced 7/7; found two triggerable HTTP
  500s (huge admin numbers, non-string chat message), NULL-column crashes,
  preference clobbering, and 10 docs-vs-code mismatches.

Fixes applied (smallest coherent changes, tests added for each — see
tests/test_app.py and DEBUGGING.md): admin range validation + missing-field
handling, ephemeral session secret (no hardcoded fallback), deterministic +
validated quiz, -100 over-budget penalty (PRD §7 now true), merge-only preference
saves, all chatbot reasons, API parsing strictness, cart/wishlist existence and
stock guards, admin 404s + allowed status list + feedback flashes, labels/titles/
responsive admin table/price formatting/out-of-stock buttons, seed-data correction
(Sunset Citrus occasions), sentiment word "last", email shape check, logout
preserving the cart, and all doc mismatches corrected.

ACTUAL results after fixes (run 2026-10-28, same environment):
```
PASS test_admin_blocked_without_login
PASS test_admin_huge_price_no_crash
PASS test_admin_login_and_crud
PASS test_admin_negative_price_rejected
PASS test_api_chat_non_string_400
PASS test_budget_ranking_in_budget_first
PASS test_cart_unknown_404_and_out_of_stock
PASS test_chatbot_from_catalog
PASS test_chatbot_shows_all_reasons
PASS test_dna_matcher
PASS test_pages_200
PASS test_profile_merge_preserves_personality
PASS test_quiz_tie_deterministic_and_validated
PASS test_recommendation_in_budget
PASS test_register_at_only_rejected_and_logout_keeps_cart
PASS test_signup_login_and_server_price
PASS test_wishlist_unknown_404_and_admin_noop_404
17/17 passed
```
One failure occurred mid-round and was fixed in the TEST, not the app: a new
test changed the status of order 1 in a fresh DB where no order existed (the app
correctly 404'd). The test was corrected to place an order first; no app test
was deleted or weakened at any point.

Live smoke test after fixes (server on 127.0.0.1:5000, then stopped, DB cleaned):
/ /catalog /finder /quiz /dna /chat /login all 200, /admin 403 anonymous,
POST /api/recommend (woody/wedding/winter/strong/5000) now returns in-budget
Jasmine Glow (Rs 3,900) first, POST /api/chat returns all reasons per perfume.

Remaining gaps (honest, not fixed in this round): no CSRF tokens, no login rate
limiting, demo admin credentials printed on the login page, no FK cascade
(orphans on perfume delete), no formal WCAG/phone visual check (needs a real
browser), no true parallel-concurrency test, no note-family normalisation
(musk vs white musk). All are must-fix or must-check before any shared/public
use — see DEBUGGING.md release review update.

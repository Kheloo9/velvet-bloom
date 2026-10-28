# DEBUGGING — Velvet Bloom root-cause log and release review

## Resolved issue 1 (real, found by tests — not invented)
- Issue: test_signup_login_and_server_price failed on the first run; the orders
  page crashed after checkout.
- Reproduction: register -> login -> add to cart -> checkout -> redirect to /orders.
- Error: TypeError: 'builtin_function_or_method' object is not iterable, in
  templates/orders.html.
- Investigation: the traceback pointed at the orders template loop. The route
  stored order lines under the key 'items' on a plain dict, but in Jinja
  `o.items` resolves to the dict's built-in .items() method, not the key.
- Root cause: key name collided with a dict method in the template namespace.
- Fix (smallest appropriate): renamed the key to 'line_items' in app.py
  (orders route) and in templates/orders.html. No other behaviour changed.
- Regression test: the same test that failed now passes; full suite re-run 7/7.
- Remaining uncertainty: none for this bug. Similar collisions were checked:
  no other template uses `.items` on a dict (wishlist/orders use plain lists).

## Resolved issues 2–15 (5-team testing round, 2026-10-28)
Each finding below was verified against the real code before fixing; items judged
non-issues or already-disclosed demo limits were left untouched (listed at the end).

- Issue 2 (Critical if shared): session forgery via the published fallback secret.
  Repro: sign {"user_id": admin id} with itsdangerous using the hardcoded
  "velvet-demo-dev-key-change-me" -> GET /admin returned 200. Root cause: Flask
  sessions are signed, not encrypted, and the key was in the code. Fix: no
  hardcoded fallback — app uses VELVET_SECRET_KEY if set, else a fresh random
  secret per process (app.py). Sessions reset on restart unless the env var is
  set; documented in AUTH.md/README/SETUP. Regression: existing auth tests pass;
  forgery with a published key is impossible because no key is published.
- Issue 3 (High): admin accepted negative/absurd prices and stock; huge values
  crashed with HTTP 500 (SQLite INTEGER overflow). Root cause: admin_new/edit
  only checked int() parsing. Fix: validate_admin_perfume() — non-empty name,
  int parsing via .get() (missing field flashes instead of bare 400), ranges
  0–10,000,000 price and 0–10,000 stock. Tests: test_admin_negative_price_rejected,
  test_admin_huge_price_no_crash.
- Issue 4 (High): POST /api/chat with a non-string message crashed (HTTP 500).
  Root cause: .strip() called on an int. Fix: isinstance(msg, str) check -> 400.
  Test: test_api_chat_non_string_400.
- Issue 5 (High): quiz ties nondeterministic across processes (max over a set).
  Fix: count only known fragrance values, tie-break by earliest answer.
  Test: test_quiz_tie_deterministic_and_validated.
- Issue 6 (High): quiz empty/unknown answers showed a false "Floral Lover" label
  while ranking with fragrance="" (list started with Citrus Dawn), and saved the
  invalid value into preferences. Fix: no valid answer -> flash prompt, no
  personality claimed, nothing saved. Same test as Issue 5.
- Issue 7 (High): PRD §7 violated — over-budget items outranked in-budget items
  (match points 75 beat the -20 penalty). Fix: over-budget penalty -100 in
  data.py score_perfume (max other points 75, min in-budget score +25), so
  in-budget always ranks first; PRD §7 is now true, no doc fudge needed.
  Test: test_budget_ranking_in_budget_first; live smoke confirms Jasmine Glow
  (Rs 3,900) first for woody/wedding/winter/strong/5000.
- Issue 8 (Medium): finder/quiz/profile saves clobbered each other's preference
  fields (INSERT OR REPLACE with different column subsets). Fix: merge-only
  save_preferences() helper updating only the fields each form owns.
  Test: test_profile_merge_preserves_personality.
- Issue 9 (Medium): chatbot showed only the first reason per perfume, hiding
  criteria an item did NOT match. Fix: join all reasons. Also: cheapest branch
  now says "I only stock Velvet Bloom perfumes" (a "Chanel price?" question used
  to be answered with the cheapest list as if it were about that brand).
  Test: test_chatbot_shows_all_reasons. Residual: full brand-name detection is
  not implemented — the bot still never invents a product, price or note.
- Issue 10 (Medium): NULL perfume columns crashed catalog (occasion split),
  product (all_notes) and chat pages (HTTP 500). Fix: None-safe guards in
  data.py all_notes/score_perfume and app.py catalog filter.
- Issue 11 (Medium): cart/wishlist accepted nonexistent ids (phantom session key
  / orphan row); out-of-stock items could be added, failing only at checkout.
  Fix: cart_add/wishlist_toggle 404 unknown ids; cart_add refuses stock-0 with a
  flash; templates hide the button and show "Out of stock". Test:
  test_cart_unknown_404_and_out_of_stock, test_wishlist_unknown_404_and_admin_noop_404.
- Issue 12 (Medium): admin delete/order-status on nonexistent ids silently
  "succeeded"; order status accepted arbitrary free text. Fix: 404 for unknown
  rows, allowed-status list, success flashes on all admin actions.
  Same test as Issue 11.
- Issue 13 (Medium/Low, UI): unlabelled catalog filters and admin status input;
  identical page titles; heading skips (catalog/wishlist h1->h3); admin prices
  unformatted; admin table with no phone layout; quiz Q3 labels mismatched its
  values; profile free-text inputs vs finder selects; admin empty-orders blank
  list; no skip link / aria-current / cart count / flash role="alert"; grid
  overflow below ~284px. Fixes: labels, per-page title blocks, h2 card titles,
  Rs formatting, .table-wrap overflow, honest Q3 wording, profile selects,
  "No orders yet.", skip link, aria-current, cart count, role="alert",
  340px grid media query. Product page also gained a wishlist button.
- Issue 14 (Low): registration accepted "@" as an email; logout wiped the cart.
  Fix: email must have non-empty local/domain parts with a dot in the domain;
  logout preserves the session cart. Test:
  test_register_at_only_rejected_and_logout_keeps_cart.
- Issue 15 (Low, docs/data): Sunset Citrus had "summer" in its occasions field
  (a season, not an occasion) — corrected to party,daily; sentiment missed
  "lasts" (5-star "lasts the whole wedding night" scored neutral) — "last"
  added to positive words; 10 docs-vs-code mismatches corrected (PRD §9 MVP
  range FR-001..FR-014, PLAN traceability, FEATURES Verified wording now backed
  by dedicated tests, API.md budget parsing + session-cookie + invalid max_price
  behaviour, requirements pinned to Flask==3.1.3, test runner docstring now
  direct-runner only since pytest is not installed).

Left untouched (verified non-issues or disclosed demo limits, with reasons):
- CSRF tokens and login rate limiting: genuine gaps, already disclosed in
  AUTH.md; fixing them touches every form/route and needs a real-browser check,
  so they stay as must-fix-before-shared-use items, not silent demo changes.
- Demo admin credentials printed on the login page: kept for viva-demo usability,
  but flagged as must-change/remove before ANY shared/public link (see below).
- No FK cascade (orphan rows when a referenced perfume is deleted): disclosed in
  DATABASE.md; schema change is out of demo scope, flagged below.
- Note-family normalisation (musk vs white musk): exact matching is internally
  consistent and documented; not a defect as coded.
- No product imagery, finder returning the full ranked list, quiz/API truncation
  differences: design choices, not defects.
- Real-browser/phone visual verification and true parallel-concurrency testing:
  could not be performed by the testing subagents (no live browser); they remain
  open checks for the parent, not claims.

## Release review update (after 5-team testing, 2026-10-28)
- Release status: UNCHANGED — **Ready with clearly documented limitations, for
  LOCAL DEMO / viva demo use only. NOT Ready for production or real customers.**
- Checks passed: 17/17 automated checks (was 7/7); live smoke test (8 pages incl.
  /admin 403, both APIs catalog-correct). Checks failed: none remaining.
  Checks that could not be run: formal accessibility audit, phone-width visual
  check, load test, real-user test, true parallel-concurrency test.
- Must-fix before ANY shared/public use (in addition to the original list):
  (a) change the demo admin password AND remove it from the login page,
  (b) add CSRF protection, (c) add login rate limiting, (d) serve over HTTPS,
  (e) audit-log admin actions, (f) replace demo data, (g) real-browser phone
  check of /admin, (h) real payment only with explicit approval + sandbox tests.
  Items (a)–(c) are the ones a public link would expose first.
- Pre-deploy update (same evening): item (a) is DONE — no admin password is
  hardcoded or printed anywhere now; admin is seeded only from
  VELVET_ADMIN_PASSWORD, login page no longer shows any credential, and tests
  use a fresh random password each run (17/17 re-verified). Items (b)–(h)
  remain open and are disclosed, not claimed as done.

## Debugging workflow (for future bugs)
Reproduce -> read the full error/log -> list possible causes -> test them ->
identify root cause with evidence -> smallest fix -> regression test -> rerun
relevant checks -> review the diff -> update docs if behaviour changed. Never
suppress errors with broad try/except, never disable a security control to pass
a test, never delete a test to go green, never run destructive commands on real data.

## Release review (evidence-based, after all 15 stages)
- Release status: **Ready with clearly documented limitations — for LOCAL DEMO /
  viva demo use only. NOT Ready for production or real customers.**
- Checks passed: 7/7 automated checks; live smoke test (7 pages 200, chatbot and
  recommendation APIs returning catalog-correct answers).
- Checks failed: none remaining at build time. Checks that could not be run:
  formal accessibility audit, phone-width visual check, load test, real-user test.
- Critical/high findings: none blocking a local demo. Medium: demo secret fallback,
  demo admin password, no rate limiting, no CSRF tokens, no HTTPS, no audit log,
  no FK cascade — all documented in AUTH.md and all must be fixed before any
  shared/real use (see must-fix list).
- Low: no lint/type/format tooling; wishlist/quiz/profile/gift paths lack dedicated
  automated tests; single-file app.py will need splitting if it grows.
- Must-fix before ANY real/shared use: (1) set VELVET_SECRET_KEY, (2) change the
  demo admin password, (3) serve over HTTPS, (4) add login rate limiting,
  (5) add CSRF protection, (6) audit-log admin actions, (7) remove or replace
  demo/sample data with real data, (8) add a real payment provider only with
  explicit approval and sandbox testing.
- Missing secrets/configuration (names only, never values): VELVET_SECRET_KEY
  (for shared use). No payment or LLM keys are needed for the demo.
- Backup/migration/monitoring/rollback: backup = copy velvet.db; no migration tool
  (init_db creates tables); no monitoring (local only); rollback = stop the app
  and restore the previous velvet.db / code folder.
- Highest-value next improvements: dedicated tests for wishlist/quiz/profile/gift;
  formal accessibility check; split app.py if features grow; optional LLM chatbot
  behind the rule-based fallback (MCP.md).
- Honest statement: this site is NOT claimed '100% secure' and NOT production-ready.
  Do not deploy it or spend money on it without explicit approval.

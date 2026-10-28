# API — Velvet Bloom contract

Only two JSON endpoints exist; every other flow is an HTML form route (see FEATURES.md).
Consistent format: JSON object; errors are {"error": "..."} with an HTTP status.

## POST /api/chat
- Purpose: rule-based chatbot answer from the catalog (FR-011). Auth: not required.
- Request: {"message": "fresh perfume for university under 4000"} (string, required).
- Logic: extract budget (first 3–5 digit number), fragrance/occasion/season keywords,
  perfume name match, or 'gift'. Named perfume -> its price/stock/notes. Criteria ->
  top 3 ranked perfumes with ALL reasons each. No criteria -> guidance message.
- Success: 200 {"answer": "..."} — answer text only ever names catalog perfumes.
- Errors: 400 {"error": "message is required"} on empty, missing, or non-string
  message. No stack traces, no DB details, no tokens are ever returned.

## POST /api/recommend
- Purpose: ranked recommendations (FR-007). Auth: not required.
- Request: {"fragrance": "fresh", "occasion": "university", "max_price": 4000,
  "strength": "soft", "season": "summer"} — all optional. max_price parsing, exact:
  int or digit string accepted; an integral float is accepted; a bool is NOT a
  budget (True used to mean Rs 1); a non-integral float or other type is treated
  as 'no budget' (documented behaviour, not a crash). Unknown fields are ignored.
- Success: 200, a JSON list (max 5) of {"name", "price", "fragrance", "score", "reasons"}.
  Reasons are the explainability output of data.score_perfume. Ranking guarantee:
  with a budget given, every in-budget item ranks above every over-budget item
  (over-budget penalty -100 exceeds the maximum 75 match points).
- Errors: /api/recommend never returns an error for bad input — it returns 200
  with the ranked list (possibly unfiltered). This is deliberate for a demo API.

## HTML routes (contract summary)
- GET / /catalog /product/<id> /finder /quiz /dna /chat /cart — public, 200 or 404.
- GET/POST /register /login; GET /logout — a session cookie is set on login, and
  also when an anonymous visitor first adds to the cart (the cart lives in the
  session). GET /logout preserves the cart.
- GET/POST /checkout, GET /orders, /wishlist, /profile — login_required, else redirect
  to /login with a flash message. POST /cart/add/<id> is public (session cart) but
  404s for an unknown perfume and refuses out-of-stock items; POST
  /wishlist/toggle/<id> is login_required and 404s for an unknown perfume.
- HTML forms treat an invalid max_price (non-numeric, negative, float) as 'no
  budget', exactly as /api/recommend does; the finder additionally shows a
  "no close match" notice when nothing scores above zero.
- GET/POST /admin*, POST /admin/perfume/<id>/delete, POST /admin/order/<id>/status —
  admin_required, else 403. Admin CRUD validates price/stock as integers.
- Server-side rules (never trust the browser): order totals are recomputed from DB
  prices; roles come from the DB session user, never from a form field; stock is
  checked at checkout; admin status changes are admin-only.

## Versioning / testing checklist
No versioning (single demo version). Test checklist: see TESTING.md — pages 200,
recommendation in-budget, chatbot catalog answer, DNA match, admin 403, server price.

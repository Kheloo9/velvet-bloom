# AUTH — Velvet Bloom authentication, authorisation and security

## 1. Flows
Register (name/email/password, min 6 chars) -> login (session cookie) -> logout
(clears session). No email verification, no password reset, no OTP — deliberately
out of scope for a local demo. Admin is a seeded role, not a self-service upgrade:
no route lets a user set their own role.

## 2. Password storage
Werkzeug generate_password_hash / check_password_hash (scrypt-based by default in
the installed Werkzeug version, salted — corrected from an earlier "PBKDF2" note).
Plaintext passwords are never stored and never logged. No admin password is
committed in code or printed on the login page: the admin is seeded only from
VELVET_ADMIN_PASSWORD (private, owner-set). Tests use a fresh random password
each run, so no admin password appears anywhere in the repo.

## 3. Server-side authorisation (every protected route)
- login_required: /checkout, /orders, /wishlist, /wishlist/toggle/*, /profile.
- admin_required: /admin, /admin/perfume/*, /admin/order/*/status — returns 403
  for anonymous and non-admin users (tested).
- Orders/wishlist/profile are filtered by session user_id, so changing an ID in a
  URL cannot show another user's data (there is no per-order ID route to abuse;
  /orders lists only the caller's rows).

## 4. Sessions and cookies
Flask session cookie, HttpOnly. Secret from VELVET_SECRET_KEY if set; otherwise a
fresh random secret is generated per process (5-team fix, Oct 2026 — there is NO
hardcoded fallback secret anymore, because a published fallback let anyone forge a
session cookie and take over admin). Consequence: sessions reset on restart unless
the env var is set. No long-lived tokens, no secrets in browser storage, no secrets
in frontend code.

## 5. Rate limiting, CSRF, reset safety
NOT IMPLEMENTED (honest gap): no login rate limiting, no CSRF tokens, no password
reset flow. Safe error messages are used ('Invalid email or password' — does not
reveal which field failed). These are must-fix items before any shared/real use.

## 6. Input validation, injection, XSS, CORS, headers, uploads
- Inputs validated server-side: integers for price/stock/budget, email shape, min
  password length. All DB access uses parameterised queries (no string-built SQL
  with user input, except LIKE patterns bound as parameters).
- XSS: Jinja autoescaping is on; no |safe is used anywhere.
- CORS: no cross-origin API is enabled. HTTPS/security headers: none (local HTTP
  only). File uploads: none exist, so no upload controls are needed.

## 7. Secrets, least privilege, logging
No secrets in code (no hardcoded session secret since the 5-team fix). SQLite file is local.
No passwords, hashes or session values are logged.

## 8. Role/permission matrix
| Action | Anonymous | Customer | Admin |
| Browse/finder/quiz/DNA/chat | yes | yes | yes |
| Cart (session) | yes | yes | yes |
| Checkout/orders/wishlist/profile | no | own only | own only |
| Perfume CRUD, all order statuses | no | no | yes |

## 9. Threat model and residual risks
Likely abuse: guessing the demo admin password; session theft on a shared machine;
CSRF against admin POSTs; brute-force login (no rate limit). Mitigations in place:
hashed passwords, HttpOnly cookie, admin 403 guard, generic login errors, no
hardcoded session secret (see §4).
RESIDUAL RISKS (do not ignore): demo admin password (also printed on the login
page — remove before any shared link), no HTTPS, no rate limiting, no CSRF tokens,
no audit log, no FK cascade. This site is therefore NOT claimed secure and NOT
production-ready.

## 10. Test plan (what was / was not tested)
Tested: admin bypass (403), wrong login (generic error), server-side price at
checkout, role cannot be set via registration (no such field), session forgery
attempts (tampered cookies rejected; forgery via a published key is impossible
now that no fallback key exists), CSRF exploitability (confirmed: no tokens —
still a gap), brute-force (confirmed: 25 wrong logins, no lockout — still a gap).
NOT tested: session expiry timing, HTTPS behaviour — listed as gaps.

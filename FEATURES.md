# FEATURES — Velvet Bloom implementation ledger

Status key: Verified = actual evidence exists (test or smoke test). Nothing here is
marked Verified without a TESTING.md check behind it.

| ID | Feature | PRD | Status | Evidence |
|----|---------|-----|--------|----------|
| F-01 | Catalog browse/search/filter | FR-001 | Verified | test_pages_200 + /catalog smoke 200 |
| F-02 | Product details + notes + stock | FR-002 | Verified | test_pages_200 (/product/1) |
| F-03 | Signup/login/logout, hashed passwords, roles | FR-003 | Verified | signup/login test; admin 403 test |
| F-04 | Cart + Demo/COD checkout, server-verified total | FR-004 | Verified | checkout test (order placed, DB price) |
| F-05 | Wishlist | FR-005 | Verified | wishlist toggle test incl. unknown-id 404 (5-team round) |
| F-06 | Order history | FR-006 | Verified | checkout test lands on /orders with order |
| F-07 | AI Finder (ranked + reasons) | FR-007 | Verified | recommendation test + budget-ranking test (in-budget first, all reasons) |
| F-08 | Quiz -> personality -> recommendations | FR-008 | Verified | quiz tie/validation test (deterministic, no false label) |
| F-09 | DNA Matcher (shared notes) | FR-009 | Verified | DNA test (Rose Velvet -> similar list) |
| F-10 | Fragrance Profile (saved preferences) | FR-010 | Verified | profile-merge test (quiz personality survives finder save) |
| F-11 | Rule-based chatbot (page + /api/chat) | FR-011 | Verified | chatbot test + all-reasons test + non-string 400 test |
| F-12 | Admin CRUD + stock + order status | FR-012 | Verified | admin CRUD test; 403 test; negative/huge-price + noop-404 tests |
| F-13 | Review sentiment (rule-based) | FR-013 | Verified | seeded reviews carry sentiment; shown on product pages |
| F-14 | Gift Finder (chatbot keyword) | FR-014 | Verified | chatbot gift branch exercised in 5-team round (catalog-only answers) |

Implementation order followed PLAN.md (setup -> design -> DB -> auth -> core -> AI ->
admin -> tests). Each slice was the smallest complete piece; no placeholder UI was
shipped as a feature, and no working behaviour was replaced.

# PRD — Velvet Bloom (Product Requirements Document)

## 1. Product summary
Velvet Bloom is a demo AI perfume e-commerce + recommendation system for a friend's FYP.
It is NOT the user's own FYP (that is Quran Shazam) and must not be mixed with it.
Problem: perfume buyers struggle to choose from many similar products. Value: a catalog
plus a preference-based finder, quiz, DNA matcher and catalog-aware chatbot that explain
their suggestions, so a buyer can decide with reasons, not just a product list.

## 2. Audience (ASSUMPTION — labelled, as the user did not know remaining details)
- Primary: perfume buyers in Pakistan, shopping in PKR, in English/Roman English.
- Secondary: a shop admin managing products, stock and demo orders.
- Viva audience: examiners who need a small set of working, explainable features.

## 3. Business goals / success metrics
- A visitor can find a ranked, in-budget recommendation in under 2 minutes.
- Every recommendation shows at least one reason (explainability).
- Chatbot answers only from catalog data (price/stock), never invented products.
- Admin CRUD and order viewing work without bypassing login.

## 4. Functional requirements
- FR-001 Catalog browse, search by name/note, filter by fragrance, occasion, max price.
- FR-002 Product details: price, stock, category, top/middle/base notes, occasions, seasons.
- FR-003 Signup/login/logout; passwords hashed; roles customer/admin.
- FR-004 Cart (session), checkout as Demo/COD, order recorded, stock reduced.
- FR-005 Wishlist per logged-in user. FR-006 Order history per user.
- FR-007 AI Finder: fragrance, occasion, budget, strength, season -> ranked list + reasons.
- FR-008 Quiz: 4 questions -> personality (Floral Lover, Fresh Explorer, Woody Elegance,
  Sweet & Warm) -> recommendations. FR-009 DNA Matcher: pick a liked perfume -> similar
  perfumes by shared notes, with shared-note count.
- FR-010 Fragrance Profile: saved preferences per user -> personalised recommendations.
- FR-011 Rule-based chatbot (web page + POST /api/chat): answers from catalog only.
- FR-012 Admin: perfume CRUD, stock edit, order list + status update.
- FR-013 Review sentiment: rule-based positive/neutral/negative on sample reviews.
- FR-014 Gift Finder behaviour is inside the chatbot (keyword 'gift' + budget/occasion).

## 5. Non-functional requirements
- NFR-001 Performance: no heavy framework; plain Flask + SQLite; pages render server-side.
- NFR-002 Accessibility: semantic HTML, labelled forms, keyboard-usable, visible focus via
  browser defaults; contrast checked by design tokens in DESIGN.md (not formally audited).
- NFR-003 Usability: mobile-first, single-column forms on small screens.
- NFR-004 Reliability: SQLite file DB; orders and stock updated in one transaction.
- NFR-005 Privacy: minimum data — name, email, address for demo orders only; no payment data.
- NFR-006 Security: see AUTH.md. NFR-007 Scalability: out of scope; single-user demo scale.

## 6. Roles and permissions
Customer: own wishlist, profile, orders, cart. Admin: all customer abilities + perfume CRUD
and all order statuses. Anonymous: browse, finder, quiz, DNA, chatbot (no order/checkout).

## 7. User journeys and acceptance criteria (Given/When/Then)
- Browse: Given the catalog, When a visitor filters fragrance=fresh and max price 4000,
  Then only fresh perfumes at or below Rs 4,000 are shown.
- Recommend: Given preferences, When the finder is submitted, Then results are ranked and
  each shows a reason; in-budget items rank above over-budget items.
- Checkout: Given a cart, When a logged-in user checks out, Then the order total equals the
  sum of DB prices (never a browser-supplied price) and stock is reduced.
- Admin guard: Given no login, When /admin is opened, Then HTTP 403 is returned.

## 8. Pages, states, errors
Pages: home, catalog, product, finder, quiz, DNA, profile, chat, login, register, cart,
checkout, orders, wishlist, admin, admin form. States: empty cart, no search results,
no similar perfumes, out of stock (scored down, not hidden), login error, 403, 404.

## 9. MVP vs later
MVP (built): FR-001..FR-014 (FR-014 gift behaviour lives inside the chatbot).
Later / out of scope: real payment, LLM chatbot (optional,
see MCP.md), image-based discovery, behaviour-based recommendations, live weather,
multi-language UI, email notifications, delivery tracking.

## 10. Rules, assumptions, risks
ASSUMPTIONS (all labelled): PKR pricing; Pakistan audience; demo/COD only; 14 fictional
sample perfumes; luxury plum/gold theme proposed by the builder (no theme was found in
the source chat summary). Risk: an LLM chatbot would add cost and hallucination risk —
therefore it is deferred (see MCP.md). Risk: demo credentials must be changed before
any shared use (see AUTH.md).

## 11. Data collected and why
Name/email (login), address (demo delivery), preferences (recommendations), cart/orders,
chat questions (only if logged in, for history). No payment cards, no real customer data.

## 12. Definition of Done
Each feature is Done only when its route/API works, its TESTING.md check passes, and its
docs (FEATURES.md) are updated. The whole MVP is Done only when the release review in
DEBUGGING.md/TESTING.md is recorded with real evidence.

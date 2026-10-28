# DESIGN — Velvet Bloom UI/UX and Design System

## 1. Principles and brand personality (PROPOSED THEME — labelled assumption)
No theme was specified in the source chat, so this theme is proposed, not copied from a
brand: luxury 'velvet' — deep plum/burgundy, gold accents, warm cream. Elegant, calm,
readable, mobile-first. Nothing here claims a real brand identity.

## 2. Colour palette (semantic tokens) — premium redesign, 2026-10-28
- Background: cream #fdf6ec, cream-2 #fbf0dd; Surface: white #ffffff;
  Text: ink #2b1a22, muted #7a5a6a; Primary action: plum #4a102e;
  Deep plum (header/hero/footer): #2a071c; Soft plum: #6b1d45; Plum tint: #f6e8ee;
  Accent: gold #c9a227, gold-light #e8c96a (large text, borders, CTAs on plum only),
  gold-pale #f5e7b8; Border: #e5d5c3.
- Contrast rule (unchanged, and still the binding rule): gold is for large/bold
  text, borders, badges and accents only, never for small body text. Body text is
  dark ink on cream/white; white text sits on deep plum. Formal WCAG audit is
  still an open gap (see TESTING.md) — this redesign does not claim a WCAG pass.
- Fragrance bottle colours (derived only from the existing `fragrance` field):
  floral rose (#f7a8c4 → #7c2d4e), woody brown (#b07a3e → #2e1c0a),
  citrus gold/amber (#ffe27a → #8a4b00), fresh teal (#8fe3d0 → #0b4a40),
  sweet pink-gold (#ffc2d9 → #8a4a2a). No product imagery is invented: the
  bottle is a pure-CSS silhouette with the perfume's initial letter, aria-hidden.

## 3. Typography, spacing, grid
- Headings: Georgia / "Times New Roman" serif (elegant, no webfont download —
  good for a slow PC and offline rendering). Body: system-ui / Arial.
  Display hero headline: 46px desktop, 36px at ≤820px, 32px at ≤600px.
- Spacing: 8–22px steps; cards 18px padding, 16px radius, top gold rule 3px;
  panels 22px padding; container max 1100px (was 1000px).
- Grid: auto-fill cards, min 260px (feature grids min 220px); single column
  under 600px; product page header (`.product-hero`) is a 120px-bottle + text
  grid that stacks to one column under 600px.

## 4. Components (what changed in the redesign)
- Header: sticky, deep-plum with backdrop blur, gold logo + "Perfume · AI Finder"
  tagline, pill nav links, current page = gold pill; nav scrolls horizontally
  on narrow screens instead of breaking or wrapping into a column.
- Hero (home only): full-width deep-plum gradient with gold radial glows,
  eyebrow label, large serif headline (text unchanged: "Find a perfume that
  fits you."), gold primary CTA + outline secondary CTA, stat chips, and an
  inline-SVG perfume bottle (no external image, cannot 404 offline).
- Perfume cards (home, catalog, wishlist): bottle visual per fragrance,
  category/fragrance/strength chips, notes paragraph, large serif price,
  in-stock (dark green) / out-of-stock (dark red) badge, hover lift
  (translateY −4px + deeper shadow), pill Add-to-cart / Wishlist buttons.
- Feature strip + "How the AI helps": four polished cards each (Finder, Quiz,
  DNA Matcher, Chatbot) linking to the existing routes — no new routes.
- Shop by occasion: five cards linking to the existing catalog filter
  (/catalog?occasion=office|university|party|wedding|daily).
- Result cards (finder, quiz, profile): gold left rule, score badge, and
  explainable reasons as chips (same reason strings as before, now as a list).
- Panels: white rounded panels for forms (finder, quiz, DNA, chat, profile,
  login/register, checkout, admin form) with 1.5px borders and gold focus rings.
- Product page: bottle + price/stock header panel, notes card, occasions/
  seasons card, similar-perfume list, reviews list with sentiment chips.
- Cart/orders/admin: list cards and panels; admin table keeps horizontal
  scroll, plum header row, and the admin status label from the 5-team fixes.
- Buttons: pill shape, plum solid, gold-on-plum for the hero primary CTA,
  white ghost with plum border; hover lift, active press-back.
- Footer: deep plum with gold top rule, demo disclaimer intact.

## 5. Page layouts
Home: hero → four-way feature strip → featured grid → shop-by-occasion →
how-the-AI-helps → footer. All pre-existing links still work; no route, form
field, or price display was renamed or removed.
Catalog: filter panel on top (labels intact), card grid below. Product:
header panel, notes/occasions cards, similar list, reviews list.
Finder/Quiz/DNA/Profile/Chat: section head + form panel first, results below.
Admin: table + recent orders. All pages share base.html header/footer.

## 6. Interaction states and motion
Default/hover (lift + shadow on cards/buttons), focus-visible (3px gold
outline, 3px offset — never removed), disabled: none used, loading: none
(server-rendered, fast), success: flash message, validation error: flash
message, empty: explicit 'empty' text, failure: 403/404 pages.
Motion: subtle only — fade-up on hero/cards, 180ms hover transitions.
`prefers-reduced-motion: reduce` disables all animation and transitions
and turns off smooth scrolling.

## 7. Accessibility (5-team fixes preserved, not regressed)
Semantic HTML (header/nav/main/footer, headings in order: h1 once per page,
h2 sections, h3 cards), skip link (visible on focus), flash `role="alert"`,
labels on every form control (catalog filters, admin status input, all
finder/quiz/profile forms), per-page `<title>` blocks, visible focus,
no JavaScript required for any core flow. Gold body-text rule above.
Open gaps, unchanged: formal WCAG contrast audit, real phone-width visual
check (CSS-level only — the redesign was verified by code + server smoke
tests, not by a live browser screenshot).

## 8. Forms and destructive actions
Unchanged from before: forms confirm by flash + redirect. Destructive admin
delete is a POST (not a GET link) and returns to the admin list. Checkout
requires a delivery address. No form field, name, or action URL changed.

## 9. Copy tone and clutter rules
Short, plain English. Prices always shown as 'Rs X,XXX'. Demo disclaimers are
in the footer and on checkout: 'No real payment is taken.' No ratings,
testimonials, real brands, or fake reviews were added — the "14 sample
perfumes" hero stat chip counts the existing sample catalog only.

## 10. Decisions needing confirmation / review criteria
- Theme approval: plum/gold/cream is a proposal; the friend may change it in style.css.
- What this redesign deliberately did NOT do: no app.py, data.py, price,
  AI scoring, auth, or database change; no JS framework, paid service, or
  build step; no external image/font (nothing can 404 offline).
- Review check: open / on a phone, /catalog, /finder, /admin — all must be
  usable without horizontal scrolling (nav scrolls, admin table scrolls,
  grids collapse to one column). Visual sign-off still needs a real
  phone/browser look — that check is open, not claimed here.

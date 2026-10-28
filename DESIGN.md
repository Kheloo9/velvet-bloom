# DESIGN — Velvet Bloom UI/UX and Design System

## 1. Principles and brand personality (PROPOSED THEME — labelled assumption)
No theme was specified in the source chat, so this theme is proposed, not copied from a
brand: luxury 'velvet' — deep plum/burgundy, gold accents, warm cream. Elegant, calm,
readable, mobile-first. Nothing here claims a real brand identity.

## 2. Colour palette (semantic tokens)
- Background: cream #fdf6ec; Surface: white #ffffff; Text: ink #2b1a22;
  Primary action: plum #4a102e; Accent: gold #c9a227; Border: #e5d5c3;
  Success/info: standard flash background #fff3cd with gold border.
- Contrast: plum on white and white on plum are high-contrast pairs; gold is used for
  borders/accents only, never for small body text (contrast risk noted, not formally
  WCAG-audited — see TESTING.md gaps).

## 3. Typography, spacing, grid
- Headings: Georgia serif (elegant, no webfont download — good for a slow PC).
- Body: system-ui/Arial. Spacing: 8–20px steps; cards 14px padding, 12px radius.
- Grid: auto-fill cards, min 260px; container max 1000px; single column under 600px.

## 4. Components
Buttons (plum, solid), ghost buttons (white/plum border), inputs/selects (9px padding,
1px border, 8px radius), cards, tables (admin), flash messages, filters row, nav header.
No invented logos, testimonials or trust badges are used.

## 5. Page layouts
Home: hero + featured grid. Catalog: filters on top, card grid below. Product: details,
notes, similar perfumes, reviews. Finder/Quiz/DNA/Profile/Chat: form first, results below.
Admin: table + recent orders. All pages share base.html header/footer.

## 6. Interaction states
Default/hover (browser default), focus (browser outline — not removed), disabled: none
used, loading: none (server-rendered, fast), success: flash message, validation error:
flash message, empty: explicit 'empty' text, failure: 403/404 pages.

## 7. Accessibility
Semantic HTML (header/nav/main/footer, labels on every form control), keyboard-usable
forms and links, no JavaScript required for any core flow (chatbot and finder are plain
forms; /api/* is an extra). Reduced motion: no animations are used at all.

## 8. Forms and destructive actions
Forms confirm by flash + redirect. Destructive admin delete is a POST (not a GET link)
and returns to the admin list. Checkout requires a delivery address.

## 9. Copy tone and clutter rules
Short, plain English. Prices always shown as 'Rs X,XXX'. Demo disclaimers are in the
footer and on checkout: 'No real payment is taken.'

## 10. Decisions needing confirmation / review criteria
- Theme approval: plum/gold/cream is a proposal; the friend may change it in style.css.
- Review check: open / on a phone, /catalog, /finder, /admin — all must be usable
  without horizontal scrolling. Formal contrast audit is an open gap (TESTING.md).

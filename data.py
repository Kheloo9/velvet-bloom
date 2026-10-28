# SAMPLE/DEMO DATA ONLY — all perfumes are fictional Velvet Bloom products.
# No real brands, real testimonials, or real customer data are used here.
# Prices are in PKR, invented for demo purposes.
PERFUMES = [
    dict(name="Rose Velvet", category="Women", fragrance="floral", occasions="wedding,party,daily",
         seasons="spring,summer", strength="soft", price=4200, stock=12,
         top="rose, bergamot", middle="peony, jasmine", base="musk, vanilla",
         desc="A soft floral perfume built around rose and peony, made for special days and daily wear."),
    dict(name="Citrus Dawn", category="Unisex", fragrance="citrus", occasions="university,daily,office",
         seasons="summer,spring", strength="soft", price=2800, stock=20,
         top="lemon, grapefruit", middle="neroli, green tea", base="white musk",
         desc="A bright citrus opening for mornings, university and office days."),
    dict(name="Woody Ember", category="Men", fragrance="woody", occasions="party,office,wedding",
         seasons="winter,autumn", strength="strong", price=5500, stock=8,
         top="cardamom, black pepper", middle="cedarwood, sage", base="amber, sandalwood",
         desc="A warm woody scent for evenings, parties and winter occasions."),
    dict(name="Amber Nights", category="Women", fragrance="woody", occasions="wedding,party",
         seasons="winter,autumn", strength="strong", price=6800, stock=6,
         top="saffron, plum", middle="amber, rose", base="oud, vanilla",
         desc="A rich amber evening perfume for weddings and formal parties."),
    dict(name="Fresh Meadow", category="Unisex", fragrance="fresh", occasions="daily,university,office",
         seasons="summer,spring", strength="soft", price=3200, stock=18,
         top="mint, green apple", middle="lavender, cucumber", base="cedar, musk",
         desc="A clean fresh scent for everyday use in warm weather."),
    dict(name="Sweet Blossom", category="Women", fragrance="sweet", occasions="party,wedding,daily",
         seasons="spring,summer", strength="soft", price=4500, stock=10,
         top="strawberry, pink pepper", middle="gardenia, peony", base="vanilla, musk",
         desc="A sweet floral perfume for parties and cheerful spring days."),
    dict(name="Ocean Breeze", category="Men", fragrance="fresh", occasions="daily,university,office",
         seasons="summer", strength="soft", price=3500, stock=15,
         top="sea salt, lime", middle="sage, driftwood", base="musk, vetiver",
         desc="A cool fresh scent inspired by a sea breeze, best in summer."),
    dict(name="Midnight Oud", category="Men", fragrance="woody", occasions="wedding,party",
         seasons="winter", strength="strong", price=7500, stock=5,
         top="oud, smoke", middle="leather, rose", base="amber, patchouli",
         desc="A bold oud perfume for winter weddings and formal evenings."),
    dict(name="Jasmine Glow", category="Women", fragrance="floral", occasions="daily,office,wedding",
         seasons="spring,summer", strength="soft", price=3900, stock=14,
         top="jasmine, pear", middle="orange blossom, lily", base="sandalwood, musk",
         desc="A glowing jasmine floral for daily wear and office days."),
    dict(name="Citrus Grove", category="Unisex", fragrance="citrus", occasions="daily,university",
         seasons="summer,spring", strength="soft", price=2900, stock=22,
         top="orange, lime", middle="basil, neroli", base="white musk, cedar",
         desc="A light citrus scent for daily and university use."),
    dict(name="Velvet Noir", category="Unisex", fragrance="woody", occasions="party,wedding,office",
         seasons="autumn,winter", strength="strong", price=6200, stock=7,
         top="blackcurrant, bergamot", middle="iris, cedarwood", base="amber, musk",
         desc="A dark, elegant woody perfume for evenings and formal events."),
    dict(name="Honey Bloom", category="Women", fragrance="sweet", occasions="party,daily,wedding",
         seasons="autumn,spring", strength="soft", price=4800, stock=9,
         top="honey, apricot", middle="rose, vanilla orchid", base="tonka, musk",
         desc="A warm sweet perfume with honey and vanilla notes."),
    dict(name="Pine Trail", category="Men", fragrance="fresh", occasions="daily,office,university",
         seasons="winter,autumn", strength="soft", price=3400, stock=16,
         top="pine, eucalyptus", middle="sage, cedarwood", base="vetiver, musk",
         desc="A crisp fresh-woody scent for cool days and office wear."),
    dict(name="Sunset Citrus", category="Women", fragrance="citrus", occasions="party,daily",
         seasons="summer", strength="soft", price=3700, stock=11,
         top="mandarin, yuzu", middle="peach, jasmine", base="amber, musk",
         desc="A sunny citrus-floral perfume for summer parties and daily wear."),
]

SAMPLE_REVIEWS = [
    ("Rose Velvet", "I love the rose smell, it lasts long and feels soft.", 5),
    ("Rose Velvet", "Nice fragrance but a bit light for evening.", 4),
    ("Citrus Dawn", "Very fresh for summer, good value for daily use.", 5),
    ("Woody Ember", "Strong and warm, perfect for winter evenings.", 5),
    ("Woody Ember", "Too strong for me in the morning.", 3),
    ("Fresh Meadow", "Clean and fresh, I use it every day.", 4),
    ("Midnight Oud", "Bold oud, lasts the whole wedding night.", 5),
    ("Ocean Breeze", "Light and cool, packaging was good too.", 4),
]

POSITIVE_WORDS = {"love", "great", "good", "fresh", "perfect", "nice", "soft", "long", "last", "lasting", "excellent", "beautiful"}
NEGATIVE_WORDS = {"bad", "poor", "weak", "too strong", "disappoint", "faded", "harsh", "heavy"}

def sentiment(text):
    t = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in t)
    neg = sum(1 for w in NEGATIVE_WORDS if w in t)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"

def all_notes(p):
    # None-safe: a perfume row with NULL note columns must not crash product/DNA/chat pages.
    parts = [p.get("top") or "", p.get("middle") or "", p.get("base") or ""]
    return ", ".join(x.strip() for x in ",".join(parts).split(",") if x.strip())

def score_perfume(p, fragrance="", occasion="", budget=None, strength="", season=""):
    """Rule-based, explainable scoring. Returns (score, [reasons]). No ML model, no LLM."""
    score, reasons = 0, []
    if fragrance and p["fragrance"] == fragrance:
        score += 30; reasons.append(f"Matches your {fragrance} fragrance preference")
    if occasion and occasion in (p.get("occasions") or "").split(","):
        score += 20; reasons.append(f"Suitable for {occasion}")
    if season and season in (p.get("seasons") or "").split(","):
        score += 15; reasons.append(f"Good for {season}")
    if strength and p["strength"] == strength:
        score += 10; reasons.append(f"{strength} strength as requested")
    if budget:
        if p["price"] <= budget:
            score += 25; reasons.append(f"Within budget (Rs {p['price']:,})")
        else:
            # Penalty -100, not -20: the maximum match points are 30+20+15+10=75,
            # so an over-budget item can never outrank an in-budget item (min +25).
            # This makes PRD §7 ("in-budget items rank above over-budget items") true.
            score -= 100; reasons.append(f"Over budget (Rs {p['price']:,})")
    if p["stock"] <= 0:
        score -= 100; reasons.append("Out of stock")
    if not reasons:
        reasons.append("General match from the catalog")
    return score, reasons

def similar_perfumes(target, all_perfumes, limit=4):
    target_notes = set(n.strip() for n in all_notes(target).split(","))
    out = []
    for p in all_perfumes:
        if p["id"] == target["id"]:
            continue
        notes = set(n.strip() for n in all_notes(p).split(","))
        shared = sorted(target_notes & notes)
        if shared:
            out.append((len(shared), p, shared))
    out.sort(key=lambda x: (-x[0], x[1]["price"]))
    return out[:limit]

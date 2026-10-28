"""Velvet Bloom — AI perfume e-commerce + recommendation (DEMO, no real payment).
Stack: Flask + SQLite + HTML/CSS/JS. No LLM key required. See README.md / AUTH.md.
Run: .venv/bin/python app.py  (then open http://127.0.0.1:5000)
"""
import os, re, secrets, sqlite3, json
from functools import wraps
from flask import Flask, g, render_template, request, redirect, url_for, session, flash, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from data import PERFUMES, SAMPLE_REVIEWS, sentiment, all_notes, score_perfume, similar_perfumes

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "velvet.db")
app = Flask(__name__)
# Security fix (5-team testing, Oct 2026): NEVER ship a hardcoded fallback secret —
# a published fallback lets anyone forge a Flask session cookie and take over admin.
# If VELVET_SECRET_KEY is set, it is used (sessions survive restarts); otherwise a
# fresh random secret is generated per process (sessions reset on restart, demo-safe).
app.secret_key = os.environ.get("VELVET_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Admin validation bounds: SQLite INTEGER overflows above 2**63-1, so a huge
# price/stock (e.g. 10**20) used to crash with HTTP 500. Bounds keep demo values
# sane while rejecting negatives, zero-price abuse is still allowed only at 0.
MAX_PRICE = 10_000_000
MAX_STOCK = 10_000
ALLOWED_STATUSES = ["Placed (Demo/COD)", "Processing", "Shipped", "Delivered", "Cancelled"]
KNOWN_FRAGRANCES = ["floral", "fresh", "woody", "sweet", "citrus"]

def save_preferences(user_id, **fields):
    """Merge-only preference save: update just the fields this form owns, never
    wipe another feature's fields (previous INSERT OR REPLACE clobbered them)."""
    db = get_db()
    row = db.execute("SELECT * FROM preferences WHERE user_id=?", (user_id,)).fetchone()
    pref = dict(row) if row else {"fragrance": None, "occasion": None, "budget_min": None,
                                  "budget_max": None, "strength": None, "season": None, "personality": None}
    for k, v in fields.items():
        if v is not None and k in pref:
            pref[k] = v
    db.execute("INSERT OR REPLACE INTO preferences VALUES(?,?,?,?,?,?,?,?)",
               (user_id, pref["fragrance"], pref["occasion"], pref["budget_min"], pref["budget_max"],
                pref["strength"], pref["season"], pref["personality"]))
    db.commit()

def validate_admin_perfume(f):
    """Validate admin perfume form data. Returns (clean_dict, error_or_None).
    Uses .get() so a missing field flashes instead of raising a bare 400."""
    name = (f.get("name") or "").strip()
    if not name:
        return None, "Perfume name is required."
    try:
        price, stock = int(f.get("price")), int(f.get("stock"))
    except (TypeError, ValueError):
        return None, "Price and stock must be numbers."
    if price < 0 or price > MAX_PRICE or stock < 0 or stock > MAX_STOCK:
        return None, f"Price must be 0–{MAX_PRICE:,} and stock 0–{MAX_STOCK:,}."
    return {"name": name, "category": f.get("category", ""), "fragrance": f.get("fragrance", ""),
            "occasions": f.get("occasions", ""), "seasons": f.get("seasons", ""), "strength": f.get("strength", ""),
            "price": price, "stock": stock, "top": f.get("top", ""), "middle": f.get("middle", ""),
            "base": f.get("base", ""), "description": f.get("description", "")}, None

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB); g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None: db.close()

def init_db():
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'customer');
    CREATE TABLE IF NOT EXISTS perfumes(id INTEGER PRIMARY KEY, name TEXT NOT NULL, category TEXT, fragrance TEXT,
      occasions TEXT, seasons TEXT, strength TEXT, price INTEGER NOT NULL, stock INTEGER NOT NULL,
      top TEXT, middle TEXT, base TEXT, description TEXT);
    CREATE TABLE IF NOT EXISTS wishlist(user_id INTEGER, perfume_id INTEGER, UNIQUE(user_id, perfume_id));
    CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, user_id INTEGER, total INTEGER NOT NULL,
      status TEXT DEFAULT 'Placed (Demo/COD)', address TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS order_items(order_id INTEGER, perfume_id INTEGER, qty INTEGER, price INTEGER);
    CREATE TABLE IF NOT EXISTS preferences(user_id INTEGER PRIMARY KEY, fragrance TEXT, occasion TEXT,
      budget_min INTEGER, budget_max INTEGER, strength TEXT, season TEXT, personality TEXT);
    CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY, perfume_id INTEGER, text TEXT, rating INTEGER, sentiment TEXT);
    CREATE TABLE IF NOT EXISTS chat_history(id INTEGER PRIMARY KEY, user_id INTEGER, question TEXT, answer TEXT,
      created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    """)
    if db.execute("SELECT COUNT(*) c FROM perfumes").fetchone()["c"] == 0:
        for p in PERFUMES:
            db.execute("INSERT INTO perfumes(name,category,fragrance,occasions,seasons,strength,price,stock,top,middle,base,description) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                       (p["name"], p["category"], p["fragrance"], p["occasions"], p["seasons"], p["strength"], p["price"], p["stock"], p["top"], p["middle"], p["base"], p["desc"]))
        for name, text, rating in SAMPLE_REVIEWS:
            row = db.execute("SELECT id FROM perfumes WHERE name=?", (name,)).fetchone()
            if row: db.execute("INSERT INTO reviews(perfume_id,text,rating,sentiment) VALUES(?,?,?,?)", (row["id"], text, rating, sentiment(text)))
    # Pre-public-link fix: NEVER seed a published/hardcoded admin password.
    # Admin is created only from VELVET_ADMIN_PASSWORD (private, set by the owner
    # and never committed). With it unset, no admin is seeded — set the env var,
    # then delete velvet.db and restart to seed the admin.
    if db.execute("SELECT COUNT(*) c FROM users WHERE email='admin@velvet.demo'").fetchone()["c"] == 0:
        _admin_pw = os.environ.get("VELVET_ADMIN_PASSWORD")
        if _admin_pw:
            db.execute("INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                       ("Admin", "admin@velvet.demo", generate_password_hash(_admin_pw), "admin"))
    db.commit(); db.close()

def rows_to_dicts(rows): return [dict(r) for r in rows]
def current_user():
    if "user_id" not in session: return None
    return get_db().execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not current_user(): flash("Please log in first."); return redirect(url_for("login"))
        return f(*a, **k)
    return w
def admin_required(f):
    @wraps(f)
    def w(*a, **k):
        u = current_user()
        if not u or u["role"] != "admin": abort(403)
        return f(*a, **k)
    return w

@app.context_processor
def inject():
    cart = session.get("cart", {})
    try:
        cart_count = sum(int(q) for q in cart.values() if int(q) > 0)
    except (TypeError, ValueError):
        cart_count = 0
    return dict(user=current_user(), cart_count=cart_count)

# ---------- Public pages ----------
@app.route("/")
def home():
    db = get_db()
    featured = rows_to_dicts(db.execute("SELECT * FROM perfumes ORDER BY stock DESC LIMIT 6").fetchall())
    return render_template("home.html", featured=featured)

@app.route("/catalog")
def catalog():
    db = get_db()
    q = (request.args.get("q") or "").strip()
    fragrance = request.args.get("fragrance") or ""
    occasion = request.args.get("occasion") or ""
    max_price = request.args.get("max_price") or ""
    sql, params = "SELECT * FROM perfumes WHERE 1=1", []
    if q: sql += " AND (name LIKE ? OR top LIKE ? OR middle LIKE ? OR base LIKE ?)"; params += [f"%{q}%"]*4
    if fragrance: sql += " AND fragrance=?"; params.append(fragrance)
    if max_price.isdigit(): sql += " AND price<=?"; params.append(int(max_price))
    items = rows_to_dicts(db.execute(sql, params).fetchall())
    if occasion: items = [p for p in items if occasion in (p.get("occasions") or "").split(",")]
    return render_template("catalog.html", items=items, q=q, fragrance=fragrance, occasion=occasion, max_price=max_price)

@app.route("/product/<int:pid>")
def product(pid):
    db = get_db()
    p = db.execute("SELECT * FROM perfumes WHERE id=?", (pid,)).fetchone()
    if not p: abort(404)
    reviews = rows_to_dicts(db.execute("SELECT * FROM reviews WHERE perfume_id=?", (pid,)).fetchall())
    sims = similar_perfumes(dict(p), rows_to_dicts(db.execute("SELECT * FROM perfumes").fetchall()))
    return render_template("product.html", p=dict(p), reviews=reviews, sims=sims)

# ---------- Auth ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name, email, pw = request.form.get("name","").strip(), request.form.get("email","").strip().lower(), request.form.get("password","")
        # Email shape: non-empty local part, non-empty domain containing a dot
        # (rejects "@" alone, which the old '"@" in email' check accepted).
        email_ok = " " not in email and email.count("@") == 1 and all(
            x for x in email.split("@")) and "." in email.split("@")[1]
        if not name or not email_ok or len(pw) < 6:
            flash("Name, a valid email and a password of at least 6 characters are required."); return render_template("register.html")
        db = get_db()
        try:
            db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)", (name, email, generate_password_hash(pw))); db.commit()
        except sqlite3.IntegrityError:
            flash("This email is already registered."); return render_template("register.html")
        flash("Account created. Please log in."); return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email, pw = request.form.get("email","").strip().lower(), request.form.get("password","")
        u = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if u and check_password_hash(u["password_hash"], pw):
            session["user_id"] = u["id"]; flash(f"Welcome, {u['name']}!")
            return redirect(url_for("admin") if u["role"] == "admin" else url_for("home"))
        flash("Invalid email or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    cart = session.get("cart")  # logout used to wipe the cart via session.clear()
    session.clear()
    if cart: session["cart"] = cart
    flash("Logged out."); return redirect(url_for("home"))

# ---------- Cart / wishlist / orders (prices always re-read from DB) ----------
def cart_items():
    db = get_db(); cart = session.get("cart", {}); out, total = [], 0
    for pid, qty in cart.items():
        p = db.execute("SELECT * FROM perfumes WHERE id=?", (int(pid),)).fetchone()
        if p:
            out.append((dict(p), int(qty))); total += p["price"] * int(qty)
    return out, total

@app.route("/cart/add/<int:pid>", methods=["POST"])
def cart_add(pid):
    p = get_db().execute("SELECT * FROM perfumes WHERE id=?", (pid,)).fetchone()
    if not p: abort(404)  # was: phantom session key for a nonexistent perfume
    if p["stock"] <= 0:
        flash("Sorry, this perfume is out of stock."); return redirect(request.referrer or url_for("catalog"))
    cart = session.get("cart", {}); cart[str(pid)] = cart.get(str(pid), 0) + 1; session["cart"] = cart
    flash("Added to cart."); return redirect(request.referrer or url_for("catalog"))

@app.route("/cart")
def cart():
    items, total = cart_items(); return render_template("cart.html", items=items, total=total)

@app.route("/cart/remove/<int:pid>", methods=["POST"])
def cart_remove(pid):
    cart = session.get("cart", {}); cart.pop(str(pid), None); session["cart"] = cart; return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items, total = cart_items()
    if not items: flash("Your cart is empty."); return redirect(url_for("catalog"))
    if request.method == "POST":
        address = request.form.get("address","").strip()
        if not address: flash("Please enter a delivery address."); return render_template("checkout.html", items=items, total=total)
        db = get_db()
        cur = db.execute("INSERT INTO orders(user_id,total,address) VALUES(?,?,?)", (session["user_id"], total, address))
        oid = cur.lastrowid
        for p, qty in items:
            if p["stock"] < qty: flash(f"Not enough stock for {p['name']}."); db.rollback(); return redirect(url_for("cart"))
            db.execute("INSERT INTO order_items VALUES(?,?,?,?)", (oid, p["id"], qty, p["price"]))
            db.execute("UPDATE perfumes SET stock=stock-? WHERE id=?", (qty, p["id"]))
        db.commit(); session["cart"] = {}
        flash(f"Demo order #{oid} placed (Cash on Delivery, no real payment taken).")
        return redirect(url_for("orders"))
    return render_template("checkout.html", items=items, total=total)

@app.route("/orders")
@login_required
def orders():
    db = get_db()
    ords = rows_to_dicts(db.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall())
    for o in ords: o["line_items"] = rows_to_dicts(db.execute("SELECT p.name, oi.qty, oi.price FROM order_items oi JOIN perfumes p ON p.id=oi.perfume_id WHERE oi.order_id=?", (o["id"],)).fetchall())
    return render_template("orders.html", orders=ords)

@app.route("/wishlist")
@login_required
def wishlist():
    db = get_db()
    items = rows_to_dicts(db.execute("SELECT p.* FROM wishlist w JOIN perfumes p ON p.id=w.perfume_id WHERE w.user_id=?", (session["user_id"],)).fetchall())
    return render_template("wishlist.html", items=items)

@app.route("/wishlist/toggle/<int:pid>", methods=["POST"])
@login_required
def wishlist_toggle(pid):
    db = get_db()
    if not db.execute("SELECT 1 FROM perfumes WHERE id=?", (pid,)).fetchone():
        abort(404)  # was: orphan wishlist row for a nonexistent perfume
    row = db.execute("SELECT 1 FROM wishlist WHERE user_id=? AND perfume_id=?", (session["user_id"], pid)).fetchone()
    if row: db.execute("DELETE FROM wishlist WHERE user_id=? AND perfume_id=?", (session["user_id"], pid))
    else: db.execute("INSERT INTO wishlist VALUES(?,?)", (session["user_id"], pid))
    db.commit(); return redirect(request.referrer or url_for("catalog"))

# ---------- AI features: finder / quiz / DNA / profile ----------
def ranked(fragrance="", occasion="", budget=None, strength="", season=""):
    db = get_db(); items = rows_to_dicts(db.execute("SELECT * FROM perfumes").fetchall())
    scored = []
    for p in items:
        s, reasons = score_perfume(p, fragrance, occasion, budget, strength, season)
        scored.append((s, p, reasons))
    scored.sort(key=lambda x: (-x[0], x[1]["price"]))
    return scored

@app.route("/finder", methods=["GET", "POST"])
def finder():
    results = None; form = {}; no_match = False
    if request.method == "POST":
        form = {k: request.form.get(k, "") for k in ("fragrance", "occasion", "strength", "season")}
        budget = int(request.form["max_price"]) if request.form.get("max_price", "").isdigit() else None
        form["max_price"] = request.form.get("max_price", "")
        results = ranked(form["fragrance"], form["occasion"], budget, form["strength"], form["season"])
        # Honest empty state: if nothing scored above zero, say so instead of
        # silently showing the full catalog as if it matched.
        if any(form.values()) and results and max(s for s, _, _ in results) <= 0:
            no_match = True
        if current_user():
            save_preferences(session["user_id"], fragrance=form["fragrance"], occasion=form["occasion"],
                             budget_max=budget, strength=form["strength"], season=form["season"])
    return render_template("finder.html", results=results, form=form, no_match=no_match)

QUIZ_MAP = {"floral": "Floral Lover", "fresh": "Fresh Explorer", "woody": "Woody Elegance", "sweet": "Sweet & Warm", "citrus": "Fresh Explorer"}
@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    results = None; personality = None
    if request.method == "POST":
        # Validate + deterministic tie-break (fixes two 5-team findings):
        # - unknown/missing answers used to default to a false "Floral Lover"
        #   label while ranking with fragrance="" (list started with Citrus Dawn);
        # - max(set(...)) tie-breaking was hash-randomised per process.
        # Now only known fragrance values count, ties go to the earliest answer,
        # and with no valid answer no personality is claimed at all.
        raw = [request.form.get(f"q{i}", "") for i in range(1, 5)]
        answers = [a for a in raw if a in KNOWN_FRAGRANCES]
        if not answers:
            flash("Please answer at least one question with a valid choice.")
            return render_template("quiz.html", results=None, personality=None)
        counts = {a: answers.count(a) for a in set(answers)}
        top = max(counts, key=lambda a: (counts[a], -answers.index(a)))
        personality = QUIZ_MAP[top]
        budget = int(request.form["max_price"]) if request.form.get("max_price", "").isdigit() else None
        results = ranked(top, "", budget, "", "")
        if current_user():
            save_preferences(session["user_id"], fragrance=top, budget_max=budget, personality=personality)
    return render_template("quiz.html", results=results, personality=personality)

@app.route("/dna", methods=["GET", "POST"])
def dna():
    db = get_db(); items = rows_to_dicts(db.execute("SELECT * FROM perfumes ORDER BY name").fetchall())
    target, sims = None, []
    if request.method == "POST":
        pid = request.form.get("perfume_id", "")
        if pid.isdigit():
            target = db.execute("SELECT * FROM perfumes WHERE id=?", (int(pid),)).fetchone()
            if target: sims = similar_perfumes(dict(target), items)
            else: flash("Perfume not found — please choose from the list.")
        else: flash("Perfume not found — please choose from the list.")
    return render_template("dna.html", items=items, target=dict(target) if target else None, sims=sims)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    if request.method == "POST":
        budget_max = int(request.form["max_price"]) if request.form.get("max_price", "").isdigit() else None
        save_preferences(session["user_id"], fragrance=request.form.get("fragrance",""),
                         occasion=request.form.get("occasion",""), budget_max=budget_max,
                         strength=request.form.get("strength",""), season=request.form.get("season",""))
        flash("Fragrance profile saved.")
    pref = db.execute("SELECT * FROM preferences WHERE user_id=?", (session["user_id"],)).fetchone()
    recs = ranked(pref["fragrance"], pref["occasion"], pref["budget_max"], pref["strength"], pref["season"])[:4] if pref else []
    return render_template("profile.html", pref=dict(pref) if pref else None, recs=recs)

# ---------- Rule-based chatbot (no LLM) ----------
FRAGRANCE_WORDS = {"floral": "floral", "woody": "woody", "citrus": "citrus", "fresh": "fresh", "sweet": "sweet"}
OCCASION_WORDS = {"wedding": "wedding", "party": "party", "office": "office", "university": "university", "daily": "daily"}
SEASON_WORDS = {"summer": "summer", "winter": "winter", "spring": "spring", "autumn": "autumn"}

def chatbot_answer(msg, user_id=None):
    db = get_db(); items = rows_to_dicts(db.execute("SELECT * FROM perfumes").fetchall())
    t = msg.lower()
    m = re.search(r"(\d{3,5})", t.replace(",", ""))
    budget = int(m.group(1)) if m else None
    fragrance = next((v for k, v in FRAGRANCE_WORDS.items() if k in t), "")
    occasion = next((v for k, v in OCCASION_WORDS.items() if k in t), "")
    season = next((v for k, v in SEASON_WORDS.items() if k in t), "")
    named = [p for p in items if p["name"].lower() in t]
    if named:
        p = named[0]
        ans = (f"{p['name']} — Rs {p['price']:,}, {p['category']}, {p['fragrance']}, {p['strength']} strength. "
               f"Notes: {all_notes(p)}. Stock: {p['stock']} left. Good for: {p['occasions']}. {p['description']}")
    elif "gift" in t:
        recs = ranked(fragrance, occasion or "party", budget, "", season)[:3]
        ans = "Gift ideas from the Velvet Bloom catalog only: " + "; ".join(f"{p['name']} (Rs {p['price']:,}, {p['fragrance']})" for _, p, _ in recs)
    elif fragrance or occasion or season or budget:
        recs = ranked(fragrance, occasion, budget, "", season)[:3]
        # Show ALL reasons, not just the first: showing only one hid the criteria
        # an item did NOT match (e.g. a spring perfume listed for a winter query).
        ans = "Based on your preferences, from the Velvet Bloom catalog only: " + "; ".join(
            f"{p['name']} (Rs {p['price']:,}, {p['fragrance']}, {p['strength']}) — {'; '.join(r)}" for _, p, r in recs)
        ans += ". Use the AI Finder for a full ranked list with reasons."
    elif "price" in t or "cheap" in t or "budget" in t:
        cheap = sorted(items, key=lambda p: p["price"])[:3]
        # Disclaimer first: a "Chanel price?" question used to be answered with
        # this list as if it were about that brand. We stock Velvet Bloom only.
        ans = "I only stock Velvet Bloom perfumes — our lowest-priced ones are: " + "; ".join(f"{p['name']} (Rs {p['price']:,})" for p in cheap)
    else:
        ans = ("I can help from the Velvet Bloom catalog only — try: 'fresh perfume for university under 4000', "
               "'wedding perfume for winter', or a perfume name. You can also try the AI Finder or the Quiz.")
    if user_id:
        db.execute("INSERT INTO chat_history(user_id,question,answer) VALUES(?,?,?)", (user_id, msg, ans)); db.commit()
    return ans

@app.route("/chat", methods=["GET", "POST"])
def chat():
    answer = None
    if request.method == "POST":
        answer = chatbot_answer(request.form.get("message", ""), session.get("user_id"))
    return render_template("chat.html", answer=answer)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    msg = data.get("message")
    # Non-string message used to crash with AttributeError -> HTTP 500.
    if not isinstance(msg, str) or not msg.strip():
        return jsonify({"error": "message is required"}), 400
    return jsonify({"answer": chatbot_answer(msg.strip(), session.get("user_id"))})

@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    data = request.get_json(silent=True) or {}
    budget = data.get("max_price")
    # Exact parsing (documented in API.md): int or digit string only; a bool is
    # NOT a budget (Python bool is an int subclass — True used to mean Rs 1);
    # an integral float is accepted, a non-integral float is not a budget.
    if isinstance(budget, bool):
        budget = None
    elif isinstance(budget, float):
        budget = int(budget) if budget.is_integer() else None
    elif isinstance(budget, str):
        budget = int(budget) if budget.isdigit() else None
    elif not isinstance(budget, int):
        budget = None
    out = [{"name": p["name"], "price": p["price"], "fragrance": p["fragrance"], "score": s, "reasons": r}
           for s, p, r in ranked(data.get("fragrance",""), data.get("occasion",""), budget, data.get("strength",""), data.get("season",""))[:5]]
    return jsonify(out)

# ---------- Admin ----------
@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    items = rows_to_dicts(db.execute("SELECT * FROM perfumes ORDER BY id").fetchall())
    orders_ = rows_to_dicts(db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20").fetchall())
    return render_template("admin.html", items=items, orders=orders_)

@app.route("/admin/perfume/new", methods=["GET", "POST"])
@admin_required
def admin_new():
    if request.method == "POST":
        clean, err = validate_admin_perfume(request.form)
        if err:
            flash(err); return render_template("admin_form.html", p=None)
        db = get_db(); db.execute("INSERT INTO perfumes(name,category,fragrance,occasions,seasons,strength,price,stock,top,middle,base,description) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (clean["name"], clean["category"], clean["fragrance"], clean["occasions"], clean["seasons"], clean["strength"], clean["price"], clean["stock"], clean["top"], clean["middle"], clean["base"], clean["description"])); db.commit()
        flash("Perfume added."); return redirect(url_for("admin"))
    return render_template("admin_form.html", p=None)

@app.route("/admin/perfume/<int:pid>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit(pid):
    db = get_db(); p = db.execute("SELECT * FROM perfumes WHERE id=?", (pid,)).fetchone()
    if not p: abort(404)
    if request.method == "POST":
        clean, err = validate_admin_perfume(request.form)
        if err:
            flash(err); return render_template("admin_form.html", p=dict(p))
        db.execute("UPDATE perfumes SET name=?,category=?,fragrance=?,occasions=?,seasons=?,strength=?,price=?,stock=?,top=?,middle=?,base=?,description=? WHERE id=?",
            (clean["name"], clean["category"], clean["fragrance"], clean["occasions"], clean["seasons"], clean["strength"], clean["price"], clean["stock"], clean["top"], clean["middle"], clean["base"], clean["description"], pid)); db.commit()
        flash("Perfume updated."); return redirect(url_for("admin"))
    return render_template("admin_form.html", p=dict(p))

@app.route("/admin/perfume/<int:pid>/delete", methods=["POST"])
@admin_required
def admin_delete(pid):
    db = get_db()
    cur = db.execute("DELETE FROM perfumes WHERE id=?", (pid,)); db.commit()
    if cur.rowcount == 0: abort(404)  # was: silent no-op for a nonexistent id
    flash("Perfume deleted."); return redirect(url_for("admin"))

@app.route("/admin/order/<int:oid>/status", methods=["POST"])
@admin_required
def admin_order_status(oid):
    db = get_db()
    if not db.execute("SELECT 1 FROM orders WHERE id=?", (oid,)).fetchone():
        abort(404)  # was: silent no-op for a nonexistent order
    status = request.form.get("status", "")
    if status not in ALLOWED_STATUSES:
        flash("Please choose a valid order status."); return redirect(url_for("admin"))
    db.execute("UPDATE orders SET status=? WHERE id=?", (status, oid)); db.commit()
    flash("Order status updated."); return redirect(url_for("admin"))

@app.errorhandler(403)
def forbidden(e): return render_template("error.html", code=403, msg="Admin access only."), 403
@app.errorhandler(404)
def notfound(e): return render_template("error.html", code=404, msg="Page not found."), 404

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)

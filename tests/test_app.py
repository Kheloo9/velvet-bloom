"""Real checks for Velvet Bloom. Run: .venv/bin/python tests/test_app.py
(pytest is NOT installed and NOT a dependency — the direct runner is the only path.)
No test is deleted to go green; failures are reported as-is.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as appmod

TEST_ADMIN_PW = None

def make_client():
    # Tests seed the admin from a fresh random password each run, so no
    # admin password is hardcoded anywhere in the repo (see app.py init_db).
    global TEST_ADMIN_PW
    TEST_ADMIN_PW = "test-" + os.urandom(8).hex()
    os.environ["VELVET_ADMIN_PASSWORD"] = TEST_ADMIN_PW
    os.environ.pop("VELVET_DEMO_ADMIN", None)
    if os.path.exists(appmod.DB):
        os.remove(appmod.DB)
    appmod.init_db()
    appmod.app.config["TESTING"] = True
    return appmod.app.test_client()

def test_pages_200():
    c = make_client()
    for path in ["/", "/catalog", "/finder", "/quiz", "/dna", "/chat", "/login", "/register", "/cart"]:
        r = c.get(path); assert r.status_code == 200, (path, r.status_code)
    r = c.get("/product/1"); assert r.status_code == 200

def test_recommendation_in_budget():
    c = make_client()
    r = c.post("/api/recommend", json={"fragrance": "fresh", "occasion": "university", "max_price": 4000})
    assert r.status_code == 200
    data = r.get_json(); assert data, "empty recommendations"
    # Ranked: first item should be in budget and have reasons
    assert data[0]["price"] <= 4000, data[0]
    assert data[0]["reasons"], "explainable reasons missing"

def test_chatbot_from_catalog():
    c = make_client()
    r = c.post("/api/chat", json={"message": "fresh perfume for university under 4000"})
    assert r.status_code == 200
    ans = r.get_json()["answer"]
    assert "Fresh Meadow" in ans or "Citrus Dawn" in ans or "Ocean Breeze" in ans, ans

def test_dna_matcher():
    c = make_client()
    # Rose Velvet (id 1) shares rose/musk with several perfumes
    r = c.post("/dna", data={"perfume_id": "1"})
    assert r.status_code == 200 and b"Similar to Rose Velvet" in r.data

def test_admin_blocked_without_login():
    c = make_client()
    assert c.get("/admin").status_code == 403
    assert c.get("/admin/perfume/new").status_code == 403

def test_signup_login_and_server_price():
    c = make_client()
    c.post("/register", data={"name": "Test User", "email": "test@demo.local", "password": "secret123"})
    r = c.post("/login", data={"email": "test@demo.local", "password": "secret123"}, follow_redirects=True)
    assert r.status_code == 200
    c.post("/cart/add/2")
    r = c.get("/cart"); assert b"2,800" in r.data or b"2800" in r.data, r.data[:500]
    # Checkout uses DB price, not any browser price (no price field is accepted)
    r = c.post("/checkout", data={"address": "Test Street 1", "price": "1"}, follow_redirects=True)
    assert r.status_code == 200 and b"Demo order" in r.data

def test_admin_login_and_crud():
    c = make_client()
    c.post("/login", data={"email": "admin@velvet.demo", "password": TEST_ADMIN_PW})
    assert c.get("/admin").status_code == 200
    c.post("/admin/perfume/new", data={"name": "Test Bloom", "category": "Unisex", "fragrance": "fresh",
        "occasions": "daily", "seasons": "summer", "strength": "soft", "price": "3000", "stock": "5",
        "top": "mint", "middle": "lavender", "base": "musk", "description": "Test perfume."}, follow_redirects=True)
    r = c.get("/catalog?q=Test+Bloom"); assert b"Test Bloom" in r.data

def _admin_client():
    c = make_client()
    c.post("/login", data={"email": "admin@velvet.demo", "password": TEST_ADMIN_PW})
    return c

def _user_client(email="fix@demo.local"):
    c = make_client()
    c.post("/register", data={"name": "Fix User", "email": email, "password": "secret123"})
    c.post("/login", data={"email": email, "password": "secret123"})
    return c

def _perfume_count(c):
    import sqlite3
    db = sqlite3.connect(appmod.DB); n = db.execute("SELECT COUNT(*) FROM perfumes").fetchone()[0]; db.close()
    return n

def test_admin_negative_price_rejected():
    c = _admin_client(); before = _perfume_count(c)
    r = c.post("/admin/perfume/new", data={"name": "Bad", "category": "Unisex", "fragrance": "fresh",
        "occasions": "daily", "seasons": "summer", "strength": "soft", "price": "-500", "stock": "-3",
        "top": "mint", "middle": "lavender", "base": "musk", "description": "Bad."})
    assert r.status_code == 200 and _perfume_count(c) == before

def test_admin_huge_price_no_crash():
    c = _admin_client(); before = _perfume_count(c)
    r = c.post("/admin/perfume/new", data={"name": "Huge", "category": "Unisex", "fragrance": "fresh",
        "occasions": "daily", "seasons": "summer", "strength": "soft", "price": "100000000000000000000", "stock": "5",
        "top": "mint", "middle": "lavender", "base": "musk", "description": "Huge."})
    assert r.status_code == 200 and _perfume_count(c) == before  # was HTTP 500 OverflowError

def test_api_chat_non_string_400():
    c = make_client()
    r = c.post("/api/chat", json={"message": 123})
    assert r.status_code == 400, r.status_code  # was HTTP 500 AttributeError

def test_quiz_tie_deterministic_and_validated():
    c = make_client()
    r = c.post("/quiz", data={"q1": "floral", "q2": "fresh", "q3": "woody", "q4": "sweet"})
    assert b"Floral Lover" in r.data  # earliest answer wins a tie, every time
    r2 = c.post("/quiz", data={})
    assert b"You are:" not in r2.data  # was: false "Floral Lover" label

def test_budget_ranking_in_budget_first():
    c = make_client()
    r = c.post("/api/recommend", json={"fragrance": "woody", "occasion": "wedding",
        "season": "winter", "strength": "strong", "max_price": 5000})
    data = r.get_json()
    assert data[0]["price"] <= 5000, data  # was: Rs 5,500 item first (score 55)

def test_profile_merge_preserves_personality():
    c = _user_client()
    c.post("/quiz", data={"q1": "woody", "q2": "woody", "q3": "woody", "q4": "woody"})
    c.post("/finder", data={"fragrance": "fresh", "occasion": "university", "strength": "soft",
        "season": "summer", "max_price": "4000"})
    import sqlite3
    db = sqlite3.connect(appmod.DB)
    row = db.execute("SELECT personality FROM preferences WHERE user_id=2").fetchone(); db.close()
    assert row and row[0] == "Woody Elegance", row  # was: NULL after finder save

def test_cart_unknown_404_and_out_of_stock():
    c = make_client()
    assert c.post("/cart/add/9999").status_code == 404
    import sqlite3
    db = sqlite3.connect(appmod.DB); db.execute("UPDATE perfumes SET stock=0 WHERE id=1"); db.commit(); db.close()
    r = c.post("/cart/add/1")
    assert b"Out of stock" in r.data or r.status_code in (200, 302)
    r = c.get("/cart"); assert b"Rose Velvet" not in r.data

def test_wishlist_unknown_404_and_admin_noop_404():
    c = _user_client()
    assert c.post("/wishlist/toggle/9999").status_code == 404
    # Place a real order first (same DB — do NOT reset it with _admin_client).
    c.post("/cart/add/2")
    c.post("/checkout", data={"address": "Test Street 1"})
    c.get("/logout")
    c.post("/login", data={"email": "admin@velvet.demo", "password": TEST_ADMIN_PW})
    assert c.post("/admin/perfume/9999/delete").status_code == 404
    assert c.post("/admin/order/9999/status", data={"status": "Shipped"}).status_code == 404
    r = c.post("/admin/order/1/status", data={"status": "Totally Arbitrary"})
    assert r.status_code == 302  # invalid status is refused, not stored
    import sqlite3
    db = sqlite3.connect(appmod.DB)
    status = db.execute("SELECT status FROM orders WHERE id=1").fetchone()[0]; db.close()
    assert status == "Placed (Demo/COD)", status

def test_chatbot_shows_all_reasons():
    c = make_client()
    r = c.post("/api/chat", json={"message": "fresh perfume for university under 4000"})
    ans = r.get_json()["answer"]
    assert "Matches your fresh" in ans and "Suitable for university" in ans and "Within budget" in ans

def test_register_at_only_rejected_and_logout_keeps_cart():
    c = make_client()
    c.post("/register", data={"name": "At", "email": "@", "password": "secret123"})
    import sqlite3
    db = sqlite3.connect(appmod.DB); n = db.execute("SELECT COUNT(*) FROM users WHERE email='@'").fetchone()[0]; db.close()
    assert n == 0
    c2 = _user_client("keep@demo.local")
    c2.post("/cart/add/2")
    c2.get("/logout")
    c2.post("/login", data={"email": "keep@demo.local", "password": "secret123"})
    r = c2.get("/cart"); assert b"Citrus Dawn" in r.data  # was: cart wiped by session.clear()

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t(); print("PASS", t.__name__)
        except Exception as e:
            failed += 1; print("FAIL", t.__name__, "->", e)
    print(f"{len(tests)-failed}/{len(tests)} passed")
    raise SystemExit(1 if failed else 0)

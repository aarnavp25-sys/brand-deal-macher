"""End-to-end and security test of the Kindred website, run against a running server.

  python3 web/db/e2e_test.py [base_url]        default http://localhost:3000

What it does (no LLM, no OpenRouter):
  1. Three test brands (separate accounts) sign in through /auth/confirm, answer every chat question through the
     real API, and load their creators. Each result is checked against an independent database query: same count,
     every creator in the chosen category, no shops / personal accounts.
  2. Security checks: signed-out access, CSRF, one brand opening another brand's search, bad input, open redirects,
     what the public (publishable) key can read directly from Supabase, private photo bucket, security headers.
Test users live on the domain kindred-test.example.com; remove them with: python3 web/db/test_login.py --delete-all
Python 3 stdlib only.
"""
import http.cookiejar, json, pathlib, subprocess, sys, urllib.error, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000").rstrip("/")
ENV = {}
for line in (HERE.parent / ".env.local").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1)
        ENV[k.strip()] = v.strip()
SB, SECRET, PUB = ENV["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/"), ENV["SUPABASE_SECRET_KEY"], ENV["NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY"]

passed, failed = 0, []


def check(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed.append(name)
        print(f"  FAIL  {name}  {detail}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


class Client:
    """A browser-like client with its own cookie jar."""

    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.follow = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))
        self.nofollow = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), NoRedirect)

    def req(self, method, path, body=None, origin=BASE, follow=False, raw=None, headers=None):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        h = {"Content-Type": "application/json", **(headers or {})}
        if origin:
            h["Origin"] = origin
        r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
        try:
            resp = (self.follow if follow else self.nofollow).open(r, timeout=60)
            return resp.status, resp.headers, resp.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.headers, e.read().decode()

    def json(self, method, path, body=None, **kw):
        s, _, t = self.req(method, path, body, **kw)
        try:
            return s, json.loads(t)
        except ValueError:
            return s, {"_text": t[:200]}

    def login(self, n):
        link = subprocess.check_output([sys.executable, str(HERE / "test_login.py"), str(n), BASE, "/dashboard"], text=True).strip()
        s, h, _ = self.req("GET", link[len(BASE):], origin=None)
        return s, h.get("Location", "")


def rest(path, key, token=None, method="GET", body=None):
    h = {"apikey": key, "Authorization": f"Bearer {token or key}", "Content-Type": "application/json"}
    r = urllib.request.Request(SB + path, method=method, headers=h, data=json.dumps(body).encode() if body is not None else None)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        t = resp.read().decode()
        return resp.status, json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        t = e.read().decode()
        try:
            return e.code, json.loads(t)
        except ValueError:
            return e.code, t[:200]


def expected(category):
    """Independent count: same rules as the site, written again here on the raw view."""
    q = urllib.parse.urlencode({"select": "username,account_type,in_india,quality,flags", "ai_status": "eq.done",
                                "activity": "eq.active", "category": f"eq.{category}", "limit": "2000"})
    _, rows = rest(f"/rest/v1/creator_overview?{q}", SECRET)
    keep = [r["username"] for r in rows if r["account_type"] in ("creator", "professional") and r["in_india"] != "no"
            and r["quality"] != "weak" and not any(f.startswith("not brand-safe") for f in (r["flags"] or []))]
    return set(keep), {r["username"] for r in rows if r["account_type"] not in ("creator", "professional")}


BRANDS = [
    (2, "Achaar Ghar", {
        "about": "Achaar Ghar is a family kitchen in Indore. My mother makes mango, lemon and mixed vegetable pickles in "
                 "mustard oil, the way her mother did, and we ship them across India.",
        "product": "Mango pickle 500g jar", "category": "Food & Beverages", "customer_gender": "all",
        "customer_ages": ["25-34", "35+"], "creator_gender": "any", "languages": ["hindi"], "size": "10-30",
        "goal": "sales", "styles": ["recipe_cooking", "review_unboxing"]}),
    (3, "Veda Roots", {
        "about": "Veda Roots makes ayurvedic grooming for men in Kochi: beard oil, charcoal face wash and a hair serum "
                 "with bhringraj. We sell online to young men.",
        "product": "Charcoal face wash for men", "category": "Beauty & Skincare", "customer_gender": "men",
        "customer_ages": ["18-24", "25-34"], "creator_gender": "male", "languages": ["hindi", "english", "malayalam"],
        "size": "any", "goal": "reach", "styles": ["talking_to_camera", "review_unboxing"]}),
    (4, "Chhota Kurta", {
        "about": "Chhota Kurta is a small label in Ahmedabad stitching cotton ethnic wear for kids aged 1 to 8: kurtas, "
                 "lehengas and festive sets. Parents buy them for festivals and weddings.",
        "product": "Festive cotton kurta set for kids", "category": "Parenting & Kids", "customer_gender": "women",
        "customer_ages": ["25-34"], "creator_gender": "female", "languages": [], "size": "any",
        "goal": "sales", "styles": ["vlog"]}),
]
ORDER = ["about", "product", "category", "customer_gender", "customer_ages", "creator_gender", "languages", "size", "goal", "styles"]


def as_answer(step, v):
    if step in ("customer_ages", "languages", "styles") and v == []:
        return ["*"]
    return v


def run_brand(n, name, answers):
    print(f"\n== Brand {n}: {name} ({answers['category']})")
    c = Client()
    s, loc = c.login(n)
    check("sign-in link logs in and goes to /dashboard", s in (302, 303, 307) and loc.endswith("/dashboard"), f"{s} {loc}")
    s, j = c.json("POST", "/api/searches")
    check("start a search", s == 200 and "id" in j, f"{s} {j}")
    sid = j["id"]
    for step in ORDER:
        s, j = c.json("POST", f"/api/searches/{sid}/answer", {"step": step, "value": as_answer(step, answers[step])})
        if s != 200:
            check(f"answer {step}", False, f"{s} {j}")
            return c, sid, None
    check("all 10 answers accepted, chat says ready", j.get("status") == "ready", j.get("status"))
    guess = next((m.get("suggest") for m in j["messages"] if m.get("step") == "category"), None)
    print(f"        category suggestion from the brand's words: {guess}")
    s, j = c.json("POST", f"/api/searches/{sid}/run", {"brief": answers})
    check("run search", s == 200 and j.get("ok"), f"{s} {j}")
    s, _, html = c.req("GET", f"/results/{sid}", origin=None)
    check("results page renders (200)", s == 200 and "Sort by" in html, str(s))

    _, rows = rest(f"/rest/v1/brand_searches?select=results,brief,user_id&id=eq.{sid}", SECRET)
    res = rows[0]["results"]
    got = [x["username"] for x in res["creators"]]
    want, not_creators = expected(answers["category"])
    check(f"result count matches independent DB count ({len(want)})", set(got) == want and len(got) == len(want),
          f"got {len(got)}; missing {sorted(want - set(got))[:3]}; extra {sorted(set(got) - want)[:3]}")
    check("every creator is in the chosen category", all(x["category"] == answers["category"] for x in res["creators"]))
    check("no shop / brand / personal accounts", not (set(got) & not_creators))
    check("brief stored exactly as answered", rows[0]["brief"] == answers)
    photos = html.count("creator-photos/")
    print(f"        {len(got)} creators, {photos} signed photo links on the page; top 5 by followers:")
    for x in res["creators"][:5]:
        print(f"          @{x['username']:<28} {x['followers']:>6}  {x['creator_gender'] or '-':<8} {(x['niche'] or x['about'] or '')[:70]}")
    return c, sid, rows[0]["user_id"]


def security(clients):
    print("\n== Security")
    (c2, sid2, uid2), (c3, sid3, _uid3) = clients[0], clients[1]
    anon = Client()

    s, h, _ = anon.req("GET", "/dashboard", origin=None)
    check("signed out: /dashboard redirects to /login", s == 307 and "/login" in h.get("Location", ""), f"{s}")
    s, h, _ = anon.req("GET", f"/results/{sid2}", origin=None)
    check("signed out: a results link redirects to /login", s == 307 and "/login" in h.get("Location", ""), f"{s}")
    s, _ = anon.json("POST", "/api/searches")
    check("signed out: API returns 401", s == 401, str(s))

    s, _ = c2.json("POST", "/api/searches", origin=None)
    check("CSRF: POST without Origin is blocked (403)", s == 403, str(s))
    s, _ = c2.json("POST", "/api/searches", origin="https://evil.example")
    check("CSRF: POST from another site is blocked (403)", s == 403, str(s))

    s, _, _ = c3.req("GET", f"/results/{sid2}", origin=None)
    check("brand 3 cannot open brand 2's results (404)", s == 404, str(s))
    s, _, _ = c3.req("GET", f"/find/{sid2}", origin=None)
    check("brand 3 cannot open brand 2's chat (404)", s == 404, str(s))
    s, _ = c3.json("POST", f"/api/searches/{sid2}/run", {"brief": BRANDS[0][2]})
    check("brand 3 cannot re-run brand 2's search (404)", s == 404, str(s))
    s, _ = c3.json("DELETE", f"/api/searches/{sid2}")
    _, still = rest(f"/rest/v1/brand_searches?select=id&id=eq.{sid2}", SECRET)
    check("brand 3 cannot delete brand 2's search (row still there)", len(still) == 1, f"{s} {still}")

    s, j = c2.json("POST", "/api/searches")
    new = j["id"]
    s, j = c2.json("POST", f"/api/searches/{new}/answer", {"step": "category", "value": "Food & Beverages"})
    check("answering out of order is refused (409)", s == 409, f"{s} {j}")
    s, j = c2.json("POST", f"/api/searches/{new}/answer", {"step": "about", "value": "x"})
    check("too-short answer is refused (400)", s == 400, f"{s} {j}")
    s, j = c2.json("POST", f"/api/searches/{new}/answer", raw=b'{"step":"about","value":"' + b"a" * 9000 + b'"}')
    check("oversized request is refused (413)", s == 413, f"{s}")
    s, j = c2.json("POST", f"/api/searches/{new}/answer", raw=b"not json")
    check("malformed JSON is refused (400)", s == 400, f"{s}")
    c2.json("POST", f"/api/searches/{new}/answer", {"step": "about", "value": "A test brand that makes things for people."})
    c2.json("POST", f"/api/searches/{new}/answer", {"step": "product", "value": "Test product"})
    s, j = c2.json("POST", f"/api/searches/{new}/answer", {"step": "category", "value": "Weapons"})
    check("unknown category is refused (400)", s == 400, f"{s} {j}")
    s, j = c2.json("POST", f"/api/searches/{new}/run", {"brief": {**BRANDS[0][2], "category": "Weapons"}})
    check("run with an unfinished chat is refused (409)", s == 409, f"{s} {j}")
    s, _, _ = c2.req("GET", "/results/not-a-uuid", origin=None)
    check("bad search id gives 404", s == 404, str(s))
    c2.json("DELETE", f"/api/searches/{new}")
    _, gone = rest(f"/rest/v1/brand_searches?select=id&id=eq.{new}", SECRET)
    check("a brand can delete its own search", gone == [], str(gone))

    for path, label in [("/auth/callback?next=//evil.example&code=x", "callback"), ("/auth/confirm?next=https://evil.example&token_hash=x&type=magiclink", "confirm")]:
        s, h, _ = anon.req("GET", path, origin=None)
        loc = h.get("Location", "")
        check(f"open redirect blocked on /auth/{label}", "evil.example" not in loc, loc)

    # Direct Supabase access with the public key (what any visitor could try from the browser)
    s, j = rest("/rest/v1/creator_overview?select=username&limit=1", PUB)
    check("public key cannot read creator_overview", s in (401, 403) or j == [], f"{s} {j}")
    s, j = rest("/rest/v1/creator_ai?select=username&limit=1", PUB)
    check("public key cannot read creator_ai", s in (401, 403) or j == [], f"{s} {j}")
    s, j = rest("/rest/v1/brand_searches?select=id&limit=5", PUB)
    check("public key cannot read brand searches", s in (401, 403) or j == [], f"{s} {j}")
    s, j = rest("/rest/v1/llm_calls?select=id&limit=1", PUB)
    check("public key cannot read llm_calls", s in (401, 403) or j == [], f"{s} {j}")

    token = next((urllib.parse.unquote(ck.value) for ck in c3.jar if "auth-token" in ck.name), None)
    if token and token.startswith("base64-"):
        import base64
        token = json.loads(base64.b64decode(token[7:] + "==").decode()).get("access_token")
    elif token:
        token = json.loads(token).get("access_token") if token.startswith("{") else None
    if token:
        s, j = rest("/rest/v1/brand_searches?select=id,user_id", PUB, token)
        check("signed-in brand reading Supabase directly sees only its own searches",
              s == 200 and all(r["user_id"] != uid2 for r in j), f"{s} {j}")
        s, j = rest("/rest/v1/brand_searches", PUB, token, "POST", {"user_id": uid2, "messages": []})
        check("signed-in brand cannot insert rows directly", s in (401, 403), f"{s} {j}")
        s, j = rest("/rest/v1/creator_overview?select=username&limit=1", PUB, token)
        check("signed-in brand cannot read creator data directly", s in (401, 403) or j == [], f"{s} {j}")
    else:
        check("found brand 3's session token for direct checks", False, "cookie not found")

    s, _ = rest("/storage/v1/object/public/creator-photos/" + urllib.parse.quote("x.jpg"), PUB)
    check("photo bucket is not public", s in (400, 404), str(s))

    s, h, _ = anon.req("GET", "/", origin=None)
    for header in ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy", "Strict-Transport-Security"]:
        check(f"header {header}", bool(h.get(header)))
    check("no X-Powered-By header", not h.get("X-Powered-By"))


def bundle_scan():
    print("\n== Browser bundle")
    static = HERE.parent / ".next" / "static"
    if not static.exists():
        print("  (no production build found, skipped)")
        return
    text = "".join(p.read_text(errors="ignore") for p in static.rglob("*.js"))
    # (supabase-js itself contains the prefix "sb_secret_" in a key-type check, so look for the real key only)
    check("secret key not in browser JavaScript", SECRET not in text)
    check("legacy service key not in browser JavaScript", "service_role" not in text)
    check("management token not in browser JavaScript", ENV.get("SUPABASE_ACCESS_TOKEN", "x") not in text)


if __name__ == "__main__":
    clients = [run_brand(*b) for b in BRANDS]
    security(clients)
    bundle_scan()
    print(f"\n{passed} passed, {len(failed)} failed")
    for f in failed:
        print("  failed:", f)
    sys.exit(1 if failed else 0)

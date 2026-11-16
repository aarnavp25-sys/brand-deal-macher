"""Demo website (prototype) for Brand Deal Matcher: a brand describes its product, gets matched creators.

Run:  python3 demo/server.py   ->  http://127.0.0.1:8788
Uses admin/.env (SUPABASE_URL, SUPABASE_SERVICE_KEY). Read-only against Supabase.

No LLM yet: the brief is parsed with the taxonomy keywords and explanations are
templated from the score breakdown. Swap parse_brief/explain for Claude calls later.
Signals with no data yet (content quality, follower growth) are left out and the
remaining weights are re-normalised, so scores stay on 0-100.
"""
import json, os, re, sys, urllib.request, urllib.parse, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "pipeline"))
from taxonomy import CATEGORIES, PRODUCT_TYPES  # noqa: E402

CITIES = ["pune", "mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata", "jaipur", "ahmedabad", "indore",
          "nagpur", "nashik", "goa", "gurgaon", "noida", "lucknow", "surat", "chandigarh"]
WEIGHTS = {"sales": {"product": 30, "engagement": 20, "reach": 15, "quality": 15, "growth": 10, "consistency": 5, "location": 5},
           "reach": {"product": 20, "engagement": 15, "reach": 30, "quality": 15, "growth": 10, "consistency": 5, "location": 5}}
_cache = {"t": 0}


def load_env():
    for path in (os.path.join(HERE, ".env"), os.path.join(HERE, "..", "admin", ".env")):
        if os.path.exists(path):
            for line in open(path):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"'))
    if not os.environ.get("SUPABASE_SERVICE_KEY"):
        raise SystemExit("Missing SUPABASE_URL / SUPABASE_SERVICE_KEY (admin/.env).")


def rest(path):
    key = os.environ["SUPABASE_SERVICE_KEY"]
    req = urllib.request.Request(os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1/" + path,
                                 headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def data():
    """Usable creators + product links, cached for 60 s."""
    if time.time() - _cache["t"] > 60:
        cols = ("id,username,full_name,bio,followers,follower_tier,niche_primary,niche_secondary,niche_share,city,"
                "engagement_rate,reel_reach,avg_reel_views,posts_per_week,collab_open,email,profile_pic_url,"
                "content_quality_est,last_post_at")
        _cache["creators"] = rest(f"creators?select={cols}&status=eq.active&fake_flag=is.false&limit=10000")
        _cache["products"] = rest("creator_products?select=*&limit=50000")
        snaps = rest("creator_snapshots?select=creator_id,taken_at,followers&order=taken_at&limit=100000")
        g = {}
        for s in snaps:
            g.setdefault(s["creator_id"], []).append(s)
        _cache["growth"] = {k: (v[-1]["followers"] - v[0]["followers"]) / v[0]["followers"]
                            for k, v in g.items() if len(v) >= 2 and v[0]["followers"]}
        _cache["t"] = time.time()
    return _cache


def has(word, text):
    # allow simple word forms: cake/cakes, bake/baker, accessory/accessories
    return re.search(r"(?<![a-z])" + re.escape(word) + r"(s|es|r|rs|ry|ries)?(?![a-z])", text) is not None


def parse_brief(q):
    """Turn the brand's free text + form choices into a structured request (what the LLM will do later)."""
    t = (q.get("brief") or "").lower().replace("jewellery", "jewelry")
    men = any(has(w, t) for w in ("men", "mens", "men's", "male", "gents", "boys", "guys"))
    women = any(has(w, t) for w in ("women", "womens", "women's", "female", "ladies", "girls"))
    products = []
    for name, (cat, kws) in PRODUCT_TYPES.items():
        if name.startswith("men's") and women and not men or name.startswith("women's") and men and not women:
            continue
        if has(name.replace("men's ", "").replace("women's ", ""), t) or any(has(k, t) for k in kws):
            products.append(name)
    if q.get("product"):
        products = [q["product"]]
    # rank categories by how many of their keywords the brief uses ("gaming accessories for bgmi" -> Gaming, not Jewelry)
    hits = {c: sum(has(k, t) for k in v[3]) for c, v in CATEGORIES.items()}
    cats = sorted((c for c in hits if hits[c]), key=lambda c: -hits[c])
    prod_cats = sorted({PRODUCT_TYPES[p][0] for p in products}, key=lambda c: -hits.get(c, 0))
    if cats and prod_cats and hits.get(cats[0], 0) > hits.get(prod_cats[0], 0):
        products = [p for p in products if PRODUCT_TYPES[p][0] == cats[0]] or products
        prod_cats = sorted({PRODUCT_TYPES[p][0] for p in products})
    cats = list(dict.fromkeys(prod_cats + cats))
    if q.get("category"):
        cats = [q["category"]] + [c for c in cats if c != q["category"]]
    city = q.get("city") or next((c.title() for c in CITIES if has(c, t)), None)
    return {"products": products[:4], "categories": cats[:3], "city": city,
            "tier": q.get("tier") or None, "goal": q.get("goal") if q.get("goal") in WEIGHTS else "sales",
            "audience": "men" if men and not women else "women" if women and not men else None}


def pct_rank(values):
    s = sorted(v for v in values if v is not None)
    return lambda v: None if v is None or not s else sum(1 for x in s if x <= v) / len(s)


def match(q):
    d, req = data(), parse_brief(q)
    creators = [c for c in d["creators"] if not req["tier"] or c["follower_tier"] == req["tier"]]
    by_c = {}
    for p in d["products"]:
        by_c.setdefault(p["creator_id"], {})[p["product_type"]] = p
    reach_r = pct_rank([c["reel_reach"] for c in d["creators"]])
    er_by_tier = {t: pct_rank([c["engagement_rate"] for c in d["creators"] if c["follower_tier"] == t])
                  for t in ("nano", "micro", "mid")}
    W = WEIGHTS[req["goal"]]
    out = []
    for c in creators:
        prods = by_c.get(c["id"], {})
        # product fit: proven product evidence beats category match beats "possible"
        fit, label, evidence = 0.0, None, None
        for p in req["products"]:
            cp = prods.get(p)
            if cp and cp["kind"] == "proven":
                f = 0.5 + 0.5 * min(float(cp["specialization"]) / 0.5, 1)
                # keyword evidence is noisy ("ring ceremony", "bike chain"): trust it fully only when the
                # creator's own category is relevant to the brand, and discount single-post evidence
                wanted = set(req["categories"]) | {PRODUCT_TYPES[p][0]}
                relevant = c["niche_primary"] in wanted  # secondary is keyword-noisy (biker -> "chain")
                if not relevant:
                    f *= 0.75 if c["niche_secondary"] in wanted else 0.55
                if cp["evidence_posts"] < 2:
                    f *= 0.8
                lab = "specialist" if relevant and float(cp["specialization"]) >= 0.5 else "wider"
            elif cp:
                f, lab = 0.3, "potential"
            else:
                continue
            if f > fit:
                fit, label, evidence = f, lab, (p, cp)
        if not req["products"] or fit < 0.5:
            for i, cat in enumerate(req["categories"]):
                share = float(c["niche_share"] or 0)
                f = (0.4 + 0.6 * min(share / 0.6, 1)) * (1 if i == 0 else 0.8) if c["niche_primary"] == cat else \
                    (0.45 if c["niche_secondary"] == cat else 0)
                if req["products"]:
                    f *= 0.75  # brand named a product; a category-only match is weaker evidence
                if f > fit:
                    fit = f
                    # a creator whose content is mostly the brand's category is a specialist audience
                    # even if captions never name the exact product (gamers rarely write "controller")
                    label = ("specialist" if share >= 0.6 and i == 0 else "wider") if f >= 0.45 else "potential"
                    evidence = (cat, None)
        if fit <= 0:
            continue
        parts = {"product": fit,
                 "engagement": er_by_tier[c["follower_tier"]](c["engagement_rate"]),
                 "reach": reach_r(c["reel_reach"]),
                 "quality": float(c["content_quality_est"]) / 10 if c["content_quality_est"] is not None else None,
                 "growth": None if c["id"] not in d["growth"] else max(0, min(d["growth"][c["id"]] / 0.1, 1)),
                 "consistency": None if c["posts_per_week"] is None else min(float(c["posts_per_week"]) / 3, 1),
                 "location": None if not req["city"] else 1.0 if (c["city"] or "").lower() == req["city"].lower()
                 else 0.3 if not c["city"] else 0.0}
        avail = {k: v for k, v in parts.items() if v is not None}
        total_w = sum(W[k] for k in avail)
        score = round(sum(W[k] * v for k, v in avail.items()) / total_w * 100)
        out.append({"creator": c, "score": score, "label": label,
                    "breakdown": {k: (None if v is None else round(W[k] * v, 1), W[k]) for k, v in parts.items()},
                    "explanation": explain(c, label, evidence, parts, req)})
    out.sort(key=lambda r: -r["score"])
    good = [r for r in out if r["score"] >= 50]
    # mix: ~40% specialists, ~50% wider, ~10% potential, then fill with the best of the rest
    n, picked = 20, []
    for lab, k in (("specialist", 8), ("wider", 10), ("potential", 2)):
        picked += [r for r in good if r["label"] == lab][:k]
    picked += [r for r in good if r not in picked][: n - len(picked)]
    picked.sort(key=lambda r: -r["score"])
    return {"understood": req, "results": picked[:n], "considered": len(creators), "matched": len(good)}


def explain(c, label, evidence, parts, req):
    """Template explanation built only from the numbers (an LLM will write this later)."""
    s = []
    if evidence and evidence[1]:
        p, cp = evidence
        if cp["kind"] == "proven":
            s.append(f"{round(float(cp['specialization']) * 100)}% of recent posts feature {p} ({cp['evidence_posts']} posts)"
                     + (f", including {cp['paid_posts']} paid collab" if cp["paid_posts"] else "") + ".")
        else:
            s.append(f"Has not posted about {p} yet, but the content fits it.")
    elif evidence:
        s.append(f"Creates {evidence[0]} content ({round(float(c['niche_share'] or 0) * 100)}% of recent posts).")
    if c["reel_reach"] is not None:
        s.append(f"Reels reach {c['reel_reach']}x their follower count" +
                 (" — top 25% of creators." if (parts["reach"] or 0) >= 0.75 else "."))
    if parts["engagement"] is not None:
        s.append(f"Engagement {c['engagement_rate']}%, better than {round(parts['engagement'] * 100)}% of {c['follower_tier']} creators.")
    if c["posts_per_week"]:
        s.append(f"Posts about {c['posts_per_week']} times a week.")
    if req["city"] and parts["location"] == 1.0:
        s.append(f"Based in {c['city']}.")
    return " ".join(s)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False, default=str).encode())

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        try:
            if u.path == "/api/meta":
                d = data()
                return self.send(200, {"categories": list(CATEGORIES), "products": sorted(PRODUCT_TYPES),
                                       "creators": len(d["creators"]),
                                       "cities": sorted({c["city"] for c in d["creators"] if c["city"]})})
            if u.path == "/api/match":
                q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
                return self.send(200, match(q))
        except Exception as e:  # show the reason in the UI instead of a blank page
            return self.send(500, {"message": str(e)})
        self.send(404, {"message": "not found"})


if __name__ == "__main__":
    load_env()
    port = int(os.environ.get("DEMO_PORT", "8788"))
    print(f"Demo website: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

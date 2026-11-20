"""Search evaluation: run fixed brand briefs against the live API and check every shown creator against the
user's rules. Written 2026-11-20 after a run of one-off fixes broke one search while fixing another; run it after
every matching change. Each uncached search costs ~$0.003 (brand profile + review); repeats are free (llm_cache).

  python3 pipeline/eval_search.py            all briefs
  python3 pipeline/eval_search.py jewel tea  only briefs whose name contains one of these words

Rules (user's definitions, 2026-11-19/20):
  R1 category column: the creator's main category is the product's own category or a close neighbour (or they
     showed the product itself)
  R2 category column: no creator from another field (the AI review's "field")
  R3 nothing the review called "weak" is shown
  R4 no personal account or own-shop page (account check) is shown
  R5 a shop that sells only at its own counter sees creators from its own city only
  R6 wider reach: at least 3,000 followers
  R7 niche: product evidence (posted it, or it fits a scene they film) or a shop-visit creator for a local store
  R8 a creator appears in one column only
  R9 a men's product never shows a creator whose audience is women and who features women's products (and back)
  W1 (warning) audience is the other gender but they feature products for the brand's buyers
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import llm_classify as L  # noqa: E402

BRIEFS = [
    ("men's jewellery", {"brief": "Affordable stainless steel jewellery for men - chains, bracelets and rings, sold online"}),
    ("men's watches", {"brief": "Budget men's watches sold online for young men, everyday style"}),
    ("women's jewellery", {"brief": "Oxidised silver earrings and jhumkas for women, Rs 400, sold on Instagram"}),
    ("perfume Rs 1000", {"brief": "We sell mens perfume at Rs 1000 a bottle, online on our website"}),
    ("perfume Rs 10000", {"brief": "Luxury niche perfumes for men, Rs 10,000 per bottle, sold online"}),
    ("gym wear", {"brief": "Gym wear for men and women, t-shirts joggers and sports bras, around Rs 800, sold online"}),
    ("protein", {"brief": "Whey protein and creatine for gym goers, Rs 2000 a jar, sold online"}),
    ("skincare", {"brief": "Ayurvedic face serum and face wash for women, Rs 600, made with kumkumadi and saffron"}),
    ("lipstick", {"brief": "Long lasting matte lipsticks for Indian skin tones, Rs 499, cruelty free"}),
    ("instant tea", {"brief": "Instant masala chai premix sachets, just add hot water, Rs 199 for 10 sachets, sold online"}),
    ("masala", {"brief": "Homemade spice blends and masalas from Kerala, garam masala and sambar powder, sold online"}),
    ("mithai Jaipur", {"brief": "Traditional mithai and sweets shop in Jaipur, ghewar and kaju katli", "city": "Jaipur",
                       "channel": "local store"}),
    ("candles", {"brief": "Hand poured soy scented candles and gift hampers, Rs 700, sold on Instagram"}),
    ("kids clothing", {"brief": "Cotton kids clothing for ages 2-8, Rs 500, sold online to mothers"}),
    ("phone accessories", {"brief": "Phone cases, chargers and earbuds for young people, budget prices, sold online"}),
    ("pet food", {"brief": "Healthy dog treats and food made in India, sold online to pet parents"}),
]

COLS = ["niche", "category", "trending"]


def env():
    L.load_env()
    url = os.environ["SUPABASE_URL"].rstrip("/") + "/functions/v1/api/match"
    return url, os.environ["SUPABASE_ANON_KEY"]


def search(url, anon, body):
    # the API allows 30 searches per 10 minutes per client: on 429 wait and retry
    for attempt in range(15):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers={
            "apikey": anon, "Authorization": "Bearer " + anon, "Content-Type": "application/json",
            "Origin": "http://127.0.0.1:8788"})
        try:
            with urllib.request.urlopen(req, timeout=150) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 14:
                raise
            print("  (rate limit: waiting 60 s)", flush=True)
            time.sleep(60)


def main(words):
    url, anon = env()
    flagged = {r["username"]: r["account_type"] for r in L.rest_all(
        "creators?select=username,account_type&account_type=in.(personal,own%20shop)&order=id")}
    total_v = total_w = 0
    for name, body in BRIEFS:
        if words and not any(w.lower() in name.lower() for w in words):
            continue
        d = search(url, anon, body)
        u = d["understood"]
        catcol = set(u.get("category_column") or [])
        local_only = u.get("channel") == "local store" and u.get("city")
        men = u.get("audience") == "men"
        women = u.get("audience") == "women"
        seen, bad, warn = {}, [], []
        print(f"\n## {name}  | products {u['products']} | category column: {sorted(catcol)} | price {u.get('price')}"
              f" | audience {u.get('audience')}{' | ' + u['city'] + ' local' if local_only else ''}")
        for col in COLS:
            rows = d["columns"].get(col, [])
            print(f"  -- {col} ({len(rows)})")
            for r in rows:
                c = r["creator"]
                tag = f"@{c['username']}"
                if c["username"] in seen:
                    bad.append(f"R8 {tag} in {seen[c['username']]} and {col}")
                seen[c["username"]] = col
                if col == "category" and c["niche_primary"] not in catcol and r.get("evidence_kind") != "proven":
                    bad.append(f"R1 {tag} main category {c['niche_primary']} not in {sorted(catcol)}")
                if col == "category" and r.get("field") == "other field":
                    bad.append(f"R2 {tag} other field")
                if r.get("verdict") == "weak":
                    bad.append(f"R3 {tag} weak shown in {col}")
                if c["username"] in flagged:
                    bad.append(f"R4 {tag} account check said {flagged[c['username']]}")
                if local_only and (c.get("city") or "").lower() != u["city"].lower():
                    bad.append(f"R5 {tag} city {c.get('city')} for a {u['city']} shop")
                if col == "trending" and (c.get("followers") or 0) < 3000:
                    bad.append(f"R6 {tag} {c.get('followers')} followers in wider reach")
                if col == "niche" and r.get("evidence_kind") not in ("proven", "natural") and not (
                        local_only and c.get("store_visits") in ("often", "sometimes")):
                    bad.append(f"R7 {tag} in niche with evidence {r.get('evidence_kind')}")
                aud, pf = c.get("audience_gender"), c.get("products_for")
                if (men and aud == "women" and pf not in ("men", "unisex")) or \
                        (women and aud == "men" and pf not in ("women", "unisex")):
                    bad.append(f"R9 {tag} audience {aud}, features products for {pf}, in {col}")
                elif (men and aud == "women") or (women and aud == "men"):
                    warn.append(f"W1 {tag} audience {aud} (features products for {pf}) in {col}")
                print(f"    {r['score']:>3} {(r.get('verdict') or '-'):6} {(r.get('field') or '-'):11} {tag} "
                      f"{c['followers']} {c['niche_primary']} [{c.get('audience_gender')}] :: {(r.get('reason') or '')[:95]}")
        for v in bad:
            print("  !! " + v)
        for w in warn:
            print("  ?? " + w)
        total_v += len(bad)
        total_w += len(warn)
    print(f"\nviolations: {total_v}, warnings: {total_w}")


if __name__ == "__main__":
    main(sys.argv[1:])

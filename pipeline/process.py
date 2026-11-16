"""Filter, enrich, classify (keyword-v1) and load creators into Supabase.

usage:
  python3 process.py filter <out_usernames.json> <search.json> [more search.json ...]
  python3 process.py build  <out_rows.json> <reels.json> <search.json> [more ...]
  SUPABASE_URL=... SUPABASE_SERVICE_KEY=... python3 process.py load <rows.json> [raw run files ...]

Classification here is keyword-based ("keyword-v1"): category from post/bio
keyword share plus the search term that found the creator. The LLM step will
replace it later (classification_method = 'llm').
"""
import json, os, re, sys, statistics as st, urllib.request
from collections import Counter
from datetime import datetime, timezone, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy import CATEGORIES, PRODUCT_TYPES, CREATOR_IG_CATEGORIES_OK, EXTRA_SEARCH_TERMS

NOW = datetime.now(timezone.utc)
TERM_CAT = {t: c for c, v in CATEGORIES.items() for t in v[2]}
TERM_CAT.update({t: c for c, ts_ in EXTRA_SEARCH_TERMS.items() for t in ts_})
TERM_CAT["pune food blogger"] = "Food & Beverages"
CITIES = ["pune", "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai", "kolkata", "ahmedabad",
          "jaipur", "indore", "nagpur", "nashik", "surat", "lucknow", "chandigarh", "goa", "kochi", "thane",
          "noida", "gurgaon", "gurugram", "navi mumbai", "pimpri", "kolhapur", "aurangabad", "bhopal", "patna"]
CITY_NORM = {"bengaluru": "Bangalore", "gurugram": "Gurgaon", "pimpri": "Pune", "navi mumbai": "Mumbai", "thane": "Mumbai"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
# bios that read like a shop/brand page rather than a creator -> status 'review'
BRANDISH = re.compile(r"premium quality|dm to order|order now|cod available|cash on delivery|free shipping|"
                      r"shipping|wholesale|booking open|free delivery|our store|shop now|manufacturer", re.I)
COLLAB = re.compile(r"collab|dm for|for promo|promotion|pr friendly|business enquir|business inquir|work with|paid promo", re.I)


def ts(x):
    try:
        return datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except Exception:
        return None


def kw_hit(kw, text, tags):
    if re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", text):
        return True
    k = kw.replace(" ", "")
    return len(k) >= 4 and any(k in h for h in tags)


def post_text(p):
    return (p.get("caption") or "").lower(), [h.lower() for h in (p.get("hashtags") or [])]


def load_search(paths):
    out = {}
    for path in paths:
        d = json.load(open(path))
        items = d["items"] if isinstance(d, dict) else d
        for it in items:
            if it.get("id") and it.get("username"):
                out.setdefault(it["id"], it)
    return out


def recent_posts(it):
    posts = [p for p in (it.get("latestPosts") or []) if not p.get("isPinned")]
    return sorted(posts, key=lambda p: p.get("timestamp") or "", reverse=True)


def passes(it):
    f = it.get("followersCount") or 0
    posts = recent_posts(it)
    last = max((ts(p.get("timestamp")) for p in posts if ts(p.get("timestamp"))), default=None)
    if not (1000 <= f < 100000): return "followers"
    if it.get("private") or it.get("isRestrictedProfile") or it.get("error"): return "private/restricted"
    if len(posts) < 3: return "few posts"
    if not last or last < NOW - timedelta(days=60): return "inactive"
    if it.get("isBusinessAccount") and it.get("businessCategoryName") not in CREATOR_IG_CATEGORIES_OK: return "business"
    if (it.get("followsCount") or 0) > 2 * f and f < 5000: return "follow-for-follow"
    return None


def cmd_filter(out, paths):
    prof = load_search(paths)
    reasons, keep = Counter(), {}
    for pid, it in prof.items():
        r = passes(it)
        reasons[r or "ok"] += 1
        if not r:
            keep[it["username"]] = TERM_CAT.get(it.get("searchTerm"), "?")
    json.dump(keep, open(out, "w"))
    print("profiles", len(prof), dict(reasons))
    print("kept per source category", dict(Counter(keep.values())))


def classify(it, posts):
    bio = (it.get("biography") or "").lower()
    n = len(posts)
    share = {}
    for c, v in CATEGORIES.items():
        kws = v[3]
        hits = sum(1 for p in posts if any(kw_hit(k, *post_text(p)) for k in kws))
        share[c] = hits / n if n else 0
    score = {c: share[c] + (0.3 if any(kw_hit(k, bio, []) for k in v[3]) else 0)
                + (0.25 if TERM_CAT.get(it.get("searchTerm")) == c else 0) for c, v in CATEGORIES.items()}
    ranked = sorted(score, key=score.get, reverse=True)
    primary = ranked[0]
    secondary = ranked[1] if share[ranked[1]] >= 0.25 else None
    return primary, secondary, round(share[primary], 2)


def products(posts, primary):
    rows, n = [], len(posts)
    for name, (cat, kws) in PRODUCT_TYPES.items():
        ev = [p for p in posts if any(kw_hit(k, *post_text(p)) for k in kws)]
        if ev:
            rows.append({"product_type": name, "kind": "proven", "evidence_posts": len(ev),
                         "specialization": round(len(ev) / n, 2),
                         "paid_posts": sum(1 for p in ev if p.get("paidPartnership")),
                         "last_seen": max(p["timestamp"] for p in ev if p.get("timestamp"))})
    proven = {r["product_type"] for r in rows}
    possible = [k for k, (cat, _) in PRODUCT_TYPES.items() if cat == primary and k not in proven][:3]
    rows += [{"product_type": k, "kind": "possible", "evidence_posts": 0, "specialization": 0,
              "paid_posts": 0, "last_seen": None} for k in possible]
    return rows


def posting_rate(posts):
    times = sorted(t for t in (ts(p.get("timestamp")) for p in posts) if t)
    if len(times) < 2:
        return None
    weeks = max((NOW - times[0]).days, 7) / 7  # oldest of the recent posts -> now
    return round(len(times) / weeks, 2)


def city_of(it, posts):
    bio = (it.get("biography") or "").lower()
    for c in CITIES:
        if c in bio:
            return CITY_NORM.get(c, c.title())
    locs = Counter()
    for p in posts:
        l = (p.get("locationName") or "").lower()
        for c in CITIES:
            if c in l:
                locs[CITY_NORM.get(c, c.title())] += 1
    return locs.most_common(1)[0][0] if locs else None


def cmd_build(out, reels_path, paths):
    prof = load_search(paths)
    reels_d = json.load(open(reels_path))
    reels = Counter()
    by_user = {}
    for r in reels_d["items"]:
        u = (r.get("inputUrl") or "").rstrip("/").split("/")[-1] or r.get("ownerUsername")
        by_user.setdefault(u, []).append(r)
    rows = {"creators": [], "snapshots": [], "posts": [], "creator_products": []}
    for pid, it in prof.items():
        if passes(it):
            continue
        u, f = it["username"], it["followersCount"]
        posts = recent_posts(it)
        rl = [r for r in by_user.get(u, []) if r.get("videoPlayCount") is not None]
        likes = [p["likesCount"] for p in posts if (p.get("likesCount") or -1) >= 0]
        comments = [p.get("commentsCount") or 0 for p in posts]
        # median, not mean: one viral post pushed mean ER to 591% in the first run
        er = (st.median(likes) + st.median(comments)) / f * 100 if likes else None
        views = [r["videoPlayCount"] for r in rl]
        avg_views = st.median(views) if views else None
        t60 = [p for p in posts if (ts(p.get("timestamp")) or NOW) > NOW - timedelta(days=60)]
        primary, secondary, nshare = classify(it, posts + rl)
        prods = products(posts + rl, primary)
        bio = it.get("biography") or ""
        em = EMAIL.search(bio)
        # low ER alone is not fake: some low-ER accounts get 98x followers in reel views
        fake = bool(er is not None and f >= 10000 and er < 0.5 and (avg_views or 0) / f < 0.3)
        brand_like = bool(BRANDISH.search(bio))
        rows["creators"].append({
            "id": pid, "username": u, "full_name": it.get("fullName"), "bio": bio, "followers": f,
            "following": it.get("followsCount"), "posts_count": it.get("postsCount"),
            "follower_tier": "nano" if f < 10000 else "micro" if f < 50000 else "mid",
            "is_business": it.get("isBusinessAccount"), "ig_category": it.get("businessCategoryName"),
            "verified": it.get("verified"), "external_url": it.get("externalUrl"),
            "profile_pic_url": it.get("profilePicUrlHD") or it.get("profilePicUrl"),
            "niche_primary": primary, "niche_secondary": secondary, "niche_share": nshare,
            "sub_tags": [p["product_type"] for p in prods if p["kind"] == "proven"
                         and PRODUCT_TYPES[p["product_type"]][0] == primary],
            "city": city_of(it, posts + rl), "email": em.group(0) if em else None,
            "collab_open": bool(COLLAB.search(bio) or em),
            "engagement_rate": round(er, 2) if er is not None else None,
            "avg_reel_views": round(avg_views) if avg_views else None,
            "reel_reach": round(avg_views / f, 2) if avg_views else None,
            # Apify returns only the latest 12 posts, so "posts in last 60 days / 8.6 weeks" capped at 1.4.
            # Use the real time span the recent posts cover instead.
            "posts_per_week": posting_rate(posts),
            "last_post_at": max(p["timestamp"] for p in posts if p.get("timestamp")),
            "fake_flag": fake, "classification_method": "keyword-v1",
            "status": "review" if brand_like else "active",
            "source_keyword": it.get("searchTerm"), "scraped_at": NOW.isoformat(),
            "updated_at": NOW.isoformat()})
        rows["snapshots"].append({"creator_id": pid, "taken_at": NOW.date().isoformat(),
                                  "followers": f, "following": it.get("followsCount")})
        seen = set()
        for src, p in [("profile", p) for p in posts] + [("reel", r) for r in rl]:
            if p.get("id") in seen or not p.get("id"):
                continue
            seen.add(p["id"])
            cap, tags = post_text(p)
            rows["posts"].append({
                "id": p["id"], "creator_id": pid, "shortcode": p.get("shortCode"), "url": p.get("url"),
                "type": p.get("type"), "source": src, "posted_at": p.get("timestamp"),
                "likes": p["likesCount"] if (p.get("likesCount") or -1) >= 0 else None,
                "comments": p.get("commentsCount"), "views": p.get("videoPlayCount"),
                "caption": (p.get("caption") or "")[:2000], "hashtags": p.get("hashtags") or [],
                "mentions": p.get("mentions") or [], "location": p.get("locationName"),
                "is_pinned": p.get("isPinned"), "paid_partnership": p.get("paidPartnership"),
                "coauthors": [c.get("username") for c in (p.get("coauthorProducers") or []) if c.get("username")],
                "product_labels": [k for k, (_, kws) in PRODUCT_TYPES.items() if any(kw_hit(w, cap, tags) for w in kws)],
                "thumbnail_url": p.get("displayUrl")})
        for pr in prods:
            rows["creator_products"].append({"creator_id": pid, **pr})
    json.dump(rows, open(out, "w"), ensure_ascii=False)
    cs = rows["creators"]
    print("creators", len(cs), "posts", len(rows["posts"]), "products", len(rows["creator_products"]))
    print("per niche_primary", dict(Counter(c["niche_primary"] for c in cs).most_common()))
    print("with reel views", sum(1 for c in cs if c["avg_reel_views"]), "fake", sum(c["fake_flag"] for c in cs),
          "tiers", dict(Counter(c["follower_tier"] for c in cs)), "cities", dict(Counter(c["city"] for c in cs).most_common(6)))


def upsert(table, rows, conflict=None):
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"]
    q = f"?on_conflict={conflict}" if conflict else ""
    for i in range(0, len(rows), 500):
        req = urllib.request.Request(f"{url}/rest/v1/{table}{q}", method="POST",
                                     data=json.dumps(rows[i:i + 500], ensure_ascii=False).encode(),
                                     headers={"apikey": key, "Authorization": f"Bearer {key}",
                                              "Content-Type": "application/json",
                                              "Prefer": "resolution=merge-duplicates,return=minimal"})
        try:
            urllib.request.urlopen(req, timeout=120).read()
        except urllib.error.HTTPError as e:
            sys.exit(f"  {table} rows {i}-{i + 500}: HTTP {e.code} {e.read().decode()[:500]}")
    print(f"  {table}: {len(rows)} rows")


def cmd_load(rows_path, raw_paths):
    rows = json.load(open(rows_path))
    upsert("categories", [{"name": c, "demo_rank": v[0], "sub_tags": v[1]} for c, v in CATEGORIES.items()])
    upsert("product_types", [{"name": k, "category": c, "keywords": kws} for k, (c, kws) in PRODUCT_TYPES.items()])
    upsert("creators", rows["creators"])
    upsert("creator_snapshots", rows["snapshots"], "creator_id,taken_at")
    upsert("posts", rows["posts"])
    upsert("creator_products", rows["creator_products"], "creator_id,product_type")
    cmd_raw(raw_paths)


def storage(method, path, data=None, ctype="application/json"):
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"]
    req = urllib.request.Request(f"{url}/storage/v1/{path}", method=method, data=data,
                                 headers={"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": ctype,
                                          "x-upsert": "true"})
    try:
        return urllib.request.urlopen(req, timeout=300).read()
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300]
        if "already exists" in body:
            return None
        sys.exit(f"  storage {path}: HTTP {e.code} {body}")


def cmd_raw(raw_paths):
    # Raw Apify JSON goes to Storage: a multi-MB jsonb row hit Postgres statement_timeout (57014).
    storage("POST", "bucket", json.dumps({"id": "raw-scrapes", "name": "raw-scrapes", "public": False}).encode())
    for p in raw_paths:
        d = json.load(open(p))
        if not isinstance(d, dict):
            d = {"actor": "instagram-search-scraper (test)", "run_id": None, "input": None, "items": d}
        name = f"{NOW.date()}/{d['actor'].split()[0]}-{d.get('run_id') or os.path.basename(p)}.json"
        storage("POST", f"object/raw-scrapes/{name}", open(p, "rb").read())
        upsert("raw_scrapes", [{"actor": d["actor"], "run_id": d.get("run_id"), "input": d.get("input"),
                                "storage_path": f"raw-scrapes/{name}", "item_count": len(d["items"]),
                                "cost_usd": d.get("cost_usd")}])


if __name__ == "__main__":
    cmd, out = sys.argv[1], sys.argv[2]
    if cmd == "filter": cmd_filter(out, sys.argv[3:])
    elif cmd == "build": cmd_build(out, sys.argv[3], sys.argv[4:])
    elif cmd == "load": cmd_load(out, sys.argv[3:])
    elif cmd == "raw": cmd_raw(sys.argv[2:])

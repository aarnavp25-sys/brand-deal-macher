"""One scraping round on one Apify account: backfill missing reels, collab snowball, optional search terms.

usage:
  python3 pipeline/round.py --account acc14 --dry-run              # plan only: balance, candidates, caps; no spend
  python3 pipeline/round.py --account acc14 --yes                  # run it
  python3 pipeline/round.py --account acc14 --terms ROUND34_TERMS --yes   # also run a search-term dict from taxonomy.py

Tokens come from APIFY_TOKENS in admin/.env (label:token,...). Replaces the per-round shell scripts of
2026-11-18/19 (rounds 12-37). What it does, in order:
  1. reads the account's balance and keeps $0.30 unspent (reel charges post minutes late; see docs, Billing lag)
  2. reels for usable creators that have none and were never sent to the Reel Scraper  -> process.py reels
  3. collab snowball: coauthor usernames from our posts, never tried before (tried = every username in a
     Profile Scraper input stored in raw_scrapes), thin categories first  -> Profile Scraper
  4. optional search terms -> Search Scraper
  5. filter (process.py filter) -> reels for the new kept creators -> build -> load only new creators -> raw upload
  6. AI profile (llm_classify.py run, capped ~$0.001 per new creator) for the new usable creators; --no-llm skips
Work files go to pipeline/runs/<date>-<account>/ (gitignored).
"""
import argparse, collections, json, os, re, subprocess, sys, time, urllib.parse, urllib.request
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import taxonomy  # noqa: E402

BUFFER = 0.30                # never spend the last $0.30 of an account
P_PROFILE, P_SEARCH, P_REEL = 0.0026, 0.0027, 0.0025   # $ per item seen in rounds 12-37 (reel ≈ per creator, 2 reels)
KEEP = 0.45                  # share of snowball profiles that pass the filter (39-49% observed)
BRANDY = re.compile(r"official|store|shop|brand|india$|_in$|media|news|clothing|jewel|studio|cafe|restaurant|hotel|"
                    r"resort|club|academy|events|foods|bakery|boutique|label|wear|beauty$|cosmetics|tv$|films|records|"
                    r"music$|productions|agency|magazine|travel(s)?$|tours|app$|\.com", re.I)


def load_env():
    for line in open(os.path.join(HERE, "..", "admin", ".env")):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def rest_all(path):
    U, K = os.environ["SUPABASE_URL"].rstrip("/"), os.environ["SUPABASE_SERVICE_KEY"]
    out, o = [], 0
    while True:
        req = urllib.request.Request(f"{U}/rest/v1/{path}&limit=1000&offset={o}", headers={"apikey": K, "Authorization": "Bearer " + K})
        page = json.load(urllib.request.urlopen(req, timeout=120))
        out += page
        o += 1000
        if len(page) < 1000:
            return out


def token(label):
    for pair in os.environ.get("APIFY_TOKENS", "").split(","):
        if pair.split(":", 1)[0] == label:
            return pair.split(":", 1)[1]
    raise SystemExit(f"{label} not in APIFY_TOKENS (admin/.env)")


def balance(tok):
    req = urllib.request.Request("https://api.apify.com/v2/users/me/limits", headers={"Authorization": "Bearer " + tok})
    d = json.load(urllib.request.urlopen(req, timeout=30))["data"]
    return d["limits"]["maxMonthlyUsageUsd"] - d["current"]["monthlyUsageUsd"]


def plan(budget, n_terms):
    """Pick the work that fits the budget: reels backfill first, then search, then as many profiles as fit."""
    cr = rest_all("creators?select=id,username,niche_primary,status,fake_flag,avg_reel_views&order=id")
    usable = [c for c in cr if c["status"] == "active" and not c["fake_flag"]]
    have = {c["username"].lower() for c in cr}
    raws = rest_all("raw_scrapes?select=actor,input&order=id")
    tried = {u.lower() for r in raws if r["actor"].startswith("instagram-profile") for u in (r["input"] or {}).get("usernames", [])}
    reeled = {u.lower() for r in raws if r["actor"].startswith("instagram-reel") for u in (r["input"] or {}).get("username", [])}
    fill = [c["username"] for c in usable if c["avg_reel_views"] is None and c["username"].lower() not in reeled]
    by_id = {c["id"]: c for c in cr}
    cnt, cats, pairs = collections.Counter(), collections.defaultdict(collections.Counter), set()
    for p in rest_all("posts?select=creator_id,coauthors&order=id"):
        c = by_id.get(p["creator_id"])
        for n in p.get("coauthors") or []:
            n = n.lower()
            if not c or n in have or n in tried or (n, c["id"]) in pairs or BRANDY.search(n):
                continue
            pairs.add((n, c["id"])); cnt[n] += 1; cats[n][c["niche_primary"]] += 1
    pool = collections.defaultdict(list)
    for n in sorted(cnt, key=lambda n: -cnt[n]):
        pool[cats[n].most_common(1)[0][0]].append(n)
    fill = fill[: int(budget * 0.5 / P_REEL)]   # reels backfill gets at most half the budget
    left = budget - len(fill) * P_REEL - n_terms * 15 * P_SEARCH * 1.3   # search: ~15 profiles/term + their reels
    n_prof = max(0, int(left / (P_PROFILE + KEEP * P_REEL)))
    order = [c for c, _ in sorted(collections.Counter(c["niche_primary"] for c in usable).items(), key=lambda x: x[1])]
    pick = []
    for c in order[:12]:
        pick += pool[c][:max(20, n_prof // 12)]
    for c in order:
        if len(pick) >= n_prof:
            break
        pick += [n for n in pool[c] if n not in pick][: n_prof - len(pick)]
    pick = pick[:n_prof]
    return {"fill": fill, "snowball": pick, "pool": sum(len(v) for v in pool.values()),
            "picked_by_category": dict(collections.Counter(cats[n].most_common(1)[0][0] for n in pick).most_common()),
            "usable": len(usable), "total": len(cr)}


def actor(tok, name, inp, out, cap, wait=True):
    json.dump(inp, open(out + ".input.json", "w"))
    p = subprocess.Popen([sys.executable, "-I", os.path.join(HERE, "apify_run.py"), name, out + ".input.json", out, f"{cap:.3f}"],
                         env={**os.environ, "APIFY_TOKEN": tok}, stdout=open(out + ".log", "w"), stderr=subprocess.STDOUT)
    return p.wait() if wait else p


def proc(*args):
    r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "process.py"), *args], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip()[-1500:], flush=True)
    return r.returncode


def split(items, n):
    return [items[i::n] for i in range(n) if items[i::n]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", required=True, help="label in APIFY_TOKENS, e.g. acc14")
    ap.add_argument("--terms", help="name of a search-term dict in taxonomy.py, e.g. ROUND34_TERMS")
    ap.add_argument("--budget", type=float, help="spend at most this (default: balance - $0.30)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true", help="really spend Apify credit")
    ap.add_argument("--no-llm", action="store_true", help="skip the automatic AI profile of the new creators")
    a = ap.parse_args()
    load_env()
    tok = token(a.account)
    left = balance(tok)
    budget = min(a.budget or 99, left - BUFFER)
    terms = [t for v in getattr(taxonomy, a.terms).values() for t in v] if a.terms else []
    print(f"{a.account}: balance ${left:.3f}, budget ${budget:.2f} (keeps ${BUFFER} unspent)", flush=True)
    if budget < 0.10:
        if not a.dry_run:
            raise SystemExit("Not enough credit for a round.")
        budget = a.budget or 4.70
        print(f"(account is empty; planning as if ${budget:.2f} were available)")
    pl = plan(budget, len(terms))
    caps = {"fill": len(pl["fill"]) * P_REEL * 1.2, "search": len(terms) * 15 * P_SEARCH * 1.1,
            "profiles": len(pl["snowball"]) * P_PROFILE * 1.05}
    caps["reels"] = max(0.05, budget - sum(caps.values()))
    print(f"DB {pl['total']} creators ({pl['usable']} usable); snowball pool {pl['pool']}")
    print(f"plan: reels backfill {len(pl['fill'])}, search terms {len(terms)}, snowball profiles {len(pl['snowball'])}"
          f" {pl['picked_by_category']}")
    print("caps $: " + ", ".join(f"{k} {v:.2f}" for k, v in caps.items()) + f" | total {sum(caps.values()):.2f}", flush=True)
    if a.dry_run or not a.yes:
        print("dry run: nothing spent" + ("" if a.dry_run else " (add --yes to run)"))
        return
    D = os.path.join(HERE, "runs", f"{date.today()}-{a.account}")
    os.makedirs(D, exist_ok=True)
    reel_inp = lambda us: {"username": us, "resultsLimit": 2, "onlyPostsNewerThan": "90 days", "skipPinnedPosts": True}  # noqa: E731

    # 1. reels backfill for creators already in the DB
    if pl["fill"]:
        f = os.path.join(D, "fill.json")
        actor(tok, "instagram-reel-scraper", reel_inp(pl["fill"]), f, caps["fill"])
        if os.path.exists(f):
            proc("reels", f)
            proc("raw", f)
    # 2. search + snowball profiles in parallel (FREE account: 5 jobs, 16 GB; search 1 GB, profiles small)
    runs, outs = [], []
    for i, part in enumerate(split(terms, 3)):
        o = os.path.join(D, f"search_{i}.json")
        runs.append(actor(tok, "instagram-search-scraper", {"search": ", ".join(part), "searchType": "user", "searchLimit": 15},
                          o, caps["search"] / len(split(terms, 3)), wait=False)); outs.append(o)
    parts = split(pl["snowball"], 2)
    for i, part in enumerate(parts):
        o = os.path.join(D, f"profiles_{i}.json")
        runs.append(actor(tok, "instagram-profile-scraper", {"usernames": part}, o, caps["profiles"] / len(parts), wait=False))
        outs.append(o)
    for r in runs:
        r.wait()
    outs = [o for o in outs if os.path.exists(o)]
    if not outs:
        raise SystemExit("no profile/search output")
    proc("filter", os.path.join(D, "keep.json"), *outs)
    existing = {c["username"].lower() for c in rest_all("creators?select=username&order=id")}
    new = [u for u in json.load(open(os.path.join(D, "keep.json"))) if u.lower() not in existing]
    print(f"new creators that passed the filter: {len(new)}", flush=True)
    # 3. reels for the new creators (Reel Scraper runs take 4 GB each: at most 3 at once)
    rparts, rruns, routs = split(new, 3), [], []
    for i, part in enumerate(rparts):
        o = os.path.join(D, f"reels_{i}.json")
        rruns.append(actor(tok, "instagram-reel-scraper", reel_inp(part), o, caps["reels"] / len(rparts), wait=False))
        routs.append(o)
    for r in rruns:
        r.wait()
    items = []
    for o in routs:
        if os.path.exists(o):
            items += json.load(open(o))["items"]
    json.dump({"items": items}, open(os.path.join(D, "reels.json"), "w"))
    # 4. build, keep only new creators, load, upload raw files
    proc("build", os.path.join(D, "rows_all.json"), os.path.join(D, "reels.json"), *outs)
    rows = json.load(open(os.path.join(D, "rows_all.json")))
    want = {u.lower() for u in new}
    keep_ids = {c["id"] for c in rows["creators"] if c["username"].lower() in want}
    rows = {k: [r for r in v if (r["id"] if k == "creators" else r["creator_id"]) in keep_ids] for k, v in rows.items()}
    json.dump(rows, open(os.path.join(D, "rows.json"), "w"), ensure_ascii=False)
    ok = [c for c in rows["creators"] if c["status"] == "active" and not c["fake_flag"]]
    print(f"loading {len(rows['creators'])} new creators ({len(ok)} usable, "
          f"{sum(1 for c in rows['creators'] if c['avg_reel_views'])} with reel views)", flush=True)
    proc("load", os.path.join(D, "rows.json"))
    for o in outs + [r for r in routs if os.path.exists(r)]:
        for t in range(3):
            if proc("raw", o) == 0:
                break
            time.sleep(3)
    print(f"{a.account} balance now ${balance(tok):.3f} (reel charges may still post)")
    # New creators get the same deep AI profile as everyone else (user, 2026-11-20: "jab naye creators du usse khud
    # se identify karna hoga" — shop-visit reels, price level, fan vs expert...). Only the new, search-visible ones
    # are sent (llm_classify skips creators already profiled), with a small cap: ~$0.001 per creator worst case.
    if ok and not a.no_llm:
        if os.environ.get("OPENROUTER_API_KEY"):
            cap = round(len(ok) * 0.001 + 0.02, 2)
            print(f"AI profile for {len(ok)} new usable creators (cap ${cap})", flush=True)
            subprocess.run([sys.executable, os.path.join(HERE, "llm_classify.py"), "run", "--max-usd", str(cap), "--yes"])
        else:
            print("OPENROUTER_API_KEY missing: run `python3 pipeline/llm_classify.py run --max-usd <cap> --yes` later")


if __name__ == "__main__":
    main()

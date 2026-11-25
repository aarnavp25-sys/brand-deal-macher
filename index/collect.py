"""Collect Instagram creator usernames (10K-100K followers) per category from the Apify India index into a
separate Supabase project. No profile scraping: only what the index returns (username + basic counts).

Sampling (changed 2026-11-23, after tests): the actor scans its 2.4M-row graph sequentially from the start (rows are
city-alphabetical: Adilabad, Agra, Ahmedabad ...) and stops with "Creator graph is temporarily unavailable" after
~8-10K rows without a match. So category + city fails even for Delhi (Food Blogging + Micro + Delhi: 8,000 scanned,
0 kept), and the planned random-city draws cannot work. It has no offset or random option. Each category therefore
gets ONE run (category + Micro, no city, up to --per results); results lean to early-alphabet cities (user accepted
this on 2026-11-23). A category is never run twice: the actor would return the same first rows and bill them again.

usage (from the project folder):
  python3 index/collect.py keys                        # free: balance of every key in INDEX_APIFY_TOKENS
  python3 index/collect.py categories                  # free: refresh the category + city lists from the actor
  python3 index/collect.py migrate                     # create the tables (needs INDEX_SUPABASE_ACCESS_TOKEN)
  python3 index/collect.py status                      # free: creators per category in the index
  python3 index/collect.py plan --per 20               # free: categories still short and the result-fee estimate
  python3 index/collect.py run --max-usd 10 --yes [--plan index/plan.json] [--only "Food Blogging,Travel" --per 20]
                                                        # plan.json = {category: count} in run order; one at a time

Config: index/.env (gitignored) with INDEX_SUPABASE_URL, INDEX_SUPABASE_SERVICE_KEY, INDEX_APIFY_TOKENS=label:token,...
and optionally INDEX_SUPABASE_ACCESS_TOKEN (for `migrate`). Tokens are never printed or stored in the database.

Spend guards: `run` needs --yes and --max-usd (counts result fees and compute); every Apify run gets maxTotalChargeUsd
and maxItems; a key is used only while its balance covers the draw plus a $0.30 reserve (free plans block until the
next cycle when they run out); one run per category, never repeated. Python 3 stdlib only.
"""
import argparse, json, os, random, sys, threading, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ACTOR = "social_developer~india-instagram-influencer-scraper-modashs"
BRACKET = "Micro (10K–99.9K)"
PRICE = 0.02            # $ per result (actor's pay-per-event price, checked 2026-11-23)
RESERVE = 0.30          # never plan to spend the last $0.30 of a key
MIN_F, MAX_F = 10_000, 100_000
MIN_KEEP = 20           # user: at least 20 per category; a partial run below this is re-run (re-buys only those few rows)
CAT_CACHE = os.path.join(HERE, "categories.json")
CITY_CACHE = os.path.join(HERE, "cities.json")
RNG = random.SystemRandom()
LOCK = threading.Lock()


def load_env():
    path = os.path.join(HERE, ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def tokens():
    out = []
    for pair in os.environ.get("INDEX_APIFY_TOKENS", "").split(","):
        if ":" in pair:
            label, tok = pair.split(":", 1)
            out.append((label.strip(), tok.strip()))
    if not out:
        raise SystemExit("No keys: add INDEX_APIFY_TOKENS=label:token,... to index/.env")
    return out


def apify(tok, method, path, body=None, timeout=120):
    req = urllib.request.Request("https://api.apify.com/v2" + path, method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.load(r)
                return d.get("data", d) if isinstance(d, dict) else d
        except (OSError, ValueError):
            if method == "POST" or attempt == 3:  # never retry the POST that starts (and bills) a run
                raise
            time.sleep(3 * (attempt + 1))


def balance(tok):
    d = apify(tok, "GET", "/users/me/limits")
    return d["limits"]["maxMonthlyUsageUsd"] - d["current"]["monthlyUsageUsd"], d["monthlyUsageCycle"]["endAt"][:10]


def sb(method, path, body=None, prefer=None):
    url, key = os.environ.get("INDEX_SUPABASE_URL", "").rstrip("/"), os.environ.get("INDEX_SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise SystemExit("Missing INDEX_SUPABASE_URL / INDEX_SUPABASE_SERVICE_KEY in index/.env")
    h = {"apikey": key, "Authorization": "Bearer " + key, "Content-Type": "application/json"}
    if prefer:
        h["Prefer"] = prefer
    req = urllib.request.Request(f"{url}/rest/v1/{path}", method=method, headers=h,
                                 data=None if body is None else json.dumps(body, ensure_ascii=False).encode())
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            t = r.read()
            return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Supabase {method} {path.split('?')[0]}: HTTP {e.code} {e.read().decode()[:300]}")


def sb_all(path):
    out, off = [], 0
    while True:
        page = sb("GET", f"{path}&limit=1000&offset={off}")
        out += page
        if len(page) < 1000:
            return out
        off += 1000


def _schema():
    tok = tokens()[0][1]
    act = apify(tok, "GET", "/acts/" + ACTOR)
    sch = apify(tok, "GET", "/actor-builds/" + act["taggedBuilds"]["latest"]["buildId"])["inputSchema"]
    return json.loads(sch) if isinstance(sch, str) else sch


def categories(refresh=False):
    if os.path.exists(CAT_CACHE) and not refresh:
        return json.load(open(CAT_CACHE))
    sch = _schema()
    cats = [c for c in sch["properties"]["category"]["enum"] if c]
    json.dump(cats, open(CAT_CACHE, "w"), indent=1, ensure_ascii=False)
    json.dump([c for c in sch["properties"]["regionalFocus"]["enum"] if c], open(CITY_CACHE, "w"), indent=1,
              ensure_ascii=False)
    return cats


def cities():
    if not os.path.exists(CITY_CACHE):
        categories(refresh=True)
    return json.load(open(CITY_CACHE))


def progress():
    return {r["category"]: r["creators"] for r in sb_all("index_progress?select=category,creators&order=category")}


def done_categories():
    """categories that already had a no-city run which returned rows or finished and now hold at least MIN_KEEP
    creators; never run again (the same first rows would be billed twice). A run that failed with 0 rows, or a
    partial one that left the category under MIN_KEEP, may be re-run (it re-buys only those few rows)."""
    prog, done = progress(), set()
    for r in sb_all("index_runs?select=category,city,status,received,new_usernames&order=run_id"):
        if r.get("city") or not ((r.get("received") or 0) > 0 or r.get("status") == "SUCCEEDED"):
            continue
        exhausted = (r.get("received") or 0) > 0 and not r.get("new_usernames")  # a re-run brought nothing new
        if prog.get(r["category"], 0) >= MIN_KEEP or exhausted or r.get("status") == "SUCCEEDED":
            done.add(r["category"])
    return done


def row_of(item):
    u = (item.get("username") or "").strip().lstrip("@").lower()
    if not u:
        return None
    return {"username": u, "followers": item.get("followersCount"),
            "follower_bracket": item.get("followerBracket"), "city": item.get("regionalFocus"),
            "posts_count": item.get("postsCount"), "engagement_rate": item.get("engagementRate"),
            "avg_likes": item.get("avgLikes"), "avg_comments": item.get("avgComments"),
            "avg_views": item.get("avgViews"), "verified": item.get("verified"), "country": item.get("country"),
            "last_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "raw": {k: v for k, v in item.items() if k != "fullName"}}  # no display names (user, 2026-11-24)


def save(cat, rid, items):
    rows = [r for r in (row_of(i) for i in items) if r and r["followers"] is not None
            and MIN_F <= int(r["followers"]) < MAX_F]
    known = set()
    if rows:  # usernames the user had removed (index_removed) are never saved again
        names = ",".join('"%s"' % r["username"].replace('"', "") for r in rows)
        gone = {r["username"] for r in sb("GET", "index_removed?select=username&username=in.(" +
                                          urllib.parse.quote(names) + ")")}
        rows = [r for r in rows if r["username"] not in gone]
    if rows:
        names = ",".join('"%s"' % r["username"].replace('"', "") for r in rows)
        known = {r["username"] for r in sb("GET", "index_creators?select=username&username=in.(" +
                                           urllib.parse.quote(names) + ")")}
        new = [r for r in rows if r["username"] not in known]
        if new:
            sb("POST", "index_creators", new, "resolution=ignore-duplicates,return=minimal")
        for r in rows:
            if r["username"] in known:  # already found under another category: refresh its counts only
                sb("PATCH", "index_creators?username=eq." + urllib.parse.quote(r["username"]),
                   {k: v for k, v in r.items() if k != "username"}, "return=minimal")
        sb("POST", "index_creator_categories", [{"username": r["username"], "category": cat, "run_id": rid}
                                                for r in rows], "resolution=ignore-duplicates,return=minimal")
    return len(rows), len(rows) - len(known)


def draw(label, tok, cat, city, n):
    """One Apify run: category + Micro bracket (+ city if given), at most n creators."""
    inp = {"category": cat, "followerBracket": BRACKET, "resultsLimit": n}
    if city:
        inp["regionalFocus"] = city
    run = apify(tok, "POST", f"/acts/{ACTOR}/runs?maxTotalChargeUsd={round(n * PRICE + 0.02, 2)}&memory=1024"
                             f"&maxItems={n}", inp)
    rid = run["id"]
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(4)
        run = apify(tok, "GET", f"/actor-runs/{rid}")
    items = apify(tok, "GET", f"/datasets/{run['defaultDatasetId']}/items?limit={n + 50}&clean=true")
    items = items if isinstance(items, list) else []
    kept, new = save(cat, rid, items)
    # Every dataset item is billed at PRICE. usageTotalUsd now includes those fees (checked 2026-11-23: 100 results →
    # $2.0016) but can lag a few seconds after SUCCEEDED (a 100-result run read $1.62), and chargedEventCounts lags
    # with it. So cost = max(what Apify says, items × price + a little compute); never fee + usage (double count).
    usage = float(run.get("usageTotalUsd") or 0)
    fee, compute = max(usage, len(items) * PRICE + 0.002), 0.0
    sb("POST", "index_runs", [{"run_id": rid, "category": cat, "city": city, "account": label, "requested": n,
                               "received": len(items), "kept": kept, "new_usernames": new,
                               "cost_usd": round(fee + compute, 4), "status": run["status"],
                               "status_message": (run.get("statusMessage") or "")[:300]}],
       "resolution=merge-duplicates,return=minimal")
    return run["status"], (run.get("statusMessage") or ""), len(items), kept, fee + compute, new


class Budget:
    def __init__(self, max_usd, reserve=RESERVE):
        self.max, self.spent, self.keys, self.stop, self.short = max_usd, 0.0, [], None, False
        self.reserve = reserve  # each run is also capped by Apify (maxTotalChargeUsd), so a small reserve is safe
        for label, tok in tokens():
            try:
                self.keys.append([label, tok, balance(tok)[0]])
            except Exception:
                pass

    def take(self, need):
        with LOCK:
            if self.stop:
                return None
            if self.spent + need > self.max:  # this category is too big for what is left; a smaller one may fit
                self.short = True
                return None
            key = max(self.keys, key=lambda k: k[2])  # spread draws over the fullest key
            if key[2] - self.reserve < need:
                self.short = True  # no single key can pay for this category; a smaller one may still fit
                return None
            key[2] -= need
            self.spent += need
            return key

    def settle(self, key, reserved, actual):
        with LOCK:
            key[2] += reserved - actual
            self.spent += actual - reserved


def fill(cat, per, budget, log, tries, wait):
    """One run per category, no city, at most `per` results. The actor's backend times out at random (~12 s per
    2,000-row page; 3% of pages on 2026-11-22, 11% on 2026-11-23), so a run that failed with 0 rows is retried up to
    `tries` times, `wait` s apart (a failed run costs ~$0.001). A run that wrote any rows is never repeated: the
    actor would return the same first rows and bill them again."""
    for attempt in range(1, tries + 1):
        reserve = per * PRICE + 0.03  # result fees + generous compute allowance
        key = budget.take(reserve)
        if not key:
            return False
        try:
            status, msg, got, kept, cost, new = draw(key[0], key[1], cat, None, per)
        except Exception as e:
            budget.settle(key, reserve, 0.0)
            log(f"{cat:22} try {attempt}: error {type(e).__name__}; stopping this category (check index_runs)")
            return True
        budget.settle(key, reserve, cost)
        log(f"{cat:22} try {attempt}: {status:9} got {got} kept {kept}/{per}  ${cost:.3f} [{key[0]}]"
            + (f"  ({msg[:50]})" if status != "SUCCEEDED" else ""))
        if status == "SUCCEEDED" or got >= min(MIN_KEEP, per):
            return True
        if got and not new:  # the re-run returned only rows we already had: the index holds no more for it
            log(f"{cat:22} exhausted: the index has only {got} creators in this category (10K-100K)")
            return True
        if got:
            log(f"{cat:22} only {got} before the backend timed out (< {MIN_KEEP}); re-running re-buys those {got}")
        if attempt < tries:
            time.sleep(wait * (1 + RNG.random()))
    log(f"{cat:22} gave up after {tries} tries (backend timeouts); run again later")
    return True


def cmd_run(plan, max_usd, tries, wait, reserve=RESERVE):
    known = set(categories())
    bad = [c for c in plan if c not in known]
    if bad:
        raise SystemExit("unknown categories: " + ", ".join(bad))
    done = done_categories()
    todo = [c for c in plan if c not in done]
    budget = Budget(max_usd, reserve)
    print(f"{len(todo)} categories to run ({len(plan) - len(todo)} already done), one at a time · "
          f"{len(budget.keys)} keys · cap ${max_usd} · up to {tries} tries each", flush=True)
    log = lambda s: print(time.strftime("%H:%M ") + s, flush=True)
    skipped = []
    for c in todo:  # never in parallel: parallel runs made the backend fail on the first page (2026-11-23)
        budget.short = False
        if not fill(c, plan[c], budget, log, tries, wait):
            if budget.stop:
                break
            skipped.append(c)  # no single key could pay for it: keep going with smaller categories
    if skipped:
        print("not run (no single key, or the --max-usd left, covered the whole count): " + ", ".join(skipped))
    print(f"done. spent ≈ ${budget.spent:.2f}" + (f" · stopped: {budget.stop}" if budget.stop else ""))


def cmd_keys():
    total = 0
    for label, tok in tokens():
        try:
            left, end = balance(tok)
            total += max(left, 0)
            print(f"{label:10} left ${left:6.2f}  (≈{int(max(left - RESERVE, 0) / PRICE)} creators)  cycle ends {end}")
        except Exception as e:
            print(f"{label:10} error {type(e).__name__}")
    print(f"total left ${total:.2f} ≈ {int(total / PRICE)} creators (result fees only)")


def cmd_plan(plan):
    done, prog = done_categories(), progress()
    left = {c: n for c, n in plan.items() if c not in done}
    print(f"{len(plan)} categories in the plan · {sum(plan.values())} creators planned · "
          f"{sum(prog.get(c, 0) for c in plan)} collected so far")
    for c, n in plan.items():
        print(f"  {c:22} {prog.get(c, 0):4}/{n:<4} {'done' if c in done else 'to run'}")
    need = sum(left.values())
    print(f"to run: {len(left)} categories, {need} creators ≈ ${need * PRICE:.2f} result fees "
          f"(+ ~$0.03 per category; each key keeps a ${RESERVE} reserve)")


def cmd_migrate():
    tokn, url = os.environ.get("INDEX_SUPABASE_ACCESS_TOKEN"), os.environ.get("INDEX_SUPABASE_URL", "")
    if not tokn or ".supabase.co" not in url:
        raise SystemExit("Needs INDEX_SUPABASE_ACCESS_TOKEN and INDEX_SUPABASE_URL; or paste index/schema.sql "
                         "into the project's SQL editor.")
    ref = url.split("//")[1].split(".")[0]
    req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{ref}/database/query", method="POST",
                                 data=json.dumps({"query": open(os.path.join(HERE, "schema.sql")).read()}).encode(),
                                 headers={"Authorization": "Bearer " + tokn, "Content-Type": "application/json",
                                          "User-Agent": "bdm-index"})
    urllib.request.urlopen(req, timeout=120).read()
    print("schema applied to", ref)


if __name__ == "__main__":
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["keys", "categories", "migrate", "status", "plan", "run"])
    ap.add_argument("--per", type=int, default=20)
    ap.add_argument("--max-usd", type=float)
    ap.add_argument("--only", help="comma-separated category names")
    ap.add_argument("--plan", default=os.path.join(HERE, "plan.json"), help="JSON {category: count}, in run order")
    ap.add_argument("--tries", type=int, default=10)
    ap.add_argument("--reserve", type=float, default=RESERVE, help="$ left untouched on every key")
    ap.add_argument("--wait", type=int, default=60, help="seconds between tries (x1-2)")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    only = list(dict.fromkeys(c.strip() for c in a.only.split(","))) if a.only else None
    if a.cmd == "keys":
        cmd_keys()
    elif a.cmd == "categories":
        cs = categories(refresh=True)
        print(len(cs), "categories,", len(cities()), "cities")
    elif a.cmd == "migrate":
        cmd_migrate()
    elif a.cmd == "status":
        p = progress()
        print(f"{sum(p.values())} category rows across {len(p)} categories")
        for c, n in sorted(p.items()):
            print(f"  {c:32} {n}")
    elif a.cmd == "plan":
        cmd_plan({k: v for k, v in json.load(open(a.plan)).items() if not k.startswith("_")})
    elif a.cmd == "run":
        if not a.yes or a.max_usd is None:
            sys.exit("run spends money: add --max-usd X and --yes")
        plan = {k: v for k, v in json.load(open(a.plan)).items() if not k.startswith("_")}
        if only:
            plan = {k: plan.get(k, a.per) for k in only}
        cmd_run(plan, a.max_usd, a.tries, a.wait, a.reserve)

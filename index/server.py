"""Local dashboard for the creator username index (separate Supabase project).

Run:   python3 index/server.py      then open http://127.0.0.1:8789
Needs: index/.env with INDEX_SUPABASE_URL, INDEX_SUPABASE_SERVICE_KEY (and INDEX_APIFY_TOKENS for the key card).
Read-only: collecting runs from the command line (index/collect.py) so nothing spends money from a browser click.
The service key and Apify tokens stay in this process; the browser only talks to 127.0.0.1.
"""
import csv, io, json, os, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import collect  # noqa: E402

COLS = ("username,followers,city,posts_count,engagement_rate,avg_likes,avg_comments,avg_views,verified,"
        "first_seen,index_creator_categories(category)")


def load_plan():
    path = os.path.join(HERE, "plan.json")
    if not os.path.exists(path):
        return {}
    return {k: v for k, v in json.load(open(path)).items() if not k.startswith("_")}


def summary():
    """Plan-first view: every planned category with target, collected, status, tries and real spend."""
    plan, prog = load_plan(), collect.progress()
    groups = {}
    gpath = os.path.join(HERE, "category_groups.json")
    if os.path.exists(gpath):
        for g, cats in json.load(open(gpath)).items():
            for c in cats:
                groups[c] = g
    runs = {}
    for r in collect.sb_all("index_runs?select=run_id,category,city,account,requested,received,kept,new_usernames,"
                            "cost_usd,status,status_message,started_at&order=started_at"):
        runs.setdefault(r["category"], []).append(r)
    rows = []
    # plan categories, then other categories that were tried and still map into one of the kept categories
    # (categories outside index/category_groups.json were removed by the user; their runs only count in spend)
    for c in list(plan) + sorted(c for c in set(runs) - set(plan) if c in groups):
        rs = [r for r in runs.get(c, []) if not r.get("city")]  # random-city pilot runs (2026-11-23) only add cost
        target, got = plan.get(c), prog.get(c, 0)
        spent = sum(float(r.get("cost_usd") or 0) for r in runs.get(c, []))
        exhausted = any((r.get("received") or 0) > 0 and not r.get("new_usernames") for r in rs) or \
            any(r.get("status") == "SUCCEEDED" and (r.get("received") or 0) < (r.get("requested") or 0) for r in rs)
        partial = any((r.get("received") or 0) > 0 for r in rs)
        if c not in plan:
            st = "dropped"     # tried before the plan existed (2026-11-23), not in plan.json now
        elif target and got >= target:
            st = "complete"
        elif exhausted:
            st = "exhausted"   # the index holds no more creators for this category
        elif got >= collect.MIN_KEEP:
            st = "partial"     # backend timed out mid-run; a re-run would re-buy these rows
        elif rs:
            st = "retry"       # only timeouts so far (or under the minimum); will be tried again
        else:
            st = "todo"
        # what this category will end with: what it has once it is finished (partial / exhausted are not re-run,
        # their shortfall was moved to other categories in plan.json), else its target
        final = got if st in ("partial", "exhausted", "complete") else (target or 0)
        rows.append({"name": c, "group": groups.get(c, "other"), "target": target, "creators": got, "status": st,
                     "final": min(final, target or final),
                     "tries": len(rs), "failed_tries": sum(1 for r in rs if not r.get("received")),
                     "spent": round(spent, 3), "in_plan": c in plan,
                     "last": rs[-1] if rs else None})
    all_runs = [r for rs in runs.values() for r in rs]
    spent = sum(float(r.get("cost_usd") or 0) for r in all_runs)
    todo_need = sum(max(r["target"] - r["creators"], 0) for r in rows
                    if r["in_plan"] and r["status"] in ("todo", "retry"))
    return {"categories": rows, "unique_creators": None, "spent_usd": round(spent, 2), "runs": len(all_runs),
            "failed_runs": sum(1 for r in all_runs if not r.get("received")),
            "plan_total": sum(r["final"] for r in rows if r["in_plan"]), "todo_creators": todo_need,
            "todo_usd": round(todo_need * collect.PRICE + 0.03 * sum(1 for r in rows if r["status"] in ("todo", "retry")), 2),
            "price_per_result": collect.PRICE, "bracket": collect.BRACKET, "min_keep": collect.MIN_KEEP}


def count_unique():
    url = os.environ["INDEX_SUPABASE_URL"].rstrip("/") + "/rest/v1/index_creators?select=username&limit=1"
    key = os.environ["INDEX_SUPABASE_SERVICE_KEY"]
    import urllib.request
    req = urllib.request.Request(url, headers={"apikey": key, "Authorization": "Bearer " + key, "Prefer": "count=exact"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers.get("Content-Range", "*/0").split("/")[-1] or 0)


def creators(q):
    cat, text = q.get("category", [""])[0], q.get("q", [""])[0].strip().lower()
    path = "index_creators?select=" + COLS + "&order=followers.desc"
    if cat:
        path = ("index_creators?select=" + COLS.replace("index_creator_categories(category)",
                                                         "index_creator_categories!inner(category)")
                + "&index_creator_categories.category=eq." + urllib.parse.quote(cat) + "&order=followers.desc")
    if text:
        path += "&or=(username.ilike.*" + urllib.parse.quote(text) + "*,city.ilike.*" + urllib.parse.quote(text) + "*)"
    rows = collect.sb_all(path)
    for r in rows:
        r["categories"] = sorted({c["category"] for c in r.pop("index_creator_categories", []) or []})
    return rows


def keys():
    def one(pair):
        label, tok = pair
        try:
            left, end = collect.balance(tok)
            return {"label": label, "left": round(left, 2), "cycle_end": end,
                    "creators_left": int(max(left - 0.05, 0) / collect.PRICE)}
        except Exception as e:
            return {"label": label, "error": type(e).__name__}
    try:
        pairs = collect.tokens()
    except SystemExit:
        return []
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(one, pairs))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                return self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
            if u.path == "/api/summary":
                s = summary()
                s["unique_creators"] = count_unique()
                return self.send(200, s)
            if u.path == "/api/creators":
                return self.send(200, creators(q))
            if u.path == "/api/keys":
                return self.send(200, keys())
            if u.path == "/api/export.csv":
                rows = creators(q)
                buf = io.StringIO()
                w = csv.writer(buf)
                head = ["username", "instagram_url", "followers", "city", "categories", "posts_count",
                        "engagement_rate", "avg_likes", "avg_comments", "avg_views", "verified", "first_seen"]
                w.writerow(head)
                for r in rows:
                    w.writerow([r["username"], "https://www.instagram.com/" + r["username"] + "/",
                                r["followers"], r["city"], "; ".join(r["categories"]), r["posts_count"],
                                r["engagement_rate"], r["avg_likes"], r["avg_comments"], r["avg_views"], r["verified"],
                                r["first_seen"]])
                return self.send(200, buf.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8")
            self.send(404, {"error": "not found"})
        except SystemExit as e:
            self.send(500, {"error": str(e)})
        except Exception as e:
            self.send(500, {"error": type(e).__name__ + ": " + str(e)[:200]})


if __name__ == "__main__":
    collect.load_env()
    for k in ("INDEX_SUPABASE_URL", "INDEX_SUPABASE_SERVICE_KEY"):
        if not os.environ.get(k):
            sys.exit(f"Missing {k} in index/.env (see index/.env.example)")
    port = int(os.environ.get("INDEX_PORT", "8789"))
    print(f"Creator index dashboard: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

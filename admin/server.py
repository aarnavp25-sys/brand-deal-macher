"""Local admin dashboard for Brand Deal Matcher.

Run:   python3 admin/server.py      then open http://127.0.0.1:8787
Needs: admin/.env with SUPABASE_URL and SUPABASE_SERVICE_KEY (see .env.example).
Optional: APIFY_TOKENS=label:token,... for the live Apify credits card (/api/apify).

The service key stays in this process; the browser only talks to 127.0.0.1.
/api/rest/<table> is a thin proxy to Supabase PostgREST, limited to known tables.
"""
import json, os, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = {"creators", "posts", "creator_products", "creator_snapshots", "categories", "product_types", "raw_scrapes",
          "creator_llm"}
PREFER_OK = {"count=exact", "return=representation", "return=minimal", "resolution=merge-duplicates"}


def load_env():
    path = os.path.join(HERE, ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))
    missing = [k for k in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY") if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"Missing {missing}. Copy admin/.env.example to admin/.env and fill it in.")


def apify_one(label, token):
    """Live usage of one Apify account. The token never leaves this process."""
    def get(path):
        req = urllib.request.Request("https://api.apify.com/v2" + path, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)["data"]
    try:
        me, lim = get("/users/me"), get("/users/me/limits")
        limit, used = lim["limits"]["maxMonthlyUsageUsd"], lim["current"]["monthlyUsageUsd"]
        return {"label": label, "username": me.get("username"), "plan": (me.get("plan") or {}).get("id"),
                "limit_usd": limit, "used_usd": round(used, 3), "left_usd": round(limit - used, 3),
                "resets": (lim.get("monthlyUsageCycle") or {}).get("endAt")}
    except Exception as e:
        return {"label": label, "error": str(e)[:150]}


def apify_accounts():
    # APIFY_TOKENS=label:token,label:token (Apify tokens contain no colon)
    items = [x.strip() for x in os.environ.get("APIFY_TOKENS", "").split(",") if x.strip()]
    accounts = [(x.rpartition(":")[0] or f"account {i + 1}", x.rpartition(":")[2]) for i, x in enumerate(items)]
    with ThreadPoolExecutor(max_workers=8) as ex:
        return list(ex.map(lambda a: apify_one(*a), accounts))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, code, body, ctype="application/json", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def supabase(self, method, path, body=None, prefer=None):
        key = os.environ["SUPABASE_SERVICE_KEY"]
        headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if prefer:
            headers["Prefer"] = prefer
        req = urllib.request.Request(os.environ["SUPABASE_URL"].rstrip("/") + path, method=method, data=body,
                                     headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read(), r.headers.get("Content-Range")
        except urllib.error.HTTPError as e:
            return e.code, e.read(), None
        except OSError as e:
            return 502, json.dumps({"message": f"Supabase unreachable: {e}"}).encode(), None

    def route(self, method):
        if method == "GET" and self.path in ("/", "/index.html"):
            return self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        if self.path.startswith("/api/apify"):
            return self.send(200, json.dumps(apify_accounts()).encode())
        if self.path.startswith("/api/users"):
            code, body, _ = self.supabase("GET", "/auth/v1/admin/users?page=1&per_page=500")
            return self.send(code, body)
        if self.path.startswith("/api/rest/"):
            rest = self.path[len("/api/rest/"):]
            table = rest.split("?", 1)[0]
            if table not in TABLES:
                return self.send(404, b'{"message":"unknown table"}')
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else None
            prefer = ",".join(p.strip() for p in (self.headers.get("Prefer") or "").split(",") if p.strip() in PREFER_OK)
            code, data, crange = self.supabase(method, "/rest/v1/" + rest, body, prefer or None)
            return self.send(code, data or b"null", extra={"Content-Range": crange} if crange else None)
        self.send(404, b'{"message":"not found"}')

    def do_GET(self): self.route("GET")
    def do_POST(self): self.route("POST")
    def do_PATCH(self): self.route("PATCH")
    def do_DELETE(self): self.route("DELETE")


if __name__ == "__main__":
    load_env()
    port = int(os.environ.get("ADMIN_PORT", "8787"))
    print(f"Admin dashboard: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

"""Public backend on Render for Brand Deal Matcher: a thin forwarder in front of the Supabase Edge Function `api`.

Routes:
  GET/HEAD /health   -> 200 {"status": "ok"}  (UptimeRobot pings this every 5 minutes so the free instance stays awake)
  GET  /api/meta     -> Edge Function /meta
  POST /api/match    -> Edge Function /match

Matching, the AI review, input checks and the rate limit all stay in the Edge Function
(supabase/functions/api/index.ts). This server only:
  - answers CORS for the website origins in ALLOWED_ORIGINS and refuses other sites;
  - adds the Supabase anon key itself, so the public page carries no key;
  - passes the visitor's IP with PROXY_SECRET, so the per-visitor rate limit still works (without it every
    visitor would share Render's IP and one bucket of 30 searches per 10 minutes).

Env: SUPABASE_URL, SUPABASE_ANON_KEY, PROXY_SECRET, ALLOWED_ORIGINS (comma list), PORT (Render sets it).
Local run: python3 render/server.py   (reads admin/.env; listens on 127.0.0.1:8790)
Python 3 stdlib only.
"""
import json, os, urllib.error, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_BODY = 4000          # same limit as the Edge Function
UPSTREAM_TIMEOUT = 90    # a new search runs two AI calls; repeats come from the cache
ROUTES = {("GET", "/api/meta"): "/meta", ("POST", "/api/match"): "/match"}


def load_local_env():
    """Local runs only: Render passes real env vars, and admin/.env is never deployed."""
    path = os.path.join(HERE, "..", "admin", ".env")
    if os.path.exists(path):
        for line in open(path):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def config():
    missing = [k for k in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "PROXY_SECRET") if not os.environ.get(k)]
    if missing:
        raise SystemExit("Missing env: " + ", ".join(missing))
    return {
        "upstream": os.environ["SUPABASE_URL"].rstrip("/") + "/functions/v1/api",
        "anon": os.environ["SUPABASE_ANON_KEY"],
        "secret": os.environ["PROXY_SECRET"],
        "origins": {o.strip().rstrip("/") for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()},
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "bdm-api"
    sys_version = ""

    def log_message(self, fmt, *args):  # one line per request, no IPs or bodies
        print(f"{self.command} {self.path.split('?')[0]} -> {args[1] if len(args) > 1 else ''}", flush=True)

    # ---------- helpers ----------
    def origin_ok(self):
        o = self.headers.get("Origin")
        return o is None or o.rstrip("/") in CFG["origins"]

    def cors(self):
        o = self.headers.get("Origin")
        if o and o.rstrip("/") in CFG["origins"]:
            self.send_header("Access-Control-Allow-Origin", o)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type")
        self.send_header("Access-Control-Max-Age", "600")
        self.send_header("Vary", "Origin")

    def reply(self, code, body, head_only=False):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def client_ip(self):
        # Render sits behind Cloudflare, which overwrites CF-Connecting-IP; X-Forwarded-For is the fallback
        ip = self.headers.get("CF-Connecting-IP") or (self.headers.get("X-Forwarded-For") or "").split(",")[0]
        return ip.strip() or self.client_address[0]

    def forward(self, method, target, body=None):
        req = urllib.request.Request(CFG["upstream"] + target, method=method, data=body, headers={
            "apikey": CFG["anon"], "Authorization": "Bearer " + CFG["anon"],
            "Content-Type": "application/json", "User-Agent": "bdm-render-proxy",
            "X-Client-IP": self.client_ip(), "X-Proxy-Key": CFG["secret"]})
        try:
            with urllib.request.urlopen(req, timeout=UPSTREAM_TIMEOUT) as r:
                return self.reply(r.status, r.read())
        except urllib.error.HTTPError as e:  # 400 / 429 / 503 from the Edge Function carry a user message
            return self.reply(e.code, e.read() or {"message": f"HTTP {e.code}"})
        except Exception as e:
            print("upstream error:", type(e).__name__, flush=True)
            return self.reply(502, {"message": "Search service is not reachable right now. Please try again."})

    # ---------- routes ----------
    def do_OPTIONS(self):
        self.send_response(204 if self.origin_ok() else 403)
        self.cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_HEAD(self):
        if self.path.split("?")[0] == "/health":
            return self.reply(200, {"status": "ok"}, head_only=True)
        self.reply(404, {"message": "Not found."}, head_only=True)

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/health":
            return self.reply(200, {"status": "ok"})
        if path == "/":
            return self.reply(200, {"service": "Brand Deal Matcher API", "health": "/health"})
        self.route("GET", path)

    def do_POST(self):
        self.route("POST", self.path.split("?")[0].rstrip("/"))

    def route(self, method, path):
        target = ROUTES.get((method, path))
        if not target:
            return self.reply(404, {"message": "Not found."})
        if not self.origin_ok():
            return self.reply(403, {"message": "Origin not allowed."})
        body = None
        if method == "POST":
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                n = MAX_BODY + 1
            if n > MAX_BODY:
                return self.reply(413, {"message": "Request too large."})
            body = self.rfile.read(n)
        self.forward(method, target, body)


if __name__ == "__main__":
    on_render = bool(os.environ.get("RENDER"))  # Render sets RENDER=true in every service
    if not on_render:
        load_local_env()
        os.environ.setdefault("ALLOWED_ORIGINS", "http://127.0.0.1:8788,http://localhost:8788")
    CFG = config()
    host, port = ("0.0.0.0", int(os.environ.get("PORT", "10000"))) if on_render else ("127.0.0.1", 8790)
    print(f"Brand Deal Matcher API on {host}:{port} -> {CFG['upstream']} | origins: {sorted(CFG['origins'])}",
          flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()

"""Demo website (prototype) for Brand Deal Matcher: a brand describes its product, gets matched creators.

Run:  python3 demo/server.py   ->  http://127.0.0.1:8788

This server only serves the page. Matching runs in the Supabase Edge Function `api`
(supabase/functions/api/index.ts); the browser calls it with the public anon key.
No secret key is read or sent here — only SUPABASE_URL and SUPABASE_ANON_KEY (public by design;
tables have RLS on with no policies, so the anon key cannot read them directly).
"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


def load_env():
    for path in (os.path.join(HERE, ".env"), os.path.join(HERE, "..", "admin", ".env")):
        if os.path.exists(path):
            for line in open(path):
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.strip().split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"'))
    if not os.environ.get("SUPABASE_URL") or not os.environ.get("SUPABASE_ANON_KEY"):
        raise SystemExit("Missing SUPABASE_URL / SUPABASE_ANON_KEY (admin/.env).")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'unsafe-inline'; "
                         "img-src https: data:; connect-src " + os.environ["SUPABASE_URL"].rstrip("/"))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            return self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
        if path == "/config.js":
            cfg = {"api": os.environ["SUPABASE_URL"].rstrip("/") + "/functions/v1/api",
                   "anon": os.environ["SUPABASE_ANON_KEY"]}
            return self.send(200, f"window.BDM = {json.dumps(cfg)};".encode(), "text/javascript")
        self.send(404, b"not found", "text/plain")


if __name__ == "__main__":
    load_env()
    port = int(os.environ.get("DEMO_PORT", "8788"))
    print(f"Demo website: http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

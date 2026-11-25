"""Testing only: sign in as a test brand without Google.

Creates the test user if needed (email confirmed, name set) and prints a one-time sign-in link that goes through the
site's normal /auth/confirm route. Needs the secret key, so only the project owner can do this.

Usage (from the repo root):
  python3 web/db/test_login.py <n> [base_url] [next_path]      e.g. python3 web/db/test_login.py 1
  python3 web/db/test_login.py --delete-all                     removes every test user and their searches
Python 3 stdlib only.
"""
import json, pathlib, sys, urllib.error, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ENV = {}
for line in (HERE.parent / ".env.local").read_text().splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        k, v = line.split("=", 1)
        ENV[k.strip()] = v.strip()
URL, KEY = ENV["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/"), ENV["SUPABASE_SECRET_KEY"]
DOMAIN = "kindred-test.example.com"


def call(path, method="GET", body=None):
    req = urllib.request.Request(URL + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    try:
        raw = urllib.request.urlopen(req, timeout=30).read()
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode()[:300]}


def test_users():
    users = call("/auth/v1/admin/users?per_page=1000").get("users", [])
    return [u for u in users if (u.get("email") or "").endswith("@" + DOMAIN)]


def main():
    if sys.argv[1:] == ["--delete-all"]:
        for u in test_users():
            call(f"/auth/v1/admin/users/{u['id']}", "DELETE")
            print("deleted", u["email"])
        return
    n = sys.argv[1] if len(sys.argv) > 1 else "1"
    base = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:3000"
    nxt = sys.argv[3] if len(sys.argv) > 3 else "/dashboard"
    email = f"brand{n}@{DOMAIN}"
    if not any(u["email"] == email for u in test_users()):
        r = call("/auth/v1/admin/users", "POST",
                 {"email": email, "email_confirm": True, "user_metadata": {"full_name": f"Test Brand {n}"}})
        if "_error" in r:
            sys.exit(f"create user failed: {r}")
    r = call("/auth/v1/admin/generate_link", "POST", {"type": "magiclink", "email": email})
    token = r.get("hashed_token") or (r.get("properties") or {}).get("hashed_token")
    if not token:
        sys.exit(f"generate_link failed: {r}")
    q = urllib.parse.urlencode({"token_hash": token, "type": "magiclink", "next": nxt})
    print(f"{base}/auth/confirm?{q}")


if __name__ == "__main__":
    main()

"""Set up and deploy the Supabase side: migrations, function secrets, the `api` Edge Function.

usage: python3 supabase/deploy.py [migrate] [anon] [secrets] [function]   (no args = all four, in order)

Needs SUPABASE_ACCESS_TOKEN (personal access token) in admin/.env; `secrets` also sends OPENROUTER_API_KEY if set.
ALLOWED_ORIGINS (env) overrides the default local origins, e.g. to add a temporary tunnel URL.
Secrets are sent only to api.supabase.com and never printed. `anon` writes the public anon key to admin/.env.
"""
import json, os, secrets as pysecrets, subprocess, sys, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENV = os.path.join(ROOT, "admin", ".env")
REF = "yqaducvspzrqokcqwlga"
CLI = "supabase@3.1.0"
ORIGINS = "http://127.0.0.1:8788,http://localhost:8788"


def load_env():
    for line in open(ENV):
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))
    if not os.environ.get("SUPABASE_ACCESS_TOKEN"):
        raise SystemExit("Missing SUPABASE_ACCESS_TOKEN in admin/.env")


def mgmt(method, path, body=None):
    req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{REF}{path}", method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['SUPABASE_ACCESS_TOKEN']}",
                                          "Content-Type": "application/json", "User-Agent": "bdm-deploy"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            t = r.read()
            return json.loads(t) if t else None
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {path}: HTTP {e.code} {e.read().decode()[:400]}")


def migrate():
    d = os.path.join(HERE, "migrations")
    for f in sorted(os.listdir(d)):
        if f.endswith(".sql"):
            mgmt("POST", "/database/query", {"query": open(os.path.join(d, f)).read()})
            print("migration applied:", f)


def set_env_line(key, value):
    lines = open(ENV).read().splitlines()
    lines = [l for l in lines if not l.startswith(key + "=")] + [f"{key}={value}"]
    open(ENV, "w").write("\n".join(lines) + "\n")


def anon():
    keys = mgmt("GET", "/api-keys")
    k = next((x["api_key"] for x in keys if x.get("name") == "anon"), None)
    if not k:
        raise SystemExit("no anon key found")
    set_env_line("SUPABASE_ANON_KEY", k)
    print("SUPABASE_ANON_KEY written to admin/.env (public key)")


def secrets():
    existing = {x["name"] for x in mgmt("GET", "/secrets")}
    body = [{"name": "ALLOWED_ORIGINS", "value": os.environ.get("ALLOWED_ORIGINS", ORIGINS)}]
    if os.environ.get("OPENROUTER_API_KEY"):  # brand profile + shortlist review (Claude Haiku 5.5 via OpenRouter)
        body.append({"name": "OPENROUTER_API_KEY", "value": os.environ["OPENROUTER_API_KEY"]})
    if os.environ.get("PROXY_SECRET"):  # shared with the Render forwarder so it may pass the visitor's IP
        body.append({"name": "PROXY_SECRET", "value": os.environ["PROXY_SECRET"]})
    if "RATE_SALT" not in existing:  # keep the salt stable so rate-limit buckets survive redeploys
        body.append({"name": "RATE_SALT", "value": pysecrets.token_hex(16)})
    mgmt("POST", "/secrets", body)
    # Bedrock dropped 2026-11-19 (account blocked); direct Anthropic API replaced by OpenRouter 2026-11-20
    stale = [n for n in ("BEDROCK_API_KEY", "ANTHROPIC_API_KEY") if n in existing]
    if stale:
        mgmt("DELETE", "/secrets", stale)
    print("secrets set:", ", ".join(b["name"] for b in body), "| removed:", ", ".join(stale) or "none")


def function():
    subprocess.run([sys.executable, os.path.join(ROOT, "pipeline", "export_taxonomy.py")], check=True)
    env = {**os.environ, "SUPABASE_ACCESS_TOKEN": os.environ["SUPABASE_ACCESS_TOKEN"]}
    subprocess.run(["npx", "-y", CLI, "functions", "deploy", "api", "--project-ref", REF, "--use-api", "--yes"],
                   cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    load_env()
    steps = sys.argv[1:] or ["migrate", "anon", "secrets", "function"]
    for s in steps:
        {"migrate": migrate, "anon": anon, "secrets": secrets, "function": function}[s]()

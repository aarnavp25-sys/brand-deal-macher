"""Apply web/db/migrations/*.sql to the "database" Supabase project through the Management API.

Usage (from the repo root):  python3 web/db/migrate.py [--check]
Reads NEXT_PUBLIC_SUPABASE_URL and SUPABASE_ACCESS_TOKEN from the environment or web/.env.local.
Every migration is idempotent, so running all of them again is safe. --check only prints the state.
Python 3 stdlib only.
"""
import json, os, pathlib, sys, urllib.error, urllib.request

HERE = pathlib.Path(__file__).resolve().parent


def env():
    vals = {}
    f = HERE.parent / ".env.local"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
    vals.update({k: v for k, v in os.environ.items() if k in ("NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_ACCESS_TOKEN")})
    return vals


def query(ref, token, sql):
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{ref}/database/query",
        data=json.dumps({"query": sql}).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "kindred-migrate"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:500]}")


CHECK = """
select c.relname as name, c.relkind as kind, c.relrowsecurity as rls,
       (select string_agg(distinct g.grantee || ':' || g.privilege_type, ' ' order by g.grantee || ':' || g.privilege_type)
          from information_schema.role_table_grants g
         where g.table_schema = 'public' and g.table_name = c.relname and g.grantee in ('anon', 'authenticated')) as grants,
       c.reloptions as options
  from pg_class c join pg_namespace n on n.oid = c.relnamespace
 where n.nspname = 'public' and c.relname in ('brand_searches', 'llm_calls', 'creator_overview', 'creator_ai', 'reel_ai')
 order by 1
"""


def main():
    e = env()
    ref = e["NEXT_PUBLIC_SUPABASE_URL"].split("//")[1].split(".")[0]
    token = e["SUPABASE_ACCESS_TOKEN"]
    if "--check" not in sys.argv:
        for f in sorted((HERE / "migrations").glob("*.sql")):
            query(ref, token, f.read_text())
            print("applied", f.name)
    for row in query(ref, token, CHECK):
        print(row)
    print(query(ref, token, "select id, public from storage.buckets where id = 'creator-photos'"))
    print(query(ref, token, "select policyname, cmd, roles from pg_policies where tablename = 'brand_searches'"))


if __name__ == "__main__":
    main()

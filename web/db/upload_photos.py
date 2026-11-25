"""Upload creator profile pictures to the private Storage bucket `creator-photos` as <username>.jpg.

Source: ../instagram-scraper/media/<username>/_profile.jpg (downloaded by the scraper before the CDN URLs expired).
Only creators with an AI profile (ai_status = 'done') are uploaded. Re-running skips files already in the bucket.
Usage (from the repo root): python3 web/db/upload_photos.py
Reads NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SECRET_KEY from the environment or web/.env.local. Python 3 stdlib only.
"""
import concurrent.futures as cf, json, os, pathlib, urllib.error, urllib.parse, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
MEDIA = HERE.parent.parent.parent / "instagram-scraper" / "media"
BUCKET = "creator-photos"


def env():
    vals = {}
    for line in (HERE.parent / ".env.local").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    vals.update({k: v for k, v in os.environ.items() if k in ("NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_SECRET_KEY")})
    return vals["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/"), vals["SUPABASE_SECRET_KEY"]


URL, KEY = env()
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}


def call(path, method="GET", body=None, headers=None):
    req = urllib.request.Request(URL + path, method=method, data=body, headers={**H, **(headers or {})})
    return json.load(urllib.request.urlopen(req, timeout=60))


def usernames():
    rows = call("/rest/v1/creator_overview?select=username&ai_status=eq.done&order=username&limit=2000")
    return [r["username"] for r in rows]


def existing():
    names, offset = set(), 0
    while True:
        page = call(f"/storage/v1/object/list/{BUCKET}", "POST",
                    json.dumps({"prefix": "", "limit": 1000, "offset": offset}).encode(),
                    {"Content-Type": "application/json"})
        names |= {o["name"] for o in page}
        if len(page) < 1000:
            return names
        offset += 1000


def upload(u):
    src = MEDIA / u / "_profile.jpg"
    if not src.exists():
        return u, "missing"
    path = urllib.parse.quote(f"{u}.jpg")
    try:
        call(f"/storage/v1/object/{BUCKET}/{path}", "POST", src.read_bytes(),
             {"Content-Type": "image/jpeg", "x-upsert": "true", "Cache-Control": "max-age=86400"})
        return u, "ok"
    except urllib.error.HTTPError as e:
        return u, f"HTTP {e.code} {e.read().decode()[:120]}"


def main():
    todo = [u for u in usernames() if f"{u}.jpg" not in existing()]
    print("to upload:", len(todo))
    res = {}
    with cf.ThreadPoolExecutor(8) as ex:
        for u, r in ex.map(upload, todo):
            res.setdefault(r if r in ("ok", "missing") else "error", []).append((u, r))
    for k, v in res.items():
        print(k, len(v))
    for u, r in res.get("error", [])[:5]:
        print("  error:", r)
    print("in bucket now:", len(existing()))


if __name__ == "__main__":
    main()

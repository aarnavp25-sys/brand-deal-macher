"""Kindred Board: read-only admin dashboard for the scraped creators and their AI profiles: http://127.0.0.1:8791

  ../instagram-scraper/.venv/bin/python kindred_board/server.py [--port 8791]   (from the Brand Deal Matcher folder)

Reads Supabase schema public (final data) with the service key (server side only; the browser never sees it) and serves the local
media files (covers, profile pictures, reel videos with Range support). Binds to 127.0.0.1 only.
"""
import argparse
import csv
import io
import json
import mimetypes
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

BDM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# data side lives in the scraper repo: igs/store.py (+ its .env) and media/
ROOT = os.environ.get("SCRAPER_DIR") or os.path.join(os.path.dirname(BDM), "instagram-scraper")
sys.path.insert(0, ROOT)
from igs.store import Store  # noqa: E402

MEDIA = os.path.realpath(os.path.join(ROOT, "media"))
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_S = 60
_cache, _lock = {}, threading.Lock()
store = None
# flat AI columns from public.creator_ai (written by tools/gemini_run.py)
AI_COLS = ("status,account_type,category,secondary_category,content_mix,format_mix,creator_gender,languages,main_language,"
           "niche,niche_status,creator_role,secondary_role,show_as_expert,credentials,audience_stated,audience_gender_est,"
           "audience_age_est,content_made_for,products_for,brand_collabs,collab_brands,sells_own_products,offers_services,"
           "what_they_do,summary,journeys,quality,in_india,needs_review,flags,reels_noted,reels_total,stopped_early,"
           "stop_reason,prompt_version,cost,error,updated_at")


def cached(key, fn):
    with _lock:
        hit = _cache.get(key)
        if hit and time.time() - hit[0] < CACHE_S:
            return hit[1]
    val = fn()
    with _lock:
        _cache[key] = (time.time(), val)
    return val


def creators():
    """One row per creator: metrics + profile + categories."""
    def load():
        m = {r["username"]: r for r in store.select("creator_metrics", {"select": "*"})}
        p = {r["username"]: r for r in store.select("scrape_profiles", {
            "select": "username,ig_id,following,total_posts,total_posts_text,bio,bio_links,is_verified,"
                      "profile_pic_file,last_post_at,scraped_at"})}
        groups = {r["category"]: r["group_name"] for r in store.select("index_category_groups",
                                                                       {"select": "category,group_name",
                                                                        "order": "category.asc"})}
        cats = {}
        for r in store.select("index_creator_categories", {"select": "username,category",
                                                           "order": "username.asc,category.asc"}):
            g = groups.get(r["category"])
            if g and g not in cats.setdefault(r["username"], []):
                cats[r["username"]].append(g)
        try:
            ai = {r["username"]: r for r in store.select("creator_ai", {"select": "username," + AI_COLS})}
        except Exception:  # noqa: BLE001  (table not created yet)
            ai = {}
        out = []
        for u, row in m.items():
            row = dict(row, **{k: v for k, v in p.get(u, {}).items() if k != "username"})
            row["categories"] = cats.get(u, [])
            row["ai"] = ai.get(u)
            out.append(row)
        out.sort(key=lambda r: r["username"])
        return out
    return cached("creators", load)


def creator(u):
    def load():
        prof = store.select("scrape_profiles", {"select": "*", "username": f"eq.{u}"})
        if not prof:
            return None
        posts = store.select("scrape_reels", {
            "select": "shortcode,kind,in_reels_tab,in_grid,is_pinned,reel_rank,taken_at,views,likes,likes_hidden,"
                      "comments,caption,hashtags,mentions,alt_text,tagged_users,coauthors,music_title,music_artist,"
                      "is_original_audio,location_name,duration_s,has_audio,thumbnail_file,video_file,audio_file",
            "username": f"eq.{u}"})
        met = store.select("creator_metrics", {"select": "*", "username": f"eq.{u}"})
        try:
            ai = store.select("creator_ai", {"select": "username," + AI_COLS, "username": f"eq.{u}"})
            notes = {r["shortcode"]: r for r in store.select("reel_ai", {"select": "shortcode,reel,note,trimmed_to_s",
                                                                          "username": f"eq.{u}"})}
        except Exception:  # noqa: BLE001
            ai, notes = [], {}
        return {"profile": prof[0], "metrics": met[0] if met else None, "posts": posts,
                "ai": ai[0] if ai else None, "reel_notes": notes}
    return cached("c:" + u, load)


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False, default=str).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def media(self, rel):
        path = os.path.realpath(os.path.join(MEDIA, rel))
        if not path.startswith(MEDIA + os.sep) or not os.path.isfile(path):
            return self.send(404, {"error": "not found"})
        size = os.path.getsize(path)
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        start, end, code = 0, size - 1, 200
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            a, _, b = rng[6:].partition("-")
            start = int(a) if a else max(0, size - int(b))
            end = int(b) if (a and b) else size - 1
            end = min(end, size - 1)
            code = 206
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Cache-Control", "max-age=3600")
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.end_headers()
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 16, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    def do_GET(self):
        url = urlparse(self.path)
        p = unquote(url.path)
        try:
            if p in ("/", "/index.html"):
                return self.send(200, open(os.path.join(HERE, "index.html"), "rb").read(), "text/html; charset=utf-8")
            if p == "/api/creators":
                return self.send(200, creators())
            if p.startswith("/api/creator/"):
                d = creator(p.split("/api/creator/", 1)[1])
                return self.send(200 if d else 404, d or {"error": "unknown creator"})
            if p == "/api/export.csv":
                rows = creators()
                cols = ["username", "categories", "followers", "reels_count", "fewer_than_12", "activity",
                        "last_reel_at", "days_since_last_reel", "median_views", "reach_ratio", "engagement_rate",
                        "engagement_estimated", "comment_rate", "likes_hidden_share", "reels_per_week",
                        "viral_reels", "collab_share", "content_format", "median_duration_s", "flags", "calc_at"]
                ai_cols = ["status", "account_type", "category", "secondary_category", "creator_gender", "main_language",
                           "languages", "niche", "niche_status", "creator_role", "show_as_expert", "audience_stated",
                           "audience_gender_est", "audience_age_est", "brand_collabs", "collab_brands",
                           "sells_own_products", "offers_services", "quality", "needs_review", "what_they_do", "summary"]
                buf = io.StringIO()
                w = csv.writer(buf)
                w.writerow(cols + ["ai_" + c for c in ai_cols])
                for r in rows:
                    a = r.get("ai") or {}
                    w.writerow(["; ".join(r[c]) if isinstance(r.get(c), list) else r.get(c) for c in cols] +
                               [json.dumps(a.get(c), ensure_ascii=False) if isinstance(a.get(c), (dict, list)) else a.get(c)
                                for c in ai_cols])
                return self.send(200, "﻿" + buf.getvalue(), "text/csv; charset=utf-8",
                                 {"Content-Disposition": "attachment; filename=creators.csv"})
            if p == "/api/refresh":
                with _lock:
                    _cache.clear()
                return self.send(200, {"ok": True})
            if p.startswith("/media/"):
                return self.media(p[len("/media/"):])
            return self.send(404, {"error": "not found"})
        except Exception as e:  # show the error instead of a blank page
            return self.send(500, {"error": f"{type(e).__name__}: {e}"})


def main():
    global store
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8791)
    a = ap.parse_args()
    store = Store()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    print(f"Kindred Board: http://127.0.0.1:{a.port}  (Ctrl-C to stop)", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

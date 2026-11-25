"""Small PAID test of the reel step (docs/ai-profile-spec.md): sends chosen reels to Gemini on OpenRouter, saves every
raw response, and prints real token usage, cached tokens and cost. Hard spend cap; stops before a call that could
pass it. The OpenRouter key is read from the Brand Deal Matcher repo's admin/.env and never printed.

  ../instagram-scraper/.venv/bin/python ai/gemini_test.py --reels user:SHORTCODE,user2:SHORTCODE --max-usd 0.10 --yes
"""
import argparse
import base64
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

BDM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # Brand Deal Matcher repo
AI_DIR = os.path.dirname(os.path.abspath(__file__))                          # this folder (ai/)
# The scraper repo holds the data side: igs/store.py (Supabase "database" project, its .env) and media/ (videos).
SCRAPER = os.environ.get("SCRAPER_DIR") or os.path.join(os.path.dirname(BDM), "instagram-scraper")
HERE = SCRAPER        # video_file / profile_pic_file paths in the DB are relative to the scraper repo
STATE = os.path.join(AI_DIR, "state")   # every AI output (raw answers, logs, cut videos); gitignored
sys.path.insert(0, HERE)
sys.path.insert(0, AI_DIR)
import gemini_dryrun as G  # noqa: E402
from igs.store import Store  # noqa: E402

ENV = os.path.join(BDM, "admin", ".env")
PER_CALL_CEILING = 0.02   # a single reel call is ~$0.002-0.004; anything near this means a wrong assumption


def key():
    for line in open(ENV):
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"')
    raise SystemExit("OPENROUTER_API_KEY missing in " + ENV)


def post(body, k):
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + k, "Content-Type": "application/json",
                                          "X-Title": "Brand Deal Matcher test"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as r:   # flex sometimes hangs ~15 min; give up and retry
            return json.loads(r.read()), time.time() - t, None
    except urllib.error.HTTPError as e:
        return None, time.time() - t, f"HTTP {e.code}: {e.read().decode()[:600]}"
    except (TimeoutError, OSError) as e:
        return None, time.time() - t, f"Timeout/network: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reels", required=True, help="user:shortcode,...")
    ap.add_argument("--max-usd", type=float, required=True)
    ap.add_argument("--tier", default="flex", choices=list(G.PRICES))
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    pairs = [x.split(":", 1) for x in a.reels.split(",")]
    if not a.yes:
        raise SystemExit("paid call: add --yes")
    store, k = Store(), key()
    out = os.path.join(STATE, "ai_test", dt.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    os.makedirs(out, exist_ok=True)
    spent, rows = 0.0, []
    for user, code in pairs:
        if spent + PER_CALL_CEILING > a.max_usd:
            print(f"stop: next call could pass the ${a.max_usd} cap (spent ${spent:.4f})")
            break
        r = store.select("scrape_reels", {"select": "*", "username": f"eq.{user}", "shortcode": f"eq.{code}"})[0]
        rid = f"R{r['reel_rank']}"
        path = os.path.join(HERE, r["video_file"])
        b64 = base64.b64encode(open(path, "rb").read()).decode()
        content = [{"type": "text", "text": G.reel_details(rid, r, user)},
                   {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + b64}}]
        body = G.body(G.REEL_PROMPT, content, G.REEL_SCHEMA, "reel_note", a.tier)
        body["usage"] = {"include": True}
        resp, secs, err = post(body, k)
        rec = {"user": user, "shortcode": code, "reel": rid, "seconds": round(secs, 1), "error": err,
               "duration_s": float(r["duration_s"]), "response": resp}
        json.dump(rec, open(os.path.join(out, f"{user}_{code}.json"), "w"), indent=1, ensure_ascii=False)
        if err:
            print(f"@{user} {code}: {err}")
            rows.append(rec)
            continue
        u = resp.get("usage") or {}
        cost = float(u.get("cost") or 0)
        spent += cost
        det = u.get("prompt_tokens_details") or {}
        print(f"@{user} {code} {rid} {rec['duration_s']:.0f}s video | {secs:.0f}s wait | provider "
              f"{resp.get('provider')} tier {resp.get('service_tier')} | in {u.get('prompt_tokens')} "
              f"(cached {det.get('cached_tokens')}, audio {det.get('audio_tokens')}, video {det.get('video_tokens')}) "
              f"out {u.get('completion_tokens')} | ${cost:.5f}")
        rows.append(rec)
    print(f"\nspent ${spent:.4f} · files {out}")


if __name__ == "__main__":
    main()

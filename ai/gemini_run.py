"""FULL PAID RUN of the AI creator profile (docs/ai-profile-spec.md, prompt in tools/gemini_dryrun.py).

Per creator: the latest 12 non-pinned reels go to Gemini (google/gemini-3.1-flash-lite, flex) in groups of up to 4
reels (a group is split further so no request passes MAX_GROUP_MB). After each group, until the account is clearly a
creator, a cheap text check asks whether it is a personal account, a shop or a repost page; the run for that account
stops only when the AI says so with high confidence AND the code's own count agrees (owner 2026-11-26: "jab tak high
confidence na ho, utni reels chalana"). Then the code counts the facts, the creator step judges the rest, and the
result is written to Supabase (public.creator_ai, public.reel_ai) and to ai/state/ai_run/<run>/<user>.json.
Videos longer than TRIM_S are cut (stream copy, no re-encode) to their first TRIM_S seconds.
Resumable: creators already finished with the same prompt version are skipped. Hard spend cap.

  caffeinate -i -s ../instagram-scraper/.venv/bin/python -u ai/gemini_run.py --activity active --max-usd 11 --yes
  ../instagram-scraper/.venv/bin/python -u ai/gemini_run.py --users a,b --max-usd 0.3 --yes        # small test
  ../instagram-scraper/.venv/bin/python ai/gemini_run.py --migrate                                   # create the two tables
"""
import argparse
import base64
import datetime as dt
import json
import math
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

BDM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # Brand Deal Matcher repo
AI_DIR = os.path.dirname(os.path.abspath(__file__))                          # this folder (ai/)
# The scraper repo holds the data side: igs/store.py (Supabase "database" project, its .env) and media/ (videos).
SCRAPER = os.environ.get("SCRAPER_DIR") or os.path.join(os.path.dirname(BDM), "instagram-scraper")
HERE = SCRAPER        # video_file / profile_pic_file paths in the DB are relative to the scraper repo
STATE = os.path.join(AI_DIR, "state")   # every AI output (raw answers, logs, cut videos); gitignored
sys.path.insert(0, HERE)
sys.path.insert(0, AI_DIR)
import gemini_dryrun as G  # noqa: E402
import gemini_compare as C  # noqa: E402  (sets the 240 s timeout post + 0.02 reserve on the pilot module)
import gemini_pilot as P  # noqa: E402
from gemini_test import key  # noqa: E402
from igs.store import Store  # noqa: E402

TRIM_S = 180
MAX_GROUP_MB = 18.0          # base64 MB of one request's videos; Google AI Studio rejects bodies over 20,000,000 bytes (seen 2026-11-26)
GROUP = 4
CREATOR_WORKERS = 6
NON_CREATOR = ("personal", "repost_or_meme_page", "shop_or_brand")
SHOP_BIO = re.compile(r"(?i)\b(order now|to order|dm (?:to|for) (?:order|price|purchase)|cod\b|cash on delivery|"
                      r"shipping|ships? (?:all over|pan)|whole ?sale|retail|showroom|store address|price list|"
                      r"₹\s?\d|rs\.?\s?\d|wholesaler|manufacturer|reseller|boutique)")
CREATOR_DIR = None   # where the creator-step raw answers go (set in main)
LOCK = threading.Lock()
STOP = threading.Event()
STATS = {"done": 0, "stopped": 0, "failed": 0, "skipped": 0, "reels_sent": 0, "trimmed": 0, "split": 0,
         "single_fallback": 0, "t0": time.time()}

SQL = """
create table if not exists public.creator_ai (
  username text primary key, status text not null, prompt_version text, model text,
  reels_total int, reels_sent int, reels_noted int, stopped_early boolean default false, stop_reason text,
  profile jsonb, counts jsonb, creator jsonb, flags text[] not null default '{}', cost numeric, error text,
  updated_at timestamptz not null default now());
create table if not exists public.reel_ai (
  username text not null, shortcode text not null, reel text not null, note jsonb not null,
  trimmed_to_s numeric, prompt_version text, updated_at timestamptz not null default now(),
  primary key (username, shortcode));
alter table public.creator_ai enable row level security;
alter table public.reel_ai enable row level security;
grant all on public.creator_ai, public.reel_ai to service_role;
-- flat, readable columns (2026-11-26): the same facts as profile/counts/creator, one column each
alter table public.creator_ai
  add column if not exists account_type text, add column if not exists category text,
  add column if not exists secondary_category text, add column if not exists content_mix jsonb,
  add column if not exists format_mix jsonb, add column if not exists creator_gender text,
  add column if not exists languages jsonb, add column if not exists main_language text,
  add column if not exists niche text, add column if not exists niche_status text,
  add column if not exists creator_role text, add column if not exists secondary_role text,
  add column if not exists show_as_expert boolean, add column if not exists credentials text,
  add column if not exists audience_stated text, add column if not exists audience_gender_est text,
  add column if not exists audience_age_est text, add column if not exists content_made_for jsonb,
  add column if not exists products_for jsonb, add column if not exists brand_collabs text,
  add column if not exists collab_brands text[], add column if not exists sells_own_products boolean,
  add column if not exists offers_services boolean, add column if not exists what_they_do text,
  add column if not exists summary text, add column if not exists journeys jsonb,
  add column if not exists quality text, add column if not exists in_india text,
  add column if not exists needs_review boolean;
create or replace view public.creator_overview as
  select p.username, p.followers, p.bio, p.activity, p.last_reel_at, m.median_views, m.reach_ratio,
         m.engagement_rate, m.engagement_estimated, m.reels_per_week, m.content_format,
         a.status as ai_status, a.account_type, a.category, a.secondary_category, a.content_mix, a.format_mix,
         a.creator_gender, a.languages, a.main_language, a.niche, a.niche_status, a.creator_role, a.secondary_role,
         a.show_as_expert, a.credentials, a.audience_stated, a.audience_gender_est, a.audience_age_est,
         a.content_made_for, a.products_for, a.brand_collabs, a.collab_brands, a.sells_own_products,
         a.offers_services, a.what_they_do, a.summary, a.journeys, a.quality, a.in_india, a.needs_review, a.flags,
         a.reels_noted, a.stopped_early, a.stop_reason, a.prompt_version, a.cost as ai_cost, a.updated_at as ai_updated_at
  from public.scrape_profiles p
  join public.creator_metrics m using (username)
  left join public.creator_ai a using (username);
grant select on public.creator_overview to service_role;
notify pgrst, 'reload schema';
"""


# flags that are information only, not a reason for a human to look
INFO_FLAGS = ("collab: AI says",)


def flat(prof, counts, creator, flags):
    """The readable columns of creator_ai (see SQL above)."""
    langs = counts.get("language_families") or {}
    return {
        "account_type": creator.get("account_type"), "category": counts.get("category"),
        "secondary_category": counts.get("secondary"), "content_mix": counts.get("content_mix"),
        "format_mix": counts.get("format_mix"), "creator_gender": counts.get("creator_gender"),
        "languages": counts.get("spoken_languages"), "main_language": max(langs, key=langs.get) if langs else None,
        "niche": creator.get("niche"), "niche_status": prof.get("niche_status"),
        "creator_role": creator.get("creator_role"), "secondary_role": creator.get("secondary_role"),
        "show_as_expert": bool(prof.get("show_as_expert")), "credentials": creator.get("credentials_stated") or None,
        "audience_stated": creator.get("target_audience_stated"),
        "audience_gender_est": creator.get("audience_gender_estimate"),
        "audience_age_est": creator.get("audience_age_estimate"), "content_made_for": counts.get("content_made_for"),
        "products_for": counts.get("products_for"), "brand_collabs": prof.get("brand_collabs"),
        "collab_brands": counts.get("collab_brands_code") or [], "sells_own_products": creator.get("sells_own_products"),
        "offers_services": creator.get("offers_services"), "what_they_do": creator.get("what_they_do"),
        "summary": creator.get("summary"), "journeys": creator.get("journeys"), "quality": creator.get("quality"),
        "in_india": creator.get("in_india"),
        "needs_review": any(not f.startswith(INFO_FLAGS) for f in flags),
    }


def log(msg):
    with LOCK:
        print(msg, flush=True)


def trimmed(user, r):
    """Path to send and seconds sent. Long videos are cut to TRIM_S with a stream copy (no quality change)."""
    src = os.path.join(HERE, r["video_file"])
    d = float(r.get("duration_s") or 0)
    if d <= TRIM_S + 5:
        return src, d
    dst = os.path.join(STATE, "ai_trim", user, f"{r['shortcode']}_{TRIM_S}s.mp4")
    if not os.path.exists(dst):
        import imageio_ffmpeg
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-i", src, "-t", str(TRIM_S),
                        "-c", "copy", "-movflags", "+faststart", dst], check=True)
        with LOCK:
            STATS["trimmed"] += 1
    return dst, float(TRIM_S)


def make_groups(user, reels):
    items = []
    for r in reels:
        path, sent = trimmed(user, r)
        items.append((r, path, sent, os.path.getsize(path) * 4 / 3 / 1e6))
    groups, cur, mb = [], [], 0.0
    for it in items:
        if cur and (len(cur) >= GROUP or mb + it[3] > MAX_GROUP_MB):
            groups.append(cur)
            cur, mb = [], 0.0
        cur.append(it)
        mb += it[3]
    if cur:
        groups.append(cur)
    if any(len(g) < GROUP for g in groups[:-1]):
        with LOCK:
            STATS["split"] += 1
    return groups


def details(user, rid, r, bio, sent, with_context):
    txt = G.reel_details(rid, r, user, bio)
    if not with_context:
        txt = txt.split("\n", 2)[2]
    d = float(r.get("duration_s") or 0)
    if sent < d - 1:
        txt = txt.replace("The video with its audio follows.",
                          f"Only the first {sent:.0f} s of this {d:.0f} s video are attached. The video with its audio follows.")
    return txt


def group_call(user, bio, group, k, cap):
    ids = [f"R{it[0]['reel_rank']}" for it in group]
    content = [{"type": "text", "text": f"Account context: @{user} · bio: {G.scrub(bio) or '(empty)'}\n\n"
                                        f"{len(group)} reels follow: {', '.join(ids)}."}]
    for rid, (r, path, sent, _) in zip(ids, group):
        content += [{"type": "text", "text": details(user, rid, r, bio, sent, False)},
                    {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," +
                                                        base64.b64encode(open(path, "rb").read()).decode()}}]
    content.append({"type": "text", "text": f"Now write one note for each of {', '.join(ids)}."})
    body = G.body(C.GROUP_PROMPT, content, C.GROUP_SCHEMA, "reel_notes", "flex")
    body["messages"][0] = P.system_msg(C.GROUP_PROMPT)
    body["max_tokens"] = 600 * len(group) + 2000
    body["usage"] = {"include": True}
    resp, secs, err, cost = P.call(body, k, cap)
    notes = {}
    if not err:
        parsed, err = P.parse(resp)
        for n in (parsed or {}).get("notes", []):
            if n.get("reel") in ids and n["reel"] not in notes:
                for person in n.get("people", []):
                    person["look"] = G.clean_look(person.get("look"))
                notes[n["reel"]] = {x: v for x, v in n.items() if x != "reel"}
    return notes, cost, err


def single_call(user, bio, item, k, cap):
    r, path, sent, _ = item
    rid = f"R{r['reel_rank']}"
    content = [{"type": "text", "text": details(user, rid, r, bio, sent, True)},
               {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," +
                                                   base64.b64encode(open(path, "rb").read()).decode()}}]
    body = G.body(G.REEL_PROMPT, content, G.REEL_SCHEMA, "reel_note", "flex")
    body["messages"][0] = P.system_msg(G.REEL_PROMPT)
    body["usage"] = {"include": True}
    resp, secs, err, cost = P.call(body, k, cap)
    note = None
    if not err:
        note, err = P.parse(resp)
        if note:
            for person in note.get("people", []):
                person["look"] = G.clean_look(person.get("look"))
    return note, cost, err


def run_group(user, bio, group, k, cap):
    """Notes for one group; reels the group answer left out are retried one by one."""
    notes, cost, err = group_call(user, bio, group, k, cap)
    errs = [err] if err else []
    for it in group:
        rid = f"R{it[0]['reel_rank']}"
        if rid not in notes:
            n, c2, e2 = single_call(user, bio, it, k, cap)
            cost += c2
            with LOCK:
                STATS["single_fallback"] += 1
            if n:
                notes[rid] = n
            elif e2:
                errs.append(f"{rid}: {e2[:120]}")
    return notes, cost, errs


def creator_call(user, profile, notes, k, cap):
    counts = G.aggregate(notes)
    recs = [{"reel": rid, "note": notes[rid]} for rid in sorted(notes, key=lambda x: int(x[1:]))]
    creator, err, cost, _ = P.creator_job(user, profile, recs, counts, k, cap, CREATOR_DIR, tag=f"_{len(notes)}")
    return counts, creator, err, cost


def code_agrees(kind, notes, bio):
    n = len(notes)
    need = max(3, math.ceil(0.75 * n))
    if kind == "personal":
        return sum(v["category"] == G.PERSONAL for v in notes.values()) >= need
    if kind == "repost_or_meme_page":
        return sum(v["is_reposted"] == "yes" for v in notes.values()) >= need
    if kind == "shop_or_brand":
        own = sum(any(p["own_brand"] for p in v["products"]) for v in notes.values())
        return own >= need or (bool(SHOP_BIO.search(bio or "")) and own >= 2)
    return False


def process(user, profile, reels, k, cap, out, store, total, idx):
    if STOP.is_set():
        return
    bio = profile.get("bio") or ""
    t0 = time.time()
    rec = {"username": user, "prompt_version": G.PROMPT_VERSION, "model": G.MODEL, "reels_total": len(reels)}
    try:
        groups = make_groups(user, reels)
        notes, cost, errs, sent, stop_reason = {}, 0.0, [], 0, None
        sure_creator = False
        for gi, g in enumerate(groups):
            if STOP.is_set():
                raise P.CapReached()
            # once the account is a sure creator, the remaining groups run in parallel
            if sure_creator and gi < len(groups):
                with ThreadPoolExecutor(len(groups) - gi) as ex:
                    res = list(ex.map(lambda gg: run_group(user, bio, gg, k, cap), groups[gi:]))
                for nn, cc, ee in res:
                    notes.update(nn)
                    cost += cc
                    errs += ee
                sent += sum(len(gg) for gg in groups[gi:])
                break
            nn, cc, ee = run_group(user, bio, g, k, cap)
            notes.update(nn)
            cost += cc
            errs += ee
            sent += len(g)
            if gi == len(groups) - 1 or len(notes) < 3:
                continue
            # early check on the notes so far (text only)
            _, cr, cerr, ccost = creator_call(user, profile, notes, k, cap)
            cost += ccost
            if not cr:
                continue
            kind, conf = cr["account_type"], cr["confidence"]["account_type"]
            if kind in NON_CREATOR and conf == "high" and code_agrees(kind, notes, bio):
                stop_reason = f"{kind} after {len(notes)} reels: {cr['account_type_reason'][:160]}"
                break
            if kind not in NON_CREATOR and conf == "high":
                sure_creator = True
        # a creator with fewer than 6 reels in total is fine when every reel was answered (aggregate flags it)
        if len(notes) < min(G.MIN_ANALYSED_REELS, len(reels)) and not stop_reason:
            raise RuntimeError(f"only {len(notes)} reel notes: {'; '.join(errs)[:300]}")
        counts, creator, cerr, ccost = creator_call(user, profile, notes, k, cap)
        cost += ccost
        if not creator:
            raise RuntimeError(f"creator step failed: {cerr}")
        prof, flags = G.finalize(counts, creator, bio, notes)
        if stop_reason:
            flags = flags + [f"stopped early: {stop_reason}"]
        status = "stopped_non_creator" if stop_reason else "done"
        rec.update(status=status, reels_sent=sent, reels_noted=len(notes), stopped_early=bool(stop_reason),
                   stop_reason=stop_reason, profile=prof, counts=counts, creator=creator, flags=flags,
                   cost=round(cost, 6), error="; ".join(errs)[:500] or None)
        json.dump(dict(rec, notes=notes), open(os.path.join(out, f"{user}.json"), "w"), indent=1, ensure_ascii=False,
                  default=str)
        store.upsert("reel_ai", [{"username": user, "shortcode": r["shortcode"], "reel": f"R{r['reel_rank']}",
                                   "note": notes[f"R{r['reel_rank']}"], "prompt_version": G.PROMPT_VERSION,
                                   "trimmed_to_s": TRIM_S if float(r.get("duration_s") or 0) > TRIM_S + 5 else None}
                                  for r in reels if f"R{r['reel_rank']}" in notes], "username,shortcode")
        store.upsert("creator_ai", [dict(rec, **flat(prof, counts, creator, flags),
                                         updated_at=dt.datetime.now(dt.timezone.utc).isoformat())], "username")
        with LOCK:
            STATS["stopped" if stop_reason else "done"] += 1
            STATS["reels_sent"] += sent
        cat = f"{counts['category']} + {counts['secondary']}"
        log(f"[{idx}/{total}] @{user}: {'STOPPED ' + stop_reason[:60] if stop_reason else 'ok'} | {cat} | "
            f"{counts['creator_gender']} | reels {len(notes)}/{len(reels)} | ${cost:.4f} | "
            f"{time.time() - t0:.0f}s{' | errors: ' + '; '.join(errs)[:150] if errs else ''}"
            f"{' | flags: ' + '; '.join(flags)[:150] if flags else ''}")
    except P.CapReached:
        STOP.set()
        log(f"CAP reached at @{user}: spent ${P.STATE['spent']:.4f}; stopping (resume later continues here)")
    except Exception as e:  # noqa: BLE001
        with LOCK:
            STATS["failed"] += 1
        try:
            store.upsert("creator_ai", [{"username": user, "status": "failed", "prompt_version": G.PROMPT_VERSION,
                                         "model": G.MODEL, "error": f"{type(e).__name__}: {e}"[:500],
                                         "updated_at": dt.datetime.now(dt.timezone.utc).isoformat()}], "username")
        except Exception:  # noqa: BLE001
            pass
        log(f"[{idx}/{total}] ERROR @{user}: {type(e).__name__}: {str(e)[:250]}")
    finally:
        with LOCK:
            n = STATS["done"] + STATS["stopped"] + STATS["failed"]
            if n and n % 25 == 0:
                el = time.time() - STATS["t0"]
                left = total - n - STATS["skipped"]
                print(f"PROGRESS {n}/{total - STATS['skipped']} · done {STATS['done']} · stopped {STATS['stopped']} · "
                      f"failed {STATS['failed']} · spent ${P.STATE['spent']:.2f} · avg ${P.STATE['spent'] / n:.4f}/creator · "
                      f"trimmed {STATS['trimmed']} · single fallbacks {STATS['single_fallback']} · "
                      f"ETA {left * el / n / 60:.0f} min", flush=True)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--users")
    g.add_argument("--activity", choices=["active", "inactive", "all"])
    g.add_argument("--migrate", action="store_true")
    g.add_argument("--flatten", action="store_true", help="fill the flat columns from the stored json")
    ap.add_argument("--max-usd", type=float)
    ap.add_argument("--workers", type=int, default=CREATOR_WORKERS)
    ap.add_argument("--redo", action="store_true", help="also redo creators already finished with this prompt")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    store = Store()
    if a.migrate:
        store.sql(SQL)
        print("tables ready")
        return
    if a.flatten:
        rows = [r for r in store.select("creator_ai", {"select": "*"}) if r.get("creator") and r.get("counts")]
        store.upsert("creator_ai", [dict({x: r[x] for x in ("username", "status")},
                                         **flat(r["profile"] or {}, r["counts"], r["creator"], r["flags"] or []))
                                    for r in rows], "username")
        print("flattened", len(rows))
        return
    if not a.yes or a.max_usd is None:
        raise SystemExit("paid run: add --max-usd X --yes")
    k = key()
    metrics = {r["username"]: r["activity"] for r in store.select("creator_metrics", {"select": "username,activity"})}
    users = ([u.strip() for u in a.users.split(",")] if a.users else
             sorted(u for u, act in metrics.items() if a.activity == "all" or act == a.activity))
    done = {r["username"] for r in store.select("creator_ai", {"select": "username,status,prompt_version"})
            if r["status"] in ("done", "stopped_non_creator") and r["prompt_version"] == G.PROMPT_VERSION}
    todo = users if a.redo else [u for u in users if u not in done]
    STATS["skipped"] = len(users) - len(todo)
    out = os.path.join(STATE, "ai_run", G.PROMPT_VERSION)
    os.makedirs(out, exist_ok=True)
    global CREATOR_DIR
    CREATOR_DIR = os.path.join(out, "_creator_steps")
    os.makedirs(CREATOR_DIR, exist_ok=True)
    profiles = {}
    for i in range(0, len(todo), 200):
        part = todo[i:i + 200]
        profiles.update({r["username"]: r for r in store.select("scrape_profiles", {
            "select": "username,bio,bio_links,profile_pic_file", "username": f"in.({','.join(part)})"})})
    log(f"START {dt.datetime.now():%Y-%m-%d %H:%M} · prompt {G.PROMPT_VERSION} · {len(todo)} to do, {STATS['skipped']} "
        f"already done · cap ${a.max_usd} · {a.workers} creators at a time")

    def job(args):
        idx, u = args
        if STOP.is_set():
            return
        reels = store.select("scrape_reels", {"select": "*", "username": f"eq.{u}", "reel_rank": "gte.1",
                                              "order": "reel_rank.asc"})[:12]
        if not reels:
            log(f"[{idx}/{len(todo)}] SKIP @{u}: no reels")
            return
        process(u, profiles.get(u, {}), reels, k, a.max_usd, out, store, len(todo), idx)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(job, enumerate(todo, 1)))
    el = time.time() - STATS["t0"]
    log(f"END · done {STATS['done']} · stopped early {STATS['stopped']} · failed {STATS['failed']} · skipped "
        f"{STATS['skipped']} · spent ${P.STATE['spent']:.4f} · {el / 60:.0f} min · trimmed videos {STATS['trimmed']} · "
        f"split groups {STATS['split']} · single-reel fallbacks {STATS['single_fallback']}"
        f"{' · STOPPED AT CAP' if STOP.is_set() else ''}")


if __name__ == "__main__":
    main()

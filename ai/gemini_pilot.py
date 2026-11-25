"""PAID pilot of the full AI profile (docs/ai-profile-spec.md) on a few creators: every latest reel (video + audio)
-> reel notes, the code's counts, the creator step, the final profile, and a readable report with real tokens and
cost. Hard spend cap (a call is only started if it cannot pass the cap). Every raw response is saved.

  ../instagram-scraper/.venv/bin/python ai/gemini_pilot.py --users a,b,c --max-usd 0.20 --yes
"""
import argparse
import base64
import datetime as dt
import json
import os
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
from gemini_test import key, post  # noqa: E402
from igs.store import Store  # noqa: E402

RESERVE = 0.01          # held back per running call; real reel calls cost ~$0.001-0.002
WORKERS = 8
LOCK = threading.Lock()
STATE = {"spent": 0.0, "reserved": 0.0, "calls": 0}


class CapReached(Exception):
    pass


def system_msg(text):
    # cache_control asks the provider to cache the long, identical instructions (checked via cached_tokens)
    return {"role": "system", "content": [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]}


def call(body, k, cap):
    with LOCK:
        if STATE["spent"] + STATE["reserved"] + RESERVE > cap:
            raise CapReached()
        STATE["reserved"] += RESERVE
    try:
        for attempt in range(3):
            resp, secs, err = post(body, k)
            if not err:
                break
            if not any(x in err for x in ("HTTP 429", "HTTP 50", "HTTP 52", "capacity", "imeout", "timed out")):
                break
            time.sleep(15 * (attempt + 1))
        cost = float(((resp or {}).get("usage") or {}).get("cost") or 0)
        with LOCK:
            STATE["spent"] += cost
            STATE["calls"] += 1
        return resp, secs, err, cost
    finally:
        with LOCK:
            STATE["reserved"] -= RESERVE


def parse(resp):
    try:
        txt = resp["choices"][0]["message"]["content"]
        return json.loads(txt), None
    except Exception as e:  # noqa: BLE001
        return None, f"unparsable answer: {e}"


def reel_job(user, r, k, cap, out, bio=""):
    rid = f"R{r['reel_rank']}"
    b64 = base64.b64encode(open(os.path.join(HERE, r["video_file"]), "rb").read()).decode()
    content = [{"type": "text", "text": G.reel_details(rid, r, user, bio)},
               {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + b64}}]
    body = G.body(G.REEL_PROMPT, content, G.REEL_SCHEMA, "reel_note", "flex")
    body["messages"][0] = system_msg(G.REEL_PROMPT)
    body["usage"] = {"include": True}
    resp, secs, err, cost = call(body, k, cap)
    note, perr = (parse(resp) if not err else (None, err))
    if note:
        for person in note.get("people", []):
            person["look"] = G.clean_look(person.get("look"))
    rec = {"reel": rid, "shortcode": r["shortcode"], "duration_s": float(r["duration_s"] or 0), "seconds": round(secs, 1),
           "cost": cost, "usage": (resp or {}).get("usage"), "provider": (resp or {}).get("provider"),
           "service_tier": (resp or {}).get("service_tier"), "error": perr, "note": note}   # captions/hashtags are never used, not even for checking (owner 2026-11-26)
    json.dump(dict(rec, raw=resp), open(os.path.join(out, f"{user}_{rid}.json"), "w"), indent=1, ensure_ascii=False)
    return rec


def creator_job(user, profile, recs, counts, k, cap, out, tag=""):
    notes = {x["reel"]: x["note"] for x in recs if x["note"]}
    head = (f"Account @{user}\nBio: {G.scrub(profile.get('bio')) or '(empty)'}\n"
            f"Links in bio: {G.fmt_links(profile.get('bio_links'))}\nProfile picture:")
    content = [{"type": "text", "text": head}]
    pic = profile.get("profile_pic_file")
    if pic and os.path.exists(os.path.join(HERE, pic)):
        b64 = base64.b64encode(open(os.path.join(HERE, pic), "rb").read()).decode()
        content.append({"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}})
    content.append({"type": "text", "text":
                    "Reel notes (R1 = newest), written by the reel analyst:\n" + json.dumps(notes, ensure_ascii=False)
                    + "\n\nCounts computed by our code from those notes:\n" + json.dumps(counts, ensure_ascii=False)
                    + "\n\nNow fill the profile."})
    body = G.body(G.CREATOR_PROMPT, content, G.CREATOR_SCHEMA, "creator_profile", "flex")
    body["usage"] = {"include": True}
    resp, secs, err, cost = call(body, k, cap)
    creator, perr = (parse(resp) if not err else (None, err))
    json.dump({"cost": cost, "seconds": round(secs, 1), "error": perr, "creator": creator, "raw": resp},
              open(os.path.join(out, f"{user}{tag}_creator.json"), "w"), indent=1, ensure_ascii=False)
    return creator, perr, cost, (resp or {}).get("usage")


def fmt_list(x):
    return ", ".join(x) if x else "-"


def report(user, act, recs, counts, creator, flags, profile, ccost, cusage):
    L = [f"## @{user} ({act})", ""]
    if creator:
        L += [f"**Account type:** {creator['account_type']} ({creator['confidence']['account_type']}) - "
              f"{creator['account_type_reason']} [{fmt_list(creator['account_type_evidence'])}]",
              f"**Sells own products:** {creator['sells_own_products']} · **Offers services:** {creator['offers_services']}",
              f"**What they do:** {creator['what_they_do']}",
              f"**Niche:** {creator['niche']} - niche reels {len(set(creator['niche_reels']))}/{counts['analysed_reels']} -> "
              f"niche creator: **{profile['niche_creator']}**",
              "**Journeys:** " + fmt_list([f"{j['what']} [{fmt_list(j['evidence'])}]" for j in creator['journeys']]),
              f"**Role:** {creator['creator_role']} · **Quality:** {creator['quality']} ({creator['quality_reason']})",
              f"**Brand collabs:** {creator['brand_collabs']} {fmt_list(creator['collab_brands'])} [{fmt_list(creator['collab_evidence'])}]",
              f"**Audience stated:** {creator['target_audience_stated']} \"{creator['stated_audience_quote']}\" · "
              f"**estimate:** {creator['audience_gender_estimate']}, {creator['audience_age_estimate']} - {creator['audience_reason']}",
              f"**In India:** {creator['in_india']} · **Summary:** {creator['summary']}"]
    L += ["", "Counted by code:",
          f"- content mix {counts['content_mix']} -> category **{counts['category']}** ({counts['category_share']}), "
          f"secondary {counts['secondary']}, scope {counts['scope']}",
          f"- format mix {counts['format_mix']}",
          f"- creator gender **{counts['creator_gender']}** ({counts['gender_share']}) · content made for "
          f"{counts['content_made_for']} · products for {counts['products_for']}",
          f"- spoken languages **{counts['spoken_languages']}** (speech in {counts['speech_reels']} reels) · owner age look "
          f"{counts['apparent_age_group']} · beard {counts['beard']} · life {counts['life_context']}",
          f"- owner on camera {counts['owner_on_camera_reels']}, owner speaks {counts['owner_speaks_reels']}, reposted "
          f"{counts['reposted_reels']} · code confidence {profile.get('code_confidence')}",
          f"- products {json.dumps(counts['products'], ensure_ascii=False)}",
          f"- **review flags:** {fmt_list(flags)}", "",
          "| reel | s | category | topic | format | made for | people (role: gender, look) | owner speaks | langs | products | milestone |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in recs:
        n = x["note"]
        if not n:
            L.append(f"| {x['reel']} | {x['duration_s']:.0f} | ERROR: {x['error']} ||||||||")
            continue
        prods = "; ".join(f"{p['level']}{' OWN' if p['own_brand'] else ''}: {p['item']} [{p['brand']}] ({p['for']})"
                          for p in n["products"])
        ppl = "; ".join(f"{p['role']}: {p['gender']}, {p['look']}" for p in n["people"]) or "-"
        langs = fmt_list(n["spoken_languages"] + [f"({o})" for o in n["other_language_names"]])
        L.append(f"| {x['reel']} | {x['duration_s']:.0f} | {n['category']} | {n['topic']} | {n['format']} | {n['made_for']} | "
                 f"{ppl} | {n['owner_speaks']} | {langs} | {prods or '-'} | {n['milestone'] or '-'} |")
    rc = sum(x["cost"] for x in recs)
    L += ["", f"Cost: reels ${rc:.4f} + creator ${ccost:.4f} = **${rc + ccost:.4f}**", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", required=True)
    ap.add_argument("--max-usd", type=float, required=True)
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    if not a.yes:
        raise SystemExit("paid run: add --yes")
    users = [u.strip() for u in a.users.split(",")]
    store, k = Store(), key()
    out = os.path.join(STATE, "ai_pilot", dt.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    os.makedirs(out, exist_ok=True)
    acts = {r["username"]: r["activity"] for r in store.select("creator_metrics", {"select": "username,activity"})}
    profiles = {r["username"]: r for r in store.select("scrape_profiles", {
        "select": "username,bio,bio_links,profile_pic_file", "username": f"in.({','.join(users)})"})}
    parts, all_recs, ctot = [], [], 0.0
    t0 = time.time()
    for user in users:
        reels = store.select("scrape_reels", {"select": "*", "username": f"eq.{user}", "reel_rank": "gte.1",
                                              "order": "reel_rank.asc"})[:G.MAX_REELS]
        bio = profiles.get(user, {}).get("bio") or ""
        try:
            first = [] if STATE["calls"] else [reel_job(user, reels[0], k, a.max_usd, out, bio)]  # warms the cache
            with ThreadPoolExecutor(WORKERS) as ex:
                recs = first + list(ex.map(lambda r: reel_job(user, r, k, a.max_usd, out, bio), reels[len(first):]))
        except CapReached:
            print(f"cap reached during @{user}; stopping (spent ${STATE['spent']:.4f})")
            break
        recs.sort(key=lambda x: int(x["reel"][1:]))
        all_recs += recs
        counts = G.aggregate({x["reel"]: x["note"] for x in recs if x["note"]})
        try:
            creator, cerr, ccost, cusage = creator_job(user, profiles.get(user, {}), recs, counts, k, a.max_usd, out)
        except CapReached:
            print(f"cap reached before the creator step of @{user}")
            break
        ctot += ccost
        if creator:
            profile, flags = G.finalize(counts, creator, profiles.get(user, {}).get("bio") or "", {x["reel"]: x["note"] for x in recs if x["note"]})
        else:
            profile, flags = {"niche_creator": None}, counts["flags"] + [f"creator step failed: {cerr}"]
        json.dump({"counts": counts, "creator": creator, "profile": profile, "flags": flags},
                  open(os.path.join(out, f"{user}_RESULT.json"), "w"), indent=1, ensure_ascii=False)
        parts.append(report(user, acts.get(user), recs, counts, creator, flags, profile, ccost, cusage))
        print(f"@{user}: {sum(1 for x in recs if x['note'])}/{len(recs)} reels ok · spent so far ${STATE['spent']:.4f}")

    ok = [x for x in all_recs if x["note"]]
    # cost model from this run: reel cost = a + b * seconds (least squares), then applied to the real DB lengths
    n = len(ok)
    proj = ""
    if n >= 5:
        xs, ys = [x["duration_s"] for x in ok], [x["cost"] for x in ok]
        mx, my = sum(xs) / n, sum(ys) / n
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sum((x - mx) ** 2 for x in xs) or 1)
        a0 = my - b * mx
        cavg = ctot / max(1, len(parts))
        rows = store.sql("""select m.activity, count(distinct r.username) c, count(*) n, coalesce(sum(r.duration_s),0) s
                            from public.scrape_reels r join public.creator_metrics m using (username)
                            where r.reel_rank between 1 and 12 group by m.activity""")
        proj = "\n".join(f"- **{r['activity']}**: {r['c']} creators, {r['n']} reels -> ~${a0 * r['n'] + b * float(r['s']) + cavg * r['c']:.2f}"
                         for r in rows)
        proj = (f"Measured: reel call ≈ ${a0:.5f} + ${b:.6f} × seconds; creator call ≈ ${cavg:.4f}.\n" + proj)
    cached = sum(((x["usage"] or {}).get("prompt_tokens_details") or {}).get("cached_tokens") or 0 for x in ok)
    prompt = sum((x["usage"] or {}).get("prompt_tokens") or 0 for x in ok)
    head = [f"# Gemini pilot {os.path.basename(out)} ({G.PROMPT_VERSION}, {G.MODEL}, flex)", "",
            f"Reel calls ok {n}/{len(all_recs)} · creator calls {len(parts)} · **spent ${STATE['spent']:.4f}** (cap ${a.max_usd})",
            f"Prompt tokens {prompt:,}, of which cached {cached:,} · wall time {time.time() - t0:.0f} s with {WORKERS} parallel calls", "", "Projection with these real costs:", proj, ""]
    open(os.path.join(out, "REPORT.md"), "w").write("\n".join(head) + "\n" + "\n".join(parts))
    print("\n".join(head))
    print("report:", os.path.join(out, "REPORT.md"))


if __name__ == "__main__":
    main()

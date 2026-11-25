"""PAID comparison of ways to send a creator's reels to Gemini (docs/ai-profile-spec.md, v3 prompt):
  1x12  one reel per request (the v3 baseline; reused from an earlier run when given --baseline)
  10in1 the latest 10 reels in ONE request (Gemini takes at most 10 videos per request)
  6+6   two requests of 6 reels
  4x3   three requests of 4 reels
For every method: request sizes, errors, time, real cost; reel-by-reel agreement with the 1x12 notes; and the final
creator profile next to the baseline's. Hard spend cap across the whole run.

  ../instagram-scraper/.venv/bin/python ai/gemini_compare.py --users a,b --baseline state/ai_pilot/<run> --max-usd 0.50 --yes
"""
import argparse
import base64
import collections
import datetime as dt
import json
import os
import sys
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
import gemini_pilot as P  # noqa: E402
from gemini_test import key  # noqa: E402
from igs.store import Store  # noqa: E402
import urllib.request  # noqa: E402
import urllib.error  # noqa: E402

METHODS = {"10in1": [10], "5+5": [5, 5], "6+6": [6, 6], "4x3": [4, 4, 4], "8in1": [8], "4+4": [4, 4], "6in1": [6]}
SUBSETS = [10, 8, 6]   # 1xN = the first N one-per-request notes from the baseline (no new video calls)
IDS = [f"R{i}" for i in range(1, 13)]
P.RESERVE = 0.02   # held back per running call (8 parallel x 0.02 must stay under the cap); real calls cost ~$0.001-0.008

GROUP_PROMPT = G.REEL_PROMPT.replace(
    "You analyse ONE Instagram reel from an Indian account, for a brand-matching product. Watch every frame\n"
    "and listen to the whole audio before answering. Report only what this reel shows or says.",
    "You analyse SEVERAL Instagram reels from one Indian account, for a brand-matching product. Each reel comes as a\n"
    "details block (R1, R2, ...) followed by its video. Analyse EACH reel on its own, as if it were the only one: never\n"
    "carry a person's role, a product, a language or a topic from one reel into another. Watch every frame and listen\n"
    "to the whole audio of each reel before answering. Return exactly one note per reel, in the given order, with its\n"
    "reel id. Report only what that reel shows or says.")
assert GROUP_PROMPT != G.REEL_PROMPT, "prompt opening changed; update GROUP_PROMPT"
NOTE = G.obj(dict({"reel": G.E(IDS)}, **G.REEL_SCHEMA["properties"]))
GROUP_SCHEMA = G.obj({"notes": {"type": "array", "items": NOTE}})


def post(body, k):
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", method="POST",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + k, "Content-Type": "application/json",
                                          "X-Title": "Brand Deal Matcher compare"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=240) as r:   # retried by P.call on timeout
            return json.loads(r.read()), time.time() - t, None
    except urllib.error.HTTPError as e:
        return None, time.time() - t, f"HTTP {e.code}: {e.read().decode()[:400]}"
    except Exception as e:  # noqa: BLE001
        return None, time.time() - t, f"{type(e).__name__}: {e}"


P.post = post   # P.call() uses it (retries + cap)


def group_job(user, bio, reels, k, cap, out, tag):
    ids = [f"R{r['reel_rank']}" for r in reels]
    content = [{"type": "text", "text": f"Account context: @{user} · bio: {G.scrub(bio) or '(empty)'}\n\n"
                                        f"{len(reels)} reels follow: {', '.join(ids)}."}]
    size = 0
    for rid, r in zip(ids, reels):
        details = G.reel_details(rid, r, user, bio).split("\n", 2)[2]   # drop the per-reel account context lines
        raw = open(os.path.join(HERE, r["video_file"]), "rb").read()
        size += len(raw)
        content += [{"type": "text", "text": details},
                    {"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + base64.b64encode(raw).decode()}}]
    content.append({"type": "text", "text": f"Now write one note for each of {', '.join(ids)}."})
    body = G.body(GROUP_PROMPT, content, GROUP_SCHEMA, "reel_notes", "flex")
    body["messages"][0] = P.system_msg(GROUP_PROMPT)
    body["max_tokens"] = 600 * len(reels) + 2000
    body["usage"] = {"include": True}
    req_mb = len(json.dumps(body)) / 1e6
    resp, secs, err, cost = P.call(body, k, cap)
    notes, perr = {}, err
    if not err:
        parsed, perr = P.parse(resp)
        if parsed:
            for n in parsed["notes"]:
                if n["reel"] in ids and n["reel"] not in notes:
                    for person in n.get("people", []):
                        person["look"] = G.clean_look(person.get("look"))
                    notes[n["reel"]] = {x: v for x, v in n.items() if x != "reel"}
            missing = [i for i in ids if i not in notes]
            extra = [n["reel"] for n in parsed["notes"] if n["reel"] not in ids]
            if missing or extra:
                perr = f"missing {missing} extra {extra}"
    rec = {"tag": tag, "ids": ids, "video_mb": round(size / 1e6, 2), "request_mb": round(req_mb, 2),
           "seconds": round(secs, 1), "cost": cost, "error": perr, "usage": (resp or {}).get("usage"),
           "provider": (resp or {}).get("provider"), "service_tier": (resp or {}).get("service_tier")}
    json.dump(dict(rec, notes=notes, raw=resp), open(os.path.join(out, f"{user}_{tag}.json"), "w"), indent=1,
              ensure_ascii=False)
    return rec, notes


def run_method(user, method, profile, reels, k, cap, out):
    sizes = METHODS[method]
    use = reels[:sum(sizes)]
    groups, i = [], 0
    for s in sizes:
        groups.append(use[i:i + s])
        i += s
    bio = profile.get("bio") or ""
    with ThreadPoolExecutor(len(groups)) as ex:
        res = list(ex.map(lambda g: group_job(user, bio, g[1], k, cap, out, f"{method}_g{g[0] + 1}"), enumerate(groups)))
    notes = {}
    for _, n in res:
        notes.update(n)
    recs = [r for r, _ in res]
    creator = cerr = None
    ccost = 0.0
    if len(notes) >= G.MIN_ANALYSED_REELS:
        fake = [{"reel": rid, "note": notes[rid]} for rid in sorted(notes, key=lambda x: int(x[1:]))]
        counts = G.aggregate(notes)
        creator, cerr, ccost, _ = P.creator_job(user, profile, fake, counts, k, cap, out, tag=f"_{method}")
        profile_out, flags = G.finalize(counts, creator, profile.get("bio") or "", notes) if creator else ({}, counts["flags"])
    else:
        counts, profile_out, flags = G.aggregate(notes) if notes else None, {}, ["too few reels; creator step skipped"]
    return {"method": method, "groups": recs, "notes": notes, "counts": counts, "creator": creator,
            "profile": profile_out, "flags": flags, "creator_cost": ccost, "creator_error": cerr,
            "cost": sum(r["cost"] for r in recs) + ccost, "seconds": max((r["seconds"] for r in recs), default=0)}


def load_baseline(path, user):
    notes = {}
    for rid in IDS:
        f = os.path.join(path, f"{user}_{rid}.json")
        if os.path.exists(f):
            d = json.load(open(f))
            if d.get("note"):
                notes[rid] = d["note"]
    res = os.path.join(path, f"{user}_RESULT.json")
    if len(notes) < G.MIN_ANALYSED_REELS or not os.path.exists(res):
        return None
    r = json.load(open(res))
    if not r.get("creator"):
        return None
    reel_costs = {rid: json.load(open(os.path.join(path, f"{user}_{rid}.json")))["cost"] for rid in notes}
    cost = sum(reel_costs.values()) + json.load(open(os.path.join(path, f"{user}_creator.json")))["cost"]
    return {"method": "1x12", "notes": notes, "counts": r["counts"], "creator": r["creator"], "profile": r["profile"],
            "flags": r["flags"], "cost": cost, "groups": [], "seconds": None, "reused": path, "reel_costs": reel_costs}


def reel_view(n):
    owner = next((p for p in n["people"] if p["role"] == "account_owner"), None)
    return {"category": n["category"], "format": n["format"], "made_for": n["made_for"],
            "owner_gender": owner["gender"] if owner else "none", "owner_on_screen": n["owner_on_screen"],
            "owner_speaks": n["owner_speaks"], "languages": ",".join(sorted(n["spoken_languages"])) or "-",
            "products": ",".join(sorted({f"{p['type']}/{p['level']}" for p in n["products"] if p["type"]})) or "-",
            "reposted": n["is_reposted"], "brand_safe": n["brand_safe"]}


def creator_view(m):
    c, k, p = m["counts"] or {}, m["creator"] or {}, m["profile"] or {}
    return {"account_type": k.get("account_type"), "category": c.get("category"), "secondary": c.get("secondary"),
            "creator_gender": c.get("creator_gender"), "languages": sorted(c.get("spoken_languages") or {}),
            "niche_creator": p.get("niche_creator"), "role": k.get("creator_role"),
            "audience": k.get("audience_gender_estimate"), "stated": k.get("target_audience_stated"),
            "collabs": k.get("brand_collabs"), "own_products": k.get("sells_own_products"),
            "services": k.get("offers_services"), "content_mix": c.get("content_mix")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", required=True)
    ap.add_argument("--baseline", help="pilot run folder with 1x12 results to reuse")
    ap.add_argument("--max-usd", type=float, required=True)
    ap.add_argument("--methods", help="only these grouped methods, comma-separated (skips the 1xN subsets)")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args()
    if not a.yes:
        raise SystemExit("paid run: add --yes")
    if a.methods:
        keep = [m.strip() for m in a.methods.split(",")]
        for m in list(METHODS):
            if m not in keep:
                del METHODS[m]
        SUBSETS.clear()
    users = [u.strip() for u in a.users.split(",")]
    store, k = Store(), key()
    out = os.path.join(STATE, "ai_compare", dt.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    os.makedirs(out, exist_ok=True)
    profiles = {r["username"]: r for r in store.select("scrape_profiles", {
        "select": "username,bio,bio_links,profile_pic_file", "username": f"in.({','.join(users)})"})}
    results = collections.defaultdict(dict)
    t0 = time.time()
    for user in users:
        reels = store.select("scrape_reels", {"select": "*", "username": f"eq.{user}", "reel_rank": "gte.1",
                                              "order": "reel_rank.asc"})[:12]
        base = load_baseline(a.baseline, user) if a.baseline else None
        if not base:   # run the 1x12 baseline now (one reel per request)
            bio = profiles[user].get("bio") or ""
            try:
                with ThreadPoolExecutor(8) as ex:
                    recs = list(ex.map(lambda r: P.reel_job(user, r, k, a.max_usd, out, bio), reels))
            except P.CapReached:
                print("cap reached during the baseline of", user)
                break
            recs.sort(key=lambda x: int(x["reel"][1:]))
            notes = {x["reel"]: x["note"] for x in recs if x["note"]}
            counts = G.aggregate(notes)
            creator, _, ccost, _ = P.creator_job(user, profiles[user], recs, counts, k, a.max_usd, out)
            prof, flags = G.finalize(counts, creator, profiles[user].get("bio") or "", notes) if creator else ({}, counts["flags"])
            base = {"method": "1x12", "notes": notes, "counts": counts, "creator": creator, "profile": prof,
                    "flags": flags, "cost": sum(x["cost"] for x in recs) + ccost, "groups": [],
                    "seconds": max(x["seconds"] for x in recs), "errors": [x["error"] for x in recs if x["error"]],
                    "reel_costs": {x["reel"]: x["cost"] for x in recs if x["note"]}}
        results[user]["1x12"] = base
        for nsub in SUBSETS:   # fewer reels, one per request: reuse the baseline notes, redo only the creator step
            sub = {rid: base["notes"][rid] for rid in IDS[:nsub] if rid in base["notes"]}
            counts = G.aggregate(sub)
            fake = [{"reel": rid, "note": n} for rid, n in sub.items()]
            try:
                creator, cerr, ccost, _ = P.creator_job(user, profiles[user], fake, counts, k, a.max_usd, out, tag=f"_1x{nsub}")
            except P.CapReached:
                break
            prof, flags = G.finalize(counts, creator, profiles[user].get("bio") or "", sub) if creator else ({}, counts["flags"])
            results[user][f"1x{nsub}"] = {"method": f"1x{nsub}", "notes": sub, "counts": counts, "creator": creator,
                                          "profile": prof, "flags": flags, "groups": [], "derived": True,
                                          "cost": sum(base["reel_costs"].get(r, 0) for r in sub) + ccost}
        for m in METHODS:
            try:
                results[user][m] = run_method(user, m, profiles[user], reels, k, a.max_usd, out)
            except P.CapReached:
                print(f"cap reached at @{user} {m}; stopping (spent ${P.STATE['spent']:.4f})")
                break
            print(f"@{user} {m}: {len(results[user][m]['notes'])} notes · ${results[user][m]['cost']:.4f} · "
                  f"spent ${P.STATE['spent']:.4f}")
        json.dump(results[user], open(os.path.join(out, f"{user}_COMPARE.json"), "w"), indent=1, ensure_ascii=False,
                  default=str)

    # ---- report
    L = [f"# Method comparison {os.path.basename(out)} (prompt {G.PROMPT_VERSION}, {G.MODEL}, flex)", "",
         f"Spent this run **${P.STATE['spent']:.4f}** (cap ${a.max_usd}) · wall {time.time() - t0:.0f} s", ""]
    agree_tot = collections.defaultdict(lambda: [0, 0])
    for user, ms in results.items():
        base = ms["1x12"]
        L += [f"## @{user}", "", "| method | requests (video MB / request MB / s) | errors | reels back | cost |", "|---|---|---|---|---|"]
        for m, r in ms.items():
            req = "; ".join(f"{g['video_mb']}/{g['request_mb']}/{g['seconds']}" for g in r.get("groups", [])) or (
                "baseline reused" if r.get("reused") else "first reels of the baseline" if r.get("derived") else "single reels")
            errs = "; ".join(g["error"] for g in r.get("groups", []) if g["error"]) or "; ".join(r.get("errors", [])) or "-"
            L.append(f"| {m} | {req} | {errs[:200]} | {len(r['notes'])} | ${r['cost']:.4f} |")
        L += ["", "Reel-by-reel agreement with 1x12 (same reel, same field):", "",
              "| method | " + " | ".join(reel_view(next(iter(base["notes"].values()))).keys()) + " |",
              "|---|" + "---|" * len(reel_view(next(iter(base["notes"].values()))))]
        for m, r in ms.items():
            if m.startswith("1x"):
                continue
            row = []
            for fld in reel_view(next(iter(base["notes"].values()))):
                same = tot = 0
                for rid, n in r["notes"].items():
                    if rid in base["notes"]:
                        tot += 1
                        same += reel_view(n)[fld] == reel_view(base["notes"][rid])[fld]
                agree_tot[(m, fld)][0] += same
                agree_tot[(m, fld)][1] += tot
                row.append(f"{same}/{tot}")
            L.append(f"| {m} | " + " | ".join(row) + " |")
        L += ["", "Creator profile by method:", "", "| field | " + " | ".join(ms) + " |", "|---|" + "---|" * len(ms)]
        views = {m: creator_view(r) for m, r in ms.items()}
        for fld in views["1x12"]:
            vals = [json.dumps(views[m][fld], ensure_ascii=False) for m in ms]
            mark = "" if len(set(vals)) == 1 else " ⚠️"
            L.append(f"| {fld}{mark} | " + " | ".join(vals) + " |")
        L += ["", "Differences reel by reel (method: reel field baseline -> method):"]
        for m, r in ms.items():
            if m.startswith("1x"):
                continue
            for rid, n in sorted(r["notes"].items(), key=lambda x: int(x[0][1:])):
                if rid not in base["notes"]:
                    continue
                a_, b_ = reel_view(base["notes"][rid]), reel_view(n)
                diff = [f"{f}: {a_[f]} -> {b_[f]}" for f in a_ if a_[f] != b_[f]]
                if diff:
                    L.append(f"- {m} {rid}: " + "; ".join(diff))
        L.append("")
    L += ["## Total agreement with 1x12 (all creators)", "", "| field | " + " | ".join(METHODS) + " |", "|---|" + "---|" * len(METHODS)]
    flds = ["category", "format", "made_for", "owner_gender", "owner_on_screen", "owner_speaks", "languages",
            "products", "reposted", "brand_safe"]
    for f in flds:
        cells = []
        for m in METHODS:
            s, t = agree_tot[(m, f)]
            cells.append(f"{s}/{t} ({100 * s / t:.0f}%)" if t else "-")
        L.append(f"| {f} | " + " | ".join(cells) + " |")
    order = ["1x12"] + [f"1x{n}" for n in SUBSETS] + list(METHODS)
    L += ["", "## Creator profile: fields equal to 1x12, and cost", "",
          "| method | reels used | requests per creator | fields equal to 1x12 (all creators) | avg cost / creator | 685 active (projection) |",
          "|---|---|---|---|---|---|"]
    for m in order:
        rows = [ms for ms in results.values() if m in ms]
        if not rows:
            continue
        same = tot = 0
        for ms in rows:
            if m == "1x12" or not ms[m].get("creator"):
                continue
            b, v = creator_view(ms["1x12"]), creator_view(ms[m])
            for f in b:
                if f == "content_mix":
                    continue
                tot += 1
                same += b[f] == v[f]
        n_reels = 12 if m == "1x12" else int(m[2:]) if m.startswith("1x") else sum(METHODS[m])
        n_req = n_reels if m.startswith("1x") else len(METHODS[m])
        avg = sum(ms[m]["cost"] for ms in rows) / len(rows)
        L.append(f"| {m} | {n_reels} | {n_req} | {'base' if m == '1x12' else f'{same}/{tot}'} | ${avg:.4f} | ~${avg * 685:.2f} |")
    open(os.path.join(out, "COMPARE.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:4]))
    print("report:", os.path.join(out, "COMPARE.md"))


if __name__ == "__main__":
    main()

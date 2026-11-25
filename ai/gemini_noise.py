"""Free analysis: how much of the difference between 1x12 (one reel per request) and 4x3 (three requests of 4 reels)
is just Gemini's run-to-run noise. Reads two gemini_compare.py runs that both hold "1x12" and "4x3" per creator,
recomputes every count with the CURRENT code (aggregate/finalize), and reports agreement for:
  noise 1x12  : run A 1x12 vs run B 1x12   (same method twice)
  noise 4x3   : run A 4x3  vs run B 4x3
  1x12 vs 4x3 : all four cross pairs, averaged
  ../instagram-scraper/.venv/bin/python ai/gemini_noise.py state/ai_compare/<runA> state/ai_compare/<runB>
"""
import collections
import glob
import json
import os
import sys

BDM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # Brand Deal Matcher repo
AI_DIR = os.path.dirname(os.path.abspath(__file__))                          # this folder (ai/)
# The scraper repo holds the data side: igs/store.py (Supabase "database" project, its .env) and media/ (videos).
SCRAPER = os.environ.get("SCRAPER_DIR") or os.path.join(os.path.dirname(BDM), "instagram-scraper")
HERE = SCRAPER        # video_file / profile_pic_file paths in the DB are relative to the scraper repo
STATE = os.path.join(AI_DIR, "state")   # every AI output (raw answers, logs, cut videos); gitignored
sys.path.insert(0, AI_DIR)
import gemini_dryrun as G  # noqa: E402


def reel_view(n):
    owner = next((p for p in n["people"] if p["role"] == "account_owner"), None)
    fam = sorted({G.LANG_FAMILY.get(l, l) for l in n["spoken_languages"] if l != "other"}
                 | {"other:" + x.lower() for x in n.get("other_language_names", [])})
    return {"category": n["category"], "format": n["format"], "made_for": n["made_for"],
            "owner_gender": owner["gender"] if owner else "none", "owner_on_screen": n["owner_on_screen"],
            "owner_speaks": n["owner_speaks"], "language_family": ",".join(fam) or "-",
            "products": ",".join(sorted({f"{p['type']}/{p['level']}" for p in n["products"] if p["type"]})) or "-",
            "promoted_brand": "yes" if any(p["level"] == "promoted" and not p["own_brand"] and p["brand"].strip()
                                           for p in n["products"]) else "no"}


def creator_view(m):
    counts = G.aggregate(m["notes"])
    prof, _ = G.finalize(counts, m["creator"])
    return {"account_type": prof["account_type"], "category": prof["category"], "secondary": prof["secondary"],
            "creator_gender": prof["creator_gender"], "language_families": sorted(prof["language_families"]),
            "main_language": max(prof["language_families"], key=prof["language_families"].get) if prof["language_families"] else None,
            "niche_status": prof["niche_status"], "role": prof["creator_role"], "audience": prof["audience_gender_estimate"],
            "own_products": prof["sells_own_products"], "services": prof["offers_services"],
            "brand_collabs": prof["brand_collabs"], "in_india": prof["in_india"]}


def load(run):
    out = {}
    for f in glob.glob(os.path.join(run, "*_COMPARE.json")):
        d = json.load(open(f))
        user = os.path.basename(f)[:-len("_COMPARE.json")]
        out[user] = {m: d[m] for m in ("1x12", "4x3") if m in d and d[m].get("creator") and len(d[m]["notes"]) >= 6}
    return out


def agree(pairs, view_fn, reel=False):
    tot = collections.defaultdict(lambda: [0, 0])
    diffs = []
    for user, a, b in pairs:
        if reel:
            for rid in sorted(set(a["notes"]) & set(b["notes"]), key=lambda r: int(r[1:])):
                va, vb = view_fn(a["notes"][rid]), view_fn(b["notes"][rid])
                for f in va:
                    tot[f][1] += 1
                    tot[f][0] += va[f] == vb[f]
        else:
            va, vb = view_fn(a), view_fn(b)
            for f in va:
                tot[f][1] += 1
                tot[f][0] += va[f] == vb[f]
                if va[f] != vb[f]:
                    diffs.append(f"@{user} {f}: {va[f]} | {vb[f]}")
    return tot, diffs


def main():
    A, B = load(sys.argv[1]), load(sys.argv[2])
    users = sorted(set(A) & set(B))
    groups = {
        "noise 1x12 (A vs B)": [(u, A[u]["1x12"], B[u]["1x12"]) for u in users if "1x12" in A[u] and "1x12" in B[u]],
        "noise 4x3 (A vs B)": [(u, A[u]["4x3"], B[u]["4x3"]) for u in users if "4x3" in A[u] and "4x3" in B[u]],
        "1x12 vs 4x3 (4 cross pairs)": [(u, X[u]["1x12"], Y[u]["4x3"]) for u in users for X in (A, B) for Y in (A, B)
                                        if "1x12" in X[u] and "4x3" in Y[u]],
    }
    L = [f"# Noise check: {os.path.basename(sys.argv[1].rstrip('/'))} vs {os.path.basename(sys.argv[2].rstrip('/'))}",
         f"creators: {', '.join('@' + u for u in users)} · counts recomputed with prompt/code {G.PROMPT_VERSION}", ""]
    for title, reel, fn in (("Reel level (same reel, same field)", True, reel_view),
                            ("Creator level (final profile)", False, creator_view)):
        res = {g: agree(p, fn, reel) for g, p in groups.items()}
        fields = list(next(iter(res.values()))[0])
        L += [f"## {title}", "", "| field | " + " | ".join(groups) + " |", "|---|" + "---|" * len(groups)]
        for f in fields:
            cells = []
            for g in groups:
                s, t = res[g][0][f]
                cells.append(f"{s}/{t} ({100 * s / t:.0f}%)" if t else "-")
            L.append(f"| {f} | " + " | ".join(cells) + " |")
        tot = {g: (sum(v[0] for v in res[g][0].values()), sum(v[1] for v in res[g][0].values())) for g in groups}
        L.append("| **all fields** | " + " | ".join(f"**{s}/{t} ({100 * s / t:.0f}%)**" for s, t in tot.values()) + " |")
        if not reel:
            for g in groups:
                if res[g][1]:
                    L += ["", f"Differences, {g}:"] + [f"- {d}" for d in res[g][1]]
        L.append("")
    print("\n".join(L))
    open(os.path.join(sys.argv[2], "NOISE.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()

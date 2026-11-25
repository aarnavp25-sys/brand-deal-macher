"""Free: score every method's answers against the hand-checked truth sheet (state/ai_truth/truth_v1.json).
Reads gemini_compare.py runs (each <user>_COMPARE.json holds all methods), recomputes counts with the CURRENT code,
and writes TRUTH.md next to the last run.
  ../instagram-scraper/.venv/bin/python ai/gemini_truth.py state/ai_truth/truth_v1.json state/ai_compare/<run1> [<run2> ...]
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


def reel_answer(n):
    owner = next((p for p in n["people"] if p["role"] == "account_owner"), None)
    return {"category": n["category"], "made_for": n["made_for"],
            "owner_gender": owner["gender"] if owner else "none", "owner_on_screen": n["owner_on_screen"],
            "promoted_brand": "yes" if any(p["level"] == "promoted" and not p["own_brand"] and p["brand"].strip()
                                           for p in n["products"]) else "no"}


def creator_answer(m):
    counts = G.aggregate(m["notes"])
    prof, _ = G.finalize(counts, m["creator"])
    return {"account_type": prof["account_type"], "category": prof["category"], "creator_gender": prof["creator_gender"],
            "niche_status": prof["niche_status"], "role": prof["creator_role"], "audience": prof["audience_gender_estimate"],
            "own_products": prof["sells_own_products"], "services": prof["offers_services"],
            "brand_collabs": prof["brand_collabs"], "in_india": prof["in_india"]}


def main():
    truth = json.load(open(sys.argv[1]))
    runs = sys.argv[2:]
    score = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))   # method -> field -> [ok, n]
    wrong = collections.defaultdict(list)
    for i, run in enumerate(runs, 1):
        for f in sorted(glob.glob(os.path.join(run, "*_COMPARE.json"))):
            user = os.path.basename(f)[:-len("_COMPARE.json")]
            if user not in truth:
                continue
            for method, m in json.load(open(f)).items():
                if not m.get("creator") or len(m.get("notes", {})) < G.MIN_ANALYSED_REELS:
                    continue
                label = f"{method} (run {i})"
                for rid, n in m["notes"].items():
                    t = truth[user]["reels"].get(rid, {})
                    a = reel_answer(n)
                    for fld, ok_vals in t.items():
                        if ok_vals is None:
                            continue
                        score[label]["reel:" + fld][1] += 1
                        if a[fld] in ok_vals:
                            score[label]["reel:" + fld][0] += 1
                        else:
                            wrong[label].append(f"@{user} {rid} {fld}: said {a[fld]}, right {ok_vals}")
                a = creator_answer(m)
                for fld, ok_vals in truth[user]["creator"].items():
                    score[label]["creator:" + fld][1] += 1
                    if a[fld] in ok_vals:
                        score[label]["creator:" + fld][0] += 1
                    else:
                        wrong[label].append(f"@{user} CREATOR {fld}: said {a[fld]}, right {ok_vals}")
    order = sorted(score, key=lambda l: (l.split()[0][:2] != "1x", l))
    fields = sorted({f for s in score.values() for f in s}, key=lambda f: (not f.startswith("creator"), f))

    def pct(s, n):
        return f"{s}/{n} ({100 * s / n:.0f}%)" if n else "-"
    L = ["# Accuracy against the hand-checked truth sheet", "",
         f"truth: {sys.argv[1]} · runs: " + ", ".join(f"run {i} = {os.path.basename(r.rstrip('/'))}" for i, r in enumerate(runs, 1)),
         "Counts recomputed with code " + G.PROMPT_VERSION + ". Languages not scored (owner checks them by ear).", "",
         "| method | creator-level right | reel-level right | all |", "|---|---|---|---|"]
    for lab in order:
        c = [v for k, v in score[lab].items() if k.startswith("creator")]
        r = [v for k, v in score[lab].items() if k.startswith("reel")]
        cs, cn = sum(x[0] for x in c), sum(x[1] for x in c)
        rs, rn = sum(x[0] for x in r), sum(x[1] for x in r)
        L.append(f"| {lab} | {pct(cs, cn)} | {pct(rs, rn)} | **{pct(cs + rs, cn + rn)}** |")
    L += ["", "## By field", "", "| field | " + " | ".join(order) + " |", "|---|" + "---|" * len(order)]
    for fld in fields:
        L.append(f"| {fld} | " + " | ".join(pct(*score[lab][fld]) for lab in order) + " |")
    L += ["", "## Every wrong answer"]
    for lab in order:
        L += ["", f"### {lab} ({len(wrong[lab])})"] + [f"- {w}" for w in wrong[lab]]
    out = os.path.join(runs[-1], "TRUTH.md")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L[:6 + len(order)]))
    print("written:", out)


if __name__ == "__main__":
    main()

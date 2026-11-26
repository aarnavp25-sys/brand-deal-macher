"""Check the AI matching end to end on real brands (spends OpenRouter credit: about $0.01 per brand).

  python3 web/db/ai_check.py [brand numbers...] [--base http://localhost:3000]

Each brand chats through the real API as an anonymous visitor, then the script prints what the AI understood about
the product, every creator shown (group, score, verdict, why, idea, evidence) and the real cost from llm_calls, and
checks the rules automatically:
  - every creator shown matches the brand's creator gender, languages and buyer rule;
  - creators outside the chosen categories are there only because they already show the product (2+ reels);
  - every "strong" creator has product or related-item reels behind it;
  - no shop / personal account is shown.
The rest (are these the right creators?) is judged by reading the output, using the AI profiles, never captions.
"""
import http.cookiejar, json, pathlib, sys, time, urllib.error, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
ENV = dict(l.strip().split("=", 1) for l in (HERE.parent / ".env.local").read_text().splitlines() if "=" in l and not l.startswith("#"))
SB, SECRET = ENV["NEXT_PUBLIC_SUPABASE_URL"].rstrip("/"), ENV["SUPABASE_SECRET_KEY"]
args = sys.argv[1:]
BASE = args[args.index("--base") + 1] if "--base" in args else "http://localhost:3000"
picked = [int(a) for a in args if a.isdigit()]

BRANDS = {
    1: ("TickTock Co", {
        "about": "TickTock Co is a small Delhi label making minimal analog wrist watches for men, steel and leather straps, sold online.",
        "product": "Men's minimal analog watch", "customer_gender": "men", "creator_gender": "male", "languages": ["*"]}),
    2: ("Achaar Ghar", {
        "about": "Achaar Ghar is a family kitchen in Indore. My mother makes mango, lemon and mixed vegetable pickles in mustard oil and we ship across India.",
        "product": "Mango pickle 500g jar", "customer_gender": "all", "creator_gender": "any", "languages": ["hindi"]}),
    3: ("Mitti & Wick", {
        "about": "Mitti & Wick is two friends in Jaipur pouring soy wax candles with desi scents like mogra and chai masala, sold on our website and Instagram.",
        "product": "Mogra candle gift box", "customer_gender": "women", "creator_gender": "female", "languages": ["hindi", "english"]}),
    4: ("Veda Roots", {
        "about": "Veda Roots makes ayurvedic grooming for men in Kochi: beard oil, charcoal face wash and a bhringraj hair serum, sold online.",
        "product": "Charcoal face wash for men", "customer_gender": "men", "creator_gender": "male", "languages": ["*"]}),
    5: ("Chhota Kurta", {
        "about": "Chhota Kurta is a small Ahmedabad label stitching cotton ethnic wear for kids aged 1 to 8: kurtas, lehengas and festive sets.",
        "product": "Festive cotton kurta set for kids", "customer_gender": "women", "creator_gender": "female", "languages": ["*"]}),
}


def rest(path):
    r = urllib.request.Request(SB + path, headers={"apikey": SECRET, "Authorization": f"Bearer {SECRET}"})
    return json.load(urllib.request.urlopen(r, timeout=60))


class Client:
    def __init__(self):
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def post(self, path, body):
        r = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST",
                                   headers={"Content-Type": "application/json", "Origin": BASE})
        try:
            return json.load(self.op.open(r, timeout=180))
        except urllib.error.HTTPError as e:
            return {"_error": e.code, "_body": e.read().decode()[:300]}


def lang_ids(r):
    ids = set()
    for raw in list((r["languages"] or {}).keys()) + [r["main_language"]]:
        if not raw:
            continue
        k = raw.replace("other:", "")
        ids |= {"hindi"} if k in ("hindi_urdu", "hindi") else {"hindi", "english"} if k == "hinglish" else {k}
    return ids


def run(n):
    name, b = BRANDS[n]
    print(f"\n{'=' * 100}\n{name}: {b['product']}  (buyers {b['customer_gender']}, creator {b['creator_gender']}, languages {b['languages']})")
    c = Client()
    sid = c.post("/api/searches", {})["id"]
    j = c.post(f"/api/searches/{sid}/answer", {"step": "about", "value": b["about"]})
    j = c.post(f"/api/searches/{sid}/answer", {"step": "product", "value": b["product"]})
    picks = next((m.get("suggests") for m in reversed(j["messages"]) if m.get("step") == "categories"), None) or ["*"]
    for m in j["messages"][-3:]:
        print("  Kindred:", m["text"])
    c.post(f"/api/searches/{sid}/answer", {"step": "categories", "value": picks})
    c.post(f"/api/searches/{sid}/answer", {"step": "customer_gender", "value": b["customer_gender"]})
    t = time.time()
    j = c.post(f"/api/searches/{sid}/answer", {"step": "creator", "value": {"creator_gender": b["creator_gender"], "languages": b["languages"]}})
    took = time.time() - t
    if "_error" in j:
        print("  ERROR", j)
        return False
    row = rest(f"/rest/v1/brand_searches?select=brief,results&id=eq.{sid}")[0]
    res, brief = row["results"], row["brief"]
    info = brief.get("product_info", {})
    print(f"  AI product: {info.get('product_type')} | for {info.get('made_for')} | words {info.get('product_words')} | related {info.get('related_words')}")
    print(f"  categories: {info.get('category')} + {info.get('close_categories')}  (source: {info.get('source')}) | chosen: {brief['categories']}")
    calls = rest(f"/rest/v1/llm_calls?select=kind,ok,cost,tokens_in,tokens_out&search_id=eq.{sid}")
    cost = sum(float(x["cost"] or 0) for x in calls)
    print(f"  AI calls: {len(calls)} ({sum(1 for x in calls if x['ok'])} ok), cost ${cost:.4f}, final step took {took:.1f}s")
    if res.get("version") != 4:
        print("  NOT AI RESULTS:", res.get("notice"))
        return False

    shown = [(g, m) for g, ms in res["groups"].items() for m in ms]
    print(f"  checked {res['checked']}, hidden as weak {res['hidden_weak']}, shown {len(shown)}")
    users = ",".join(m["username"] for _, m in shown) or "x"
    q = "select=username,account_type,category,creator_gender,languages,main_language,audience_gender_est&username=in.(" + ",".join(f'"{u}"' for u in users.split(",")) + ")"
    db = {r["username"]: r for r in rest(f"/rest/v1/creator_overview?{q}")}
    ok = True
    for g, m in shown:
        r = db[m["username"]]
        bad = []
        if r["account_type"] not in ("creator", "professional"):
            bad.append("not a creator")
        if b["creator_gender"] != "any" and r["creator_gender"] != b["creator_gender"]:
            bad.append("wrong gender")
        langs = [l for l in b["languages"] if l != "*"]
        ids = lang_ids(r)
        if langs and ids and not (ids & set(langs)):
            bad.append("wrong language")
        if b["customer_gender"] == "men" and r["audience_gender_est"] == "women":
            bad.append("audience women")
        if b["customer_gender"] == "women" and r["audience_gender_est"] == "men":
            bad.append("audience men")
        if r["category"] not in brief["categories"] and brief["categories"] and len(m["product_reels"]) < 2:
            bad.append("outside chosen categories without product evidence")
        if m["verdict"] == "strong" and not (m["product_reels"] or len(m["related_reels"]) >= 2):
            bad.append("strong without evidence")
        ok &= not bad
        print(f"  [{g:11}] {m['score']:3} {m['verdict']:6} @{m['username']:<26} {r['category'] or '-':<22} prod {len(m['product_reels'])} rel {len(m['related_reels'])}"
              f"{'  !! ' + ', '.join(bad) if bad else ''}")
        print(f"        why:  {m['why']}\n        idea: {m['idea']}")
    print(f"  RULES {'PASS' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    results = [run(n) for n in (picked or sorted(BRANDS))]
    print(f"\n{sum(results)}/{len(results)} brands passed the automatic rules")

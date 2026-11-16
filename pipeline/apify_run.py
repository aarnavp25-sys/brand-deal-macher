"""Run an Apify actor with a hard spend cap and save its dataset.

usage: APIFY_TOKEN=... python3 apify_run.py <actor> <input.json> <out.json> <max_usd>
The cap is passed as maxTotalChargeUsd, so Apify stops charging at that amount.
"""
import json, sys, time, urllib.request, os

API = "https://api.apify.com/v2"
TOKEN = os.environ["APIFY_TOKEN"]


def call(method, path, body=None, tries=5):
    for attempt in range(tries):
        req = urllib.request.Request(API + path, method=method,
                                     data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except (OSError, json.JSONDecodeError) as e:
            # Never retry the POST that starts a run: a retry could start (and bill) a second run.
            if method == "POST" or attempt == tries - 1:
                raise
            print(f"  network error ({e}); retrying", flush=True)


def main(actor, input_path, out_path, max_usd, existing_run=None):
    inp = json.load(open(input_path))
    if existing_run:  # re-attach to a run that is already going (e.g. after a crash)
        run = call("GET", f"/actor-runs/{existing_run}")["data"]
    else:
        run = call("POST", f"/acts/apify~{actor}/runs?maxTotalChargeUsd={max_usd}", inp)["data"]
    rid = run["id"]
    print(f"started {actor} run {rid}, cap ${max_usd}", flush=True)
    while run["status"] in ("READY", "RUNNING"):
        run = call("GET", f"/actor-runs/{rid}?waitForFinish=60")["data"]
        print(f"  status={run['status']} items={run.get('stats', {}).get('resultCount') or '?'}"
              f" usd={run.get('usageTotalUsd')}", flush=True)
    items, offset, size = [], 0, 100  # small pages: profile items are large and big pages timed out
    while True:
        page = call("GET", f"/datasets/{run['defaultDatasetId']}/items?offset={offset}&limit={size}")
        items += page
        if len(page) < size:
            break
        offset += size
    json.dump({"actor": actor, "run_id": rid, "input": inp, "status": run["status"],
               "cost_usd": run.get("usageTotalUsd"), "items": items}, open(out_path, "w"), ensure_ascii=False)
    print(f"done status={run['status']} items={len(items)} cost=${run.get('usageTotalUsd')}")


if __name__ == "__main__":
    main(*sys.argv[1:6])

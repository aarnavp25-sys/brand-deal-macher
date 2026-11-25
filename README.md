# brand-deal-macher

Brand Deal Matcher helps small and homegrown Indian brands find growing Instagram
creators (1K–100K followers) that fit their product, ranked by product fit, reel
reach, engagement and consistency, with a reason for every match.

Status: prototype. Creator data is collected with Apify, stored in Supabase, and
browsed through a local admin dashboard and a local demo website.

## Layout

| Path | What it is |
|---|---|
| `pipeline/` | Apify scraping (`round.py`, spend caps), filtering, metrics, keyword classification, Supabase load (`process.py`), taxonomy (`taxonomy.py`), LLM labels (`llm_classify.py`, test set `gold20.py`) |
| `admin/` | Local admin dashboard: browse, filter, edit creators, categories, products, scrape runs |
| `supabase/` | Database schema (`migrations/`, in order), Edge Function `api` (matching + security), `deploy.py` |
| `demo/` | Demo website: a brand describes its product and gets matched creators (calls the Edge Function) |
| `ai/` | AI creator profiles from reel videos (Gemini via OpenRouter): `gemini_run.py` (full run, resumable, spend cap), prompts and counting rules in `gemini_dryrun.py`, pilot / method-comparison / accuracy tools |
| `kindred_board/` | Kindred Board: local admin dashboard of the final creators with their AI profiles and per-reel notes |
| `docs/` | Product design, data collection and matching, AI profile spec (`ai-profile-spec.md`): how it works and why |
| `context/` | Session journal |

## Run locally

Python 3, standard library only.

```bash
cp admin/.env.example admin/.env   # fill in SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY
python3 admin/server.py            # admin dashboard  -> http://127.0.0.1:8787
python3 demo/server.py             # demo website     -> http://127.0.0.1:8788
```

A scraping round: `python3 pipeline/round.py --account acc1 --dry-run` (plan, no spend), then `--yes`.
LLM labels: `python3 -m pip install -r pipeline/requirements.txt`, then
`python3 pipeline/llm_classify.py estimate | test | batch --yes | collect`.
Each script documents its commands at the top of the file.

AI profiles and Kindred Board read the final creator data through the separate scraper repo (`../instagram-scraper`:
its `igs/store.py`, `.env` and `media/`), so run them with its Python environment from this folder:

```bash
../instagram-scraper/.venv/bin/python kindred_board/server.py          # Kindred Board -> http://127.0.0.1:8791
../instagram-scraper/.venv/bin/python ai/gemini_dryrun.py --selftest    # counting rules (no cost)
../instagram-scraper/.venv/bin/python ai/gemini_run.py --activity active --max-usd 11 --yes   # paid run, resumable
```

AI outputs (raw answers, logs, cut videos) go to `ai/state/`, which is gitignored. Never commit `.env` files; they are
gitignored.

## Team

| Name | Role |
|---|---|
| Aarnav Mathakiya ([@aarnavp25-sys](https://github.com/aarnavp25-sys)) | Project lead: product, data pipeline, backend |
| Shreyash ([@shreyashp25](https://github.com/shreyashp25)) | UI/UX and frontend: looks after the design of the demo website and the admin dashboard |

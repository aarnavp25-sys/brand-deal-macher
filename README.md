# brand-deal-macher

Brand Deal Matcher helps small and homegrown Indian brands find growing Instagram
creators (1K–100K followers) that fit their product, ranked by product fit, reel
reach, engagement and consistency, with a reason for every match.

Status: prototype. Creator data is collected with Apify, stored in Supabase, and
browsed through a local admin dashboard and a local demo website.

## Layout

| Path | What it is |
|---|---|
| `pipeline/` | Apify scraping (with spend caps), filtering, metrics, keyword classification, Supabase load. Schema in `schema.sql`, taxonomy in `taxonomy.py` |
| `admin/` | Local admin dashboard: browse, filter, edit creators, categories, products, scrape runs |
| `supabase/` | Edge Function `api` (matching + security), database migrations, `deploy.py` |
| `demo/` | Demo website: a brand describes its product and gets matched creators (calls the Edge Function) |
| `docs/` | Product design, data collection and matching: how it works and why |
| `context/` | Session journal |

## Run locally

Python 3, standard library only.

```bash
cp admin/.env.example admin/.env   # fill in SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY
python3 admin/server.py            # admin dashboard  -> http://127.0.0.1:8787
python3 demo/server.py             # demo website     -> http://127.0.0.1:8788
```

Pipeline commands are documented at the top of `pipeline/apify_run.py` and
`pipeline/process.py` (need `APIFY_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`).

Never commit `.env` files; they are gitignored.

## Team

| Name | Role |
|---|---|
| Aarnav Mathakiya ([@aarnavp25-sys](https://github.com/aarnavp25-sys)) | Project lead: product, data pipeline, backend |
| Shreyash ([@shreyashp25](https://github.com/shreyashp25)) | UI/UX and frontend: looks after the design of the demo website and the admin dashboard |

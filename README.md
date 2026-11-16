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
| `demo/` | Local demo website: a brand describes its product and gets matched creators |
| `docs/product-design.md` | Product design and the reasons behind it |
| `context/`, `CLAUDE.md` | Session journal and working notes |

## Run locally

Python 3, standard library only.

```bash
cp admin/.env.example admin/.env   # fill in SUPABASE_URL and SUPABASE_SERVICE_KEY
python3 admin/server.py            # admin dashboard  -> http://127.0.0.1:8787
python3 demo/server.py             # demo website     -> http://127.0.0.1:8788
```

Pipeline commands are documented at the top of `pipeline/apify_run.py` and
`pipeline/process.py` (need `APIFY_TOKEN`, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`).

Never commit `.env` files; they are gitignored.

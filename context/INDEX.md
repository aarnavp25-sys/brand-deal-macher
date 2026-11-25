# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-24 (S-022).

> **Auto-compact is OFF** (`~/.claude/settings.json`). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** (user's order 2026-11-18; hooks block it). **Nothing from S-021/S-022 is committed.**
> **Do not build or install anything without the user's explicit "bana"** (S-022). Research/reading is fine.
> **Index work goes to schema `work` only; `public` is the frozen original** (S-022).
> **Budget:** LLM $8.5 total, OpenRouter key ~$0.95 left. Apify: acc1–acc19 all ≈ empty (resets 2026-12-09…22).
> Ask before every paid step. Project = `~/Documents/ojt/brand deal matcher/` (`cd` there first); network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`. Servers: admin 8787, demo 8788, index 8789.

## Where things stand

Brand Deal Matcher helps small Indian brands find Instagram creators. The prototype is live (Vercel site → Render
forwarder → Supabase Edge Function, main DB 3,229 shown creators); it was not touched in S-022. Its results are weak
because discovery used name/bio search and the collab snowball and the AI read captions only (S-021 audit, docs).

The new direction is a username index plus our own scraper. The index lives in a separate Supabase project
"database" (ref rhaqbnvmyjcwgeosltaf, Singapore). In S-022 `index/collect.py` collected usernames from the Apify
`social_developer` India index: 85 runs, $26.83, 1,322 usernames. The actor scans its list from row 0 and dies on any
slow page, so city filters and ranked sorts never work and late-alphabet categories rarely finish (docs). After a
hand review of every name and the user's choices, **961 creators** remain in 9 categories (Fashion 244, Food 189,
Beauty 187, Fitness 87, Parenting 86, Travel 81, Tech 40, Auto 37, Jewellery 10). 361 were removed into
`index_removed` with full backups (shops/brands 173, foreign 85, mobile shops 40, pages 33, clothing shops 18, car
pages 12). 43 salon/gym accounts are kept with review "local business: decide at scrape". Full names were removed
from the whole index DB. The index numbers (likes, views, engagement, city) are unreliable; only usernames and rough
followers are trusted. `index/plan.json` still has 9 categories / 678 usernames to collect when new Apify keys come.
The whole index was cloned into schema `work` (a third Supabase project was refused: free plan limit 2), with a
local backup in index/backups/2026-11-24_1711/.

The own scraper is researched and planned but **not built**: the user stopped building ("abhi kuchh bana mat") after
curl_cffi was installed in scraper/.venv and scraper/probe.py saved test pages. ~21 logged-out Instagram requests
showed every required field is reachable: profile page (followers, following, total posts via og:description, bio,
bio links, verified, private, 12 grid types), reels-tab JSON (views, likes, comments, pinned; hidden likes come as a
fake 3), next-page JSON, reel JSON (date, caption, alt, music, collab, tags, location, video URL, DASH audio URL,
length, thumbnail). Cloudflare WARP in proxy mode works (new IPv6 per reconnect; Instagram returns full data).
Per creator ≈ 14–15 requests, ≈1.15 MB; 961 creators ≈ 14K requests; time ≈ 24 h on one IP, ≈ 4–8 h on 3 IPs.

Credits: the advisor will not give GCP; Vultr or "other" credits are possible. Recommendation given: AWS (~$150) if
Bedrock opens on that account (Nova video, Transcribe, Claude Haiku), else Vultr (server/storage/Whisper) +
OpenRouter (Gemini/Qwen Omni/Haiku with one key). Gemini cost for 1,000 creators × 12 reels: ≈$8 (2.5 Flash-Lite) to
≈$44 (3.8 Flash; batch ≈$22). Session ended after the Vultr-vs-AWS answer.

## Continue from here

1. Wait for the user's "bana", then build `scraper/` per the plan (docs "Own scraper…" sections): fetch/parse/limiter/
   store/run, writes to `work.scrape_profiles`, `work.scrape_reels`, `work.scrape_log` only; WARP proxy + home +
   hotspot lanes; step 0 (parser on scraper/raw/probe), step 1 (10 creators), step 2 (100), step 3 (all).
2. When credits arrive: check Bedrock model access first (AWS), then the 50-reel model test on gold creators.
3. New Apify keys → `python3 index/collect.py plan` then `run --max-usd X --reserve 0.05 --yes` (writes to `public`
   today; switch collect.py to `work` before the next run).
4. Ask before committing index/ and scraper/ (scraper/.venv, raw/, state/, index/backups/ are gitignored).
5. Pending reminders: rotate the Render API key, acc14–19 Apify keys and the Supabase access token (pasted in chat);
   demo video due 2026-11-28; UptimeRobot.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall; refused budget/WhatsApp | docs/product-design.md; 001 (S-001) |
| Deployment (Render forwarder, Vercel, PROXY_SECRET) | docs (Public API → Deployment); 001 (S-021) |
| Apify actors audit, why results are poor | docs ("Apify actors: what they return"); 001 (S-020, S-021) |
| social_developer index: order, timeouts, sortBy, costs | docs ("Discovery alternatives"); 001 (S-022) |
| Username index: plan.json, rules, removals, 9 categories | docs ("Creator username index"); index/; 001 (S-022) |
| Working copy schema `work`, backups | docs ("Working copy: schema `work`"); 001 (S-022) |
| Own scraper: page/JSON fields, requirements, network/WARP | docs ("Own scraper: …" sections); scraper/probe.py; 001 (S-022) |
| Keep-check design (salon case; not active) | docs ("Keep check at scrape time"); 001 (S-022) |
| Credits: GCP/AWS/Vultr/OpenRouter, Gemini costs, models | 001 (S-020, S-021, S-022) |
| Pipeline, metrics, deletions, account check | docs (Pipeline); 001 (S-016–S-020) |
| Search rules, eval, LLM prompt v10 | docs (Matching, LLM notes); pipeline/; 001 (S-017–S-019) |
| Accounts, keys by name, live URLs, index keys acc14–19 | ~/Documents/ojt/PRIVATE-GUIDE.md |

## Open decisions

1. Build the scraper now ("bana")? Lanes: WARP + home + hotspot (free); Docker WARP containers (needs install).
2. Credits to request: AWS (~$150) vs Vultr (~$100) + OpenRouter (~$50); check Bedrock access first.
3. AI model after the 50-reel test (Gemini 3.8 Flash vs Qwen3.8 Omni Flash vs MiMo-V2.6-Pro vs Nova; Haiku for profiles).
4. Salon/gym accounts (43): decide after scraping; city column (drop now or keep as "index estimate"?).
5. Fill the remaining 678 usernames (needs ~3–4 Apify keys) or stop at 961.
6. Commit index/ and scraper/; older: final site name, UptimeRobot, Shreyash's access.

## Ruled out

- Budget fields, WhatsApp flow, creators >100K (S-001); live scraping at search time; city as a requirement (S-010/S-014).
- AWS Bedrock for the old LLM pipeline (blocked, S-009–S-020); Kimi K3, Mem0, Jev Router (S-017).
- Name/bio search and collab snowball for discovery; copying Modash/Qoruz data; login-based scraping (S-021).
- social_developer with city filters or ranked sortBy; parallel runs on it (S-022).
- Cloudflare Workers as proxy, free open proxy lists (iplocate etc.), Tor, cloud datacenter IPs for Instagram (S-022).
- A third Supabase project (free limit) (S-022). Claude as git co-author.

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat (A.txt) | 001 |
| S-002–S-008 | 2026-11-16 → 17 | Context system, Apify research, pipeline, admin/demo, GitHub | 001 |
| S-009–S-012 | 2026-11-17 → 19 | Demo fixes, Edge Function API, rounds 12–37, private guide | 001 |
| S-013–S-019 | 2026-11-19 → 21 | Brand-first matching, OpenRouter, prompt v10, eval, account check | 001 |
| S-020 | 2026-11-21 → 22 | Credits form; why results fail; Vercel/Render CLIs | 001 |
| S-021 | 2026-11-22 → 23 | Deployed; Apify data audit; discovery research; index/ built; scraper test | 001 |
| S-022 | 2026-11-23 → 24 | Index collected (961 kept), `work` clone, scraper research/probes, WARP test, credits | 001 |

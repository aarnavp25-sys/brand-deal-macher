# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-25 (S-023).

> **Auto-compact is OFF** (`~/.claude/settings.json`). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** (user's order 2026-11-18; hooks block it in both repos).
> **Do not build or install anything without the user's explicit "bana" / "banana shuru karo"**; research is fine.
> **Final creator DB = Supabase project "database", schema `public` (848 creators).** Schema `legacy` there = old index
> (read-only). The old main DB (yqaducvspzrqokcqwlga, 3,229) is legacy too, but the live site still reads it.
> Two repos: this one (`brand deal matcher/`, PUBLIC) and `~/Documents/ojt/instagram-scraper/` (PRIVATE; scraper, final
> data code, dashboard). `cd` into the right one first; network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`.

## Where things stand

Brand Deal Matcher helps small Indian brands find Instagram creators (10K–100K). The old prototype (Vercel → Render →
Supabase Edge Function on the old main DB, 3,229 creators found by Apify name search) is still live but its data is weak.

In S-023 (2026-11-24 → 25) we built our own logged-out Instagram scraper as a separate private repo,
`~/Documents/ojt/instagram-scraper/` (README + docs/instagram-notes.md + docs/metrics.md explain everything). It uses
curl_cffi through "lanes": 10 Docker WARP containers (127.0.0.1:1081–1090), the Mac's WARP app (40000, proxy mode) and the
hostel Wi-Fi (direct, slow, pauses 30 min on a block). It scraped all 961 index usernames: profile, latest 12 non-pinned
reels with full detail, pinned reels, grid posts, every reel's 360p mp4 + m4a, cover images and profile pictures (~20 GB
in instagram-scraper/media/, only on this Mac). Blocks were few (20 in ~11,400 requests) and handled by IP rotation.

After cleanup the final set is **848 creators** (113 removed with reasons and JSON backups: 57 not found, 28 now >100K,
16 not creators after manual review, 7 private, 5 restricted). 10,093 latest reels; 685 active / 163 inactive under the
user's rule (inactive = newest non-pinned reel older than 45 days). `public.creator_metrics` holds per-creator numbers
(median views, reach, engagement with an `est.` flag, comment rate, reels/week, viral, collab share, content_format
own_audio/music/mixed, fewer_than_12); content_topic is empty until AI. Metrics are written only when Python and an
independent SQL computation agree (0 differences). A read-only admin dashboard runs at http://127.0.0.1:8791
(`instagram-scraper/dashboard/server.py`); the old dashboards 8787 and 8789 were stopped on the user's order.

The "database" Supabase project was reorganised at the end of S-023: final tables in `public` (scrape_profiles,
scrape_reels, creator_metrics, scrape_status, scrape_runs, scrape_log, index_*), old index in read-only `legacy`, `work`
dropped; backup in instagram-scraper/state/backups/2026-11-25_before_reorg/. Everything was re-verified after the move.

Credits: only Vultr is available; the user submitted $215 on the OJT portal (GPU for Whisper + Qwen-VL, Serverless
Inference, Archival Object Storage, a VPS, buffer). Nothing is approved yet. OpenRouter key has ~$0.95.

## Continue from here

1. Ask the user what next; likely candidates: (a) when Vultr credits arrive, a 50-reel test of Whisper large-v3 + an open
   vision model on gold creators, then content_topic; (b) review the remaining creators for personal accounts like the
   31 reviewed in S-023; (c) integrate the final DB into this repo's matching/API and switch the live site.
2. Decide fareeha.ganie (active, but all collabs South African).
3. Back up instagram-scraper/media (20 GB) — single copy on the Mac.
4. Refresh later: `cd ~/Documents/ojt/instagram-scraper && .venv/bin/python scrape.py run --users … --yes`, then
   `scrape.py metrics`; Docker Desktop + `cd warp-docker && docker compose up -d` first.
5. Reminders: rotate Render API key, Apify keys acc14–19 and the Supabase access token (pasted in chat); demo video due
   2026-11-28; UptimeRobot.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall; refused budget/WhatsApp | docs/product-design.md; 001 (S-001) |
| Old pipeline, matching, LLM prompt, eval, deployment | docs/data-and-matching.md; 001 (S-016–S-021) |
| Apify actors audit; social_developer index; username index | docs/data-and-matching.md; 001 (S-020–S-022) |
| Own scraper: requirements, lanes, WARP/Docker, hostel IP, IP pool limit | instagram-scraper/README.md, docs/instagram-notes.md; 002 (S-023) |
| Logged-out page/JSON fields, not-found/restricted markers, doc_ids | instagram-scraper/docs/instagram-notes.md; 002 |
| Steps 0–3, blocks, bugs found and fixed, audit | instagram-scraper/docs/instagram-notes.md; 002 |
| Metric definitions, content_format, checks | instagram-scraper/docs/metrics.md; 002 |
| Removed creators (97 + 16), inactive rule | 002; backups in index/backups/2026-11-25_* |
| Supabase "database" layout (public final, legacy old) | instagram-scraper/README.md; 002 |
| Vultr credits ($215) breakdown and reason text | 002 (S-023) |
| Accounts, keys by name, live URLs, project refs | ~/Documents/ojt/PRIVATE-GUIDE.md |

## Open decisions

1. Next main track: AI analysis on Vultr (after approval) vs personal-account review of the rest vs site integration.
2. fareeha.ganie: keep or remove (likely South African).
3. Media backup target (external drive / cloud) for 20 GB.
4. When integrating: move the final data into the main project or point the app at the "database" project.
5. Older: final site name, UptimeRobot, Shreyash's access.

## Ruled out

- Budget fields, WhatsApp flow, creators >100K (S-001); live scraping at search time; city as a requirement.
- Name/bio search and collab snowball for discovery; copying Modash/Qoruz data; login-based scraping (S-021).
- social_developer with city filters or ranked sortBy (S-022); a third Supabase project (free limit).
- Cloud/datacenter IPs, GitHub Actions (GitHub terms), free proxy lists, Tor for scraping (S-022/S-023).
- More than ~11 Docker WARP exits (BLR pool has ~12 /64s) (S-023).
- AWS/GCP credits (only Vultr offered); Claude as git co-author.

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat (A.txt) | 001 |
| S-002–S-008 | 2026-11-16 → 17 | Context system, Apify research, pipeline, admin/demo, GitHub | 001 |
| S-009–S-012 | 2026-11-17 → 19 | Demo fixes, Edge Function API, rounds 12–37, private guide | 001 |
| S-013–S-019 | 2026-11-19 → 21 | Brand-first matching, OpenRouter, prompt v10, eval, account check | 001 |
| S-020 | 2026-11-21 → 22 | Credits form; why results fail; Vercel/Render CLIs | 001 |
| S-021 | 2026-11-22 → 23 | Deployed; Apify data audit; discovery research; index/ built; scraper test | 001 |
| S-022 | 2026-11-23 → 24 | Index collected (961 kept), `work` clone, scraper research/probes, WARP test | 001 |
| S-023 | 2026-11-24 → 25 | Own scraper repo; 961 scraped; 848 final; metrics + dashboard 8791; Supabase reorganised; Vultr $215 | 002 |

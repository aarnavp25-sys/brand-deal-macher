# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-26 (S-024).

> **Auto-compact is OFF** (`~/.claude/settings.json`). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** (user's order 2026-11-18; hooks block it in both repos).
> **Do not build or install anything without the user's explicit "bana" / "banana shuru karo"**; research is fine.
> **Never use reel captions or hashtags** for AI profiles, and not when checking results either (user, 2026-11-26).
> **OpenRouter has a key limit AND a workspace daily budget** (resets 05:30 IST): check both before any paid run.
> Two repos: this one (`brand deal matcher/`, GitHub PUBLIC) and `~/Documents/ojt/instagram-scraper/` (PRIVATE, scraper
> only). `cd` into the right one first; network git needs `-c credential.helper= -c credential.helper='!gh auth git-credential'`.

## Where things stand

The product is named **Kindred** (user, 2026-11-25; live URLs still say brand-deal-matcher). It helps small Indian
brands find Instagram creators (10K–100K). The live prototype (Vercel → Render → Supabase Edge Function) still runs on
the OLD main DB (3,229 creators, legacy) and the user's demo was on the morning of 2026-11-26 with that site.

The final creator data is the 848 creators in Supabase project "database", schema `public`, collected by the private
scraper repo (S-023). In S-024 (2026-11-25 → 26) every one of the **685 active creators got an AI profile from their
reel videos**: Gemini 3.1 Flash Lite via OpenRouter (flex tier) watched the latest 12 non-pinned reels with audio, in
three requests of 4 reels, chosen by a paid method comparison scored against a hand-checked truth sheet (creator level
100%). The AI writes facts per reel; code counts the creator facts (category = subject, comedy/dance as the second
category, Lifestyle for > 5 real categories, gender and life context only from the account owner, every spoken
language, niche only for one-topic creators, collabs from reel evidence, "expert" only with a stated credential).
Result: 662 profiled, 23 stopped as not creators (salons, shops, brands, repost pages), 0 failed, $8.80; 139 flagged for
review. Results are in tables `creator_ai` (json + flat columns) and `reel_ai`, view `creator_overview`. Everything is
explained in `docs/ai-profile-spec.md`.

The AI code (`ai/`) and the admin dashboard **Kindred Board** (`kindred_board/`, http://127.0.0.1:8791; AI columns,
filters, per-reel notes; non-creators hidden) were moved into this repo on the user's order ("scraper mein sirf
scraper"); they read the scraper repo's `igs/store.py`, `.env`, `media/` and are run with its `.venv`. AI outputs are
in `ai/state/` (gitignored). Commits 0f67cc3, 0a5f6a3 here and 1257bfe in the scraper repo are local only, not pushed.

The new data is NOT yet used by matching or the website. A per-brand matching design was discussed (hard filters →
relevance gate → per-brand score → embeddings → Haiku review → 3 columns; adjacency for "never promoted but fits";
audience-persona idea) but nothing is built.

## Continue from here

1. Ask how the demo went and what next. Likely: build matching on `creator_overview` (the design in S-024 / the
   matching section of `docs/data-and-matching.md`), then switch the live site to the "database" project.
2. Ask before pushing: this repo is PUBLIC (no keys or creator usernames in the pushed files; data is gitignored).
3. Review list: 139 flagged creators and the 23 stopped ones on Kindred Board (decide whether salon business accounts
   count as creators); the user's language check of the 5 pilot creators.
4. Small fixes: the PROGRESS denominator in `ai/gemini_run.py`; @trivago_expedition_'s missing reel (compress and
   redo); set an OpenRouter key limit again (it showed none after the run).
5. Reminders: rotate Render API key, Apify keys acc14–19, Supabase token; back up `instagram-scraper/media` (20 GB);
   Vultr $215 request still pending; UptimeRobot.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall; refused budget/WhatsApp | docs/product-design.md; 001 (S-001) |
| Old pipeline, matching rules R1–R9, eval, deployment | docs/data-and-matching.md; 001 (S-016–S-021) |
| Own scraper, lanes, WARP, 848 final creators, metrics | instagram-scraper/README.md, docs/; 002 (S-023) |
| AI creator profiles: rules, method choice, run, platform limits | docs/ai-profile-spec.md; 002 (S-024) |
| Method comparison numbers, truth sheet, noise check | 002 (S-024); ai/state/ai_compare/, ai/state/ai_truth/ |
| Kindred Board, creator_ai / reel_ai / creator_overview | README.md, docs/ai-profile-spec.md; 002 (S-024) |
| Name Kindred, website flow plan, Vultr / OpenRouter model research | 002 (S-024) |
| Per-brand matching design for the new data, failure cases | 002 (S-024) (discussion only) |
| Vultr credits ($215) breakdown | 002 (S-023) |
| Accounts, keys by name, live URLs, project refs | ~/Documents/ojt/PRIVATE-GUIDE.md |

## Open decisions

1. Next track: matching on the new data + site switch vs review of flagged creators vs inactive 163.
2. Push both repos (this one is public).
3. Salon / studio business accounts: keep stopped or treat as creators.
4. Audience-persona field (why people follow a creator) and comment scraping (research only so far).
5. Site name rollout to Kindred (domain, URLs); older: UptimeRobot, Shreyash's access, media backup target.

## Ruled out

- Budget fields, WhatsApp flow, creators >100K (S-001); live scraping at search time; city as a requirement; city /
  location in AI profiles (S-024).
- Captions and hashtags as AI input or as evidence when checking (S-024).
- Haiku for video (no video/audio input); 12 videos in one request (Gemini max 10); fewer than 12 reels (worse niche
  and collab calls); body type, skin colour, "married", price level as AI fields (S-024).
- Name/bio search and collab snowball for discovery; copying Modash/Qoruz data; login-based scraping (S-021).
- Cloud/datacenter IPs, GitHub Actions, free proxies, Tor for scraping; > ~11 Docker WARP exits (S-022/S-023).
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
| S-023 | 2026-11-24 → 25 | Own scraper repo; 961 scraped; 848 final; metrics + dashboard; Supabase reorganised; Vultr $215 | 002 |
| S-024 | 2026-11-25 → 26 | Name Kindred; Gemini video AI profiles for 685 active ($8.80); Kindred Board; AI moved here | 002 |

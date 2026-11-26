# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-26 (S-025).

> **Auto-compact is OFF** (`~/.claude/settings.json`). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** (user's order 2026-11-18; hooks block it in both repos).
> **Do not build or install anything without the user's explicit go**; research is fine. **No LLM call / OpenRouter
> credit without the user's yes** (2026-11-26: "Abhi OpenRouter se kuch bhi credits use mat karna").
> **Never use reel captions or hashtags** for AI profiles or when checking results (user, 2026-11-26).
> **This repo is PUBLIC:** no keys and no creator usernames in pushed files (journal included). Scan before every push.
> **Deploy:** push to GitHub only; the user deploys on Vercel himself (memory deploy-via-github). Never `vercel deploy`.
> Two repos: this one (`brand deal matcher/`) and `~/Documents/ojt/instagram-scraper/` (PRIVATE, scraper only). Network
> git needs `-c credential.helper= -c credential.helper='!gh auth git-credential'`.

## Where things stand

The product is **Kindred**: small Indian brands find Instagram creators (10K–100K). The final creator data is the 848
creators in Supabase project "database" (ref rhaqbnvmyjcwgeosltaf), 662 with AI profiles from their 12 latest reels
(S-024), of which 598 count as creators on the site. Per-reel notes (`reel_ai`) hold topic, format, products on camera,
owner on screen / speaking and sponsored signs.

In S-025 (2026-11-26) the brand-facing website was built in **`web/`** (Next.js 16 + Supabase, everything on Vercel, no
Render). How it works and why is in **`docs/website.md`**; setup, env vars and Vercel steps in `web/README.md`. Today it
is: landing page → "Find creators" → a **conversation** (Kindred reacts to the brand's words, short bubbles with typing
pauses, tap or type) with **5 questions** (brand, product, creator categories with a keyword-guessed pre-pick, who buys
it, creator gender + languages, with a live "N creators fit" count) → results = **top 20 by Kindred Score** (`lib/rank.ts`,
code only, no LLM: product relevance leads; creators with no link to the product and portfolio/showcase pages never reach
the top 20). **No sign-in** for the demo: a private anonymous Supabase session is created when a chat starts; each
visitor sees only their own searches. Security: RLS, server-only secret key, CSRF origin check, input validation, private
photo bucket, headers; `web/db/e2e_test.py` = 92/92 passing.

**AI matching is built but OFF** (`LLM_ENABLED=false`, `LLM_REVIEW=false`): Haiku 5.5 via OpenRouter reads the product
(`lib/product.ts`) and judges who can sell it from 12 reel notes with cited reels checked by code (`lib/review.ts`). One
pilot cost $0.0055; a fix after it (AI counted outfit reels as "watch seen") is untested. The user will explain how he
wants personalisation before it is switched on. OpenRouter has ~$4.64 left, key without a limit.

The session ended after the user checked a watch search on localhost: two wrong creators (a nail-art studio, a
designer's showcase page) were fixed (commit 8be9d22, pushed); the rest of that list was right. The site runs locally
(`cd web && npm run start -- -p 3000` after `npm run build`); it is not deployed yet. Demo video due 2026-11-28.

## Continue from here

1. Ask whether the user deployed on Vercel; if yes, set Supabase Auth site URL / redirect list to the live domain and
   run `python3 web/db/e2e_test.py https://<domain>` against it.
2. Wait for the user's explanation of personalisation before touching the AI. Before switching it on: re-run
   `python3 web/db/ai_check.py` (paid, ~$0.01/brand, ask first) to test the product_seen fix.
3. Open small calls for the user: music-only creators in every language filter (yes today); stop the old Render API;
   update the diagram artifact (it shows 5 questions + anonymous sessions but not the top-20 ranking).
4. Older reminders: push the scraper repo (2 commits ahead); review the 139 flagged / 23 stopped creators; rotate Render
   API key, Apify keys acc14–19, Supabase token; back up `instagram-scraper/media` (20 GB); Vultr $215 request.

## Topic -> file

| Topic | File |
|---|---|
| Website: flow, questions, conversation, filters, ranking, anonymous sessions, security, design | docs/website.md; 002 (S-025) |
| Website setup, env vars, Vercel and Google OAuth steps, tests | web/README.md |
| AI matching (product understanding, review, Kindred Score groups) — built, off | docs/website.md; web/src/lib/review.ts; 002 (S-025) |
| LLM model choice + prices (Haiku 5.5 text, Gemini video) and the 2026-11-20 rules | docs/data-and-matching.md; 002 (S-025) |
| Product idea, brand flow, paywall; refused budget/WhatsApp | docs/product-design.md; 001 (S-001) |
| Old pipeline, matching rules R1–R9, eval, old deployment | docs/data-and-matching.md; 001 (S-016–S-021) |
| Own scraper, lanes, WARP, 848 final creators, metrics | instagram-scraper/README.md, docs/; 002 (S-023) |
| AI creator profiles: rules, method choice, run, platform limits | docs/ai-profile-spec.md; 002 (S-024) |
| Kindred Board, creator_ai / reel_ai / creator_overview | README.md, docs/ai-profile-spec.md; 002 (S-024) |
| Visual request diagram (private artifact) | https://claude.ai/artifact/FNjYEvRJMr9BPb7fq5gvwL; 002 (S-025) |
| Vultr credits ($215) breakdown | 002 (S-023) |
| Accounts, keys by name, live URLs, project refs | ~/Documents/ojt/PRIVATE-GUIDE.md |

## Open decisions

1. How personalisation / the AI should work (user to explain); then 3 columns vs one list, and whether the score's fit
   part may come from AI answers (2026-11-20 rule: the LLM never sets the number).
2. Music-only creators: show for every language (today) or only "Any language".
3. Old Render API (old DB): shut down or keep. Google sign-in and paywall: later.
4. Salon / studio business accounts as creators (S-024); portfolio pages are already out of the top 20.
5. Audience-persona field and comment scraping (research only).

## Ruled out

- Budget fields, WhatsApp flow, creators >100K (S-001); live scraping at search time; city as a requirement; city /
  location in AI profiles (S-024); buyer age / persona / mood in matching (S-025).
- Captions and hashtags as AI input or as evidence when checking (S-024).
- Render as backend, split frontend/backend hosting, CLI deploys to Vercel (S-025); old Vercel project (deleted by user).
- Sign-in screen for the demo; email/password sign-up (S-025).
- Fine-tuning an LLM (no data, no OpenRouter option); Sonnet for live searches (cost) (S-025).
- Haiku for video; 12 videos in one Gemini request; fewer than 12 reels (S-024).
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
| S-025 | 2026-11-26 | Kindred website in web/: conversational 5-question chat, no sign-in, top 20 by Kindred Score; AI built but off | 002 |

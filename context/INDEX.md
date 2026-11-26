# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-26 (S-026).

> **Auto-compact is OFF** (`~/.claude/settings.json`). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** (user's order 2026-11-18; hooks block it in both repos).
> **Do not build or install anything without the user's explicit go**; research is fine. **Paid LLM calls only with the
> user's yes** (the live site's searches are covered by the $1 cap the user set; tests that call the AI are not).
> **Never use reel captions or hashtags** for AI profiles or when checking results (user, 2026-11-26).
> **This repo is PUBLIC:** no keys and no creator usernames in pushed files (journal included). Scan before every push.
> **Deploy:** push to GitHub first, deploy only when the user asks in that session (memory deploy-via-github). Vercel has
> no GitHub connection yet, so deploys are `vercel deploy --prod` from a `git archive HEAD` export in the scratchpad.
> Two repos: this one (`brand deal matcher/`) and `~/Documents/ojt/instagram-scraper/` (PRIVATE, scraper only). Network
> git needs `-c credential.helper= -c credential.helper='!gh auth git-credential'`.

## Where things stand

The product is **Kindred**: small Indian brands find Instagram creators (10K–100K). The final creator data is the 848
creators in Supabase project "database" (ref rhaqbnvmyjcwgeosltaf, Singapore), 662 with AI profiles from their 12 latest
reels, of which 598 count as creators on the site. Per-reel notes (`reel_ai`) hold topic, format, products on camera,
owner on screen / speaking and sponsored signs.

**The website is live: https://kindred-eta-black.vercel.app** (Vercel project `kindred`, team dragon-44d8, Root
Directory `web`, functions in Singapore `sin1`). How it works is in `docs/website.md`; setup in `web/README.md`. Flow:
landing → "Find creators" → chat. The chat first asks the visitor's name once (kept on their anonymous Supabase user,
then "Hey <name>, good to see you again"), then five fixed questions (brand, product, categories with a pre-pick,
buyers, creator gender + languages, live "N creators" count). The chat itself is code, not AI. **AI is ON in
production**: Haiku 5.5 reads the product after question 2, and after question 5 reviews a code shortlist of 40 creators
(4 parallel batches) citing reels; code checks every claim, hides weak fits and sets the Kindred Score (40 sell, 20
evidence, 15 engagement, 10 audience, 10 reach, 5 brand-ready). If the AI fails, the code-only top 20 shows. A search
costs ~$0.0055 and takes ~45 s. **Spend cap: `LLM_TOTAL_CAP_USD=1` over all `llm_calls` ever**; when reached, new chats
get a 503 "demo search budget is used up". Spent so far $0.043 (~$0.96 left); OpenRouter has ~$4.6 in total.
No sign-in: history lives per browser (cookie → anonymous user → `brand_searches` rows). e2e: 102/102 (AI off).

S-026 (2026-11-26) deployed the site for the user's teacher, added the cap, the name question and the region fix
(start chat went from 5–7 s to ~1 s), made a 12-slide deck (artifact Wses6ZjK7eCxJSCZrtoKuV, private, not previewed)
and answered viva questions in chat (scraper internals, WARP IPv6, curl_cffi, why our own scraper, backend per button,
problem statement, market numbers, how the AI and score work). Demo / viva with teachers: 2026-11-28. Everything is
committed and pushed (last code commit d2bd5e9).

## Continue from here

1. Ask how the demo went / whether the user wants changes; if the site is changed, push, then deploy only on their
   ask (export with `git archive HEAD`, keep the `.vercel` link folder, `vercel deploy --prod --scope dragon-44d8`).
2. Google sign-in when the user wants it (~2.5–3 h; user does Google Cloud Console + Supabase provider; code uses
   `linkIdentity` so anonymous searches carry over; handle an already-registered Google account). Not before the demo.
3. Ask the user to add the Vercel GitHub Login Connection so pushes auto-deploy.
4. Older: personalisation of the AI (user to explain); music-only creators in every language filter; stop the old Render
   API; review 139 flagged / 23 stopped creators; rotate Render API key, Apify keys acc14–19, Supabase token; back up
   `instagram-scraper/media` (20 GB); Vultr $215 request.

## Topic -> file

| Topic | File |
|---|---|
| Website: flow, name question, questions, filters, ranking, AI review, score, $1 cap, hosting/region, security | docs/website.md; 002 (S-025, S-026) |
| Website setup, env vars, Vercel steps (region sin1), tests | web/README.md |
| Live deploy details, what failed (git connect, region PATCH, logs retention) | 002 (S-026) |
| Presentation deck + viva explanations (scraper, WARP, curl_cffi, backend, problem, market numbers) | 002 (S-026) |
| LLM model choice + prices (Haiku 5.5 text, Gemini video) and the 2026-11-20 rules | docs/data-and-matching.md; 002 (S-025) |
| Product idea, brand flow, paywall; refused budget/WhatsApp | docs/product-design.md; 001 (S-001) |
| Old pipeline, matching rules R1–R9, eval, Apify audit (why our own scraper) | docs/data-and-matching.md; 001 (S-016–S-022) |
| Own scraper, lanes, WARP, 848 final creators, metrics | instagram-scraper/README.md, docs/; 002 (S-023) |
| AI creator profiles: rules, method choice, run, platform limits | docs/ai-profile-spec.md; 002 (S-024) |
| Kindred Board, creator_ai / reel_ai / creator_overview | README.md, docs/ai-profile-spec.md; 002 (S-024) |
| Visual request diagram (private artifact, outdated) | https://claude.ai/artifact/FNjYEvRJMr9BPb7fq5gvwL; 002 (S-025) |
| Vultr credits ($215) breakdown | 002 (S-023) |
| Accounts, keys by name, live URLs, project refs | ~/Documents/ojt/PRIVATE-GUIDE.md |

## Open decisions

1. Google sign-in: when (recommended after the demo).
2. How personalisation / the AI should work (user to explain); 3 columns vs one list; the LLM never sets the number.
3. Raise the $1 cap after the demo, or switch AI off again.
4. Music-only creators: show for every language (today) or only "Any language".
5. Old Render API (old DB): shut down or keep. Paywall: later. Salon / studio accounts as creators (S-024).

## Ruled out

- Budget fields, WhatsApp flow, creators >100K (S-001); live scraping at search time; city as a requirement; city /
  location in AI profiles (S-024); buyer age / persona / mood in matching (S-025).
- Captions and hashtags as AI input or as evidence when checking (S-024).
- Render as backend, split frontend/backend hosting (S-025); old Vercel project (deleted by user); Vercel region
  `iad1` (S-026: 5–7 s chat start).
- Sign-in screen for the demo; email/password sign-up (S-025).
- Fine-tuning an LLM; Sonnet for live searches (cost) (S-025).
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
| S-026 | 2026-11-26 | Live on Vercel (AI on, $1 total cap), name question, Singapore region; deck; viva explanations | 002 |

# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-22 (S-020).

> **Auto-compact is OFF** (`~/.claude/settings.json`, S-012). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** — no `Co-Authored-By: Claude` or AI line in any commit/PR (user's order 2026-11-18; hooks block it).
> **Another Claude session also works on this repo** (S-020 found 5 deletion commits it made on 2026-11-21 without a
> journal entry). At session start compare `git log` with this INDEX.
> **Budget:** $8.5 total for all LLM work incl. demo day. Spent ~$4.04. OpenRouter key credit limit $5 ($0.96 left) +
> a workspace daily budget (raised by the user in S-019). Get the user's "haa" before every paid step.
> **Layout:** project = `~/Documents/ojt/brand deal matcher/` (own git repo, github.com/aarnavp25-sys/brand-deal-macher,
> PUBLIC, `main`). Workspace root holds stale copies + `PRIVATE-GUIDE.md` (chmod 600) + skills in
> `.claude/skills/context-{read,write}/`. `cd ~/Documents/ojt/"brand deal matcher"` first. Network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`. Type-check the Edge Function:
> `cd supabase/functions/api && npx -y deno@2.1.4 check index.ts`; deploy `python3 supabase/deploy.py function`
> (load `admin/.env` first). Servers: admin 8787, demo 8788. CLIs in `~/.local/bin`: vercel 66.6.0, render 2.38.0
> (both logged in, S-020); `RENDER_API_KEY` in admin/.env; Render MCP registered (loads after restart).
> **After any matching change run `python3 pipeline/eval_search.py`** (16 briefs, rules R0–R9; 0 violations).
> API rate limit 30 searches / 10 min per IP. Debug a search with `"debug": <DEBUG_TOKEN>` (Supabase secret).

## Where things stand

Brand Deal Matcher helps small Indian brands find Instagram creators (1K–100K followers). Working prototype: Python
stdlib pipeline, Supabase DB (`yqaducvspzrqokcqwlga`, free tier), local admin, demo page calling the Edge Function
`api` (the real backend: matching + AI). Code commits since S-018 are not pushed.

**Data.** On 2026-11-21 (21:31–22:11 IST) another session deleted, on the user's order, 2,825 non-shown accounts
(shop/brand pages, fake, organisations, foreign, personal, own shop, review, non-promoting professionals), with full
backups in Supabase Storage and a `removed_creators` skip-list (2,824 usernames) that round.py honours. The DB now
has 3,399 creators; **3,229 are shown in search** (1,510 under 5K followers). @jass.dhingra777 was set to review by
hand in S-020. raw_scrapes (174 files) are intact. Roughly 1 in 5 shown accounts is still not a hireable creator
(S-020 sample of 40), because hashtag scraping brings in personal accounts and services, and the AI reads captions
only (image links expire; images were never stored).

**LLM.** Claude Haiku 5.5 via OpenRouter. ~$0.003 per new search; repeats free 7 days; 400 calls/day cap. If the AI
fails, `/match` returns 503 (never unchecked creators). The user applied for $25 GCP college credits to get a
Gemini key; Gemini must beat or match Haiku on the gold set and the eval before any switch.

**Matching** (`supabase/functions/api/index.ts`; rules R0–R9 in docs/data-and-matching.md "Search rules,
consolidated"): niche = product evidence; category = product's own category + `CAT_NEIGHBOURS`, relevance-gated,
audience-first shortlist; wider reach ≥3K followers; review verdict + field + account enforced in code; gender rule;
local-store city rule. Demo shows field badges and per-column empty messages.

**How the session ended.** The user asked to deploy: backend on Render, frontend on Vercel, UptimeRobot pinging
`/health` every 5 minutes. Both CLIs are installed and logged in, the Render API key is saved and verified, and the
Render MCP is registered. Placeholder names: Vercel `brand-deal-matcher`, Render `brand-deal-matcher-api` (ask the
user before a final name). Deployment has not started: three design questions are unanswered.

## Continue from here

1. Get the user's answers: (1) Render backend = small Python service (`/health` + forwards `/api/match`, `/api/meta`
   to the Supabase Edge Function; recommended) or all matching moved to Render; (2) admin stays local (recommended;
   service key, no login) or online behind a password; (3) Vercel = current demo page or a new Next.js site.
2. Then build: Render service (Python stdlib, `/health`, CORS for the Vercel domain, Supabase URL + anon key as
   env vars), add the Vercel domain to the Edge Function `ALLOWED_ORIGINS`, Vercel static deploy of `demo/` with the
   API base pointing at Render, UptimeRobot HTTP monitor every 5 min on `https://<render>/health`. Test end to end.
3. After deploy: rotate the Render API key (it was pasted in chat); suggest Vercel 2FA; raise the OpenRouter key
   limit; push commits (ask first).
4. Later: Gemini test when GCP credits arrive; December Apify rounds (acc3 2026-12-09) with creator-centric terms and
   thumbnails sent to the AI while links are fresh; stricter account check / human Keep-Remove pass (set aside by
   the user in S-020).

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price-of-deal and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake rule, business-account rule | docs (Pipeline); 001 (S-016, S-017) |
| Account check; review_reason; deletions + removed_creators skip-list | pipeline/account_check.py; docs (Pipeline); 001 (S-018, S-020) |
| Running a scraping round | pipeline/round.py; 001 (S-011, S-015) |
| Taxonomy (16 categories, 82 product types) | pipeline/taxonomy.py; docs (Taxonomy) |
| Search rules R0–R9, neighbours, relevance, audience-first | docs (Matching, "Search rules, consolidated"); 001 (S-018, S-019) |
| Search evaluation; debug token | pipeline/eval_search.py; index.ts; 001 (S-018, S-019) |
| Why results kept failing; captions-only limit | 001 (S-020) |
| OpenRouter workspace budget vs key limit | docs (R0); 001 (S-019) |
| College cloud credits (GCP for Gemini) | 001 (S-020) |
| Deployment plan: Render + Vercel + UptimeRobot; CLIs; Render MCP | 001 (S-020) |
| Creator profile prompt v10; LLM cost; providers | pipeline/llm_classify.py; docs (LLM notes); 001 (S-017, S-018) |
| Jev Router test; Bedrock/Nova/Kimi tests | docs (LLM notes); 001 (S-009, S-010, S-017) |
| Admin dashboard | admin/; 001 (S-008, S-018) |
| Demo page | demo/index.html; 001 (S-009, S-019) |
| Public API, security, rate limit, daily LLM cap | docs (Public API); supabase/deploy.py; index.ts |
| Accounts, keys by name, how to run (private) | ~/Documents/ojt/PRIVATE-GUIDE.md |
| Rounds 1–37, GitHub cleanup, Shreyash, tunnel | 001 (S-003–S-011) |

## Open decisions

1. Render backend shape (thin forwarder vs move matching) — pending.
2. Admin local or online with a password — pending.
3. Vercel: current demo page or a new Next.js site — pending.
4. Final public site name (placeholder now).
5. Raise the OpenRouter key limit; push commits now or later.
6. Stricter account check / human Keep-Remove pass for demo searches (set aside).
7. Repo public or private; unlock price; Shreyash's data access; cleanup of old backup branch and archive folders.

## Ruled out

- Budget-of-deal fields, WhatsApp/concierge flow, creators >100K (001, S-001). Product price level is allowed (S-015).
- Live scraping at search time; "Lifestyle" as a category; city as a requirement (docs; S-010, S-014).
- AWS/Bedrock for the LLM (S-009–S-015, S-017; restated S-020: Bedrock Haiku lacks JSON-schema enforcement).
- Kimi K3; Mem0; Jev Router (S-017). Batching creators per LLM call; temperature 0 on Haiku (S-017).
- Brand AI's categories deciding the category column; review rules as prose only; "own field only"; a
  promotion-signal gate on category/wider columns (S-018). Showing unreviewed results when the AI is down (S-019).
- Keyword-only shop-visit detection; own Instagram scraper; Claude as git co-author (S-009–S-014).

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat (from A.txt) | 001 |
| S-002 | 2026-11-16 | Context system set up | 001 |
| S-003–S-008 | 2026-11-16 → 17 | Apify research, pipeline, rounds 1–11, admin/demo, GitHub | 001 |
| S-009 | 2026-11-17 → 18 | Demo fixes; viva prep; Bedrock model test | 001 |
| S-010 | 2026-11-18 → 19 | Edge Function API; Bedrock blocked; rounds 12–37 → 6,224 creators | 001 |
| S-011–S-012 | 2026-11-19 | Shreyash; tunnel; private guide; auto-compact off | 001 |
| S-013 | 2026-11-19 → 20 | Brand-first matching (3 columns + AI review), OpenRouter, taxonomy 82 | 001 |
| S-014–S-015 | 2026-11-20 | Local shops; $8.5 budget; price level; round.py auto profile | 001 |
| S-016 | 2026-11-20 | Free prep: PII scrub, fake-flag fix, DB hygiene | 001 |
| S-017 | 2026-11-20 | Key in; prompt v5→v10 on paid tests; columns/natural fits/quality; 173 business accounts; Jev rejected | 001 |
| S-018 | 2026-11-20 → 21 | Full profile run; live search; matching rethought (R1–R9, eval); account check; admin | 001 |
| S-019 | 2026-11-21 | Workspace budget stop → 503 fix; audience-first category; demo texts | 001 |
| (other session) | 2026-11-21 | 2,825 non-shown accounts deleted on the user's order, backups + removed_creators (git only) | — |
| S-020 | 2026-11-21 → 22 | Credits form (GCP/Gemini); why results fail; Vercel + Render CLIs and Render MCP connected | 001 |

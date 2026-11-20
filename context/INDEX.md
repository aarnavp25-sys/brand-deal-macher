# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-20 (S-017).

> **Auto-compact is OFF** (`~/.claude/settings.json`, S-012). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** — no `Co-Authored-By: Claude` or AI line in any commit/PR (user's order 2026-11-18; hooks block it).
> **Budget:** $8.5 total for all LLM work incl. demo day (teachers test live). Spent $0.33 so far. Stop and get the
> user's "haa" before every paid step. No accuracy loss for cost.
> **Layout:** project = `~/Documents/ojt/brand deal matcher/` (own git repo, github.com/aarnavp25-sys/brand-deal-macher,
> PUBLIC, `main`). Workspace root holds stale copies + `PRIVATE-GUIDE.md` (private map, chmod 600) + the skills in
> `.claude/skills/context-{read,write}/`. `cd ~/Documents/ojt/"brand deal matcher"` first. Network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`. Type-check the Edge Function:
> `cd supabase/functions/api && npx -y deno@2.1.4 check index.ts`. Deploy: `python3 supabase/deploy.py function`
> (load `admin/.env` into the shell first for `mgmt` SQL). Servers: admin 8787, demo 8788.

## Where things stand

Brand Deal Matcher helps small Indian brands find Instagram creators (1K–100K followers). Working prototype: Python
stdlib pipeline, Supabase DB (`yqaducvspzrqokcqwlga`, free tier), local admin, demo page calling the Edge Function
`api`. `main` is at `0cebbcb` plus the S-017 context commit.

**Data.** 6,224 creators; **5,213 search-visible** (active, not fake). 173 moved to `status='business'` in S-017
(shops, restaurants, colleges, dealers, esports teams by Instagram category; `process.py business_account()`), 553
fake, ~311 review. Mid tier (50K–100K) thin (~316); perfume specialists thin (3 in keyword data). All 13 Apify
accounts empty until the December resets.

**LLM.** Claude Haiku 5.5 through OpenRouter (`anthropic/claude-haiku-5.5`, providers anthropic → azure →
google-vertex only, because the AWS/Bedrock endpoints do not enforce the JSON schema). Key in `admin/.env`
(`OPENROUTER_API_KEY`), key limit $4, used $0.33; account ~$8.17 left. The key is NOT yet in the Supabase secrets,
so live search still runs on keyword-v1 and has no AI brand profile or review. Measured cost ~$0.00064–0.0007 per
creator (11,400 cached + 1,900 uncached input, ~670 out), so the full run is ~$3.3–3.5.

**Creator profile prompt v10** (`pipeline/llm_classify.py`, `PROMPT_VERSION v10-profile-2026-11-20`), built over
paid tests v5→v10 in S-017: products need a named `item` (activity is not a product; gold 18/20), role, credibility,
price level, products_for, values, scope, store visits (venues excluded), settings, natural fits (scene-based
products, e.g. chai on mountain treks or in a hostel room → beverages), content quality 1-10 (+percentile in search),
`creator_type` (creator/professional/celebrity/organization), `takes_promotions` (own-company posts do not count),
`in_india`. `creator_llm` holds v10 rows for the 100 pilot creators only. v10 pilot: watch-list creators (makeup
artist, meme page, coach, esports player, dancer, DJ) visible; foreign accounts, organisations, non-promoting
professionals and shops hidden; 2 borderline cases left.

**Matching** (deployed, `supabase/functions/api/index.ts`; full design in docs/data-and-matching.md "Matching"):
AI brand profile (incl. customer `moments`) → formula score (product, price, brand fit, audience, engagement,
reach, quality, …) → three columns by the user's definitions: **niche** = specialists (product ≥20% of posts or
expert from the field; shop-visit creators for local stores), **category** = general category content, **wider
reach** = big reach + believable fit, ordered by reach-weighted score → AI review (strong/good/weak + ≤20-word
reason + reel idea, owner's view, "can they really promote it?"). Who is hidden: docs "5d". Daily cap 400 paid LLM
calls; 7-day `llm_cache`.

**How the session ended.** The user asked whether Jev Router would be cheaper and as good; `compare` showed Jev
10/13/18 of 20 with 11 cut-off replies at 6x the cost and three different underlying models, Haiku 16/16/19. The
user then asked which would be best "if trained"; answer: Haiku (prompt tuning applies to both; Jev mixes models
and bills reasoning). Waiting on: key limit raised to ~$5 and a yes for the full run.

## Continue from here

1. User raises the OpenRouter key limit to ~$5 and says yes. Then, in the background:
   `python3 pipeline/llm_classify.py run --max-usd 3.8 --yes` (~5,100 creators, ~1 hour; resumable; saves every 10).
2. After it: `python3 pipeline/llm_classify.py estimate` (should be ~0 left), spot-check ~30 random profiles,
   count hidden by reason (foreign/organization/professional/shop) and how many creators each of the 82 product
   types now has (the 40 new types were empty in keyword data).
3. `python3 supabase/deploy.py secrets` (sends `OPENROUTER_API_KEY`), then ~10 demo searches through the live API:
   perfume men ₹1,000 vs ₹10,000, instant tea, masala, mithai shop Jaipur (local store), gym wear, skincare,
   makeup. Check each column against the user's definitions; list weak results to the user.
4. Professionals still visible with "maybe": show the count and the web-check cost (~$0.01–0.02 each) before any
   Google/web check.
5. User: delete the two Bedrock keys in AWS IAM; then update PRIVATE-GUIDE.md (AWS section).
6. After the Apify resets (acc3 2026-12-09; others 2026-12-15/16/17): `round.py` for perfume and the mid tier.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price-of-deal and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake rule, business-account rule | docs/data-and-matching.md (Pipeline); 001 (S-016, S-017) |
| Running a scraping round | pipeline/round.py; 001 (S-011, S-015) |
| Taxonomy (16 categories, 82 product types) | pipeline/taxonomy.py; docs (Taxonomy) |
| Matching: columns, natural fits, quality, review, who is shown | docs (Matching 3–5d); 001 (S-013, S-017) |
| Price level; local shops | docs (Matching 5a, 5b); 001 (S-014, S-015) |
| Creator profile prompt v10, lessons v5→v10 | pipeline/llm_classify.py; docs (LLM notes); 001 (S-017) |
| LLM cost measured, providers, temperature 400, compare | docs (LLM notes); 001 (S-017) |
| Jev Router test; earlier Bedrock/Nova/Kimi tests | docs (LLM notes); 001 (S-009, S-010, S-017) |
| Gold test set | pipeline/gold20.py |
| Public API, security, deploy, daily LLM cap | docs (Public API); supabase/deploy.py; index.ts |
| Accounts, keys by name, how to run (private) | ~/Documents/ojt/PRIVATE-GUIDE.md |
| Coverage target (category × tier × audience) | docs (Coverage) |
| Rounds 1–37, GitHub cleanup, Shreyash, tunnel | 001 (S-003–S-011) |

## Open decisions

1. Raise the key limit to ~$5 and approve the full run (pending, S-017).
2. Web check of "maybe" professionals after the full run (cost shown first).
3. Repo public or private? (The anon key is public by design; `admin/.env` is gitignored.)
4. Unlock price and what an unlock sells; when/where to deploy the website (Next.js not started).
5. Change `/context-read` to start free work by itself? (offered in S-016, no answer)
6. Delete `backup-before-coauthor-removal`, `_archive-2026-11-16-stale-copies/`, `.playwright-mcp/`?
7. How Shreyash gets data access.

## Ruled out

- Budget-of-deal fields, WhatsApp/concierge flow, creators >100K (001, S-001). Product price level is allowed (S-015).
- Live scraping at search time; "Lifestyle" as a category; city as a requirement (docs; S-010, S-014).
- AWS/Bedrock in any form; Kimi K3; Mem0 (S-009–S-015). **Jev Router** (S-017: worse, 6x cost, mixes models).
- One list sorted only by score; unrelated high-reach creators in the wider column (S-013, S-015).
- Batching several creators per LLM request (saves ≤$0.50, risks accuracy) (S-017).
- Temperature 0 on Haiku 5.5 (API rejects it) (S-017).
- Instagram category alone as a creator test except the curated business set (S-017).
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

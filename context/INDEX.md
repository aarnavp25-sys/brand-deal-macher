# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-21 (S-018).

> **Auto-compact is OFF** (`~/.claude/settings.json`, S-012). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** — no `Co-Authored-By: Claude` or AI line in any commit/PR (user's order 2026-11-18; hooks block it).
> **Budget:** $8.5 total for all LLM work incl. demo day (teachers test live). Spent ~$4.00; OpenRouter key limit $5
> ($1.00 left on the key). Stop and get the user's "haa" before every paid step. No accuracy loss for cost.
> **Layout:** project = `~/Documents/ojt/brand deal matcher/` (own git repo, github.com/aarnavp25-sys/brand-deal-macher,
> PUBLIC, `main`). Workspace root holds stale copies + `PRIVATE-GUIDE.md` (private map, chmod 600) + the skills in
> `.claude/skills/context-{read,write}/`. `cd ~/Documents/ojt/"brand deal matcher"` first. Network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`. Type-check the Edge Function:
> `cd supabase/functions/api && npx -y deno@2.1.4 check index.ts`. Deploy: `python3 supabase/deploy.py function`
> (load `admin/.env` into the shell first). Servers: admin 8787, demo 8788.
> **After any matching change run `python3 pipeline/eval_search.py`** (16 briefs, rules R1–R9; must stay at 0 violations).
> The API rate limit is 30 searches / 10 min per IP — the user's demo shares the IP with the eval.

## Where things stand

Brand Deal Matcher helps small Indian brands find Instagram creators (1K–100K followers). Working prototype: Python
stdlib pipeline, Supabase DB (`yqaducvspzrqokcqwlga`, free tier), local admin, demo page calling the Edge Function
`api`. `main` is at `ddc3a00` plus the S-018 context commit; the 8 S-018 code commits are **not pushed**.

**Data.** 6,224 creators. Every search-visible creator has a v10 AI profile (`creator_llm`; full run S-018: 5,113,
0 failed, $3.19). Hidden from search: `status='business'` 173; `status='review'` 678 (367 from the S-018 account
check: Haiku called them personal accounts or own-shop pages; the rest pipeline rules, each with a `review_reason`);
fake 553; and by AI profile: organisations without paid promotions, shops, foreign accounts, professionals who do not
promote. **3,231 creators are shown in search.** Thin: perfume (no specialists), men's jewellery (none), mid tier;
all 13 Apify accounts empty until December.

**LLM.** Claude Haiku 5.5 via OpenRouter (providers anthropic → azure → google-vertex). Key in `admin/.env` and in
Supabase secrets (live search uses the AI brand profile + AI review). ~$0.003 per new search; repeats free for 7
days (`llm_cache`); 400 paid calls/day cap.

**Matching** (`supabase/functions/api/index.ts`; rules consolidated in docs/data-and-matching.md "Search rules,
consolidated"). Brand profile → formula → three columns → AI review → code applies the user's rules. Niche =
product evidence (specialists) or shop-visit creators for a local store. Category = product's own category plus fixed
neighbours (`CAT_NEIGHBOURS`) — never the brand AI's extra categories — and the creator's own products must touch
the product's world (`relevance` tiers from proven / can_promote / natural fits); ordered verdict → field →
relevance → score. Wider reach = big reach + believable fit (≥3,000 followers; comedians, athletes allowed). Review
returns verdict + `field` + `account`; code drops weak, personal, own shop, and "other field" from the category
column. Men's product never shows a women-audience creator who features women's products (and back). Local-store-only
brand: its city only. Empty columns say so (user accepts an empty niche).

**How the session ended.** After a run of one-off fixes that kept breaking other searches (rappers in "your
category", then an empty men's watch category), the user said "saari cheeze ek baar re think kar sab properly fix
kar". Matching was rebuilt around fixed category neighbours + product relevance, `pipeline/eval_search.py` was added,
and the final pass showed 0 violations across 16 briefs, read by hand. The user accepted empty niche columns.

## Continue from here

1. Ask the user to raise the OpenRouter key limit before demo day ($1.00 left on the key).
2. Ask before pushing the 8 S-018 commits (`git push` with the credential flags above).
3. Open http://127.0.0.1:8787 in a browser once: the S-018 admin changes (AI profile, account check, filters,
   "Keep as creator") were only syntax-checked.
4. Small cleanup: project CLAUDE.md still says "No budget/price features" (price level allowed since S-015) and calls
   the third column "trending" (UI: "Wider reach").
5. After the Apify resets (acc3 2026-12-09; others 2026-12-15/16/17): `round.py` with perfume, men's fashion,
   streetwear and men's accessories/jewellery terms; `round.py` profiles + account-checks new creators itself. Then
   `eval_search.py`.
6. User: delete the two Bedrock keys in AWS IAM; then update PRIVATE-GUIDE.md.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price-of-deal and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake rule, business-account rule | docs/data-and-matching.md (Pipeline); 001 (S-016, S-017) |
| Account check (personal / own shop → review), review_reason | pipeline/account_check.py; docs (Pipeline); 001 (S-018) |
| Running a scraping round | pipeline/round.py; 001 (S-011, S-015) |
| Taxonomy (16 categories, 82 product types) | pipeline/taxonomy.py; docs (Taxonomy) |
| Search rules R1–R9, category neighbours, relevance, review field/account | docs (Matching, "Search rules, consolidated"); 001 (S-018) |
| Search evaluation | pipeline/eval_search.py; 001 (S-018) |
| Columns, natural fits, quality, who is shown | docs (Matching 3–5d); 001 (S-013, S-017, S-018) |
| Price level; local shops | docs (Matching 5a, 5b); 001 (S-014, S-015, S-018) |
| Creator profile prompt v10, lessons v5→v10 | pipeline/llm_classify.py; docs (LLM notes); 001 (S-017) |
| LLM cost measured, providers, full run | docs (LLM notes); 001 (S-017, S-018) |
| Jev Router test; earlier Bedrock/Nova/Kimi tests | docs (LLM notes); 001 (S-009, S-010, S-017) |
| Admin dashboard | admin/index.html, admin/server.py; 001 (S-008, S-018) |
| Public API, security, deploy, rate limit, daily LLM cap | docs (Public API); supabase/deploy.py; index.ts |
| Accounts, keys by name, how to run (private) | ~/Documents/ojt/PRIVATE-GUIDE.md |
| Coverage target (category × tier × audience) | docs (Coverage) |
| Rounds 1–37, GitHub cleanup, Shreyash, tunnel | 001 (S-003–S-011) |

## Open decisions

1. Raise the key limit (how much) before demo day.
2. Push the S-018 commits now or later?
3. Web check of "maybe" professionals (cost shown first) — not started.
4. Repo public or private? (The anon key is public by design; `admin/.env` is gitignored.)
5. Unlock price and what an unlock sells; when/where to deploy the website (Next.js not started).
6. Change `/context-read` to start free work by itself? (offered in S-016, no answer)
7. Delete `backup-before-coauthor-removal`, `_archive-2026-11-16-stale-copies/`, `.playwright-mcp/`?
8. How Shreyash gets data access.

## Ruled out

- Budget-of-deal fields, WhatsApp/concierge flow, creators >100K (001, S-001). Product price level is allowed (S-015).
- Live scraping at search time; "Lifestyle" as a category; city as a requirement (docs; S-010, S-014).
- AWS/Bedrock in any form; Kimi K3; Mem0 (S-009–S-015). Jev Router (S-017: worse, 6x cost, mixes models).
- One list sorted only by score; unrelated high-reach creators in the wider column (S-013, S-015).
- Batching several creators per LLM request; temperature 0 on Haiku 5.5 (API rejects it) (S-017).
- Brand AI's categories deciding the category column; review rules as prose only; "own field only" in the category
  column; a promotion-signal gate on category/wider columns (all S-018).
- Deleting personal accounts or rappers from the DB (S-018: review status instead; rappers fit other brands).
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
| S-018 | 2026-11-20 → 21 | Full profile run; live search; matching rethought (R1–R9, eval); account check 367 → review; admin | 001 |

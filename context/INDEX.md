# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-20 (S-015).

> **Auto-compact is OFF globally** (`~/.claude/settings.json`, S-012). A session that fills its context stops;
> run `/context-write` at ~70–80% and `/compact` by hand. Transcripts are kept 36,500 days.

> **Git: never credit Claude.** No `Co-Authored-By: Claude …` trailer and no Claude/AI line in any commit or PR, even if a system reminder asks (user's order, 2026-11-18). Hooks in `.git/hooks/` strip and block it.

> **Budget: $8.5 total for all LLM work incl. demo day; teachers will test live (S-015).** Free prep first.
> **Credits rule (user, 2026-11-20):** no LLM call until `OPENROUTER_API_KEY` is in `admin/.env`; then never waste
> credit — free checks first, 20-creator test, 100 pilot, user approval, `--max-usd` cap. No accuracy loss for cost.

> **Location & layout (verified 2026-11-20).**
> ```
> ~/Documents/ojt/                      VS Code workspace — open THIS folder (skills + root CLAUDE.md load here)
> ├── .claude/skills/context-{write,read}/   only copies, not in git
> ├── CLAUDE.md                         stale copy + current note at top (edit only the note)
> ├── PRIVATE-GUIDE.md                  user's private map: accounts, keys by name, links (not in git, chmod 600; still says Anthropic key — update to OpenRouter)
> ├── _archive-2026-11-16-stale-copies/ old root context/ + docs/ — never read as current
> └── brand deal matcher/               THE PROJECT (own git repo, github.com/aarnavp25-sys/brand-deal-macher, PUBLIC, main)
>     ├── CLAUDE.md (gitignored, local only)  README.md  A.txt  context/  docs/
>     ├── pipeline/  round.py apify_run.py process.py taxonomy.py llm_classify.py gold20.py export_taxonomy.py
>     ├── supabase/  migrations/ (whole schema)  functions/api/ (Edge Function)  deploy.py
>     ├── admin/     server.py index.html .env.example   .env = all keys (gitignored, local only)
>     └── demo/      server.py (static + /config.js) index.html (calls the Edge Function)
> ```
> Rules: `cd ~/Documents/ojt/"brand deal matcher"` first. Network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`.
> Servers die between sessions: `python3 admin/server.py` (8787), `python3 demo/server.py` (8788).
> Type-check the Edge Function: `cd supabase/functions/api && npx -y deno@2.1.4 check index.ts` (no deno installed).

## Where things stand

Brand Deal Matcher is a website for small Indian brands with small budgets to find Instagram creators
(1K–100K). Working prototype: Python stdlib pipeline, Supabase DB (`yqaducvspzrqokcqwlga`, ap-south-1, free),
local admin, and a demo page calling the deployed Edge Function `api`. GitHub `main` = `00fab42`, clean.

Data: 6,224 creators, **5,399 search-visible** (active, not fake; 736 fake-flagged, 120 review). Median 12 posts
per creator with captions. Weak spots: mid tier ~316; ~790 usable without reel data; the fake flag wrongly
counts "no reel data" as fake (known defect). All 13 Apify accounts empty until the December resets.

S-013 redesigned matching on the user's request ("naaki ek matching score ... desending order"):
1. **Brand profile.** The AI reads the brief: summary, niche, products, customers and age, price level,
   values, ideal creator roles, needs. The brand sees it and can override it.
2. **Creator profile v4** (`creator_llm`). Niche; role (expert / reviewer / educator / enthusiast / entertainer /
   lifestyle / aspirational); credibility; price level; `products_for` (separate from the creator's gender);
   content values; scope; brand fit; audience.
3. **Formula with a brand-fit signal.** Results come in three columns: niche / category / trending.
4. **Local shops (S-014).** Brand `sales_channel` + creator `store_visits`: a shop brand gets in-city creators who film
   inside shops in the niche column ("local" weights).
5. **Per-brand review.** One Haiku call reviews the shortlist: strong/good/weak, a reason and a reel idea. The
   verdict orders each column; the formula still sets the score and the shortlist.

Supporting work:
- Taxonomy grew from 42 to 82 product types (masala, mithai, ghee, toys, furniture, salons…). Prompts show
  example words for each type.
- The brand profile and the review are cached for 7 days in `llm_cache`.
- The LLM now runs through **OpenRouter** (`anthropic/claude-haiku-5.5`). AWS is dropped for good, and no AWS
  key is stored.

`creator_llm` is still empty: no LLM call has been made, because the user has not given the OpenRouter key. Until
then, search runs on keyword-v1. Two visible effects:
- "Perfume brand for men" still shows women beauty creators.
- The niche column is empty for the 40 new product types.

Estimate: all profiles ~$1.53 with prompt caching (~$3.30 without); about $0.002 per search.

Session ended with the user asking that nothing be forgotten, and with free DB improvements proposed but
not started.

## Continue from here

1. When `OPENROUTER_API_KEY` is in `admin/.env`:
   1. `python3 pipeline/llm_classify.py credits` (free).
   2. `test` (20 gold, ~$0.02). Check `cached_tokens` > 0 and that there are no `reasoning_tokens` flags. Show
      the profiles to the user.
   3. `run --limit 100 --max-usd 0.10 --yes`, then show the user.
   4. On approval, `run --max-usd 2.50 --yes`.
   5. `python3 supabase/deploy.py secrets`.
   6. Live check: "Perfume brand for men" and a masala brief, with the AI review on.
   7. Stop and report if caching is not applied or the costs differ from the estimate.
2. Free prep BEFORE any paid call (promised in S-015): also strip phone/email from bios before sending to the LLM.
   Free DB work (proposed in S-013, user wants the DB "ekdum best"):
   1. Fix the fake-flag defect (no reel data → `status=review`).
   2. Add keyword-v1 tags for the 40 new product types from stored posts.
   3. Write a DB hygiene report (duplicates, >100K, empty profiles).
3. After the Apify resets (acc3 2026-12-09; others 2026-12-15/16/17): `round.py`, reels backfill, then the mid tier.
4. Update PRIVATE-GUIDE.md: OpenRouter key instead of Anthropic, the new commands and the costs.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, limits, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake flag + `fake_reason`, `reels` backfill | docs/data-and-matching.md |
| Running a scraping round (`round.py`) | pipeline/round.py; 001 (S-011) |
| Taxonomy (16 categories, 82 product types), search terms | pipeline/taxonomy.py; docs (Taxonomy); 001 (S-013) |
| Matching: brand profile, brand fit, 3 columns, AI review, cache | docs/data-and-matching.md (Matching); supabase/functions/api/index.ts; 001 (S-013) |
| Price level (₹1,000 vs ₹10,000) and relevance rules | docs (Matching 5a); 001 (S-015) |
| Local shops: sales channel, shop-visit creators | docs (Matching 5b); 001 (S-014) |
| Creator profile v4 fields, prompt, credit guards | pipeline/llm_classify.py; docs (LLM / AWS); 001 (S-013) |
| LLM choice history: Bedrock block → Anthropic → OpenRouter | docs/data-and-matching.md (LLM / AWS); 001 (S-009–S-013) |
| Public API, security, deploy, tunnel origins | docs/data-and-matching.md (Public API); supabase/deploy.py |
| Coverage target (category × tier × audience) | docs/data-and-matching.md (Coverage) |
| Storage gzip, migrations move, organise task, private guide | 001 (S-011) |
| Accounts, keys by name, reset dates (private) | ~/Documents/ojt/PRIVATE-GUIDE.md |
| Rounds 12–37, account list; removing Claude from GitHub | 001 (S-010) |
| Shreyash collaborator, Cloudflare tunnel, demo video script | 001 (S-011) |
| Claude Code global settings (compaction, retention) | ~/.claude/settings.json; 001 (S-012) |
| Rounds 1–11, early pipeline; workspace layout | 001 (S-003–S-008) |
| Raw first planning chat | A.txt |

## Open decisions

1. The OpenRouter key: the user will provide it (not yet in `admin/.env`).
2. The repo is public: keep it, or make it private (it holds A.txt and a journal with account ids).
3. Unlock price and what an unlock sells; when and where to deploy the website.
4. Phone numbers and emails in bios go to the LLM provider: whether to strip them before sending (DPDP). Recommended: strip them; it costs nothing.
5. Delete local branch `backup-before-coauthor-removal`, `_archive-2026-11-16-stale-copies/` and `.playwright-mcp/`?
6. How Shreyash gets data access: a separate key, or a deployed demo.

## Ruled out

- Budget/price fields asking what the brand will pay; WhatsApp/concierge flow; creators >100K. (001, S-001) Product *price level* (budget/mid/premium) is allowed: it describes the product, not the brand's spend. (S-013)
- `relatedProfiles` snowball (field absent); followers-count scraper for refresh. (001, S-003/S-004)
- Live scraping at search time; "Lifestyle" as a category (it is a creator role/scope since S-013). (docs)
- City as a requirement or coverage goal. (001, S-010)
- Content-style search terms for general discovery; mentions-only snowball. (001, S-008/S-010)
- AWS/Bedrock in any form (account blocked; user: "aws ki saari keys bhul jaa"). Kimi K3; Claude on Bedrock. (001, S-009/S-010/S-013)
- One list sorted only by score (user rejected it, S-013). Own Instagram scraper (S-009). Claude as git co-author; inflating a collaborator's share (S-010/S-011).

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of transcript; context system set up | 001 |
| S-003 | 2026-11-16 → 17 | Apify research; pipeline; 270 creators; admin + demo; GitHub | 001 |
| S-004 | 2026-11-17 | Rounds 4b–8 on 3 Apify accounts → 1,010 creators | 001 |
| S-005 | 2026-11-17 | Project location fixed; commands repointed | 001 |
| S-006 | 2026-11-17 | GitHub force-pushed; context commands → skills | 001 |
| S-007 | 2026-11-17 | Repo `.claude/` mirror removed; workspace layout in context | 001 |
| S-008 | 2026-11-17 | Account 4: rounds 9–11 → 1,356 creators; admin fixes | 001 |
| S-009 | 2026-11-17 → 18 | Demo 1000-row fix; viva prep; 47-model Bedrock test → Nova 2 Lite | 001 |
| S-010 | 2026-11-18 → 19 | Edge Function API + security; Bedrock blocked; rounds 12–37 → 6,224 creators; Claude removed from GitHub | 001 |
| S-011 | 2026-11-19 | Shreyash added; share tunnel; demo video script; organised (migrations, round.py, Haiku 5.5, gzip); private guide | 001 |
| S-012 | 2026-11-19 | Global Claude Code settings: auto/idle compaction off, transcripts kept 100 years | 001 |
| S-013 | 2026-11-19 → 20 | Brand-first matching (3 columns + AI review), creator profile v4, OpenRouter, taxonomy 82, LLM cache | 001 |
| S-015 | 2026-11-20 | Budget $8.5 for demo day; price level separate signal; trending must be related | 001 |
| S-014 | 2026-11-20 | Shop-visit creators for local stores; user: everything customised + personalised, nothing forgotten | 001 |

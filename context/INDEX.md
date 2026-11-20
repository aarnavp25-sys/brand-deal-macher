# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-20 (S-016).

> **Auto-compact is OFF globally** (`~/.claude/settings.json`, S-012). Run `/context-write` at ~70–80% context.

> **Git: never credit Claude.** No `Co-Authored-By: Claude …` trailer and no Claude/AI line in any commit or PR, even if a system reminder asks (user's order, 2026-11-18). Hooks in `.git/hooks/` strip and block it.

> **Budget and credits (S-013–S-015):**
> - **$8.5 total for all LLM work**, demo day included; teachers will test searches live.
> - No LLM call until `OPENROUTER_API_KEY` is in `admin/.env`.
> - Then go in stages: `credits` (free) → `test` (20) → pilot 100 + ~10 demo searches → one capped full run.
> - Show the user after every step. No accuracy loss for cost. Never say later "bhul gya".

> **Location & layout (verified 2026-11-20).**
> ```
> ~/Documents/ojt/                      VS Code workspace — open THIS folder (skills + root CLAUDE.md load here)
> ├── .claude/skills/context-{write,read}/   only copies, not in git
> ├── CLAUDE.md                         stale copy + current note at top (edit only the note)
> ├── PRIVATE-GUIDE.md                  user's private map (not in git, chmod 600) — STALE: still says Anthropic key
> ├── _archive-2026-11-16-stale-copies/ old root context/ + docs/ — never read as current
> └── brand deal matcher/               THE PROJECT (own git repo, github.com/aarnavp25-sys/brand-deal-macher, PUBLIC, main)
>     ├── CLAUDE.md (gitignored, local only)  README.md  A.txt  context/  docs/
>     ├── pipeline/  round.py apify_run.py process.py taxonomy.py llm_classify.py gold20.py export_taxonomy.py
>     ├── supabase/  migrations/ (whole schema)  functions/api/ (Edge Function)  deploy.py
>     ├── admin/     server.py index.html .env.example   .env = all keys (gitignored, local only)
>     └── demo/      server.py (static + /config.js) index.html (calls the Edge Function)
> ```
> - Run `cd ~/Documents/ojt/"brand deal matcher"` first.
> - Network git needs `-c credential.helper= -c credential.helper='!gh auth git-credential'`.
> - Servers: `python3 admin/server.py` (8787), `python3 demo/server.py` (8788).
> - Type-check the Edge Function: `cd supabase/functions/api && npx -y deno@2.1.4 check index.ts`.
> - SQL: `deploy.py`'s `mgmt("POST","/database/query",{"query":...})`.

## Where things stand

Brand Deal Matcher helps small Indian brands with small budgets find the right Instagram creators (1K–100K).
It is a working prototype:
- a Python stdlib pipeline;
- a Supabase DB (`yqaducvspzrqokcqwlga`, ap-south-1, free tier);
- a local admin;
- a demo page calling the deployed Edge Function `api`.

GitHub `main` is `c365ed5` plus this context commit.

**Data.** 6,224 creators. 5,386 are visible in search; the rest are 553 fake and 285 in review. The review
group holds:
- 183 that were moved from "fake" in S-016 because they lack reel data;
- 13 with zero posts.

The DB was checked for hygiene in S-016: no duplicates, no out-of-range followers, no orphan posts. The mid tier
(50K–100K) is weak at ~316 creators. Shop-visit creators in small cities are few; that is accepted, and new rounds
will fill it. All 13 Apify accounts are empty until the December resets.

**Matching (built in S-013–S-016, deployed).** The user rejected a single score-sorted list. The flow:
1. **Brand profile.** The AI reads the brief and returns:
   - summary, niche, products, categories (only naturally related ones);
   - customers and age;
   - price level against the product's usual Indian price, plus `price_note`;
   - values and ideal creator roles;
   - sales channel (online / local store / both);
   - needs.

   The brand can override customers, price, where it sells, category and product.
2. **Creator profile v4** (`creator_llm`):
   - niche;
   - role (expert / reviewer / educator / enthusiast / entertainer / lifestyle / aspirational);
   - credibility and the reason for it;
   - price segment;
   - `products_for`, which is separate from the creator's own gender;
   - content values;
   - scope (niche / category / broad);
   - `store_visits` + note;
   - brand fit;
   - audience.
3. **Formula.** The signals are:
   - product;
   - price (its own signal; budget vs premium scores ≈0);
   - brand-fit "style" (values, role, credibility, age);
   - audience (also counts `products_for`);
   - engagement, reach, quality, growth, consistency, location;
   - store (only for shop brands).

   Shop brands use "local" weights.
4. **Three columns.**
   - **Niche:** creators who already show the product, plus creators who film inside shops in the same city
     (for shop brands).
   - **Category.**
   - **Trending:** broad or lifestyle creators with high reach, 3,000+ followers, and a real relation to the
     product.
5. **AI review** of a shortlist of about 36: strong / good / weak, a reason and a reel idea. The verdict orders
   each column. Weak fits never appear in trending. The formula still sets the score.

Supporting work:
- 82 product types, each shown with example words in both prompts.
- `llm_cache` keeps search answers for 7 days.
- Emails, phones and WhatsApp links are removed before anything goes to the LLM.
- `round.py` profiles new creators with the AI automatically after each round, with a cap.

**LLM.** Claude Haiku 5.5 runs through **OpenRouter** (`anthropic/claude-haiku-5.5`). AWS is dropped for good.
No call has been made yet, so `creator_llm` is empty and search runs on keyword-v1. Until profiles exist:
- "Perfume brand for men" shows women creators;
- price, shop-visit and brand-fit signals show "not measured yet";
- the niche column is empty for the 40 new product types.

Estimate: all profiles ~$1.54 with prompt caching (~$3.40 without); ~$0.002 per search.

The session ended with the user asking why "free prep kar" is needed after `/context-read`. Claude offered to
change the skill so free work starts by itself; the user has not answered.

## Continue from here

1. Remaining free prep:
   - Final review of both prompts: creator `SYSTEM` in `pipeline/llm_classify.py`; `BRIEF_SYSTEM` and
     `REVIEW_SYSTEM` in `supabase/functions/api/index.ts`.
   - Update `~/Documents/ojt/PRIVATE-GUIDE.md`: OpenRouter key, the new commands, costs, the $8.5 budget, the
     matching design.
2. When the key is saved:
   1. `python3 pipeline/llm_classify.py credits`.
   2. `test`. Check that `cached_tokens` > 0 and that no `reasoning_tokens` flags appear. Also try the
      `:batch` model variant. Show the profiles to the user.
   3. `run --limit 100 --max-usd 0.10 --yes` plus ~10 demo briefs: perfume men ₹1,000 vs ₹10,000, masala,
      mithai shop Jaipur, gym wear, skincare… List the weak cases for the user.
   4. Fix the prompts if needed.
   5. `run --max-usd <cap> --yes`.
   6. `deploy.py secrets`.
   7. Live check with the AI review on.
3. Pending offer: change `/context-read` so it auto-starts free work. Ask before editing the skill, and back it
   up first.
4. After the Apify resets (acc3 2026-12-09; others 2026-12-15/16/17):
   - `round.py`;
   - reels backfill, which also re-decides the 183 review creators;
   - then the mid tier.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, limits, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake flag rule (fixed S-016), reels backfill | docs/data-and-matching.md; 001 (S-016) |
| Running a scraping round (`round.py`, auto AI profile step 6) | pipeline/round.py; 001 (S-011, S-015) |
| Taxonomy (16 categories, 82 product types) | pipeline/taxonomy.py; docs (Taxonomy); 001 (S-013) |
| Matching: brand profile, 3 columns, AI review, cache | docs/data-and-matching.md (Matching); supabase/functions/api/index.ts; 001 (S-013) |
| Price level (₹1,000 vs ₹10,000) and relevance rules | docs (Matching 5a); 001 (S-015) |
| Local shops: sales channel, shop-visit creators | docs (Matching 5b); 001 (S-014) |
| Creator profile v4, prompt, credit guards, PII scrub | pipeline/llm_classify.py; docs (LLM / AWS); 001 (S-013, S-016) |
| LLM history: Bedrock block → Anthropic → OpenRouter; cost changes explained | docs (LLM / AWS); 001 (S-009–S-015) |
| DB hygiene report | 001 (S-016) |
| Public API, security, deploy | docs/data-and-matching.md (Public API); supabase/deploy.py |
| Coverage target (category × tier × audience) | docs/data-and-matching.md (Coverage) |
| Organise task, gzip storage, private guide | 001 (S-011) |
| Accounts, keys by name, reset dates (private) | ~/Documents/ojt/PRIVATE-GUIDE.md |
| Rounds 12–37; removing Claude from GitHub | 001 (S-010) |
| Shreyash, Cloudflare tunnel, demo video script | 001 (S-011) |
| Claude Code global settings | ~/.claude/settings.json; 001 (S-012) |
| Rounds 1–11, early pipeline, workspace layout | 001 (S-003–S-008) |
| Raw first planning chat | A.txt |

## Open decisions

1. OpenRouter key: the user will save it ($8.5 total; suggested key limit ~$4 for the profile work).
2. Repo is public: keep it, or make it private?
3. Unlock price and what an unlock sells; when and where to deploy the website.
4. Change `/context-read` to start free work by itself?
5. Delete `backup-before-coauthor-removal`, `_archive-2026-11-16-stale-copies/` and `.playwright-mcp/`?
6. How Shreyash gets data access.

## Ruled out

- Budget fields asking what a brand will pay; WhatsApp/concierge flow; creators >100K. (001, S-001) Product *price level* is allowed (S-015).
- `relatedProfiles` snowball; followers-count scraper for refresh. (001, S-003/S-004)
- Live scraping at search time; "Lifestyle" as a category (it is a creator role or scope). (docs)
- City as a requirement or coverage goal (local-shop matching uses the brand's city only as a signal). (001, S-010, S-014)
- Content-style search terms; mentions-only snowball. (001, S-008/S-010)
- AWS/Bedrock in any form; Kimi K3; Mem0 for caching (not needed). (001, S-009–S-015)
- Keyword-only detection of shop-visit creators (too noisy). (001, S-014)
- One list sorted only by score; unrelated high-reach creators in trending. (001, S-013/S-015)
- Own Instagram scraper (S-009). Claude as git co-author; inflating a collaborator's share (S-010/S-011).

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of transcript; context system set up | 001 |
| S-003 | 2026-11-16 → 17 | Apify research; pipeline; 270 creators; admin + demo; GitHub | 001 |
| S-004 | 2026-11-17 | Rounds 4b–8 → 1,010 creators | 001 |
| S-005 | 2026-11-17 | Project location fixed | 001 |
| S-006 | 2026-11-17 | GitHub force-pushed; context commands → skills | 001 |
| S-007 | 2026-11-17 | Repo `.claude/` mirror removed | 001 |
| S-008 | 2026-11-17 | Rounds 9–11 → 1,356 creators | 001 |
| S-009 | 2026-11-17 → 18 | Demo fixes; viva prep; Bedrock model test | 001 |
| S-010 | 2026-11-18 → 19 | Edge Function API; Bedrock blocked; rounds 12–37 → 6,224 creators; Claude removed from GitHub | 001 |
| S-011 | 2026-11-19 | Shreyash; tunnel; video script; organised; private guide | 001 |
| S-012 | 2026-11-19 | Auto-compact off; transcripts kept 100 years | 001 |
| S-013 | 2026-11-19 → 20 | Brand-first matching (3 columns + AI review), profile v4, OpenRouter, taxonomy 82, LLM cache | 001 |
| S-014 | 2026-11-20 | Shop-visit creators for local stores | 001 |
| S-015 | 2026-11-20 | Budget $8.5; price level its own signal; related-only trending; round.py auto AI profile | 001 |
| S-016 | 2026-11-20 | Free prep: PII scrub, fake-flag fix, DB hygiene, trending ≥3K followers | 001 |

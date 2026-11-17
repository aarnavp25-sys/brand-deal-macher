# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-17 (S-008).

> **Location & layout (read first; verified 2026-11-17).**
> ```
> ~/Documents/ojt/                      VS Code workspace — open THIS folder (Claude Code loads skills + CLAUDE.md here)
> ├── .claude/skills/context-write/     /context-write skill — only copy, not in git
> ├── .claude/skills/context-read/      /context-read skill — only copy, not in git
> ├── CLAUDE.md                         STALE 2026-11-16 copy + this note (auto-loaded; edit only this note)
> ├── context/  docs/                   STALE 2026-11-16 copies — never read as current, never write
> ├── .playwright-mcp/                  Playwright test screenshots/logs — disposable
> └── brand deal matcher/               THE PROJECT — do all work here (own git repo)
>     ├── .git → github.com/aarnavp25-sys/brand-deal-macher (private, branch main)
>     ├── CLAUDE.md  README.md  .gitignore  A.txt (first planning chat)
>     ├── context/INDEX.md, context/001-*.md     current context (journal + index)
>     ├── docs/product-design.md, docs/data-and-matching.md
>     ├── pipeline/  apify_run.py process.py taxonomy.py schema.sql   (no .env)
>     ├── admin/     server.py index.html .env.example  .env = Supabase key + APIFY_TOKENS, gitignored, local only
>     └── demo/      server.py index.html
> ```
> Rules: `cd ~/Documents/ojt/"brand deal matcher"` before any project, git or context step. Never edit the
> stale root copies (only this note). Skills are edited at `~/Documents/ojt/.claude/skills/` and are not
> versioned — back them up before big changes. Commit only real project changes, never just for moving
> files. Network git needs `-c credential.helper= -c credential.helper='!gh auth git-credential'`.
> Servers: `python3 admin/server.py` (8787), `python3 demo/server.py` (8788), run from the project folder.

## Where things stand

Brand Deal Matcher is a website for small/homegrown Indian brands: a brand
describes its product and gets ranked growing Instagram creators (1K–100K) with a
match score and a reason. The project folder above has its own git repo, remote
https://github.com/aarnavp25-sys/brand-deal-macher (private); GitHub `main` =
721f643 (pushed 2026-11-17, S-008), local and remote in sync. Design docs:
`docs/product-design.md` and `docs/data-and-matching.md` (verified Apify facts,
pipeline, taxonomy, matching, load gotchas incl. parallel-run limits, LLM/AWS notes).
Project `CLAUDE.md` still says "design only … no git repo" — stale, fix it.

The prototype is Python stdlib and runs locally. `pipeline/` scrapes with Apify
under hard spend caps (`apify_run.py`), filters/enriches/classifies with keywords
(`process.py`, `keyword-v1`) into 16 categories and 42 product types
(`taxonomy.py`, per-round term dicts `ROUND5_TERMS`…`ROUND11_TERMS`), and loads
Supabase (`yqaducvspzrqokcqwlga`, ap-south-1, free; RLS on, no policies; raw JSON
in Storage `raw-scrapes`). Supabase holds **1,356 creators, 1,168 usable**; every
category has 43–113 usable creators (thinnest: Jewelry 43, Education 45, Home
Decor 46). 115 creators have follower snapshots on two dates (2026-11-16/17).
`admin/` (8787) is the local admin dashboard — since S-008 it pages past
Supabase's 1000-row cap and shows a live "Apify credits" card from
`APIFY_TOKENS` in `admin/.env`; `demo/` (8788) is the brand-facing demo.

Apify: four FREE accounts, $5/month each. Balances: account 1 $0.30, account 2
$0.43, account 3 $0.65 (journal values from S-004, no tokens stored to check),
account 4 (`obeying_mussel`) $0.37 live (in `admin/.env` as `acc4`). Resets
2026-12-15/16. Round scripts live only in session scratchpads (S-008:
`round9b.sh`, `round9c.sh`, `round10.sh`, `round11.sh`); the pattern is 3
parallel search runs → filter vs paginated existing creators → ≤3 parallel reel
runs (4 GB each) → merge → build → load only new creators.

What is weak: classification is keyword-based (noisy product matches, e.g.
`rider_girls_pune` for men's jewelry); creator gender and content quality are
empty; brief parsing and explanations are keyword/template. All wait for an LLM:
no Anthropic key; AWS has $100 credits (Free plan, until 2027-05-16), Bedrock
untested; the user postponed AWS on 2026-11-17. 284 usable creators have no city.

How the last session ended (S-008): the user gave a fourth Apify account; all
but $0.37 went into rounds 9–11 (+346 creators) run in parallel at the user's
request ("full speed"). Admin was fixed and extended, everything committed and
pushed as 721f643, then this INDEX was written.

## Continue from here

1. Security: Apify account-4 token and earlier tokens were pasted in chat →
   user regenerates them; put new tokens in `admin/.env` `APIFY_TOKENS=acc1:…,acc2:…,acc3:…,acc4:…`
   and restart admin. Supabase `sbp_…` token also still to revoke.
2. LLM classification for all 1,356 creators (`classification_method='llm'`):
   products with evidence, gender, content style; then vision quality; then
   replace `parse_brief`/`explain` in `demo/server.py`. Needs an Anthropic key or
   a Bedrock test (us-east-1). Test on 20 creators first and report cost.
3. Before any demo: run the 6 example briefs on http://127.0.0.1:8788 and fix
   wrong product links in admin (start with `rider_girls_pune`).
4. Weekly follower refresh with Profile Scraper after the 2026-12-15/16 resets
   (acc4's $0.37 covers ~140 creators now).
5. Fix the stale "Current state" line in project `CLAUDE.md`.
6. Scraping rules: ≤3 reel runs at once; page every Supabase read past 1000;
   prefer city + niche terms; grep load logs for `Traceback`.

## Topic -> file

| Topic | File |
|---|---|
| Workspace layout, where to work, what is stale | this INDEX (Location & layout); 001 (S-005, S-007) |
| Product idea, positioning, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, filters, what they return | docs/data-and-matching.md |
| Pipeline steps, metrics, fixes, load gotchas | docs/data-and-matching.md |
| Parallel Apify runs, 402 = memory, 1000-row cap, term yield | docs/data-and-matching.md; 001 (S-008) |
| 16 categories, product types, search terms per round | pipeline/taxonomy.py |
| Matching: product fit, labels, weights, mix | docs/data-and-matching.md; demo/server.py |
| Why DB-first instead of live scraping | docs/data-and-matching.md |
| Claude prices, Bedrock vs Claude Platform on AWS, AWS credits | docs/data-and-matching.md; 001 (S-003) |
| Supabase schema, ref, key handling | pipeline/schema.sql; 001 (S-003) |
| Admin dashboard and demo website | admin/, demo/; 001 (S-003, S-008) |
| Admin Apify credits card, `APIFY_TOKENS` | admin/server.py; 001 (S-008) |
| Rounds 1–4 and every failure | 001 (S-003) |
| Rounds 4b–8, three Apify accounts, Profile Scraper refresh | 001 (S-004) |
| Rounds 9–11, account 4, recovery of failed runs | 001 (S-008) |
| GitHub push method, force-push to 40168a6 | 001 (S-003, S-006) |
| Context skills (`/context-write`, `/context-read`) location | CLAUDE.md; 001 (S-006) |
| Raw first planning chat | A.txt |

## Open decisions

1. LLM route: Anthropic API key vs AWS Bedrock ($100 credits; free-plan access
   unverified; Amazon Nova fallback). Bulk model: Opus 5.5 vs Haiku 5.5.
2. Weekly refresh budget: all 1,168 usable ≈ $3/run, more than one free Apify
   account covers per month — subset, rotate the four accounts, or pay.
3. Phone numbers in scraped bios: hide from brands or not (DPDP).
4. Unlock price and what an unlock sells.
5. When to deploy (Amplify/Vercel) — local only for now.

## Ruled out

- Budget/price fields; WhatsApp/concierge flow; creators >100K. (001, S-001)
- `relatedProfiles` snowball — Profile Scraper never returns it. (001, S-003/S-004)
- Followers-count scraper for refresh — same price as Profile Scraper. (001, S-003)
- Live scraping at search time; "Lifestyle" as a category. (docs/data-and-matching.md)
- Raw Apify JSON in a jsonb column — statement timeout. (001, S-003)
- Chatbot, login, Instagram login, payment in the demo — later. (001, S-003)
- Flattening the project into the workspace root, or committing just to move files. (001, S-005)
- More than 3 parallel Reel Scraper runs on a free account (402, memory). (001, S-008)
- Content-style search terms ("room makeover india") — ~1/3 the yield of city + niche. (001, S-008)

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | unknown (≤ 2026-11-16) | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of transcript; context system set up | 001 |
| S-003 | 2026-11-16 → 17 | Apify research; pipeline; 270 creators; admin + demo; GitHub | 001 |
| S-004 | 2026-11-17 | Rounds 4b–8 on 3 Apify accounts → 1,010 creators; Profile Scraper refresh | 001 |
| S-005 | 2026-11-17 | Project location fixed (ojt/"brand deal matcher"); commands repointed | 001 |
| S-006 | 2026-11-17 | GitHub force-pushed to 40168a6; context commands → skills | 001 |
| S-007 | 2026-11-17 | Repo `.claude/` mirror removed (25b8c02); full workspace layout written into context | 001 |
| S-008 | 2026-11-17 | Account 4: rounds 9–11 in parallel → 1,356 creators; admin 1000-row fix + Apify card; 721f643 | 001 |

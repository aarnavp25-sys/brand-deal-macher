# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-17 (S-006).

> **Location (read first).** The VS Code workspace is `~/Documents/ojt`. The real project, its git repo
> and the only current context live in `~/Documents/ojt/brand deal matcher/`. Do every step inside that
> folder (`cd ~/Documents/ojt/"brand deal matcher"`): its `CLAUDE.md`, `context/INDEX.md`,
> `context/NNN-*.md` and `docs/` are the current ones. The `CLAUDE.md`, `context/` and `docs/` at the
> workspace root are stale S-002 copies kept on purpose — never read them as current, never write to them.

## Where things stand

Brand Deal Matcher is a website for small/homegrown Indian brands: a brand
describes its product and gets ranked growing Instagram creators (1K–100K) with a
match score and a reason. The project folder above has its own git repo, remote
https://github.com/aarnavp25-sys/brand-deal-macher (private). GitHub `main` is
40168a6; it was force-pushed back there on 2026-11-17 after two wrong "move"
commits. On 2026-11-17 the S-005/S-006 context updates were committed and pushed, and
the repo's `.claude/` mirror was removed (skills live only at the workspace root). Design docs: `docs/product-design.md` and
`docs/data-and-matching.md` (verified Apify facts, pipeline, taxonomy, matching,
load gotchas, LLM/AWS notes).

The prototype is Python stdlib and runs locally. `pipeline/` scrapes with Apify
under hard spend caps (`apify_run.py`), filters/enriches/classifies with keywords
(`process.py`, `keyword-v1`) into 16 categories and 42 product types
(`taxonomy.py`, per-round term dicts `ROUND5_TERMS`…`ROUND8_TERMS`), and loads
Supabase (`yqaducvspzrqokcqwlga`, ap-south-1, free; RLS on, no policies; raw JSON
in Storage `raw-scrapes`). Supabase holds **1,010 creators, 863 usable**, 12,515
posts, 5,037 product links; every category has 31–92 usable creators. 115
creators have follower snapshots on 2026-11-16 and 2026-11-17 (growth tracking
started). `admin/` (port 8787) is the local admin dashboard; `demo/` (port 8788)
is the brand-facing demo. Start both from the project folder with
`python3 admin/server.py` and `python3 demo/server.py`. Supabase keys live only
in `admin/.env` (gitignored). No Apify token is stored in the project; the three
tokens used so far were in the session scratchpad only.

What is weak: classification is keyword-based (noisy product matches, e.g.
`rider_girls_pune` for men's jewelry); creator gender and content quality are
empty; brief parsing and explanations are keyword/template. All wait for an LLM:
no Anthropic key; AWS has $100 credits (Free plan, until 2027-05-16), Bedrock
untested; the user postponed AWS on 2026-11-17.

How the last sessions ended: S-004 finished scraping (Apify left: account 1
$0.30, account 2 $0.43, account 3 $0.65; reset 2026-12-15/16). S-005 fixed where
the project lives after two wrong moves. S-006 reset GitHub to 40168a6 and turned
`/context-write` and `/context-read` into skills at `~/Documents/ojt/.claude/skills/`
(Claude Code loads them from the workspace; the repo has no `.claude/`).
They work: this INDEX was written by `/context-write` running from the skill.

## Continue from here

1. Network git needs `-c credential.helper= -c credential.helper='!gh auth git-credential'`
   until `gh auth setup-git` is run).
2. LLM classification for all 1,010 creators (`classification_method='llm'`):
   products with evidence, gender, content style; then vision quality; then
   replace `parse_brief`/`explain` in `demo/server.py`. Needs an Anthropic key or
   a Bedrock test (us-east-1). Test on 20 creators first and report cost.
3. Before any demo: run the 6 example briefs on http://127.0.0.1:8788 and fix
   wrong product links in admin (start with `rider_girls_pune`).
4. Weekly follower refresh with Profile Scraper after the 2026-12-16 reset.
5. After every pipeline round, grep its log for `Traceback` (load is piped to grep).

## Topic -> file

| Topic | File |
|---|---|
| Where the project and the current context live | this INDEX (Location); 001 (S-005) |
| Product idea, positioning, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, filters, what they return | docs/data-and-matching.md |
| Pipeline steps, metrics, fixes, load gotchas | docs/data-and-matching.md |
| 16 categories, product types, search terms per round | pipeline/taxonomy.py |
| Matching: product fit, labels, weights, mix | docs/data-and-matching.md; demo/server.py |
| Why DB-first instead of live scraping | docs/data-and-matching.md |
| Claude prices, Bedrock vs Claude Platform on AWS, AWS credits | docs/data-and-matching.md; 001 (S-003) |
| Supabase schema, ref, key handling | pipeline/schema.sql; 001 (S-003) |
| Admin dashboard and demo website | admin/, demo/; 001 (S-003) |
| Rounds 1–4 and every failure | 001 (S-003) |
| Rounds 4b–8, three Apify accounts, Profile Scraper refresh | 001 (S-004) |
| GitHub push method, force-push to 40168a6 | 001 (S-003, S-006) |
| Context skills (`/context-write`, `/context-read`) location | CLAUDE.md; 001 (S-006) |
| Raw first planning chat | A.txt |

## Open decisions

1. LLM route: Anthropic API key vs AWS Bedrock ($100 credits; free-plan access
   unverified; Amazon Nova fallback). Bulk model: Opus 5.5 vs Haiku 5.5.
2. Weekly refresh budget: all 863 creators ≈ $2.25/run, more than one free
   Apify account covers per month — subset, rotate accounts, or pay.
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

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | unknown (≤ 2026-11-16) | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of transcript; context system set up | 001 |
| S-003 | 2026-11-16 → 17 | Apify research; pipeline; 270 creators; admin + demo; GitHub | 001 |
| S-004 | 2026-11-17 | Rounds 4b–8 on 3 Apify accounts → 1,010 creators; Profile Scraper refresh | 001 |
| S-005 | 2026-11-17 | Project location fixed (ojt/"brand deal matcher"); commands repointed | 001 |
| S-006 | 2026-11-17 | GitHub force-pushed to 40168a6; context commands → skills | 001 |

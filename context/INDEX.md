# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-17 (S-003).

## Where things stand

Brand Deal Matcher is a website for small/homegrown Indian brands: a brand
describes its product and gets ranked growing Instagram creators (1K–100K) with a
match score and a reason. The project lives in `~/Documents/brand deal matcher`
and is pushed to the private repo https://github.com/aarnavp25-sys/brand-deal-macher
(`main`, first commit 9c90af0). Design: `docs/product-design.md` (product, flows,
business) and `docs/data-and-matching.md` (verified Apify facts, pipeline,
taxonomy, matching, LLM/AWS notes; supersedes the older Apify/scoring parts).

A working prototype exists, all Python stdlib, all local. `pipeline/` scrapes
with Apify under hard spend caps, filters, computes metrics, classifies with
keywords (`keyword-v1`) into 16 categories and 42 product types, and loads
Supabase (project `yqaducvspzrqokcqwlga`, ap-south-1, free; 7 tables, RLS on,
no policies; raw JSON in Storage bucket `raw-scrapes`). Supabase held 270
creators / 226 usable (active, not fake) before the last round; every category
has 9–20 usable creators. `admin/` (port 8787) is a full local admin dashboard;
`demo/` (port 8788) is the brand-facing demo: brief → "We understood" →
~20 mixed creators (Specialist / Wider reach / Potential) with score breakdown
and a templated explanation. Keys live only in `admin/.env` (gitignored).

What is weak: classification is keyword-based, so product matches are noisy
(e.g. `rider_girls_pune` appears for men's jewelry because of "chain"), and
creator gender and content quality are empty. Brief parsing and explanations are
also keyword/template. All three wait for an LLM: no Anthropic key yet; the
user's AWS account has $100 credits (Free plan, until 2027-05-16) but Bedrock
access to Claude was never tried, and the user postponed AWS on 2026-11-17.

How S-003 ended: the user asked to spend the remaining Apify credit and to try
the Profile Scraper. A first round-4 script picked the wrong search terms; its
run was aborted at $0.26 (97 items recovered). The corrected `round4b.sh` was
still running in the background: remaining round-4 search (cap $0.40) → reels
(cap $0.30) → load → Profile Scraper on 15 top creators writing 2026-11-17
follower snapshots (the first second-date snapshots, i.e. first growth data).
Apify had $0.86 left before round4b; the cycle resets 2026-12-16.

Pending on the user: revoke the Supabase `sbp_…` token and regenerate the Apify
token (both were pasted in chat); delete the stray `~/Documents/ojt` folder.

## Continue from here

1. Verify round4b's result (its scratchpad log may be gone): in admin
   (`python3 admin/server.py`) check total/usable counts per category; in
   Supabase check `creator_snapshots` for rows dated 2026-11-17; check Apify
   usage (`/v2/users/me/limits`). Load anything that was scraped but not loaded.
2. Commit and push the uncommitted changes (round-4 terms in
   `pipeline/taxonomy.py`, `docs/data-and-matching.md`, docs pointer, context).
   Push needs `gh auth setup-git` once, or the `-c credential.helper` form in 001.
3. Next build step: LLM classification (`classification_method='llm'`) for all
   creators — fills products with evidence, gender, content style; then vision
   quality from thumbnails; then swap `parse_brief`/`explain` in `demo/server.py`
   to Claude. Needs either an Anthropic API key or a Bedrock test in us-east-1.
4. Before showing the demo: run its 6 example briefs and clean wrong product
   links in admin (start with `rider_girls_pune` → men's jewelry).

## Topic -> file

| Topic | File |
|---|---|
| Product idea, positioning, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, filters, what they return | docs/data-and-matching.md |
| Pipeline steps, metrics, fixes (median ER, posts/week, fake rule) | docs/data-and-matching.md; failures in 001 (S-003) |
| 16 categories, product types, search terms per round | pipeline/taxonomy.py; docs/data-and-matching.md |
| Matching: product fit, labels, weights, mix, explanation | docs/data-and-matching.md; demo/server.py |
| Why DB-first instead of live scraping | docs/data-and-matching.md |
| Claude model prices, Bedrock vs Claude Platform on AWS | docs/data-and-matching.md |
| AWS credits, card question | 001 (S-003) |
| Supabase schema, ref, keys handling | pipeline/schema.sql; 001 (S-003) |
| Admin dashboard features | admin/index.html; 001 (S-003) |
| Demo website and test briefs | demo/; 001 (S-003) |
| Every failed attempt in S-003 (network, timeouts, wrong terms, git push) | 001 (S-003) |
| GitHub repo and push method | README.md; 001 (S-003) |
| Context system rules | CLAUDE.md; 001 (S-002) |
| Raw first planning chat | A.txt |

## Open decisions

1. LLM route: Anthropic API key (needs a card/prepaid) vs AWS Bedrock with the
   $100 credits (free-plan access to Claude unverified; Amazon Nova fallback).
   Model for bulk classification: Opus 5.5 (default) vs Haiku 5.5 (~20x cheaper).
2. Weekly follower refresh: Apify (~$3/month for 300, over free tier with other
   work) vs local Instaloader vs Graph API. Profile Scraper test (round4b) is the
   first data point.
3. Phone numbers in scraped bios: hide from brands or not (DPDP).
4. Unlock price and what an unlock sells (handles are public).
5. When to deploy (Amplify/Vercel) — user said local only for now.

## Ruled out

- Budget/price fields; WhatsApp/concierge flow; creators >100K. (001, S-001)
- `relatedProfiles` snowball — Profile Scraper does not return it. (001, S-003)
- Followers-count scraper for cheap refresh — same price as a profile. (001, S-003)
- Live scraping at search time. (docs/data-and-matching.md)
- "Lifestyle" as a main category. (docs/data-and-matching.md)
- Raw Apify JSON in a jsonb column — statement timeout. (001, S-003)
- Chatbot, login, Instagram login, payment in the demo — later. (001, S-003)

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | unknown (≤ 2026-11-16) | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of transcript; context system set up | 001 |
| S-003 | 2026-11-16 → 17 | Apify research; 16-category pipeline; 270 creators in Supabase; admin + demo; GitHub | 001 |

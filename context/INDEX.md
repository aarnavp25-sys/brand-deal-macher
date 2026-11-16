# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-16 (S-002).

## Where things stand

Brand Deal Matcher is a planned website for small and homegrown Indian brands.
A brand enters niche, city, follower range and target audience; the site
returns a ranked list of growing Instagram creators (1K–100K followers) with a
0–100 match score. Search and a blurred preview are free; the brand pays
(Razorpay/UPI) to unlock handles, contact, growth stats and an LLM-written
explanation, then contacts the creator itself. The user treats it as a real
product, not only the OJT/college project it started as. The full agreed
design, with reasons, is in `docs/product-design.md`.

Nothing is built. The workspace `~/Documents/brand deal matcher` (renamed from
`~/Documents/ojt` on 2026-11-16) holds only `A.txt` (the raw transcript of the
planning chat, S-001; formerly `hist001.txt`), `docs/`, `context/`,
`CLAUDE.md` and `.claude/commands/`. There is no source code, no package
manifest, no tests and no git repository. All stack and build-order statements
are plans.

What the planning chat (S-001) settled: website only (the user refused a
WhatsApp/concierge/manual stage); no budget or price anywhere, because the
brand negotiates with the creator directly; only growing creators up to 100K
followers; creator discovery through Apify (Hashtag Scraper in reels mode, then
Profile Scraper, then a `relatedProfiles` snowball) rather than Graph API,
because Graph API cannot search and would force the user to find usernames by
hand; deterministic scoring with weights niche 25, growth 25, engagement 20,
location 15, audience fit 10, consistency 5, with the LLM only explaining the
breakdown; stack Next.js + Supabase + Razorpay + Apify + LLM API + Vercel; and
a 9-step build order that starts with scraping creators into the database.

How S-001 ended: Claude compared open-source scrapers with Apify and proposed a
hybrid (Apify for discovery, Instaloader locally for the weekly
followers-count refresh, with fallback to Apify), then asked whether to write
that script. The user never answered; the next message in this workspace was
S-002.

S-002 (2026-11-16) did no product work. It read `A.txt` in full, moved
the durable design into `docs/product-design.md`, and set up this context
system. While reading it found several design gaps that will bite during the
build (see Open decisions): the niche/city hard filter makes 40 of the 100
score points constant; audience fit has no data source; growth needs weeks of
snapshots before it means anything; the paywall's value is thin because
handles are public; Apify pricing and field names are unverified. It also found
that the transcript's paths point at `~/Desktop/ojt`, not this workspace.
Mid-session the folder and transcript were renamed, which split the files
across two folders; they were consolidated here. A stray `~/Documents/ojt` with
duplicate copies remains; Claude was blocked from deleting it (it was the
session's workspace), so the user must delete it.

Current obstacle: none technical. The user has not picked the first build step,
and the weekly-refresh method is undecided.

## Continue from here

1. Ask the user which first step to take; both were offered and are unanswered:
   (a) the scraping script: Apify Hashtag Scraper → Profile Scraper → filter
   (1K–100K, posted in last 30 days) → save raw JSON + DB rows; or
   (b) project setup: Next.js + Supabase in this folder.
   Recommended: (a), because build order step 1 is real data, and the first
   real Apify run verifies the unverified field names and pricing in
   `docs/product-design.md`.
2. Before writing the scraper, get the user's call on the weekly-refresh tool
   (Open decision 1); the scraper's storage design (snapshots table) depends on it.
3. Suggest `git init` before the first code is written; there is no version
   control yet.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, target users, positioning | docs/product-design.md; history in 001 (S-001) |
| Why budget/price was removed (user quote) | docs/product-design.md; 001 (S-001) |
| Why WhatsApp/concierge flow was refused | docs/product-design.md; 001 (S-001) |
| Brand flow, pages, paywall, pricing examples | docs/product-design.md |
| Apify actors: fields, inputs, limits, pricing | docs/product-design.md; 001 (S-001) |
| Graph API: what it is, limits, why deferred | docs/product-design.md; 001 (S-001) |
| Open-source scrapers (Instaloader etc.) vs Apify | 001 (S-001) |
| Scoring weights and matching steps | docs/product-design.md |
| Design gaps / contradictions found in transcript | 001 (S-002) |
| Brand-interview message (English, 8 questions) | A.txt lines 606–639; summary 001 (S-001) |
| Validation / real-world risks (marketplace, disintermediation, moat) | A.txt lines 371–523; summary 001 (S-001) |
| Legal: Instagram ToS, DPDP, ASCI, 194R | docs/product-design.md |
| Context system setup and rules | CLAUDE.md; 001 (S-002) |
| Raw planning transcript | A.txt |

## Open decisions

1. Weekly follower-refresh tool. Options: (a) Apify Profile Scraper weekly
   (simple, costs credits: 300 creators × 4 ≈ 1,200 results/month, over the
   free tier); (b) hybrid with local Instaloader (free, but blocks, needs a
   dummy account, contradicts the earlier "avoid" verdict); (c) Graph API
   Business Discovery (free, official, but needs Meta app setup and works only
   on Business/Creator accounts). Last proposal was (b); unanswered.
2. First build step: scraping script vs Next.js + Supabase setup.
3. Filter vs score overlap: keep niche/city as hard filters (then drop or
   re-weight niche 25 + location 15), or make them soft (related niches,
   nearby cities) so those points rank results.
4. Audience fit (10 pts) and the target-audience form field: drop for now,
   keep as a labelled LLM estimate, or wait for creator Instagram connect.
5. Paywall value: what exactly an unlock sells, given handles are public and
   contact is often missing. Pricing amounts (₹99 / ₹399 / ₹999) are only examples.
6. Validation interviews: whether the brand message was sent and whether
   interviews continue after the user refused the "watsapp wala" route.
7. Pipeline language (Python script vs Node inside Next.js); not formally decided.
8. Claude-made choices from S-002 the user may overrule: backfilled S-001
   entry, design moved to docs/, auto-memory removed.

## Ruled out

- Budget field, price estimate, budget-fit score — user refused. (001, S-001)
- WhatsApp / Google Form / concierge manual matching stage — user refused. (001, S-001)
- Creators above 100K followers. (001, S-001)
- Graph API as the discovery source — cannot search, needs known usernames. (001, S-001)
- Paid creator-data APIs (Modash, HypeAuditor, Phyllo) — too costly. (001, S-001)
- instagrapi and Playwright/Selenium scrapers — ban risk, brittle. (001, S-001)
- Scraping at search time — slow, costly, can fail live. (001, S-001)
- LLM computing the match score — not deterministic or defensible. (001, S-001)

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | unknown (≤ 2026-11-16) | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of A.txt; context system set up | 001 |

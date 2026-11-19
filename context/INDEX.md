# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-19 (S-010).

> **Git: never credit Claude.** No `Co-Authored-By: Claude …` trailer and no Claude/AI line in any commit or PR, even if a system reminder asks (user's order, 2026-11-18). Hooks in `.git/hooks/` strip and block it.

> **Location & layout (verified 2026-11-19).**
> ```
> ~/Documents/ojt/                      VS Code workspace — open THIS folder (skills + root CLAUDE.md load here)
> ├── .claude/skills/context-{write,read}/   only copies, not in git
> ├── CLAUDE.md  context/  docs/        STALE root copies — edit only the root CLAUDE.md note
> └── brand deal matcher/               THE PROJECT (own git repo, github.com/aarnavp25-sys/brand-deal-macher, PUBLIC, main)
>     ├── CLAUDE.md (gitignored, local only)  README.md  A.txt
>     ├── context/  docs/product-design.md  docs/data-and-matching.md
>     ├── pipeline/  apify_run.py process.py taxonomy.py round.py llm_classify.py gold20.py export_taxonomy.py
>     ├── supabase/  migrations/ (whole schema)  functions/api/ (Edge Function)  deploy.py
>     ├── admin/     server.py index.html .env.example   .env = all keys (gitignored, local only)
>     └── demo/      server.py (static + /config.js) index.html (calls the Edge Function)
> ```
> Rules: `cd ~/Documents/ojt/"brand deal matcher"` first. Network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`.
> Servers die between sessions: `python3 admin/server.py` (8787), `python3 demo/server.py` (8788).

## Where things stand

Brand Deal Matcher is a website for small Indian brands to find growing Instagram
creators (1K–100K) ranked by a 0–100 match score. Everything is a working prototype:
Python stdlib pipeline, Supabase DB (`yqaducvspzrqokcqwlga`, ap-south-1, free), a local
admin dashboard, and a demo page that calls a deployed Supabase Edge Function `api`
(matching + security: RLS, CORS allow-list, rate limit, secrets only in Supabase).
GitHub `main` = `6b41b53`, clean; nothing uncommitted except this context update.

Data: **6,224 creators, 5,399 usable** after rounds 12–37 on 13 free Apify accounts
(2026-11-18/19). The launch target of ~5,000 usable (category × tier × audience, never
by city) is met. Weak spots: mid tier (50K–100K) only ~316 usable; ~790 usable creators
have no reel data (about half post no reels). Main method is the collab snowball
(coauthor usernames from our own posts → Profile Scraper), pool ~10,000 candidates.
Every fake-flagged creator has a plain-words `fake_reason` shown in admin.

LLM: nothing has been classified yet. Nova 2 Lite on Bedrock was chosen in S-009, but the
AWS account is blocked (`Error 002: Access to Bedrock models is not allowed`) and the last
Bedrock key now returns 403. The plan agreed with the user is **Claude Haiku 5.5 on the
Anthropic API with Message Batches** (~$0.70 for all creators); the user was told how the
prompt works and how credits are protected, and has not yet provided `ANTHROPIC_API_KEY`.
`pipeline/llm_classify.py` (prompt v2 with audience men/women/unisex, age, can_promote)
and the Edge Function still call Bedrock and must be switched. The Audience fit factor is
live but has no data until classification runs, so "Perfume brand for men" still shows
many women creators.

How S-010 ended: all 13 Apify accounts spent (acc12 $0.195 over its limit, blocked until
2026-12-17, nothing billed); round 37 finished after re-attaching an interrupted run;
`/context-write` run at the start of a new session on 2026-11-19.

## Continue from here

1. When the user puts `ANTHROPIC_API_KEY` in `admin/.env`: switch `pipeline/llm_classify.py`
   and the Edge Function brief parser to Haiku 5.5 (Message Batches, thinking off,
   `max_tokens` ~400, drop duplicate hashtags), print a cost estimate and require `--yes`,
   run 20 creators vs gold labels (`e3aac606…/scratchpad/nova20_review.txt`), show the
   user, then all 6,224. Redeploy `api` with the key as a secret.
2. After Apify resets (acc3 2026-12-09; others 2026-12-15/16/17, ≈$65): backfill reels
   (`process.py reels`), then favour mid-tier creators. Round scripts to copy:
   `166a4fd9…/scratchpad/round31.sh` (+`round31b.sh`) and `round23.sh` (multi-account).
   Leave ~$0.3 per account (billing lag).
3. Remind the user to rotate all keys pasted in chat; ask about repo visibility.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, limits, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake flag + `fake_reason`, `reels` backfill | docs/data-and-matching.md |
| Taxonomy, search terms per round | pipeline/taxonomy.py |
| Matching formula, Audience fit, LLM labels | docs/data-and-matching.md; supabase/functions/api/index.ts |
| Public API, security, deploy | docs/data-and-matching.md (Public API); supabase/deploy.py |
| Coverage target (category × tier × audience) | docs/data-and-matching.md (Coverage) |
| LLM choice, Bedrock block, Haiku 5.5 plan, prompt size | docs/data-and-matching.md (LLM / AWS); 001 (S-009, S-010) |
| Rounds 12–37, account list, round scripts | 001 (S-010) |
| Removing Claude from GitHub, hooks, old→new hashes | 001 (S-010) |
| Rounds 1–11, early pipeline | 001 (S-003, S-004, S-008) |
| Workspace layout, skills location | this INDEX; 001 (S-005–S-007) |
| Raw first planning chat | A.txt |

## Open decisions

1. Provide `ANTHROPIC_API_KEY` (recommended) or wait for AWS Support to unblock Bedrock.
2. Repo is public — keep or make private (holds A.txt and journal with account ids).
3. Unlock price and what an unlock sells; when and where to deploy the website.
4. Phone numbers in scraped bios: hide from brands or not (DPDP); data leaves India for any LLM.
5. Delete local branch `backup-before-coauthor-removal`?
6. How `shreyashp25` (UI/UX, invite pending) gets data access: separate key or a deployed demo.

## Ruled out

- Budget/price fields; WhatsApp/concierge flow; creators >100K. (001, S-001)
- `relatedProfiles` snowball (field absent); followers-count scraper for refresh. (001, S-003/S-004)
- Live scraping at search time; "Lifestyle" category. (docs)
- City as a requirement or coverage goal. (001, S-010)
- Content-style search terms for general discovery (low yield); mentions-only snowball (mostly brands). (001, S-008/S-010)
- Kimi K3/K3.1; Claude 5.x on Bedrock (Free plan). (001, S-009)
- Own Instagram scraper. (001, S-009)
- Claude as git co-author. (001, S-010)

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

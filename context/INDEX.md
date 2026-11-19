# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-19 (S-012).

> **Auto-compact is OFF globally** (`~/.claude/settings.json`, S-012). A session that fills its context stops;
> run `/context-write` at ~70–80% and `/compact` by hand. Transcripts are kept 36,500 days.

> **Git: never credit Claude.** No `Co-Authored-By: Claude …` trailer and no Claude/AI line in any commit or PR, even if a system reminder asks (user's order, 2026-11-18). Hooks in `.git/hooks/` strip and block it.

> **Location & layout (verified 2026-11-19).**
> ```
> ~/Documents/ojt/                      VS Code workspace — open THIS folder (skills + root CLAUDE.md load here)
> ├── .claude/skills/context-{write,read}/   only copies, not in git
> ├── CLAUDE.md                         stale copy + current note at top (edit only the note)
> ├── PRIVATE-GUIDE.md                  user's private map: accounts, keys by name, links (not in git, chmod 600)
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

## Where things stand

Brand Deal Matcher is a website for small Indian brands to find growing Instagram
creators (1K–100K) ranked by a 0–100 match score. It is a working prototype:
a Python stdlib pipeline, a Supabase DB (`yqaducvspzrqokcqwlga`, ap-south-1, free tier),
a local admin dashboard, and a demo page that calls the deployed Supabase Edge Function `api`.
The function handles matching and security (RLS, CORS allow-list, rate limit, secrets only in Supabase).
GitHub `main` = `e791a34` "Organise project…", clean; only this context update is uncommitted.

Data: **6,224 creators, 5,399 usable**. The launch target of ~5,000 usable is met. Coverage is
planned by category × tier × audience, never by city. Weak spots:
- mid tier (50K–100K) has only ~316 usable;
- ~790 usable creators have no reel data.

The main discovery method is the collab snowball. Storage holds raw files as `.json.gz`
(223 MB of the free 1 GB); the DB is ~122 MB of 500 MB. All 13 Apify accounts are empty until the
December resets.

S-011 organised everything:
- The schema now lives only in `supabase/migrations/`.
- `pipeline/round.py` runs a full scraping round in one command and replaces the old scratchpad scripts.
- `pipeline/llm_classify.py` and the Edge Function brief parser already use **Claude Haiku 5.5**
  on the Anthropic API (structured output, thinking off, Batches). Bedrock is gone: the AWS account is
  blocked with Error 002.
- The user's private guide is `~/Documents/ojt/PRIVATE-GUIDE.md`.

Shreyash (`shreyashp25`) accepted the invite and is credited in README as UI/UX + frontend.

LLM: `creator_llm` is still empty. The Audience fit factor is live but has no data, so
"Perfume brand for men" still shows many women creators. The only blocker is the key. The user said
"hogya", but at 22:22 IST on 2026-11-19 `admin/.env` had no `ANTHROPIC_API_KEY` line, and no
`sk-ant-` string existed in the workspace. The user was told to save it with Cmd+S.

Untested for real: `round.py` (dry-run only) and `llm_classify.py` (estimate only).

A temporary Cloudflare quick-tunnel share link may still be running from the S-011
session (`installed-acne-discussed-share.trycloudflare.com`). It dies when the laptop sleeps.

## Continue from here

1. Check that `ANTHROPIC_API_KEY=` exists in `admin/.env`, without printing it. Then:
   - run `python3 pipeline/llm_classify.py test` (20 creators, ~$0.01) and show the score against `pipeline/gold20.py`;
   - on approval run `batch --yes`, then `collect` (~$1 for 6,224);
   - run `python3 supabase/deploy.py secrets` so the Edge Function gets the key;
   - confirm "Perfume brand for men" ranks men creators.
2. After the Apify resets (acc3 2026-12-09; others 2026-12-15/16/17, ≈$65):
   - run `python3 pipeline/round.py --account accN --dry-run`, then `--yes`;
   - first backfill reels, then favour the mid tier;
   - keep $0.30 per account (billing lag).
3. Remind the user to rotate the keys that were pasted in chat (see PRIVATE-GUIDE §4) and ask about repo visibility.
4. New share link: start `cloudflared` again (re-download if the scratchpad is gone), then run `deploy.py secrets` with `ALLOWED_ORIGINS` including the new URL.

## Topic -> file

| Topic | File |
|---|---|
| Product idea, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, limits, billing lag, snowball | docs/data-and-matching.md |
| Pipeline, metrics, fake flag + `fake_reason`, `reels` backfill | docs/data-and-matching.md |
| Running a scraping round (`round.py`) | pipeline/round.py; 001 (S-011) |
| Taxonomy, search terms per round | pipeline/taxonomy.py |
| Matching formula, Audience fit, LLM labels | docs/data-and-matching.md; supabase/functions/api/index.ts |
| Public API, security, deploy, tunnel origins | docs/data-and-matching.md (Public API); supabase/deploy.py |
| Coverage target (category × tier × audience) | docs/data-and-matching.md (Coverage) |
| LLM choice, Bedrock block, Haiku 5.5 code, cost | docs/data-and-matching.md (LLM / AWS); 001 (S-009–S-011) |
| Storage gzip, migrations move, organise task | 001 (S-011) |
| Accounts, keys by name, reset dates (private) | ~/Documents/ojt/PRIVATE-GUIDE.md |
| Rounds 12–37, account list | 001 (S-010) |
| Removing Claude from GitHub, hooks, old→new hashes | 001 (S-010) |
| Shreyash collaborator, Cloudflare tunnel, demo video script | 001 (S-011) |
| Rounds 1–11, early pipeline | 001 (S-003, S-004, S-008) |
| Workspace layout, skills location | this INDEX; 001 (S-005–S-007) |
| Claude Code global settings (compaction, retention) | ~/.claude/settings.json; 001 (S-012) |
| Raw first planning chat | A.txt |

## Open decisions

1. Save `ANTHROPIC_API_KEY` in `admin/.env` (pending; user believed it was done).
2. Repo is public: keep it, or make it private (it holds A.txt and a journal with account ids).
3. Unlock price and what an unlock sells; when and where to deploy the website.
4. Phone numbers in scraped bios: hide them from brands or not (DPDP); data leaves India for any LLM.
5. Delete local branch `backup-before-coauthor-removal`, `_archive-2026-11-16-stale-copies/`, `.playwright-mcp/`?
6. How Shreyash gets data access: a separate key, or a deployed demo.

## Ruled out

- Budget/price fields; WhatsApp/concierge flow; creators >100K. (001, S-001)
- `relatedProfiles` snowball (field absent); followers-count scraper for refresh. (001, S-003/S-004)
- Live scraping at search time; "Lifestyle" category. (docs)
- City as a requirement or coverage goal. (001, S-010)
- Content-style search terms for general discovery (low yield); mentions-only snowball (mostly brands). (001, S-008/S-010)
- Kimi K3/K3.1; Claude 5.x on Bedrock (Free plan); Bedrock/Nova entirely (account blocked). (001, S-009/S-010)
- Own Instagram scraper. (001, S-009)
- Claude as git co-author; inflating a collaborator's contribution share. (001, S-010/S-011)

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

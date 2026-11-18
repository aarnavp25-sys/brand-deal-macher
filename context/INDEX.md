# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`.
Read this every session. Read numbered files only when the topic map below
points to them, or when the user asks for full history.

Last rewritten: 2026-11-18 (S-009).

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
4f81073. **Uncommitted:** `demo/server.py` (1000-row fix), `docs/data-and-matching.md`
and this context update (S-009). Project `CLAUDE.md` still says "design only … no
git repo" — stale.

The prototype is Python stdlib and runs locally. `pipeline/` scrapes with Apify
under spend caps, filters/classifies with keywords (`keyword-v1`) into 16
categories and 42 product types (`taxonomy.py`, `ROUND5_TERMS`…`ROUND11_TERMS`) and
loads Supabase (`yqaducvspzrqokcqwlga`, ap-south-1, free). Supabase holds **1,356
creators, 1,168 usable**; every category has 43–113 usable. `admin/` (8787) and
`demo/` (8788) both page past PostgREST's 1000-row cap now. Apify: four FREE
accounts ($0.30 / $0.43 / $0.65 journal values; acc4 $0.37 live), resets
2026-12-15/16.

The LLM is now chosen: **Amazon Nova 2 Lite on Bedrock** (Sydney, AWS credits),
after a 20-creator test on 47 Bedrock models on 2026-11-18. Keyword-v1 is weak
(wrong product on ~17 of 20 creators, shops such as a bakery, a furniture store, a
gym and an arcade counted as usable creators). Nothing has been classified with
the LLM yet: the user said "abhii kuch mat karna mai kahu tabhii karna" — wait
for an explicit go. No Bedrock key is stored in the project (two keys were pasted
in chat; the long-term one belongs to IAM user `BedrockAPIKey-wxuw`).

How the last session ended (S-009): demo fixed and verified; long viva-prep
explanations (system, taxonomy, fake flag, refresh, costs); Bedrock model tests
and the Nova 2 Lite decision; then the user asked to turn off unused Claude Code
skills — a list of 28 `skillOverrides: off` entries for `~/.claude/settings.json`
was shown and is awaiting approval; `/usage` fixes await its pasted output.

## Continue from here

1. Do nothing on the project until the user says so. When asked: commit + push
   `demo/server.py`, docs and context (gh credential helper).
2. On the user's go: Nova 2 Lite (`global.amazon.nova-2-lite-v1:0`, Converse API,
   ≤2–3 parallel calls with retry on 403) for all 1,356 creators, written to new
   fields/table — never overwrite keyword-v1. Needs a Bedrock key from the user
   (put it in `admin/.env`, not chat). Then an image test for content quality.
3. Skill cleanup outside the project: apply `skillOverrides` only after "yes".
4. Fix the fake-flag defect in `process.py cmd_build` (docs: Metrics).
5. Refresh: build `process.py refresh` (Profile Scraper; reuse search reappearances);
   check Instagram Graph API Business Discovery limits before relying on it.
6. Remind the user to rotate both Bedrock keys and all pasted Apify/Supabase tokens.

## Topic -> file

| Topic | File |
|---|---|
| Workspace layout, where to work, what is stale | this INDEX; 001 (S-005, S-007) |
| Product idea, positioning, brand flow, paywall | docs/product-design.md |
| Why budget/price and WhatsApp flow were refused | docs/product-design.md; 001 (S-001) |
| Apify actors, prices, parallel limits, term yield | docs/data-and-matching.md |
| Pipeline steps, metrics, fake flag (+ defect), load gotchas | docs/data-and-matching.md |
| 16 categories, product types, search terms per round | pipeline/taxonomy.py |
| Matching: product fit, labels, weights, mix | docs/data-and-matching.md; demo/server.py |
| Why DB-first instead of live scraping | docs/data-and-matching.md |
| LLM choice (Nova 2 Lite), Bedrock limits, 47-model test, prices | docs/data-and-matching.md (LLM / AWS); 001 (S-009) |
| Kimi K3.1 evaluation | 001 (S-009); docs/data-and-matching.md |
| Profile refresh plan and costs, Graph API idea | 001 (S-009) |
| Supabase schema, ref, key handling | pipeline/schema.sql; 001 (S-003) |
| Admin dashboard, Apify credits card, demo website | admin/, demo/; 001 (S-003, S-008, S-009) |
| Rounds 1–4 / 4b–8 / 9–11 | 001 (S-003 / S-004 / S-008) |
| GitHub push method, force-push to 40168a6 | 001 (S-003, S-006) |
| Context skills location | CLAUDE.md; 001 (S-006) |
| Unused-skill cleanup (`skillOverrides`) | 001 (S-009) |
| Raw first planning chat | A.txt |

## Open decisions

1. When to run Nova 2 Lite on all creators (user will say). Where to store LLM
   labels: new columns vs a separate table.
2. Data locality (DPDP): Nova 2 Lite is `global`; in-region fallback is Claude
   Haiku 4.5 (`au.`), which needs the Bedrock use-case form and may not use credits.
3. Weekly/2-weekly refresh budget and whether to use the Instagram Graph API.
4. Phone numbers in scraped bios: hide from brands or not (DPDP).
5. Unlock price and what an unlock sells; when to deploy.
6. Skill cleanup list (28 skills) — approve or edit.

## Ruled out

- Budget/price fields; WhatsApp/concierge flow; creators >100K. (001, S-001)
- `relatedProfiles` snowball; followers-count scraper for refresh. (001, S-003/S-004)
- Live scraping at search time; "Lifestyle" as a category. (docs/data-and-matching.md)
- Raw Apify JSON in a jsonb column. (001, S-003)
- Flattening the project into the workspace root; commits only for moving files. (001, S-005)
- More than 3 parallel Reel Scraper runs on a free account; content-style search terms. (001, S-008)
- Kimi K3/K3.1 for classification: no better than Nova 2 Lite, ~16× cost, 3–4× slower. (001, S-009)
- Claude 5.x on this AWS account: blocked on the Free plan. (001, S-009)
- Own Instagram scraper for refresh: blocks and bans. (001, S-009)

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat; backfilled from A.txt | 001 |
| S-002 | 2026-11-16 | Deep read of transcript; context system set up | 001 |
| S-003 | 2026-11-16 → 17 | Apify research; pipeline; 270 creators; admin + demo; GitHub | 001 |
| S-004 | 2026-11-17 | Rounds 4b–8 on 3 Apify accounts → 1,010 creators | 001 |
| S-005 | 2026-11-17 | Project location fixed; commands repointed | 001 |
| S-006 | 2026-11-17 | GitHub force-pushed to 40168a6; context commands → skills | 001 |
| S-007 | 2026-11-17 | Repo `.claude/` mirror removed; workspace layout in context | 001 |
| S-008 | 2026-11-17 | Account 4: rounds 9–11 → 1,356 creators; admin fixes; 721f643 | 001 |
| S-009 | 2026-11-17 → 18 | Demo 1000-row fix; viva prep; 47-model Bedrock test → Nova 2 Lite; skill cleanup proposed | 001 |

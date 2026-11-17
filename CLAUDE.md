# CLAUDE.md — Brand Deal Matcher

## Orientation

> **Location (read first).** The VS Code workspace is `~/Documents/ojt`. The real project, its git repo
> and the only current context live in `~/Documents/ojt/brand deal matcher/`. Do every step inside that
> folder (`cd ~/Documents/ojt/"brand deal matcher"`): its `CLAUDE.md`, `context/INDEX.md`,
> `context/NNN-*.md` and `docs/` are the current ones. The `CLAUDE.md`, `context/` and `docs/` at the
> workspace root are stale S-002 copies kept on purpose — never read them as current, never write to them.


Brand Deal Matcher: a website where small/homegrown Indian brands find growing
Instagram creators (1K–100K followers), ranked by a 0–100 match score, and pay
to unlock their details. Started as the user's OJT project; the user treats it
as a real product.

Current state: **design only**. No source code, no package manifest, no tests,
no git repo. Read `context/INDEX.md` next for where things stand.

Files:
- `docs/product-design.md` — the agreed product design and the reasons behind it.
- `context/INDEX.md` — current state, next action, open decisions, topic map.
- `context/NNN-*.md` — append-only session journal (read on demand only).
- `A.txt` — raw transcript of the first planning chat (S-001); named
  `hist001.txt` until 2026-11-16. Its paths say `~/Desktop/ojt`; the project now lives in `~/Documents/ojt/brand deal matcher` (moved 2026-11-17).

## Build / run / test

No dependencies: Python 3 stdlib only. Secrets come from env / `admin/.env`
(gitignored), never from code.

- Admin dashboard (local only): `python3 admin/server.py` → http://127.0.0.1:8787
- Pipeline (`pipeline/`): `apify_run.py <actor> <input.json> <out.json> <max_usd> [run_id]`
  (needs `APIFY_TOKEN`; always pass a spend cap), then `process.py filter|build|load|raw`
  (load/raw need `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`). Schema: `pipeline/schema.sql`.
- Supabase project ref `yqaducvspzrqokcqwlga` (ap-south-1, free tier). RLS on, no policies.
- No tests yet. Website (Next.js) not started.

## Project conventions (design-level; no code conventions exist yet)

- Never scrape when a brand searches. Scraping runs offline into the DB;
  search reads only the DB.
- The match score is a deterministic weighted formula. The LLM only explains a
  score breakdown it is given; it never scores.
- Store raw scraper JSON so the same data is never paid for twice.
- Mark estimated fields (audience, anything LLM-inferred) as "estimated" in DB and UI.
- Creators above 100K followers are never stored.
- No budget/price features and no manual/WhatsApp flow — the user refused both.
- Facts from web pages (Apify pricing, field names) are unverified until a real
  run confirms them.
- The user writes in Hinglish. Reply in Hinglish unless they ask for English.
  Give one recommendation, not a survey.

## Context system (two-tier) — rules

Purpose: sessions end when the context window fills; this system carries state
into the next session.

Tier 1, always read: this file + `context/INDEX.md` (together under ~250 lines;
keep it that way). Tier 2, on demand: `context/NNN-topic-slug.md`. Read a
numbered file only when the INDEX topic map points to it or the user asks for
full history. Never read all numbered files at once.

Numbered files:
- Name `context/NNN-topic-slug.md`, zero-padded (001, 002, ...).
- Append-only. Never rewrite, summarise or delete.
- Target ~1000 lines; 900–1100 is acceptable.
- One session entry never spans two files. If it does not fit, start the next
  numbered file and put the whole entry there.

`context/INDEX.md` is the only mutable file in `context/`. Each
`/context-write` rewrites it fully with: Where things stand (deep prose),
Continue from here, Topic -> file, Open decisions, Ruled out, Sessions.

Entry format (separate entries with `---`; drop empty sections, never write N/A):

```
## S-NNN · YYYY-MM-DD · short title
Asked:        user's own words, verbatim, in their language; trimmed.
Done:         what happened, in order; real file/symbol names; commands with 1–2 line output summary.
Did not work: what failed and exactly how (error, wrong output, silent no-op); why, or "unknown".
Established:  new facts about machine/codebase/platform, or assumptions that proved wrong.
User decided: choices, refusals, changes, with their reason. Refusals are binding.
Open:         what is unfinished and where to pick it up.
```

What to record: ask "would this surprise someone later?" Yes → write it fully,
especially failed attempts. No → one line or skip. When unsure, write it.

Style: narration in English; user quotes verbatim in their language; absolute
dates (2026-11-16), never "today"/"kal"; write for a reader with zero memory
(name files and things, no "as discussed"); past tense, plain, no praise.

Skills: `/context-write` (run at ~70–80% context, not 95%) and
`/context-read [topic|all]` (run at the start of a new session). They live only at the
workspace root `~/Documents/ojt/.claude/skills/context-*/SKILL.md` (Claude Code loads
skills from the opened workspace); the repo carries no `.claude/` folder.

## docs/ vs context/ boundary

- `docs/` = durable product knowledge: how it works and why. Timeless;
  rewritten as the product changes.
- `context/` = journal: what happened on a date and what broke. Date-bound,
  append-only.
- A finding that outlives its session (why a capability was removed, a defect's
  root cause) goes in `docs/`; the context entry keeps a one-line pointer.
  Never write the same thing in both places.
- Create a new `docs/` file only when there is real durable knowledge for it.

---
description: Save this session to the context journal and rewrite context/INDEX.md
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

Record the current session in the two-tier context system defined in
`CLAUDE.md`. Run this at ~70–80% context, not at 95%: by then the start of the
session is compacted and small failed attempts, the most valuable part, are lost.

## 1. Pick the target file

- `ls context/` and take the highest-numbered `NNN-*.md`. `wc -l` it.
- Under 900 lines → append to it.
- 900 or more → create the next number (`NNN+1-topic-slug.md`, zero-padded,
  slug naming the main topic of the new file).
- If the entry would push the current file past 1100 → create the next file and
  put the whole entry there. Never split one entry across two files, never cut
  an entry to make it fit.
- Find the last `S-NNN` in `context/INDEX.md`; this session is the next number.

## 2. Decide docs/ vs context/

- Durable knowledge (how something works and why; why a capability was
  removed; a defect's root cause) → write or update the right file in `docs/`.
  The journal entry gets one pointer line.
- Date-bound events (what was done, tried, broke) → the journal entry.
- Never put the same content in both. Do not create an empty `docs/` file.

## 3. Write the entry (append-only)

Append after a `---` rule. Never edit earlier entries.

```
## S-NNN · YYYY-MM-DD · short title

Asked:        user's own words, verbatim, in their language (Hinglish stays Hinglish), trimmed to what matters.
Done:         what happened, in order. Real file and symbol names. Commands as run; output in 1–2 lines, never a dump.
Did not work: every attempt that failed and exactly how (error text, wrong output, silent no-op). Why, if known; "unknown" if not.
Established:  new facts about the machine, codebase or platform; assumptions that turned out wrong.
User decided: what the user chose, refused or changed, with their reason. Refusals are as binding as approvals.
Open:         what is unfinished and exactly where to resume.
```

- Drop empty sections. Never write "N/A".
- Filter each item by "would this surprise someone later?". Yes → write it in
  full, especially failures. No → one line or skip. When unsure, write it.
- English narration, verbatim user quotes, absolute dates (YYYY-MM-DD), past
  tense, no "as discussed" or "that file": name things. No praise.

## 4. Rewrite context/INDEX.md completely

Do not append. Keep it under ~250 lines combined with `CLAUDE.md`; every line
must earn its place. Sections, in order:

1. **Where things stand** — deep prose, not compressed bullets. Enough for a
   cold-start session: what exists, what is unfinished, what exactly was
   happening last time and how it ended, the current obstacle.
2. **Continue from here** — concrete next action with file and reason; if the
   session stopped mid-task, exactly where.
3. **Topic -> file** — every topic someone might come back for, mapped to the
   numbered file (and session) or `docs/` file that holds it.
4. **Open decisions** — pending user calls, with options.
5. **Ruled out** — tried and abandoned or refused; one line + file number.
6. **Sessions** — table: number, date, one line, file.

Update "Last rewritten" with the date and session number.

## 5. Report to the user

Tell the user, briefly:
- which numbered file was written; if a new file was created, why;
- line count of that file now, and of `context/INDEX.md`;
- what went to `docs/`;
- what you deliberately left out, so the user can overrule it.

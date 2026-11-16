---
description: Resume from the context journal: read INDEX, then only the relevant history
argument-hint: "[topic, optional]"
allowed-tools: Read, Glob, Grep, Bash
---

Resume work using the two-tier context system defined in `CLAUDE.md`.
Argument: `$ARGUMENTS` (empty, a topic, or `all`).

## 1. Always

- Read `context/INDEX.md` in full.
- Run `ls context/` (and `wc -l context/*.md`) to see what numbered files exist.

## 2. Numbered files, selectively

- No argument → read only the highest-numbered file (latest history).
- A topic → look it up in the INDEX "Topic -> file" table and read only the
  files (or `docs/` files) it lists. If the topic is not in the table, `grep`
  `context/` and `docs/` for it before reading anything whole.
- `all` → read every numbered file from 001 upward. If there are 4 or more,
  first tell the user the file count and total lines (rough token cost) and
  wait for them to confirm.
- Never read all numbered files unless the argument is `all`.

## 3. Report, then stop

Give a 6–10 line report:
- where things stand;
- how the last session ended;
- the next action from "Continue from here";
- decisions pending on the user.

Then stop. Do not start work until the user says what to do; they may have
changed their mind since INDEX was written.

## 4. Check against reality

The journal can be stale; the code cannot. Spot-check what INDEX claims
(files, functions, state) against the workspace. If something contradicts
INDEX, say so in the report and trust the code.

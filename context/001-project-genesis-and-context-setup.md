# Context journal 001 — project genesis and context-system setup

Append-only. Never rewrite, summarise or delete entries. Entries are separated
by `---`. A single entry never spans two files.

---

## S-001 · date unknown (≤ 2026-11-16) · Product planning chat (backfilled from A.txt)

Backfilled in S-002 from the raw Claude Code transcript `A.txt` (named
`hist001.txt` until 2026-11-16; 1674
lines, 14 user turns). The transcript carries no dates; the file was copied
into the workspace on 2026-11-16 at 12:43. The transcript's working directory
was `~/Desktop/ojt`, not the current `~/Documents/brand deal matcher`. Nothing was coded; the
only tool calls were two web fetches of Apify actor pages.

Asked:
- "Brand Deal Matcher ... AI-powered platform hai jo brands ko unke marketing campaigns ke liye suitable Instagram influencers/creators find karne mein help karega ... i want you to tell me the flow how thing goes and how i gathere the dat from yhe instagrm ... thr idem i a mcoing is i scrap with apify do you have any other openions"
- "mai ye homegrown brad aur creators aur chote brands aur creator ke liye bana raha hu taaki unke marketing ka budget naa ho toh bhii woh log reels pe product promote kar paye ... kya mai sahi soch rha hu"
- "mai isse college project ke baare mai nhii soch raha isse real world problem ki tarah soch raha hu"
- "phele mujhe ek msg bana ke de jo mai homegrown brand se puch saku" → then "english mai bata meri unse baat hoti rehti hai toh ek msg mai hii bata"
- "mujhe ek baar bta kya flow hoga ab"
- "mujhe ye watsapp wala aur ye sab nhii karna hau mujhe ek website banani hai jaha per search par brand pay karegi aur creator dhundegi"
- "budget jane de buget ka kya woh brand apne aap hi creator se baat kar ke dekh legi bas hum usse best creator dhund ke dge aur hum creator bhii waise rakhege jo growwing ho aur phele se bade creator na ho"
- "tu jo instagram graph api ke bare mai bata raha woh kya hai" → "but isme mujhe manually creators dhundne padege na" → "toh usse accha mai appify se direct creators dhund scrap kar lu toh"
- "apify se mujhe kya kya milegega ek baar dekh ke bata"
- "apify ke badle open source scrapper bhii use kar sakte locally chalake"

Done:
- Claude laid out a two-part architecture: offline data pipeline (scrape → enrich → DB) and live matching (filter → deterministic score → rank → LLM explanation of top results). Rule set: never scrape at search time.
- Compared data sources: Apify, Graph API Business Discovery, creator OAuth + Insights, Kaggle, own scraper, paid APIs (Modash/HypeAuditor/Phyllo).
- Re-scoped to homegrown brands + nano/micro creators; drafted a problem statement.
- Gave a real-world view: validate first (30–40 interviews), chicken-and-egg, monetization options, disintermediation, outcome data as the real moat, ASCI/DPDP/194R.
- Drafted a brand-interview message in Hinglish (3 messages), then a single English message with 8 questions (`A.txt` lines 606–639).
- Produced a website flow with free search, blurred preview, Razorpay unlock, dashboard, creator claim-profile, admin.
- After the budget removal, replaced budget/price with a growth score and a 1K–100K follower cap; new weights niche 25, growth 25, engagement 20, location 15, audience fit 10, consistency 5.
- Explained Instagram Graph API (Business Discovery, Insights, limitations, setup steps).
- Fetched https://apify.com/apify/instagram-profile-scraper and https://apify.com/apify/instagram-hashtag-scraper (both 200 OK) and listed fields, gaps and pricing.
- Compared open-source scrapers (Instaloader, instagrapi, Playwright/Selenium) with Apify; recommended a hybrid.
- Session ended on Claude's unanswered question: "Kya main is hybrid setup ka script likh doon? Apify discovery + Instaloader weekly refresh + database."

Established:
- Apify facts (fields, limits, pricing: $5/month free credit, about $2.60 per 1,000 results) as read from the actor pages; recorded in `docs/product-design.md`. Unverified against a real run.
- Scraping never yields audience age/gender/city, follower history, or contact info beyond the bio.
- Graph API Business Discovery needs a known username (no search), only works on Business/Creator accounts, needs Meta app + Facebook Page + App Review. Meta has two API variants (Facebook Login vs Instagram Login); Business Discovery is in the Facebook Login variant.
- Instaloader: hashtag feature often broken, blocks fast without login, login risks the account and IP.

User decided:
- Target: homegrown/small brands and growing creators; treat as a real product, not a college project.
- Website only. Refused the WhatsApp/concierge/manual flow ("mujhe ye watsapp wala aur ye sab nhii karna hau").
- Brand searches, pays, and contacts creators itself.
- Budget and price removed entirely; brand negotiates directly.
- Only growing creators, 1K–100K; no big creators.
- Discovery via Apify instead of Graph API, because Graph API would need usernames found by hand ("isme mujhe manually creators dhundne padege na").
- Asked for the brand-interview message in English, as one message, because the user already talks with these brands.

Open:
- Hybrid refresh (Apify discovery + local Instaloader weekly followers refresh) was proposed but not accepted or rejected.
- Whether the brand-interview message was sent, and whether interviews still happen after the "watsapp wala" refusal, is unknown.
- No code exists. Claude's repeated offer to set up Next.js + Supabase or write the Apify script was never answered.

---

## S-002 · 2026-11-16 · Deep read of A.txt and context-system setup

Asked:
- "hist0001 file se cotext ache se consume kar lo samaj lo"
- "Is project me ek context-management system setup karna hai. Mujhe har chat ke end me context save karna hota hai kyunki context window jaldi bhar jaati hai aur main naya session shuru karta hoon - purana context kho jata hai, yahi rokna hai." Full spec given inline: two-tier system (CLAUDE.md + context/INDEX.md always read; numbered files on demand), append-only numbered files of about 1000 lines, INDEX rewritten every write, docs/ vs context/ boundary, entry format, `/context-write` and `/context-read` commands, seed this session as 001.

Done:
- Listed the workspace, then `~/Documents/ojt`: only `hist001.txt` (94,936 bytes, 1674 lines, UTF-8, mtime 2026-11-16 12:43). No hidden files, no source, no README, no config.
- `git status` → "fatal: not a git repository". No history to read.
- Read `A.txt` in full; summarised it to the user in Hinglish.
- In the first turn, saved a Claude auto-memory `brand-deal-matcher-project.md` with the product decisions. Removed it (and emptied the memory `MEMORY.md` index) later in this session because `CLAUDE.md`, `docs/` and `context/` now hold the same facts.
- Created `docs/product-design.md`, `CLAUDE.md`, `context/INDEX.md`, this file, `.claude/commands/context-write.md`, `.claude/commands/context-read.md`.

Did not work:
- Files appeared to vanish. The first Write of `docs/product-design.md` and of this file (12:47–12:48) returned "File created successfully", but a later `find . -type f` in `~/Documents/ojt` showed neither file, and `wc -l docs/*.md` failed with zsh "no matches found". Both files were written again, and `hist001.txt` was then also missing. Cause found: around 12:48, between Claude's writes, the folder `~/Documents/ojt` was renamed to `~/Documents/brand deal matcher` and `hist001.txt` was renamed to `A.txt` (same 94,936 bytes). The first two files moved with the renamed folder; the next Writes (`CLAUDE.md`, `context/INDEX.md`, both command files) recreated a new, empty `~/Documents/ojt`. The project was split across two folders. Fix: all files were copied into `~/Documents/brand deal matcher` (newer versions overwrote the older drafts there), references updated (`hist001.txt` → `A.txt`, workspace path), and Claude tried to delete the stray `~/Documents/ojt` (containing only Claude's six files). `rm -r ~/Documents/ojt` was blocked by Claude Code's built-in safety check because it was the session's workspace directory; the folder was left for the user to delete. Lesson: if files go missing, check whether the folder was renamed or moved (`ls -la ~/Documents`) before rewriting anything; Write recreates missing parent folders silently.

Established:
- Project location from 2026-11-16 12:48: `~/Documents/brand deal matcher`; transcript file `A.txt`. The old names `~/Documents/ojt` and `hist001.txt` no longer exist.
- The project is design-only. There is no code, no build, no tests, no git. Every "stack" and "build order" in `A.txt` is a plan.
- Path mismatch: `A.txt` shows cwd `~/Desktop/ojt`; the real workspace is `~/Documents/brand deal matcher`. Any path in the transcript refers to the Desktop location.
- Internal contradictions and gaps found in `A.txt` (all also listed in INDEX "Open decisions"):
  - Instaloader was rated "❌ Avoid" early (own-scraper row of the data-source comparison) and then recommended for weekly refresh in the last turn.
  - The weekly-refresh tool changed three times: Apify → Graph API Business Discovery → Apify only → hybrid Apify + Instaloader (unconfirmed).
  - The matching engine hard-filters on niche and city, then awards niche match 25 and location 15. For exact-match filters those 40 points are the same for every result and do not rank anything. They only work if the filter is soft (related niches, nearby cities).
  - Audience fit (10 points) and the "target audience (age, gender)" search field have no real data source under Apify-only; it would be an LLM guess.
  - Growth score (25 points) needs 3–4 weeks of weekly snapshots; at launch it can only use proxies (reel reach, engagement trend, consistency).
  - The paywall sells "Instagram handle + contact", but handles are public and contact exists only when a creator put it in the bio.
  - Apify pricing and field names come from web pages read on an unknown date and were never checked against a real run.
  - The early "Finalized MVP" list (budget, ₹20,000 example) is superseded by the budget removal.

User decided:
- Context system design as specified in the pasted spec (two-tier, append-only, INDEX rewrite, docs/context boundary).
- Asked where the context system should live after the rename; chose `brand deal matcher` (Claude's recommended option) over moving back to `ojt` or leaving both folders.

Open:
- Next product step not chosen: write the scraping script (Apify discovery, refresh method pending) or set up the Next.js + Supabase project.
- The VS Code workspace and this Claude Code session were still pointed at `~/Documents/ojt`; the next session must be opened at `~/Documents/brand deal matcher`. Claude Code's auto-memory folder is keyed on the project path, so the new path starts with an empty one (the old one was emptied anyway).
- Stray `~/Documents/ojt` still exists (copies of `CLAUDE.md`, `context/`, `docs/`, `.claude/commands/`; nothing unique). User to delete it by hand.
- Claude-made choices for the user to confirm or overrule: S-001 numbered as a backfilled session in this file; product design placed in `docs/product-design.md`; auto-memory removed.

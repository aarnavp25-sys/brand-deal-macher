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

---

## S-003 · 2026-11-16 → 2026-11-17 · Apify research, 16-category data pipeline, Supabase, admin + demo, GitHub

Same Claude Code conversation as S-002 (workspace still opened at the stray `~/Documents/ojt`; all files live in `~/Documents/brand deal matcher`). Durable results are in `docs/data-and-matching.md`.

Asked:
- "abhi mujhe ek baar mera work flow samjha do" → "brand deal matcher ke liye"
- (pasted an Apify API token) "ispe instagram scapper dhund aur apne use case ke liye acche se dekh ki data scrap karta hai ... सारे parameters देख ले, कोई filter डालने का option आ रहा है ... 100K से नीचे"
- "कितने कैटेगरीज बना सकते हैं ... हर कैटेगरी में हमें कितने क्रिएटर्स रखने चाहिए ... प्रोटोटाइप ... डेमो" → "तुमने जैसे बहुत सारे मेन जाने दिए, टैक है ... स्पोर्ट्स ... एंटरटेनमेंट"
- Men's jewelry walkthrough; per-creator "पॉसिबल टारगेट ... उसने क्या क्या चीज़ों पे रील बनाई है"; watch specialist vs fashion creator; "दोनों को मिक्स ऑफ बोथ मिलना चाहिए ब्रांड को ... 20-30 क्रिएटर्स ... एडिटिंग अच्छी है, ये क्रिएटर्स की रीच अच्छी है"
- "एग्जैक्ट वर्क फ्लो बता ... LLM मॉडल यूज़ करेंगे, क्या क्या मॉडल"; AWS credits; "live scraping better रहेगा या फिर पहले से स्क्रैप करा हुआ"
- (pasted Supabase access token `sbp_…`) "tere pass total 4 dollars hai apify ke aur tujhe abhii haar category ke kuch creators dhundne hai aur usse superbas mai sotore kar"
- "एक एडमिन डैशबोर्ड बना दे ... एडिट कर पाऊँ ... फ़िल्टर ... एक दिन पहले का, 2 दिन पहले का ... क्लोज पे रन करना, डिप्लॉय वगैरह नहीं करना"
- "डेमो दिखाने के लिए एक वेबसाइट ... चैटबॉट ... इंस्टाग्राम यूज़र खुद से लॉगिन ... ये सब अभी मत डालना ... कोई आए ब्रांड ... एक्सप्लेन करे ब्रांड के हिसाब से और हम दिखा पाए"
- AWS "100 credits mil gaye hai abhi bata mai kya karu" → "kahi pe bhi credit card ... daalna padega" → "haa toh th k hai isse jana abhi ke liye"
- "baaki credits se naaye creators dhund ke supabase mai add kardo"; "yaha git repo bana li hai yha push hi kar do"; "instagram profile scrapper bhii use karke dekh lena"

Done:
- Explained workflows; design answers moved to `docs/data-and-matching.md`.
- Apify research: listed store actors, read input schemas and pricing via API, ran tests (~$0.10): hashtag #punefoodie 15 reels, search "pune food blogger" 15, profile 6, followers-count 3, reel 2×6.
- Supabase: applied `pipeline/schema.sql` via Management API (`/v1/projects/yqaducvspzrqokcqwlga/database/query`), 7 tables, RLS on with no policies; later added `raw_scrapes.storage_path`.
- Wrote `pipeline/taxonomy.py`, `pipeline/apify_run.py` (spend cap via `maxTotalChargeUsd`, retries, re-attach), `pipeline/process.py` (filter/build/load/raw).
- Search round 1 (47 terms × 15, $1.44, 533 items, run jvxxSuKnPnFxBjuZD), round 2 (19 city terms, $0.55, 202 items, run gkdquUu4E5RzFkCEn), reels 223×2 (~$1.17) → loaded 223 creators, 2,771 posts, 1,081 product links; 187 usable.
- Round 3 (20 terms, $0.45, 160 items) + reels 47 → 47 new creators loaded; totals 270 / 226 usable.
- Built `admin/server.py` + `admin/index.html` (port 8787): overview KPIs incl. added last 24h/2d/7d, creators table with all filters, date range, sort, bulk status/category/delete, CSV, edit drawer with products and posts, taxonomy editor, scrape runs, auth users. Tested with curl and Playwright.
- Built `demo/server.py` + `demo/index.html` (port 8788): brief → "We understood" chips → ~20 mixed creators with score, label, breakdown bars, templated explanation. Tested 6 briefs.
- Fixed posts_per_week in DB with one SQL update (median now 1.96).
- Wrote `README.md`, `.gitignore`; `git init`, commit 9c90af0, pushed to private repo https://github.com/aarnavp25-sys/brand-deal-macher (main).
- Updated `CLAUDE.md` Build/run section.

Did not work:
- `apify_run.py` polling crashed: `ConnectionResetError: [Errno 54] Connection reset by peer`. The Apify run kept going server-side; re-attached by run id. Added retries (never retry the POST that starts a run — could start a second billed run).
- Dataset download with `limit=1000` hit `TimeoutError: The read operation timed out` (profile items are large). Fixed with pages of 100 through the retrying `call()`.
- `python3 -I process.py` → `ModuleNotFoundError: No module named 'taxonomy'` (`-I` drops the script dir from sys.path). Fixed with `sys.path.insert` in process.py.
- Inline `python3 -c` with `\"` inside f-strings → `SyntaxError: unexpected character after line continuation character` (several times). Use heredoc script files.
- Loading raw Apify JSON into `raw_scrapes.items` jsonb → HTTP 500 `57014 canceling statement due to statement timeout`. Raw JSON now goes to Storage bucket `raw-scrapes`.
- Mean-based ER gave 591% (viral post) → switched to median; `piyush.zgamer` still ~590% (data anomaly, left in DB).
- posts_per_week was 1.4 for everyone (12 posts / 8.57 weeks) → span-based `posting_rate()`.
- Fake rule "ER <0.5% at ≥10K" flagged accounts with 98x reel reach → added reach <0.3 condition (31 flagged).
- Brand pages passed the filter (`7days_mens_wear`, bio "Premium Quality Only") → `BRANDISH` regex sets `status=review` (5 accounts).
- Demo matching v1: "cakes" not matched (no plural forms); "gaming accessories" ranked Jewelry first; keyword product evidence false positives (`rider_girls_pune` via "chain", `babyshower_dance_group_morya_` via "ring"); gamers got 0 Specialist labels. All fixed in `demo/server.py`; `rider_girls_pune` still shows as #2 "wider" for men's jewelry (fix data in admin).
- Profile Scraper has no reel views and no `relatedProfiles` (0/21) — snowball plan dead.
- `git push` over HTTPS: `fatal: could not read Username for 'https://github.com': Device not configured`. Pushed with `git -c credential.helper= -c credential.helper='!gh auth git-credential' push` (no global config change).
- Round 4 first attempt (`round4.sh`): term list built as `[x for v in EXTRA_SEARCH_TERMS.values() for x in v][-22:]`, which flattens by category and picked round-3 terms too. Its run id was hidden by `| tail -1`. Found via `/acts/apify~instagram-search-scraper/runs?desc=1`, aborted run rn4Qji7O28b4GLCrF at $0.26 (97 items, recovered). Retried with a hardcoded list (`round4b.sh`).
- Playwright click with a non-unique selector failed in strict mode (matched 50 cells); use `:first-child`.

Established:
- Apify facts, Claude/AWS pricing and matching design: see `docs/data-and-matching.md`.
- Apify spend this cycle: $4.137 after the abort, before round4b.
- Supabase: project ref `yqaducvspzrqokcqwlga`, ap-south-1, free, Postgres 17; legacy `service_role` key works for PostgREST and Storage. Kept locally only in `admin/.env` (gitignored, mode 600).
- Git identity on this Mac: `aarnavp25-sys` / university email; `gh` logged in as aarnavp25-sys.
- AWS: Free plan, $100 credits until 2027-05-16; Bedrock access for Anthropic models not tried.
- Instagram bios contain phone numbers (e.g. WhatsApp) — DPDP decision needed before showing to brands.

User decided:
- 16 categories, including Tech, Sports, Gaming, Entertainment (user: "ये सारी चीज़ें तो भूल ही गया").
- Per-creator product list (proven/possible) is the user's own idea; results must mix specialists and wider creators, 20–30, and rank by quality (editing, reach) too.
- Admin and demo run locally only; no deploy. Demo excludes chatbot, login, Instagram login and payment for now ("ये सब अभी मत डालना ... बाद में लास्ट में").
- AWS work postponed ("isse jana abhi ke liye").
- Spend all remaining Apify credit on more creators; push the project to GitHub.

Open:
- `round4b.sh` (scratchpad, background task) was running when this entry was written: 12 remaining round-4 terms (cap $0.40) → reels (cap $0.30) → load → Profile Scraper on 15 top creators (cap $0.05) writing 2026-11-17 follower snapshots (first growth data). Next session: check Supabase counts, `creator_snapshots` with 2 dates, and Apify usage. Scratchpad files may be gone.
- Uncommitted: round-4 terms in `pipeline/taxonomy.py`, `docs/data-and-matching.md`, the pointer line in `docs/product-design.md`, this journal entry, INDEX.
- LLM classification not done (no Anthropic key; Bedrock untested); gender and content quality columns empty.
- User should revoke the Supabase `sbp_…` token and regenerate the Apify token (both pasted in chat).
- Stray `~/Documents/ojt` still exists (Claude was blocked from deleting it in S-002).
- Admin (8787) and demo (8788) servers were running in the background.

---

## S-004 · 2026-11-17 · Rounds 4b–8 across three Apify accounts → 1,010 creators; Profile Scraper refresh

Same conversation as S-003, after its /context-write. Load gotchas are in `docs/data-and-matching.md` ("Load gotchas").

Asked:
- "dono apify account ka bata" → "<YOUR_API_TOKEN> ... ye token le isske bhi sare credits use karle" (placeholder, no token) → pasted account-2 token: "ye le aur instagram profile scrapper bhii try karke dekhna"
- "haa acc 2 se 1.82 doloors bhii use kar lo"
- pasted account-3 token: "ye le isse bhii cretors lete jaa" → "bacche hue 1.36 dollors bhi use kar lo"
- "mujhe ye bata ki 223 phele the aur tune sirf 40 add kiye"; "saare tune admin dashboard mai add karde"; "abhii mujhe admin dashbird bata"

Done:
- round4b finished (account 1): +37 creators; Profile Scraper on 15 top creators wrote 2026-11-17 snapshots ($0.04).
- Committed/pushed 4cc2b93 (docs, S-003 journal).
- Round 5 (account 2, `ROUND5_TERMS` 64 terms, Delhi/Bangalore/Hyderabad): search 636 items $1.76, reels 226 creators $1.14, +226 creators; Profile Scraper refreshed 100 existing creators ($0.25, 0 errors) → 115 creators now have 2 snapshot dates. Commit 6a450ca.
- Round 6 (account 2, `ROUND6_TERMS` 28 terms): +110 creators (search ~$0.83, reels $0.56). Commit 88d2a0f.
- Round 7 (account 3, `ROUND7_TERMS` 64 terms, tier-2 cities): search 748 items $2.02, reels 320 creators $1.60, +320. Commits a644ac7, 3df1f14.
- Round 8 (account 3, `ROUND8_TERMS` 19 terms, thinnest categories): search 174 items $0.47, reels 47 creators $0.24, +47. Commit 490a342.
- Round scripts were derived with `sed` from the previous round's script (`round5.sh` … `round8.sh` in the session scratchpad) and verified (terms dict, caps, token file) before running.
- Opened the admin dashboard with `open http://127.0.0.1:8787`.

Did not work:
- Round 5 load: posts upsert of 500 rows → `TimeoutError: The read operation timed out`; creators were loaded, posts/products/raw were not. Fixed `upsert()` (posts batch 100, retry on OSError) and re-ran `process.py load` for round 5.
- Round 7 load: `HTTP 500 {"code":"21000", ... "ON CONFLICT DO UPDATE command cannot affect row a second time"}` at posts rows 3100–3200 (same collab reel id under two creators). Fixed with dedupe in `cmd_load`; reloaded round 7 (3,955 posts, 1,644 product links).
- The round scripts pipe `process.py load` into `grep`, so a Python failure did not stop `set -e`; failures only showed in the log. Check logs for Traceback after every round.
- The user's pasted URL `https://api.apify.com/v2/users/me/usage/monthly?token=<YOUR_API_TOKEN>` contained no token; asked for the real one.

Established:
- Totals after round 8: 1,010 creators, 863 usable (active, not fake), 12,515 posts, 5,037 product links. Usable per category 31 (Jewelry) to 92 (Travel). Cities: Pune 103, Mumbai 77, Delhi 56, Kolkata 54, Lucknow 53, Bangalore 53; ~208 unknown.
- Apify balances 2026-11-17: account 1 $0.30, account 2 $0.43, account 3 $0.65 (all FREE, reset 2026-12-15). Tokens are in session-scratchpad files `.token`, `.token2`, `.token3` only.
- Profile Scraper (100 profiles): 0 errors, still no reel views and no relatedProfiles; usable for the weekly follower refresh at $0.0026/creator.
- Cost per usable creator ≈ $0.017 (search + 2 reels).

User decided:
- Spend all remaining credit on all three Apify accounts on more creators.
- Use the Profile Scraper (for refresh) — tried and kept.

Open:
- LLM classification still not done; product matching is keyword-noisy; gender and quality empty.
- Weekly refresh: run Profile Scraper on all usable creators once a week to build growth (~$2.25/week for 863 — more than one free account covers per month).
- User must revoke/regenerate: Supabase `sbp_…`, Apify tokens for accounts 1, 2, 3 (all pasted in chat).
- ~$1.38 left across accounts; next full credit 2026-12-15/16.

---

## S-005 · 2026-11-17 · Project location confusion fixed; context commands repointed

Asked:
- "uss brand deal macher folder ko yaha leke aao , ok yaha se hi sab control hoga"
- "mera matlab tha ki ek alag folder bana k uske ander sab rakhte jo repo me bhi hai"
- "jo already root folder me tha waise hi rakho , jo brand deal macther wala folder ko yaha move karna tha alag se aur git uske ander hi rahte settupoed jaisa tha , uso commit push ki need nahi thi ?"
- "iss cheej ko completely ach se context me uodate kar do ... kaha actual me kaam kar rahe hai aur jaha actual context hai" and "/context-wrie and read wali command kaam nahi kr rahi inhe fix karo"

Done:
- Final layout: VS Code workspace `~/Documents/ojt` (root keeps its stale S-002 `CLAUDE.md`, `context/`, `docs/`, `.claude/`, plus `.playwright-mcp/`); the project with its own `.git` is `~/Documents/ojt/brand deal matcher/`. `~/Documents/brand deal matcher` no longer exists.
- Local repo reset to 40168a6 (state before the moves); `admin/.env` kept.
- Added a "Location (read first)" block to: root `CLAUDE.md` and root `context/INDEX.md` (marked STALE COPY), both copies of `.claude/commands/context-write.md` and `context-read.md`, inner `CLAUDE.md` and inner `context/INDEX.md`. It says all context work happens inside `brand deal matcher/`.
- Saved a Claude auto-memory note with the location.
- Restarted admin (8787) and demo (8788) from the new folder.

Did not work:
- Claude first flattened the project into the `ojt` root (commit e4e1ead, pushed), then into `ojt/brand-deal-macher/` (commit 0bbaa3b, pushed). Both misread the request; the user wanted the folder moved as-is next to the root files, with no commits. Root files had been moved to a scratchpad backup during this and were restored.
- `/context-write` and `/context-read` misbehaved because Claude Code loads them from the workspace root `ojt/.claude/commands` and their paths were relative to the root, i.e. the stale `context/`; while the root `.claude` was in the backup they did not exist at all.

Established:
- Claude Code loads slash commands and `CLAUDE.md` from the opened workspace (`~/Documents/ojt`), not from the project subfolder; commands must name the subfolder explicitly.

User decided:
- Keep the workspace root as it was; project stays a separate folder with its own git; do not commit or push just for moving files.

Open:
- GitHub `main` still has e4e1ead and 0bbaa3b (path notes only); local is "behind 2". User to choose: leave them, or force-push back to 40168a6.
- The S-005 notes in inner files are uncommitted on purpose (user asked for no commits).

---

## S-006 · 2026-11-17 · GitHub reset to 40168a6; context commands → skills

Asked:
- "git ko jo tumne push kiia tha wrong formt me use bhi fix kar do / GitHub se hata do. Main git push --force se GitHub ko wapas 40168a6 pe le"
- "aur fir ahe se cintext update kar do / aur skill command bhi fix karo"

Done:
- `git push --force-with-lease=main:0bbaa3b origin 40168a6:main` (with the gh credential helper). Verified with `gh api repos/aarnavp25-sys/brand-deal-macher/commits/main` → 40168a6. Commits e4e1ead and 0bbaa3b are gone from GitHub.
- Converted `.claude/commands/context-write.md` and `context-read.md` into skills `.claude/skills/context-write/SKILL.md` and `.claude/skills/context-read/SKILL.md` (added `name:`; body and Location block unchanged), at both `~/Documents/ojt/.claude/` (the copy Claude Code loads) and the repo's `.claude/`. Removed the old command files.
- Updated inner `CLAUDE.md` (skills location) and `context/INDEX.md` (GitHub state, S-006 row; removed the force-push decision).

Did not work:
- `git fetch` without the gh credential helper → `fatal: could not read Username for 'https://github.com': Device not configured`. Every network git command needs `-c credential.helper= -c credential.helper='!gh auth git-credential'` until the user runs `gh auth setup-git`.

Established:
- GitHub `main` = 40168a6. Local repo has uncommitted edits (S-005/S-006 notes, skills move), left uncommitted because the user did not ask to commit.

Open:
- Reload the VS Code Claude panel so the skills are picked up.

---

## S-007 · 2026-11-17 · Repo `.claude/` mirror removed; workspace layout written everywhere

Asked:
- "repo me .caude kyo hai waise agar need nahi hai to hata k updated code push kar do ache se"
- "ye sab bhi context me update kar do ache se saari cindition ki kaha kaam karna hai ctuak root me kya kya hai wo sab"

Done:
- Removed `.claude/` from the repo (`git rm -r --cached .claude`, deleted locally, added `.claude/` to `.gitignore`); the skills stay only at `~/Documents/ojt/.claude/skills/`. Committed with the S-005/S-006 context as 25b8c02 and pushed; GitHub root now lists `.gitignore A.txt CLAUDE.md README.md admin context demo docs pipeline`.
- Replaced the short "Location" note with a full "Location & layout" block (tree of `~/Documents/ojt` and the project, what is stale, where `.env` files are, rules for git, skills and servers) in: root `CLAUDE.md` and root `context/INDEX.md` (marked STALE COPY), project `CLAUDE.md`, project `context/INDEX.md`, both skill files. Updated the `project-location` auto-memory.

Established:
- Skills at `~/Documents/ojt/.claude/skills/` are not under version control; a deleted or broken skill cannot be restored from git.

Open:
- `pipeline/.env` (Apify token) does not exist; create it before the next scraping run.

---

## S-008 · 2026-11-17 · Rounds 9–11 on Apify account 4 (parallel runs); admin 1000-row fix and credits card

Asked:
- "hinglish me baat karna ok" + `/context-read`
- "3 account mai kitne credits baaki hai"
- pasted a new Apify token: "ye le aur creators laa"
- "kya tu script ko bahut sare instance me chalake ek sath bahut speed nahi badha sakte kya ki ek bar m ahe se credts use karke userd bahut speedme scrap ho ske"
- "haa ab ache se jitni speed me kaise bhi bas full speed me scrap karna hai"
- "waise abhi kitni speeed hai ? per minute ?"; "kitne creators hue"; "aur acc mai credits"
- "update kar lo admin mai"; "haa saari cheeze git pe push karde"; "kar de" (this /context-write)

Done:
- `/context-read`: no live balance possible for accounts 1–3 (no tokens stored; old scratchpad `.token*` files gone), answered from the S-004 journal ($0.30 / $0.43 / $0.65).
- The pasted token was a new, fourth account: username `obeying_mussel`, FREE, $5, $0 used, cycle 2026-11-17 → 2026-12-16. Token saved only to this session's scratchpad `.token`, later also to `admin/.env` as `APIFY_TOKENS=acc4:…` (gitignored).
- Old round scripts were still on disk in the S-004 scratchpad (`/private/tmp/claude-501/-Users-aarnavmathakiya-Documents-ojt/ef84ece9-…/scratchpad/round4.sh … round8.sh`, plus `data/rows*.json`); round 9 was built from `round7.sh` with the new project path.
- Added `ROUND9_TERMS` (72 terms: NCR, Vadodara, Nashik, Dehradun, Patna, Coimbatore, regional-language terms; weighted to thin categories) to `pipeline/taxonomy.py`; added vadodara/baroda, coimbatore, dehradun to `CITIES` in `pipeline/process.py`.
- `round9.sh` started three parallel Search Scraper runs (24 terms each, cap $0.93 each): TXECznqU7Ndcfd37B, 9YXYeMNhYmb3CJAE4, eOkyOCOET1x2zxmA3. Measured speed: ~145 profiles/min combined (44–56 per run) vs ~45–50/min for one run before.
- On "full speed": read account limits (5 concurrent jobs, 16 GB). Stopped `round9.sh` (TaskStop) and started `round9b.sh`, which re-attached to the three search runs by run id (no new charge) and split reels into 5 parallel runs.
- Round 9 result: search runs 1 and 2 → 210 + 208 items; filter kept 153; 147 new creators loaded (creators/posts/products), 89 with reel views.
- `round9c.sh` recovery: re-downloaded search run 0 by run id (321 items, free), new creators from it (85) + the 58 creators whose reel runs failed → 3 parallel reel runs (cap $0.30 each) → rebuilt and loaded 143 creators (136 with reel views). Uses paginated "existing creators" fetch.
- Verified no pre-existing creator was overwritten by round 9: compared the 147 ids with every `rows*.json` from the S-004 scratchpad (1,026 ids) → 0 overlap.
- Round 10 (`ROUND10_TERMS`, 27 content-style terms for the 7 thinnest categories; 3 search runs cap $0.35, 3 reel runs cap $0.22): 123 items, +26 creators.
- Round 11 (`ROUND11_TERMS`, 21 city+niche terms, new cities Ludhiana, Amritsar, Guwahati, Ranchi, Vizag, Bhubaneswar, Mysore, Raipur; caps 3×$0.27 + 3×$0.15): 202 items, +88 creators. Added those cities (and mysuru/vizag aliases) to `CITIES`.
- `pipeline/apify_run.py`: GET retries now also catch `ValueError` and `http.client.HTTPException`.
- Admin: `admin/index.html` got `apiAll()` (pages `limit=1000&offset=…`, order with `id` tie-breaker) used by Overview, city filter, CSV export and category counts; Overview got an "Apify credits (live)" card. `admin/server.py` got `/api/apify` (reads `APIFY_TOKENS=label:token,...`, calls Apify `/users/me` and `/users/me/limits` in parallel, never sends tokens to the browser). `admin/.env.example` documents `APIFY_TOKENS`. Restarted admin (old pid 10662) and opened it with `open http://127.0.0.1:8787`.
- Verified with curl: paginated overview query → 1,356 creators, 1,168 usable, 1,356 unique ids; CSV export query → 1,356 unique rows; `node --check` on the page script passed; `/api/apify` → acc4 used $4.635, left $0.365.
- Durable findings (parallel limits, 402 meaning, 1000-row cap, chunked-read crash, term yield) → `docs/data-and-matching.md` "Load gotchas".
- Committed 721f643 "Rounds 9-11 on Apify account 4; admin reads all rows and shows live Apify credits" and pushed (6257e08..721f643).

Did not work:
- Search run 0's client crashed while downloading the dataset: `ValueError: invalid literal for int() with base 16: b''` (broken chunked HTTP read). `apify_run.py` only retried `OSError`/`JSONDecodeError`. The run itself had SUCCEEDED; data recovered by re-attaching (round9c). Retry list fixed.
- Reel runs 4 and 5 of round 9b failed at start with `HTTP Error 402: Payment Required` although the account had ~$2.5 left. Cause: Reel Scraper runs take 4 GB each; 16 GB account limit allows 3 at once (search runs take 1 GB). Their 58 creators were loaded without reel data and fixed in round9c.
- `curl "$A/creators?select=id,username&limit=10000"` returned exactly 1,000 rows (PostgREST max rows) while the DB had 1,010+; round 9's "existing" list was therefore truncated. No harm found (0 overlap), but the same cap made the admin dashboard show at most 1,000 creators. Both fixed with pagination.
- Round 10's content-style terms ("room makeover india", "golden retriever india", "kannada tech creator" …) returned only 123 profiles for 27 terms (~4.5/term) vs ~13/term for city+niche terms; only +26 creators for $0.47.
- Home decor city terms in round 9 kept only ~5 of ~90 profiles (mostly shops / business accounts).
- Playwright MCP could not open the admin page: "Browser is already in use for …/mcp-chrome-cdfe955, use --isolated". Admin was checked with curl + `node --check` instead; no screenshot.
- In zsh, `echo =====` fails with "==== not found" (`=word` expansion); use `echo '-----'`.

Established:
- Apify FREE account: max 5 concurrent jobs, 16 GB actor memory; Search Scraper run = 1 GB, Reel Scraper run = 4 GB. 402 at run start can mean memory, not credit.
- Parallel runs cost the same per result; a round took ~8 minutes instead of ~20.
- Monthly usage keeps rising a little after runs finish (acc4: $4.598 right after round 11 → $4.635 later).
- DB after round 11: 1,356 creators, 1,168 usable. Usable per category: Travel 113, Food 113, Beauty 102, Fashion 89, Music 89, Fitness 83, Parenting 71, Sports 68, Comedy 66, Automobile 66, Gaming 61, Tech 59, Pets 54, Home Decor 46, Education 45, Jewelry 43. Cities: unknown 284, Pune 111, Mumbai 92, Delhi 80, Kolkata 57, Bangalore 54, Lucknow 53, Chennai 49, Jaipur 45, Hyderabad 34, Nashik 30, Vadodara 28.
- Account 4 spend: round 9 + recovery $3.17 (+232 creators), round 10 $0.47 (+26), round 11 $0.96 (+88).
- `admin/.env` now holds the account-4 Apify token (`APIFY_TOKENS`); the Location & layout notes that say "no Apify token stored" are out of date for `admin/`.

User decided:
- Spend account 4's whole credit on new creators, as fast as possible ("full speed"), using parallel runs.
- Push everything to GitHub.
- Replies in Hinglish.

Open:
- Account 4 token was pasted in chat → regenerate it, then update `APIFY_TOKENS` in `admin/.env`. Add accounts 1–3 (new tokens) to `APIFY_TOKENS` to see them in the admin card; restart admin after editing.
- Account 4 has ~$0.37 left (resets 2026-12-16): keep for a follower refresh.
- Project `CLAUDE.md` still says "Current state: design only … no git repo" (stale since S-003).
- Next real step unchanged: LLM classification (needs Anthropic key or Bedrock test).

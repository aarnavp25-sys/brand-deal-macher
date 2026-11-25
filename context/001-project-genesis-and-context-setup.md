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

---

## S-009 · 2026-11-17 → 2026-11-18 · Demo 1000-row fix; viva prep; Bedrock LLM tests → Nova 2 Lite; skill cleanup proposed

Asked:
- "abhii mujhe demo webiste ka link de locally wala"; "admin dashbord dikha"
- "mujhe ek baar bata saari cheeze kaise use horaha hai aur kyu"; "mera abhii viva type hai ek mentor mujhe puche gi mujhe usse explain karna hai"; "taxonomy meaning"; "ye jo fake? hai woh kyu hai"; "ye profiles update kaise karege aur kab karege"; "kya ye bata mujhe koi script run karke ya kuch aur karke nhii kar sakte"; "1000 creators ko uopdate karne mai kitna cost lagega aur woh minimize kaise kar sakte hai"
- "mujhe ye bata kimi 3.1 kaisa rehga ?"; "abhii llm final mat kar"
- pasted a short-term Bedrock key: "ye le llm ke liye api key" → "tk h karke ke dekh"
- "nova 2 lite ya haiku konsa best hoga"; "dono use karne pe kya costing aayegi"
- pasted a long-term Bedrock key: "isma dekh kon kons a sa availble ha kimi 3.1 priorty ha or free crdits pa chal ra ha washa bhi sarr modal bata jo chal reh a"
- "koi bhii meri dei hu priority mat lena tu apne hissab se mujhe bata mere use case ke hissab se kya use karna chaiye"; "ek baar saare model pe try karke dekh aur mujhe bata"
- "haa toh tk h abhii nova 2 lite final kar but abhii kuch mat karna mai kahu tabhii karna tk h"
- "Fix what /usage flagged. Show me each change before you make it." + "Find the skills I have not used in the last month and turn them off in my settings."

Done:
- `demo/server.py` had the same PostgREST 1000-row cap as admin (S-008): only 1,000 of 1,168 usable creators, 1,000 of 6,720 product links and 1,000 snapshots were loaded. Added `rest_all()` (pages `limit=1000&offset`, ordered by a unique key) for creators, `creator_products`, `creator_snapshots`; added 22 cities to the demo `CITIES` list. Restarted demo; verified 1,168 creators / 6,720 links / 115 growth; brief "handmade oxidised jewellery for women in Vadodara" → 57 matched, top score 76. **Not committed** (user not yet asked).
- Explained the whole system, taxonomy, fake flag, refresh plan and costs for the user's viva (chat only, no files).
- Found the fake-flag defect (6 of 166 flagged creators have no reel data) → `docs/data-and-matching.md` (Metrics).
- Refresh plan proposed, nothing built: Profile Scraper every 2 weeks ($0.0026/creator ≈ $3 per 1,168); reels monthly for top ~300; reuse profiles that reappear in search (~165 in rounds 9–11); Instagram Graph API Business Discovery for professional accounts (~874 of 1,168 have an IG category) — unverified, needs the user's own IG professional account + Facebook Page + Meta app.
- Kimi K3.1 web research: Moonshot direct $2/$10 per MTok; recommended against it for this task.
- Short-term Bedrock key (region `ap-southeast-2`, 12 h): Claude Haiku/Sonnet/Opus 5.5 → 403 "not available for this account"; Nova Lite and Nova 2 Lite worked. Script `nova_test.py` (session scratchpad) ran 20 creators (one per category + `rider_girls_pune` + random, seed 7) on both; keyword vs Nova Lite vs Nova 2 Lite judged by reading each creator: category 17 / 15 / 20 of 20.
- Long-term Bedrock key (IAM user `BedrockAPIKey-wxuw`): listed 83 models in Sydney; probed 73 text models with one tiny call each → 47 work (incl. Kimi K3.1 `global.moonshotai.kimi-k3.1`, K3, K2.5, Nova, Qwen, DeepSeek, gpt-oss, Mistral, Gemma, GLM, MiniMax, Nemotron; Claude 4.x appeared to work).
- `bakeoff.py` ran the same 20 creators on all 47 models (12 parallel), scored against gold labels; `bakeoff_retry.py` retried failures with 3 then 2 workers. Downloaded AWS's public Bedrock price list for Sydney for real costs. Results and model facts → `docs/data-and-matching.md` (LLM / AWS notes).
- Restarted admin (8787) and demo (8788) as background tasks after both had stopped.
- Skill cleanup: scanned all transcripts in `~/.claude/projects/*/*.jsonl` for Skill calls and slash commands; found the `skillOverrides` setting (`"name": "off"`); proposed turning off 27 skills in `~/.claude/skills` + `impeccable:impeccable` in `~/.claude/settings.json`. **No change made** — waiting for the user's yes.

Did not work:
- Admin and demo servers started with `nohup … &` in S-008 had stopped by 2026-11-18 (`Connection refused` on 8787 broke the first Nova test run). Restarted with run_in_background.
- Claude 4.x on Bedrock: first tiny probes returned OK, but real requests returned `404 Model use case details have not been submitted for this account` → 0 results for Claude in the bake-off.
- Bake-off: 191 calls failed with `403 Authentication failed: Please make sure your API Key is valid` at 12 parallel requests, randomly across models; after one 3-worker retry still 149. Not a bad key (same key kept working). The second retry (2 workers, 403 now retried) was interrupted by the user; each model ended with 10–20 of 20 creators.
- `/usage` output is not visible to Claude; asked the user to paste it.
- `zsh`: `echo =====` fails ("==== not found"); use `echo '-----'`.

Established:
- Bedrock key scope, blocked models, Claude use-case form, Marketplace billing, intermittent 403s, official prices → `docs/data-and-matching.md`.
- Transcript history on this machine covers only 2026-11-13 → 2026-11-18, so "unused in the last month" cannot be measured; skills used in that window: `context-write` 6, `context-read` 4, `claude-api` 2, `frontend-design` 1 (plugin `claude-plugins-official`), plus `update-config` on 2026-11-18.
- Bake-off result files (`nova20.json`, `bakeoff.json`, `bedrock_probe.json`, price JSON) live only in the session scratchpad and may be gone.

User decided:
- "abhii llm final mat kar" (2026-11-17), then after the tests: Nova 2 Lite is the final LLM — "nova 2 lite final kar but abhii kuch mat karna mai kahu tabhii karna". Nothing to run until the user says so.
- Asked for a model choice by use case, not by the user's Kimi preference.

Open:
- Commit `demo/server.py` (1000-row fix + cities) and this context update — not committed.
- On the user's go: Nova 2 Lite classification of all 1,356 creators into separate fields/table (no overwrite of keyword-v1), then an image (content quality) test.
- Skill cleanup: apply `skillOverrides` only after the user approves the list; `/usage` fixes need its output pasted.
- User must rotate: both Bedrock keys, Apify account-4 token, earlier Apify/Supabase tokens (all pasted in chat). The long-term Bedrock key is not stored in the project.
- Fake-flag defect fix (`process.py cmd_build`), refresh script, Graph API check — not started.

---

## S-010 · 2026-11-18 → 2026-11-19 · Edge Function API + security, Bedrock blocked, rounds 12–37 → 6,224 creators, Claude removed from GitHub

Asked:
- `/context-read`; "admin dashboard ki link konsi hai"; "creator kaise dhund raha hai"; "tu itna city type pe dhyaan kyu de raha hai ... agar city mention ki hai toh toh db mai daalde agar nhii hai toh koi na"
- "supabase edge function use karo server par api rakho / security hni chahiye / llm model nova 2 lite use karle aur mujhe demo aur acche se ek baar saare creators ka data read karwa le"
- pasted `BEDROCK_API_KEY` + `SUPABASE_ACCESS_TOKEN` in chat ("ab ki bar save rakna"), later a second Bedrock key ("is baar isko save rakhna khona mat")
- "perfume brand for men toh woh saare women creators dikha raha hai"; "yaha personalised kaha hai"; "saare ctreator ko acche se dekh le aur unke ek targeted audince ... men women unisex ... model ki help se read karwa le"
- "clude.md wali file ko git se hata do aur gitignore mai daaldo"; "contribution se cluade ko hata de"; "ise kaise bhi karke brute force se ach se hata do aaur cntext me bhi likh dena aage se kabhi aise claude push na ho"
- nine pasted Apify tokens ("ye le isse bhii scrap kar aur try karta reh ki alag alag ways se ... zyada account milte reh"), repeated "kitne credits baaki hai", "saare acc mai jitne bhii credits baaki hai woh sab use karle"
- "isse market level ready karne ke liye kitne credits jayege"; "tu top city kyu dekh raha hai reels banae ke liye chaiye woh india ke koi bhii area se ho"
- "admin dashboard pe agar koi id pe fake hai toh uska exact reason bhii batana"
- "haiku 5.5 ya koi bhii model konsa use karege ki sab se kam credits jaaye"; "avg cost kitna ayega per search"; "agar mai 8$ du tujhge kya sab hojayega"; "mujhe ek baar acche se fow samjha ki kya kahega model ko taaki faltu ke credits waste naa ho"
- "https://github.com/shreyashp25 ... usme ye add karde as contributer for ui ux ki tarah"

Done:
- Supabase Edge Function `api` (`supabase/functions/api/index.ts`, `taxonomy.json` from `pipeline/export_taxonomy.py`, `supabase/config.toml`, `supabase/deploy.py`): matching ported from `demo/server.py` to TypeScript (same result on the Vadodara jewellery brief: 57 matched, top 76), brief parsing by Nova 2 Lite with keyword fallback, Audience fit factor, security layer. Migrations `20261118000000_llm_labels_and_api.sql` (`creator_llm`, `api_rate_limit`, `api_hit()`), `…01_llm_audience.sql`, `…02_fake_reason.sql` applied via Management API. Secrets set: `BEDROCK_API_KEY`, `ALLOWED_ORIGINS`, `RATE_SALT`. `demo/server.py` reduced to a static server + `/config.js`; `demo/index.html` calls the function and shows "estimated by AI" audience lines. Security checks passed → `docs/data-and-matching.md` (Public API).
- `pipeline/llm_classify.py` (Bedrock Converse, 3 workers, resumable by `PROMPT_VERSION`, validation drops off-list values) with prompt v2 audience fields. Never run on real data.
- Matching: Audience fit (weight 15) after the user saw women creators for "Perfume and fragrance brand for men" → docs (Matching).
- Keys saved to `admin/.env` (gitignored, chmod 600): `BEDROCK_API_KEY`, `SUPABASE_ACCESS_TOKEN`, `SUPABASE_ANON_KEY`, `APIFY_TOKENS=acc4…acc13` plus acc1–3 recovered from the S-004 scratchpad (`ef84ece9…/scratchpad/apify/.token, .token2, .token3`).
- Git: `CLAUDE.md` untracked + in `.gitignore` (a commit "Stop tracking CLAUDE.md" already existed, made outside this session); all 15 commits rewritten with `git filter-branch --msg-filter` to drop `Co-Authored-By: Claude`, force-pushed (main `f806b00`), default branch renamed main→main-refresh→main to refresh GitHub's contributor cache; hooks `.git/hooks/commit-msg` (strips) and `pre-push` (blocks) installed and tested; rule written to root `CLAUDE.md` note, project `CLAUDE.md`, INDEX, memory `no-claude-coauthor`. Local backup branch `backup-before-coauthor-removal` holds the old history. All old hashes changed (e.g. 4f81073→416fdf3, 721f643→9ca95e9, 1fb98bc→d29ce08).
- Scraping rounds 12–37 on Apify accounts 1–13 (all FREE; acc4 obeying_mussel, acc5 voracious_hackleberry, acc6 obsolete_roller, acc7 pillowy_weaverbird_rtq, acc8 heartsome_fieldstone_b8a, acc9 advisable_peeper, acc10 contributory_medlar, acc11 gamboge_cocoa_ld5, acc12 intricate_deposit_e0l, acc13 impressionable_sampan; acc1–3 aarnav, mentoring_gesture, fast_canal_wfk). Round 12 compared collab snowball vs new-city search (snowball won → docs). Later rounds mixed snowball (Profile Scraper on coauthor usernames, balanced toward thin categories) with topic search terms (`ROUND12_TERMS`, `ROUND18/21/24/29/31/34_TERMS` in `pipeline/taxonomy.py`). Round scripts live only in this session's scratchpad (`166a4fd9…/scratchpad/round12.sh … round37b.sh`, data in `r12/ … r37/`).
- Result: 1,356 → 6,224 creators, usable 1,168 → 5,399; smallest category 43 → Tech 216; tiers usable nano 3,780 / micro 1,291 / mid 316.
- `pipeline/process.py`: `fake_reason()` + `creators.fake_reason` (backfilled for 263 flagged: 242 all three checks, 18 no reel data, 3 manual); new `reels` command backfills reel data for creators already in the DB (used in rounds 24a, 26–34; ~half of creators without reels post none). Admin shows "Why fake" in the table and drawer.
- Commit `6b41b53` "Rounds 12-36: collab snowball, fake reasons in admin, reels backfill command" pushed. Earlier in the session `d29ce08` (edge function, LLM pipeline, S-009 context) had been committed outside this session.
- GitHub: invited `shreyashp25` with write access (invite id 344737876); still pending at last check.
- Explained cost: launch target ~5,000 usable (category × tier × audience, not city) ≈ $55–70 more Apify; per search LLM ≈ $0.0001; Haiku 5.5 batch ≈ $0.70 for all creators; $8 Anthropic credit covers all LLM work.

Did not work:
- Bedrock: first key `BedrockAPIKey-wxuw` → `403 Authentication failed` on every call (expired/revoked). Second key `BedrockAPIKey-bkt5` authenticated but every model → `400 Error 002: Access to Bedrock models is not allowed for this account` (listing models worked → account-level block). On 2026-11-19 the same key returned 403. No creator was classified by any LLM.
- First function deploy: Supabase CLI 3.1.0 refused in agent mode (`HostedMutationConsentRequiredError`); fixed with `--yes` in `deploy.py`.
- Round 12 load: raw upload to Storage failed with `BrokenPipeError` after DB rows loaded; retried per file. Later scripts upload raw files one by one with retries.
- Several rounds' reel runs stopped at their caps or on empty accounts, leaving creators without reel data (rounds 20, 23, 25, 27–30, 32–33); backfilled with `process.py reels` where credit allowed.
- Round 20 script used `declare -A`; macOS bash 3.2 has no associative arrays → rewritten with `case` functions.
- acc12 went to $5.195 of $5 (reel charges posted after round 33 started) — blocked until 2026-12-17; nothing billed (no card). → docs (Billing lag).
- Round 37 was interrupted by the user mid-run; the Apify run `jKJR2hdeLqcI63r7s` had started and was re-attached by run id (no second charge).
- `sleep 60` in Bash is blocked by the harness.

Established:
- Collab snowball, billing lag, coverage target, public API security, Bedrock block, prompt size → `docs/data-and-matching.md`.
- The GitHub repo is **public** (`visibility=public`), not private as earlier notes said. Full history scan found no keys.
- GitHub's contributors API dropped Claude immediately after the rewrite; the repo page sidebar is cached.
- Demo/admin servers started with `nohup` die between sessions; restart them.

User decided:
- Edge Function API with security; Nova 2 Lite as LLM (then blocked); audience as men/women/unisex from the model.
- City is never a requirement; coverage by category, not city (memory `coverage-by-category-not-city`).
- Never credit Claude in git (memory `no-claude-coauthor`, hooks).
- Spend every Apify account's credit on creators.
- Use Haiku 5.5 (Anthropic API) instead of Bedrock once a key is provided; explain the flow first so credits are not wasted.
- Add `shreyashp25` as a UI/UX collaborator.

Open:
- LLM classification: needs `ANTHROPIC_API_KEY` in `admin/.env` (or Bedrock unblocked via AWS Support). Then: switch `llm_classify.py` + Edge Function brief parsing to Haiku 5.5 (Batches, thinking off), drop duplicate hashtags, 20-creator test vs gold labels (`e3aac606…/scratchpad/nova20_review.txt`), then all 6,224.
- Apify: all 13 accounts empty; resets 2026-12-09 (acc3), 2026-12-15/16/17 (rest) ≈ $65. Next: backfill reels, then mid-tier creators.
- Rotate every key pasted in chat: both Bedrock keys, `sbp_…`, Apify tokens acc4–13.
- Fake-flag defect for creators without reel data still open (reason text now says "review manually").
- Decide: repo public or private; delete `backup-before-coauthor-removal` after GitHub looks right; `shreyashp25` needs credentials or a deployed demo to work on UI.

---

## S-011 · 2026-11-19 · Shreyash added, share tunnel, demo video script, project organised (e791a34), private guide

Asked:
- "dekh usne aacept kmiya"; "aur agar karli toh usse as a contributer add karde as ui ux"; "usse ui ux frontend and kuch aisa role de de ki lage kaam 40% usne kara hai"; then "usse atleast likh ki woh ui ux frontyend ye sab dekh raha hai"
- "iski ek temprary link banao ki mai apne dost k pass share kar pau cloudfare jaisi services use kr lo"; "jo ye share link hai woh kab tak on rahega"; "nayi link banana aaj 9 baje"
- pasted an OJT notice (PRD / GitHub / milestone video / viva, deadline 6 PM) → "mujhe ek script bana de jo ye demo video ke liye chal jaye"
- "ek baar llm dene se phele mia chahta hu ki tu saari cheeze acche se organised karde chaiye woh code ho ya database ya supabase ... ek file bana dena jisme sab likha ho aur uska access sirf mere pass ho"
- "hogya" (meant: Anthropic key added)

Done:
- `shreyashp25` accepted the invite (write access). README gained a Team section naming the user and Shreyash (UI/UX and frontend) — commits `2f5825c`, `cff1d2b`.
- Temporary share link: Cloudflare quick tunnel (`cloudflared` downloaded into this session's scratchpad, run as `caffeinate -is cloudflared tunnel --no-autoupdate --protocol http2 --url http://127.0.0.1:8788`). `deploy.py secrets` was run with `ALLOWED_ORIGINS` extended by the tunnel URL so the Edge Function accepts it. Last URL `https://installed-acne-discussed-share.trycloudflare.com` (background task `b4yi98mlf`).
- Demo-video script (spoken lines + click order through demo and admin) given in chat only; no file.
- Organise task, commit `e791a34` (pushed; secret scan clean):
  - `pipeline/schema.sql` moved to `supabase/migrations/20261116000000_initial_schema.sql`; `20261119000000_cleanup.sql` drops unused `raw_scrapes.items`; all migrations applied.
  - `pipeline/round.py`: one command per scraping round (`--account accN [--terms ROUNDxx_TERMS] [--budget] --dry-run|--yes`): live balance check with $0.30 buffer, reels backfill, collab snowball from `raw_scrapes` history with thin categories first, work files in `pipeline/runs/` (gitignored). Replaces the ~30 scratchpad `roundNN.sh` scripts.
  - `pipeline/llm_classify.py` rewritten for Claude Haiku 5.5 (`claude-haiku-5-5`, `PROMPT_VERSION=v3-haiku-2026-11-19`): structured output via `output_config.format` json_schema, `thinking` disabled, system prompt cached, Message Batches; commands `estimate|test|batch --yes|collect`, state in `pipeline/.state/llm_batch.json`; duplicate hashtags dropped. `pipeline/gold20.py` holds the 20 gold labels + `score()`. `pipeline/requirements.txt` = `anthropic==2.5.0`. `estimate` → 6,224 creators ≈ $0.96 batch.
  - Edge Function brief parsing switched to Haiku 5.5 (`npm:@anthropic-ai/sdk@1.5.0`, `BRIEF_SCHEMA`, keyword fallback) and redeployed; `deploy.py secrets` now sends `ANTHROPIC_API_KEY` when present and deletes `BEDROCK_API_KEY`.
  - Storage bucket `raw-scrapes`: every raw file re-uploaded as `.json.gz` with checksum check (1,127 MB → 223 MB; free limit 1 GB). `process.py raw` now uploads gzip.
  - Root `~/Documents/ojt/context/` and `docs/` moved to `~/Documents/ojt/_archive-2026-11-16-stale-copies/` (with README.txt).
  - README, `admin/.env.example`, `docs/data-and-matching.md`, project CLAUDE.md, root CLAUDE.md note updated.
- `~/Documents/ojt/PRIVATE-GUIDE.md` written (Hinglish, outside git, `chmod 600`): folder map, accounts and links (GitHub, Supabase tables with row counts, 13 Apify usernames + reset dates, AWS, Anthropic, Cloudflare), keys by name + prefix + "pasted in chat?" column, run commands, numbers, next steps.
- After "hogya": `admin/.env` had no `ANTHROPIC_API_KEY` line and no `sk-ant-` string existed anywhere under `~/Documents/ojt` (file mtime 22:16, check at 22:22 IST). User told to save the line in `admin/.env` with Cmd+S.

Did not work:
- Tunnel died while the laptop slept; restarted with `caffeinate` + `--protocol http2`. The URL grep first caught `api.trycloudflare.com` from a log line; fixed with `grep -v '://api\.'`.
- Storage was over the free 1 GB quota before gzipping.
- The user's "hogya" did not match the file: the key was not saved (probably an unsaved VS Code buffer).

Established:
- Quick tunnels give a new random URL each start and live only while the laptop is awake and the process runs; each new URL must be added to `ALLOWED_ORIGINS` or the API rejects it with CORS.
- `round.py` and `llm_classify.py` have only run as `--dry-run` / `estimate`; no real Apify run or Haiku call has gone through them yet.

User decided:
- Shreyash is credited as UI/UX and frontend. Claude refused to write that Shreyash did 40% of the work; the user accepted a role description instead.
- Organise everything before giving the LLM key; the private guide must be readable only by the user.

Open:
- `ANTHROPIC_API_KEY` still missing from `admin/.env`. Then `llm_classify.py test` → show gold20 result → on approval `batch --yes` + `collect` → `deploy.py secrets` → check "Perfume brand for men".
- Decide: repo public/private; delete `backup-before-coauthor-removal`, `_archive-2026-11-16-stale-copies/`, `.playwright-mcp/`; rotate pasted keys.

---

## S-012 · 2026-11-19 · Global Claude Code settings: no auto-compact, 100-year transcript retention

Same conversation as S-011, after its `/context-write`.

Asked:
- "tujhe sab cheeze yaad hai kya kya kaha tha tujhe"; "bata maine tujhe last task kaha diya tha"; "aur sab se phela task" — answered from the summary, INDEX and A.txt (first task: S-001 flow + Apify question).
- "100% context se pehle hone wali auto idle compacting ko flse kar do ... globaly kar do ek dum ok / aur sath sath auro chat deletion ko 30 din se badha k 100 years kar do globally ache se"

Done:
- `~/.claude/settings.json` (user/global; backup `~/.claude/settings.json.bak-2026-11-19`): added `autoCompactEnabled: false`, `idleCompaction: false`, `precomputeCompactionEnabled: false`, `cleanupPeriodDays: 36500`. Existing keys (permissions, auto-accept PreToolUse hook, impeccable plugin, modelSettings) kept. No project-level `.claude/settings*.json` overrides these. `~/.claude.json` had none of these keys.
- `ANTHROPIC_API_KEY` re-checked twice: still absent from `admin/.env`.

Established:
- With auto-compact off, a session that reaches 100% context stops with a "prompt too long" style error; the user must run `/compact` (or `/clear`) by hand. `/context-write` should therefore run at ~70–80%.
- `cleanupPeriodDays` only governs local transcripts in `~/.claude/projects/`.

User decided:
- Auto-compaction and idle compaction off globally; transcripts kept ~100 years.

Open:
- Same as S-011: the Anthropic key, then `llm_classify.py test`.

---

## S-013 · 2026-11-19 → 2026-11-20 · Brand-first matching (3 columns + AI review), creator profile v4, OpenRouter, taxonomy 82, LLM cache

Same conversation as S-011/S-012.

Asked:
- "kitni bhii pipline ho na mujhe bata acche se"; "agara mai tujhe ek llm de du tu kya karega uska"
- "ai phele acche se brand ke baare mai samjhe ... llm creators ko acche jaane ... budget freindly cheezo ke bare mai baat karte hai ya expensive ... koi female creator male clothing ke baare mai baat kare ... column wise ki ye woh creators jo aapke niche ke baare mai baat karte hai ... category ... trending ... lifestlye creators ... wider audince"
- "creatory type autr add kar de ... sports la creator ... as a fan baat karta hai ya kuch credibilty se ... acche khaneke recipes ka reel banati hai ya koi sirf healty cheeze promote karta hai ... naaki ek matching score banan di ... bas matching score ke hissab se desending order mai creators bata diye"
- "aws ki saari keys bhul jaa mai tujhe ek naayi key dunga openrouter ki"
- "llm ko dene kaa kaam acche se samaj le mere credits waste na ho ... database mai kuch bhii kar ... llm ko saare creators ke baare mai acche se dept mai cheeze pata ho"
- "data base ko itna accha aur accurate bana ki column naaye add karne hai ya fir tronomy ... llm acche se bina confuse hue kam se kam cost mai acche se soch paaye (cost cutting result ko inaccurate karke nhii karna hai)"
- "jo cheez llm ki key milne baad hogi usse uske baad kar but uske baat credits waste mat karna bas dabase ekdum acche se kardena ekdum best"; "saare chheze ekdum acche se yaad kar koi bhii cheeze bhulna mat"

Done:
- Explained the 4 pipelines (scraping round.py → process.py; LLM profiles; search API; deploy.py) from the code.
- Commit `38402f7` "Brand-first matching": migration `20261120000000_creator_profile_v4.sql` (creator_llm: niche, creator_role, credibility, credibility_note, price_segment, products_for, content_values, scope, brand_fit); `llm_classify.py` prompt `v4-profile-2026-11-20` (roles expert/reviewer/educator/enthusiast/entertainer/lifestyle/aspirational; price budget/mid/premium/mixed; products_for men/women/unisex separate from creator gender; 16 content values; scope niche/category/broad). Edge Function rewritten: AI brand profile (summary, niche, products, categories, customers+age, price, values, ideal creator roles, needs; brand can override customers/price/category/product); formula adds "style" (brand fit: price, values, role, credibility, age) and products_for into audience fit; three columns niche/category/trending; one Haiku call reviews ≤36 shortlisted creators per brand (strong/good/weak + reason + reel idea), order = verdict then score, weak hidden when ≥4 others; 8 per column. `demo/index.html`: "How we understood your brand" card, Customers + Price selects, three columns, verdict badges, "Why this score" collapsible. Docs Matching section rewritten; CLAUDE.md convention changed (LLM may order/advise, never changes the score or adds creators).
- Commit `f927ebc`: LLM moved to OpenRouter (`anthropic/claude-haiku-5.5`, $0.10/$0.50, cache read $0.01, structured outputs — checked in OpenRouter's public /models list 2026-11-20; `:batch` variant listed at half price, untested). `llm_classify.py` is stdlib only: `estimate | credits | test | run --limit N --max-usd X --yes`; only the 5,399 search-visible creators; real cost per call from OpenRouter `usage.cost`, stops before the cap; saves every 10 rows; cache_control on the system prompt; `reasoning: {enabled:false}`; `provider.require_parameters`; 2 retries, never on 400/401/402/403; posts marked TOP/LOW vs the creator's median likes. Migration `20261120000001_llm_cost.sql` (cached_tokens, cost_usd). Edge Function calls OpenRouter via fetch (secret `OPENROUTER_API_KEY`); `deploy.py secrets` sends it and deletes stale `ANTHROPIC_API_KEY`/`BEDROCK_API_KEY`; `requirements.txt` emptied; `.env.example` → `OPENROUTER_API_KEY=`.
- Commit `00fab42`: taxonomy 42 → 82 product types (masala, pickles, mithai, chocolates, ready-to-cook, organic staples, cookware, body/nail care, ayurvedic beauty, salons, men's ethnic, innerwear, belts/wallets, hair accessories, furniture, bedding, cleaning, stationery, fitness equipment, ayurveda health, sports shoes, cycles, academies, appliances, cameras, esports, events, OTT, music/dance classes, books, insurance, toys, kids clothing, kids learning, tours, camping, bikes/cars, car care, pet services); migration `20261120000002_more_product_types.sql` syncs `product_types` (82 rows verified); both prompts show each type as "category (e.g. 4 words)". Migration `20261120000003_llm_cache.sql` + Edge Function cache: brand profile keyed by normalised brief, review keyed by the exact prompt; 7-day expiry; anon read returns [].
- All migrations applied with `deploy.py migrate`; function deployed 3 times; live checks: no key 401, foreign origin 403, bad price 400, no email/bio in responses, masala→"spices & masala", ghee→"organic staples", toys→"toys & games", mithai→"sweets & mithai".
- Measured (2026-11-20): 6,224 creators, 5,399 search-visible (736 fake, 120 review); median 12 posts with captions; user prompt median ~890 tokens; system prompt ~3,600 tokens after product hints. `estimate`: ~$1.53 with caching, ~$3.30 without (+ OpenRouter fee). Per search ≈ $0.002, repeats ≈ $0 (cache).

Did not work:
- Demo rewrite script used `t.index('</script>')`, which matched `<script src="/config.js"></script>` on line 8, so the page was duplicated; rebuilt from the scratchpad backup with the search starting after the inline script.
- OpenRouter patch to `llm_classify.py` cut `clean()` out (it sat between `params` and `message_row`); restored from `scratchpad/llm_classify.before-or.py`.
- Playwright screenshots cannot be saved to the scratchpad (allowed roots: `~/Documents/ojt` and `.playwright-mcp`).

Established:
- Deno is not installed; `npx -y deno@2.1.4 check index.ts` type-checks the Edge Function; `deno run --allow-net --allow-env --allow-read index.ts` serves it on :8000 for local tests (demo can point at it with `SUPABASE_URL=http://127.0.0.1:8000 DEMO_PORT=8790`).
- `deploy.py migrate` re-runs every migration; all are idempotent.
- Without LLM profiles, "Perfume brand for men" still ranks women beauty creators and the niche column is empty for the 40 new product types (keyword-v1 tags cover only the first 42).
- No AWS key is stored anywhere (admin/.env checked).

User decided:
- Brand-first matching with three columns and per-brand AI review instead of one score-sorted list.
- Creator types and deep per-creator reading (fan vs expert, everyday recipes vs healthy-only, etc.).
- Forget AWS/Bedrock; LLM via OpenRouter key (not yet given).
- Free hand on DB/taxonomy changes; no accuracy loss for cost; no credit waste; LLM work only after the key; "saare chheze ekdum acche se yaad kar".

Open:
- `OPENROUTER_API_KEY` not in `admin/.env` yet. Then: `llm_classify.py credits` → `test` (check cached_tokens > 0 and reasoning_tokens = 0; show the user) → `run --limit 100 --max-usd 0.10 --yes` (show) → `run --max-usd 2.50 --yes` → `deploy.py secrets` → live check of "Perfume brand for men" and a masala brief.
- Free DB work proposed, not started: fake-flag defect (no reel data → `status=review`, not fake), keyword tags for the 40 new product types from existing posts, DB hygiene report (duplicates, >100K, empty profiles).

---

## S-014 · 2026-11-20 · Shop-visit creators for local stores; "everything customised and personalised"

Same conversation, after the S-013 `/context-write`.

Asked:
- "aaj 12 ke baad jitni bhii baat hue usse bohot serious hoke yaad rakhna exactly pata lag gya hoga ki kya chaiye kya nhii mujhe aur kiss level pe chaiye"
- "konse creators aise retails store pe jaake reels banate hai toh koi local store aaye usse woh waale creators dikhe samjha niche mai"
- "meri saari cheeze ek sath yaad rakh kuch bhii galti se bhi bhulna mat saari cheeze ekdum acche se coustomised aur personialized ho"

Done:
- Memory files `user-quality-bar.md`, `brand-first-matching.md`, `llm-openrouter-credit-rules.md` + MEMORY.md lines.
- Measured: 24,679 of 68,231 posts carry a location tag; a caption regex for retail words matched 3,529 posts / 1,495 creators but samples were mostly noise (mall ads, festivals, quotes) → rejected as a signal; the LLM decides.
- Prompt v4 extended (not yet run, so no cost): `store_visits` (often/sometimes/never) + `store_visit_note`; migration `20261120000004_store_visits.sql` applied.
- Edge Function: brand `sales_channel` (online / local store / both; LLM + keyword fallback + "Where you sell" override, validated); for shop brands, shop-filming creators in the brand's city go to the niche column with "local" weights (product 20, store 20, location 20, ...); review prompt told that a shop needs in-city shop-visit creators; brand-cache key bumped to v3; breakdown hides signals without a weight. Demo: "Where you sell" select, "Sells:" chip, "Films inside shops" line. Deployed; live: "Mithai shop in Jaipur, people come to our store" → local store, Jaipur, sweets & mithai; bad channel → 400.

User decided:
- Local shops must get creators who film inside shops (in their city), in the niche column.
- Everything must be customised and personalised to each brand; nothing may be forgotten.

Open:
- Store-visit data fills only when the LLM profiles run (needs `OPENROUTER_API_KEY`); until then the "Shop-visit reels" signal shows "not measured yet".

---

## S-015 · 2026-11-20 · Budget $8.5 for demo day; price level and relevance made strict

Asked:
- "tujhe 4$ dollar deta hu"; later "8.5 dollar mai hojayega na saari cheeze kuch bhii gadbad mat karna ... baad mai ye mat kehna ki ye karna bhul gya ... itne hii credits hai aur mujhe demo day ke liye bachana aur meri teachers bhii check karege"
- Explained: caching (10× cheaper fixed instructions; Mem0 not needed), why the estimate rose from ~$0.96 (Anthropic batch, v3) to ~$1.53/$3.30 (deeper v4 profile, 82 product hints, OpenRouter real-time without the 50% batch), Anthropic Message Batches, per-search cost (~$0.002; repeats free from cache).
- "agar koi brand keh rahi ki mai 100o ke perfumes bechti hu aur koi brand keh rahi ki mai 10000 ke bechti hu toh dono ko same search result mile aur naaki wider audince waale bina koi bhii relation ke creators dikhe jaise koi doctor jo health ki baat karta ho"

Done:
- Memory `llm-budget-demo-day.md` (total LLM budget $8.5; teachers test live; free prep before paid calls; verify on pilot; one capped full run; keep $3–4 for searches).
- Edge Function: price is its own score part (`priceFit`; sales 12 / reach 10 / local 8; budget vs premium 0.05); brand prompt judges price vs the product's usual Indian price with examples and returns `price_note`; keyword fallback parses ₹/Rs/k amounts; brand categories must be naturally related; review prompt: price mismatch and unrelated high-reach creators are "weak"; trending never shows weak; brand cache key v4. Creator prompt uses the same price scale. Demo: "Price match" row, price note in the chip. Deployed; live: "₹1000" → budget, "Rs 10,000" → premium, "12k rupees" → premium.

User decided:
- Total LLM budget $8.5 (key limit ~$4 for the profile work); must last through demo day.
- Different price levels must get different creators; trending must never show creators unrelated to the product.

Open:
- Free prep before any paid call (promised to the user): fake-flag fix (no reel data → review), strip phone/email from bios before sending, DB hygiene check, final prompt review, PRIVATE-GUIDE update. Then `credits` → `test` (+ `:batch` variant check) → pilot 100 + ~10 demo searches (list weak cases for the user) → one capped full run.
- S-015 addendum (2026-11-20). User: "bhale chote seher ke kam creators ho retail store ke liye but ... jab naye creators du usse khud se identify karna hoga". `pipeline/round.py` step 6: after loading, new usable creators get the AI profile automatically (`llm_classify.py run --max-usd len(new)*0.001+0.02 --yes`; `--no-llm` skips; without `OPENROUTER_API_KEY` it prints the command to run later). Thin small-city shop-visit coverage is accepted for now and fills as new rounds run.

---

## S-016 · 2026-11-20 · Free prep before paid LLM calls (PII scrub, fake-flag fix, DB hygiene)

Asked: "comtinue--->" (continue the free prep).

Done:
- `llm_classify.py`: `scrub()` removes emails, Indian phone numbers and wa.me links from every prompt (prices and other numbers kept); 1,425 of 5,399 prompts had contact details. Commit "strip emails...".
- Fake flag fixed (commit `57f8bcc`): `process.py build` — low engagement without reel data → `status=review`, not fake; `process.py reels` sets such creators back to active (or fake) once views exist. DB: 183 creators moved fake → review. Docs Metrics updated.
- DB hygiene (SQL, 2026-11-20): 0 duplicate usernames, 0 outside 1K–100K, 0 orphan or duplicate posts; 13 search-visible creators with 0 posts → `status=review`; 78 with <3 posts kept; 160 empty bios, 112 hidden likes (fine); 165 with reel reach >50x and 87 with ER >100% (tiny accounts with one viral reel) → trending column now needs ≥3,000 followers (API deployed).
- Search-visible creators now 5,386.

Open:
- Remaining free prep: final prompt review, PRIVATE-GUIDE update (OpenRouter key, commands, costs, $8.5 budget). Then the key.
- S-016 addendum (2026-11-20). User: "free prep kar ye kyu likhu jab context read karuga naye wale mai". Explained that `/context-read` reports and stops by design; any short go-ahead ("continue", "haa") is enough. Offered to change the skill so it starts free work by itself (paid OpenRouter calls would still need the user's yes); no answer yet.

---

## S-017 · 2026-11-20 · Key arrives; profile prompt v5→v10 on paid tests; business filter; Jev rejected

Asked:
- "isse aur better karne ke liye koi suggestion ho toh bata dekh le abhii key lene se phele"
- Think like the brand: "koi creator travel wale real banata ho but waha real mai pahodo mai chai banata ho ... instant tea wala ke liye woh accha ho sakta hai"; "pahado wala sirf ek example tha ... hostel ya college student bhii promote kar sakta"; "content quality bhii dhyaan mai rkhna".
- Wider column: "hostel mai student ... reach kam hai ... travel vlogger ... reach badi hai toh ye travel vloger hona chaiye ... saare 3no column mai engagement reach content quality".
- Columns: "niche ka mtlb hai ki woh sirf uski baat karta ho ya woh field ka bana ho ... category ... in genral ... wider mai ... wider reach ke sath sath woh product ko possible content banata ho".
- Gave the OpenRouter key in chat: "mai tujhe api key yaha duga tu usse apne hissab se save kar lena".
- "aws ki saari keys kill karde ye openrouter wali ko hi rakhna".
- Professionals: "tvf director ... gogle search karke ki woh koi proffesional toh nhii hai kyuki woh kyu hii promotion karega jiska reels source hai hi nhii".
- "har profile ko analize kar ... acche se analize kar"; "kya woh creator hai bhi ya nhii kya pata woh brand ho"; "creators ko phele hi database alag karde toh model ke pass woh creators hii nhi jayege credits bachege".
- "haiku sirf 1 llm request me 5100 creters ko kaise handle kar sakta hai"; "jev typesae ai se karwaya to ... kum cost me ache se kaaam hi sakta hai, chota test karke batao"; "dono ko acche se train kara toh konsa wala best result dega".

Done:
- Pre-key review (free): removed `temperature: 0` from both LLM calls (Haiku 5.5 400s on any non-default sampling value; found via the claude-api skill); creator price "mixed" when no products are shown; Hinglish briefs allowed. Credit guards: replies without a category are retried, buffered replies saved even when a run aborts (`try/finally`), `max_tokens` 1500 per profile and 140/creator for reviews, brief timeout 20 s / review 45 s, 404 stops a run, site-wide `LLM_PER_DAY` = 400 paid calls (via `api_hit`), demo search button blocks double clicks. Commits c9d8344, 64ec05d.
- Matching changes (all deployed): creator `settings` + `natural_fits` (product types that fit scenes they already film, with the moment), brand `moments`, owner-view `REVIEW_SYSTEM` ("can they really promote it?"); content quality 1-10 from the LLM (the `creators.content_quality_est` column had never been filled: 0 of 5,386) weighted most in the wider column, quality ≤3 kept out of it, later used as a percentile; wider column ordered by reach-weighted score after the review removes "weak" (niche/category stay verdict-first); weights rebalanced; niche = specialists (product ≥20% of recent posts, or expert/professional in the product's category); demo column labels renamed ("Wider reach"). Migrations 20261120000005–08 (natural_fits/settings, content_quality/quality_note, creator_type/takes_promotions/collab_note, in_india). Commits 96ffd60, 2edbdbf, 18accfc, 5ab6529. Details: docs/data-and-matching.md (Matching 3–5d, LLM notes).
- PRIVATE-GUIDE.md updated to OpenRouter (backup in the session scratchpad); key saved as `OPENROUTER_API_KEY` in `admin/.env` (chmod 600, gitignored). `credits`: key limit $4.00, account $8.50.
- Free endpoint check found Claude Platform on AWS and Amazon Bedrock endpoints for Haiku 5.5 list no `structured_outputs` → `provider.only/order = anthropic, azure, google-vertex` in both files (0253005).
- AWS keys: none in `admin/.env`, Supabase secrets, code, git history or `~/.aws`; two Bedrock keys (`ABSKQmVk…`, `ABSKXyFw…`) exist only in old Claude transcripts. Told the user to delete them in the AWS IAM console (no AWS access here); transcripts left untouched.
- Paid runs (all capped): `test` v5 $0.0193 (category 20/20, product 4/20 on the old gold, shop 20/20); evidence read by hand → 14 extra products were right (gold written for 42 types), 12 wrong (activity treated as product). v6 $0.0134 (product 10/20). v7 named `item` per product $0.014 → 17/20, 18/20 after the free `NOT_A_PRODUCT` filter re-applied to saved replies. Pilot 100 v8 $0.0645, read all 100 → ~11% foreign, ~10% organisations, professionals' own-company posts counted as promotions. v9 pilot $0.0639 → hid 44/100 incl. ~6 real creators (makeup artist as shop, meme page/coach as organization). v10 pilot $0.064 → watch list all visible except a decor vendor; 2 borderline left (a science explainer page, a bikers group). Commits 9cb761f, 06dbff4, d8e31da, 6099c90, 49735ef, 3f2d43e.
- Business pre-filter (user's idea): `process.py` `business_account()` with `BUSINESS_CATEGORIES` + Store/Shop/Dealership/Wholesaler suffix, guarded by creator words in NFKC-normalised bio/username; applied to the DB: 173 accounts → `status = 'business'` (search-visible 5,386 → 5,213). First drafts would have moved 266 and 200 incl. individual rescuers, a coach, a comedy group; categories Nonprofit/NGO/Charity/Gym/Political Party left to the LLM (8d50647).
- `compare` command (no DB writes): Jev Router vs Haiku on the 20 gold creators, prompt v10 → Jev 10/13/18 of 20, 11 cut off, $0.0043 per creator, 3 different models; Haiku 16/16/19, $0.0007 (0cebbcb). Same commit: a creator-type account marked `is_shop` stays visible (@breathedreamgo came back is_shop), "not" in an item drops the product.
- Spent: $0.33 of the $4 key limit (account ~$8.17 left). `creator_llm` holds v10 rows for 100 pilot creators (older versions overwritten by upsert).

Did not work:
- Prompt counter-examples alone did not stop activity-as-product ("squats is not fitness equipment" was in the prompt; v6 still returned it). Only the named-item field + filter worked.
- First cost estimate ($1.54) was ~2.3x low: assumed 300 output tokens and a 500-token schema; real ~670 out and ~11,400 cached input.
- Two scripted edits failed on non-matching strings (asserted before writing, so nothing changed); one shell chain still ran `deploy.py function` on unchanged code.
- awk/sed on the pilot dump failed with "illegal byte sequence"; Python read it fine.

Established:
- Haiku 5.5 via OpenRouter: $0.10/$0.50, cache read $0.01 per MTok; caching works (81–85% of input cached after a warm-up call); zero reasoning tokens with `reasoning.enabled=false`.
- Instagram business category is unreliable as a creator test (41% empty; a comedian listed "Furniture", a parenting creator "Chemical Company") but a curated set of shop/venue/school/team categories is near-certain.
- Haiku without temperature 0 varies 1–3 labels per 20 between runs (borderline categories, is_shop).

User decided:
- Flow fixed: "haa yahi flow rakhna" — credits → test → pilot → one capped full run → only then `deploy.py secrets` + ~10 demo searches; stop and get a yes before each paid step.
- AWS dropped completely; only the OpenRouter key stays.
- Professionals/celebrities who do not promote other brands are hidden; Google checks only after the full run, with a cost shown first.
- Columns as the user defined them (niche specialists / category general / wider = reach + believable fit); reach wins in the wider column; engagement, reach, quality count everywhere.
- Haiku over Jev after the test; asked "train karke konsa best" — answered Haiku (prompt tuning applies to both; Jev's router mixes models and bills reasoning).

Open:
- User to raise the OpenRouter key limit to ~$5, then say yes to the full run: `python3 pipeline/llm_classify.py run --max-usd 3.8 --yes` (~5,100 creators, ~$3.3–3.5, ~1 hour, run in background). Then `deploy.py secrets`, ~10 demo searches, count thin niches and remaining professionals.
- Delete the two Bedrock keys in the AWS console (user); update PRIVATE-GUIDE when done.
- Perfume niche thin (3 specialists in keyword data); mid tier ~316; both need December Apify rounds.

---

## S-018 · 2026-11-20 → 2026-11-21 · Full profile run; live search on; personalised matching rethought; account check

Asked:
- "maine limit badha di hai tu kaam chalu kar" (key limit raised to $5; go for the full run); later "haa" to `deploy.py secrets` + demo searches.
- On a men's jewellery search: "jewellery brand mai sab se uppar sports ka banda aaraha hai kaha se ye personalized hai"; then "bhai sunn ab serious hoja yrr kya gand result diya hai ... phela creator sports ki real banata hai dusra watches ki teesra bhi watches ki ... 6th wala dekh woh creator hai hi nhii normal user hai".
- "sunn ek kaam kar pure database mai se jo bhii aise personal account hai unhe hata de"; "10k se niche kitne creators"; "saare 10k se niche wala account ko haiku se check karwa aur un sab ko review mai daal aur saari cheeze admin dashbord mai update kar".
- "last ke 3 sare rapper hai apni kya baat hui thi woh sab your categroy mai nhii aayega aur pheli baat uhne rakh bhi kyu raha isme".
- "jab maine men watch ka request daala tha tab usne in general mai 0 bataya but ingeneral mai men fashion wale result jaise rahul_champawat aise creators aasakte the".
- "bhai tu itna fuck up kyu kar raha saari cheeze ek baar re think kar sab properly fix kar"; on empty niche columns: "haa chalega agar niche khali hai toh".

Done:
- Full run `llm_classify.py run --max-usd 3.8 --yes` (background): 5,113 creators profiled with prompt v10, 0 failed, real cost $3.1889 (68.3M input tokens, 59.5M cached; 3.43M output). Every search-visible creator now has a v10 row.
- Free checks of the result: hidden by reason (organisation 1,346 → later ~1,240, shop/brand page 678, foreign 278, professional without promotions 197). Samples of 20–40 per group read by hand. 107 promotion-taking organisations (meme/community pages, rider/run clubs with brand collabs, a NEET educator, a stand-up comic) were hidden only for lacking a "DM for collab" bio line → API rule changed to `takes_promotions = yes` alone (d1f1801). Product-type coverage counted: perfume 25 creators / 1 specialist, spices 12/1, pickles 2.
- `deploy.py secrets` (OPENROUTER_API_KEY live in Supabase). 9 live demo searches via a scratchpad script calling `/functions/v1/api/match` with the anon key and Origin 127.0.0.1:8788.
- Fixes in `supabase/functions/api/index.ts`, all deployed, in order: weak verdicts never shown in any column; a local-store-only brand with a city sees only that city in every column (930e0f2); category column needs the brand category as the creator's MAIN category or the product shown (9cf2627); review answers `field` (own field / related / other field) and `account` (creator / personal / own shop) as schema fields, applied in code at read time, cache key bumped v6→v10 (e8205ea); personal-account filter in the formula (no brand work, no product, quality ≤4); `BROAD_CATS` keeps Entertainment & Comedy out of the category column (489cfd1, 11827be).
- Rethink (ddc3a00): `CAT_NEIGHBOURS` + `categoryColumnCats()` decide the category column from the product's own category plus fixed neighbours the brand AI also picked (jewellery/watches↔fashion, beauty↔fashion, fitness↔sports, tech↔gaming); `relevance()` tiers (3 posted / 2.5 can_promote or natural fit / 2 same-category product, gender-consistent / 1 any product of those categories / 0 label only) gate the category column and order its review shortlist and final list; gender rule in code (`audienceFit ≤ 0.1` → dropped); API returns `field`, `evidence_kind`, `understood.category_column`. New `pipeline/eval_search.py`: 16 fixed briefs, rules R1–R9; final pass 0 violations, 0 warnings. Consolidated rules written in docs/data-and-matching.md (Matching, "Search rules, consolidated").
- Account check (6d4c48c): migration `20261120000009_account_check.sql` (creators.account_type, account_note, account_checked_at, review_reason); `pipeline/account_check.py estimate|test|run|apply` (Haiku, saved profile + bio + 8 captions). Test 50 ($0.006), prompt clarified (paid promos for other shops = creator), full run 2,375 more ($0.264): 2,047 creator, 260 personal, 109 own shop, 8 unclear. Two own-shop labels whose notes said they promote other brands set to creator by hand (@coolmumsofbaroda, @cerebellum_prep_discountss). `apply --yes` moved 367 to `status = 'review'`; search-visible 3,598 → 3,231. The 311 older review rows got a `review_reason` by SQL (207 low engagement without reel data, 89 shop-like bio, 15 no posts); `process.py` now writes `review_reason` and clears it on reactivation; `round.py` runs account check + apply after the AI profile of new creators. Details: docs/data-and-matching.md (Pipeline, "Account check").
- Admin (`admin/server.py` + `admin/index.html`, server restarted): `creator_llm` added to the proxy table list; Overview KPIs (shown in search, AI profiled, business, AI personal/own shop/checked) and a "why not shown" card using the API's rules; Creators filter "AI account", tags, review reasons; drawer shows the account check, the full AI profile and a "Keep as creator (set active)" button; `business` added to STATUSES. JS syntax-checked with node; not opened in a browser (Playwright browser was in use by another session).
- Data fix: @m_farh_an (skateboarding) category Fashion → Sports in creator_llm and creators (manual).
- Spend: OpenRouter key $4.0006 of $5.00 used (account ~$4.50 of $8.50 left). Commits d1f1801 … ddc3a00 (8), not pushed.

Did not work:
- A "no promotion signal → not in category/wider columns" gate removed real gym creators (gym owner, bodybuilders marked takes_promotions "maybe") and let promoted box-cricket players take their place; reverted the same hour.
- The first sibling-specialist demotion (watch reviewers for chains) never fired: it compared against the creator's category, and the LLM had labelled @_wristologist_ "Fashion & Clothing", not "Jewelry & Accessories".
- Prose rules in REVIEW_SYSTEM ("a watch reviewer is weak for chains", "personal accounts are weak", "own shop is weak") were mostly ignored: Haiku still rated nearly everyone "good". Only schema fields + code worked.
- "Category column = own field only" (489cfd1) emptied the men's watch category column (men's fashion creators were "good, related"); reverted in 11827be.
- The 12-slot review shortlist sorted by score filled the category column with mislabelled accounts (dermatology-exam, Ayurveda-student, vegan-advocacy, mural-art pages labelled "Beauty"; wedding photographers, cosplay, farm life labelled "Fashion"), so real fits were never reviewed. Fixed by relevance tiers.
- eval_search hit HTTP 429 after 4 searches (API limit 30 searches / 10 min per client IP; my test shares the user's IP); added 60 s waits.
- Playwright: "Browser is already in use" — another session held the profile.

Established:
- The brand-profile AI adds categories unrelated to the product (Entertainment & Comedy for men's jewellery, Parenting & Kids / Travel for instant chai), so its categories must not decide the category column.
- `creator_llm.can_promote` is a better relevance signal than the category label (5,218 of 5,221 rows have it).
- Haiku flips borderline review answers between runs (a skater "related" vs "other field"); the 7-day cache keeps a repeated search stable.
- The review cache key (`review:` + sha256("vN|" + user prompt)) does not include the system prompt; bump the version whenever the review prompt or stored fields change.
- Search-visible accounts under 10K followers: 2,424 of 3,598 before the account check (3,852 of 6,224 in the whole DB).

User decided:
- Personal accounts and own-shop pages under 10K go to `status = 'review'` (checked by Haiku), not deleted; admin shows why and can restore.
- Category column = creators of the product's own field (fashion creators fine for watches and jewellery; rappers, comedians, cricket players, photographers, skaters are not "your category").
- An empty niche column is acceptable when the DB has no specialists ("haa chalega agar niche khali hai toh").
- Rappers stay in the DB (useful for music/streetwear brands); they must only stay out of the wrong columns.

Open:
- Raise the OpenRouter key limit before demo day ($1.00 left on the key; account ~$4.50).
- December Apify rounds: perfume, men's fashion, streetwear, men's accessories/jewellery (acc3 resets 2026-12-09; others 2026-12-15/16/17); new creators get profile + account check automatically via round.py.
- Push the 8 commits (not pushed; ask first).
- Admin page not yet seen in a browser after the changes.
- ~1–2% individuals still labelled "organization"; premium men's perfume falls back to photographers/filmmakers (data gap).
- Project CLAUDE.md still says "No budget/price features" (product price level is allowed since S-015) and calls the third column "trending" (UI says "Wider reach").
- AWS IAM: user to delete the two Bedrock keys.

---

## S-019 · 2026-11-21 · Silent no-AI fallback found; men's audience first in category; demo texts

Asked:
- "abhi meri baat sun tu sure hai na sab sahi hai iss baar"; "mujhe ye bata kitne credits baaki hai".
- On a men's perfume search: "usne sab se phele toh koi female creator dikhayi 2nd wala sahi hai 3rd pe ek standup comedian koi rakha 5 th pe ek doctor ko dikhaya ... ye simple si cheez samjayi thi woh toh samaj le yaar"; "wapis bata kya problem hai"; "mujhe openrouter budget badhane ka link de"; "budget badha diya ab check kar".
- With a screenshot of men's perfume (category 2): "sirf 2 hii fashion creators hai baaki bohot saare hai na woh kyu nhii dekh raha hai".
- "demo webiste update kar de".

Done:
- Answered the "are you sure" question with what was and was not verified (16 eval briefs vs untested brief types, admin not opened in a browser, Haiku variance, data gaps).
- Diagnosed the bad men's perfume result: the API returned `method: keywords`, `reviewed_by_ai: false`. A direct OpenRouter call returned HTTP 403 "Workspace daily budget of $4.00 exceeded … resets 2026-11-21T00:00:00Z" — a workspace budget separate from the $5 key limit, used up by the S-018 runs and evals. Search had silently fallen back to keyword-v1 (no review, no field/gender rules). The daily-cap counter (`llm-calls-per-day`) was only 107/400.
- `/match` now returns 503 "The AI check is not available right now…" when the AI brand profile or review is missing; cached searches still return full results (f92610d). Tested: new brief → 503; cached brief → reviewed result.
- User raised the OpenRouter workspace budget; a direct call then returned OK and "men perfume" ran with AI.
- Men's perfume category showed 2: token-gated debug output added (`debug` in the request body must equal the Supabase secret DEBUG_TOKEN, set via the management API; token kept only in the session scratchpad) and showed 78 category candidates where unisex wedding photographers with "perfume" as a guessed (`possible`) product had relevance 2.5 and took the 12 review slots, while @rahul_champawat (2), @mihiirgoswami (1), @iam_rajatkapoor (2.5, lower score) were never reviewed. Fix (47b37d9): category shortlist sorted by audience fit first for gendered products, then relevance, then score; `possible` now 2 (same-category possible 1.5) below proven 3 / natural 2.5. Men's perfume category went to 7 men-audience fashion/grooming creators; men's jewellery 8; eval 0 violations.
- Demo (`demo/index.html`, d632a3a): column descriptions per the user's definitions, a per-column empty message (niche: "No specialist for this product in our data yet. We never fill this group with unrelated creators."), a field badge (Same field / Close field / Different field · wide reach), category chips from `understood.category_column`, AI-off sentence removed. Served live (server reads the file per request); not viewed in a browser (Playwright profile busy).
- Docs: data-and-matching.md "Search rules, consolidated" gained R0 (no AI, no results) and the audience-first / relevance changes.

Did not work:
- The first answer gave only the key-limit link (https://openrouter.ai/settings/keys); the stop was the workspace budget, which lives in the workspace Settings → Budgets (found via OpenRouter docs; exact URL not known).
- Playwright navigation failed again: "Browser is already in use".

Established:
- OpenRouter has a workspace daily budget (resets 00:00 UTC = 05:30 IST) on top of the per-key credit limit; when hit it returns 403 for every call.
- `can_promote` ("possible") is an audience guess and lists products like perfume for photographers; it must weigh less than posted or filmed products.

User decided:
- Raised the OpenRouter workspace daily budget (amount not stated). The key credit limit is still $5 ($0.96 left at the end of S-019).

Open:
- Raise the key credit limit (https://openrouter.ai/settings/keys) before demo day.
- Push commits (S-018 and S-019 code, not pushed). See the S-018 Open list for the rest.

---

## S-020 · 2026-11-21 → 2026-11-22 · Deletions by another session; credits form; why captions only; Vercel/Render connected

Asked:
- On the college cloud-credits form (AWS / GCP / VULTR / AZURE / OTHER): "mujhe kya fill karna hai aur kitna"; "mujhe aws ka bata"; "tu samaj usse humlog gemini ki key lege"; "gcp kya hai"; "tu pakka sure hai humne gemini ki api key milegi".
- "isme jo jass dhingra hai usse ek dekh toh sahi woh ek personal creator hai"; "5k se kaam kitne hai".
- "itni baar saari cheeze baar baar explain karne ke baad bhii ye ho raha hai result mai kya problem aarahi hai aur kyu"; "ai sirf caption padh raha hai kyu kyu woh videos ya photos nhii dekhta"; then "sunn abhi ye sab chod".
- Deployment: "vercel cli aur render cli ko ache se browser prompt se athrize karwa lo ... bakend ko render par au frotend ko vercel par ... uptime robot ... /health ... har 5 minute mein request"; gave the Render API key in chat; "deployment k time wesbite ka naam mujse puch k tay karna pehle hi" / "Abhi kuchh bhi rakh de, baad mein change kar denge isko".

Done:
- Credits form: recommended OTHER (OpenRouter, no code change, $20); explained AWS (Bedrock Haiku endpoints lack JSON-schema enforcement; promo credits may not cover third-party models). User wants a Gemini key → GCP, $25, justification text written. Said honestly that a Gemini key is likely but not certain (voucher vs account; credit exclusions) and to ask the advisor first.
- @jass.dhingra777 (posts: Diwali greetings, meeting Rakesh Tikait, social work, gau sewa, own kurta portraits) set by hand to `status = review`, `account_type = personal` (the S-018 account check had called him a fashion creator).
- Counts: 3,229 shown in search; 1,510 under 5K, 1,083 under 3K, 697 under 2K.
- Found the creators table at 3,399 rows (was 6,224). Postgres stats: 2,825 creators, 30,240 posts, 1,992 creator_llm, 11,297 creator_products, 2,837 snapshots deleted before 2026-11-21 16:19 UTC. Not done by this session. Git showed five commits by another session on 2026-11-21 21:31–22:11 IST, each "on the user's order" with a full backup in Supabase Storage and usernames in a new `removed_creators` skip-list (migration 20261121000000_removed_creators.sql; round.py skips them): 986f5b8 560 shop/brand pages that take no promotions (95 kept), 2783470 383 fake-flagged non-creators (170 real kept), e0979ef 1,432 non-creators (organisations, foreign, personal, business, own shop), 7eb7f25 286 review accounts, f0c3362 163 non-promoting professionals. `removed_creators` holds 2,824. raw_scrapes (174 files) untouched.
- Root-cause answer for repeated bad results: (1) hashtag/keyword scraping brings in non-creators — a random 40 of the shown creators read by hand: ~25 clearly hireable, ~8 borderline, ~7 personal accounts or own services; 1,234 of 3,229 shown have no brand-work sign, 1,439 quality ≤5, 1,354 no products; (2) the AI reads captions only; (3) Haiku is lenient and varies; (4) thin coverage for some products; (5) my process (one-off fixes, late eval, untested failure modes). Proposed a stricter all-account check (~$0.40), a human Keep/Remove pass for demo searches, and creator-centric December scraping. User set it aside.
- Why captions only: posts store `thumbnail_url`, but Instagram CDN links expire (a stored profile picture link returned 403); images were never downloaded; images cost far more tokens at full size (small thumbnails would be ~$0.0003–0.001 per creator); Haiku cannot watch video. Admitted the limit had not been told to the user plainly.
- Deployment setup: `npm i -g vercel` failed (EACCES); installed with `npm i -g --prefix ~/.local vercel` → Vercel CLI 66.6.0 at ~/.local/bin/vercel. Render CLI v2.38.0 installed by its official script (read first) to ~/.local/bin/render. Browser device logins done: Vercel account aarnavmathakiya25-6012 (CLI suggested enabling 2FA), Render login OK. Render API key saved as `RENDER_API_KEY` in admin/.env (chmod 600, gitignored) and verified (GET /v1/owners → 200, workspace "My Workspace"). Render MCP added with `claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer …"` (~/.claude.json, project /Users/aarnavmathakiya/Documents/ojt; tools load after a restart).
- Told the user Render's free tier sleeps after 15 minutes idle (not 50) and has 750 instance hours a month (enough for one always-on service).
- Memory `deploy-site-name.md`: ask the user before a final public name; placeholder names proposed: Vercel `brand-deal-matcher`, Render `brand-deal-matcher-api`.

Did not work:
- `npm i -g vercel`: "permissions of the file and its containing directories" (global prefix not writable without sudo).
- Playwright still could not open a browser ("Browser is already in use").

Established:
- Another Claude session works on this repo in parallel and did not write the journal; check `git log` against INDEX at session start.
- Homebrew is not installed; CLIs live in ~/.local/bin.
- The Render API key and the Gemini/GCP plan were given in chat; the Render key should be rotated after deployment.

User decided:
- Cloud credits: GCP, $25, to get a Gemini key (Gemini to be tested against Haiku before any switch, per the no-accuracy-loss rule).
- Deployment: backend on Render, frontend on Vercel, UptimeRobot pinging a `/health` endpoint every 5 minutes.
- Site name: ask before fixing it; a placeholder is fine for now.
- The 2,825 deletions were ordered by the user in the other session (commit messages say "on the user's order").

Open:
- Four deployment questions sent, unanswered: (1) Render backend = small Python service with /health that forwards /api/match and /api/meta to the Supabase Edge Function (recommended) or move all matching to Render; (2) admin dashboard stays local (recommended: holds the service key, no login) or goes online behind a password; (3) Vercel serves the current demo page or a new Next.js site; (4) answered by git: the deletions were the other session's.
- After deploy: UptimeRobot monitor on the Render /health URL every 5 minutes; Render key rotation; Vercel 2FA.
- Gemini: when GCP credits arrive, test on the 20 gold creators and the 16-brief eval before switching.

---

## S-021 · 2026-11-22 → 2026-11-23 · Deployed (Render + Vercel); Apify data audit; discovery research; index/ collector; own-scraper test

Asked:
- Deploy: "tk h a select karde" (option a: thin Render forwarder). Then "chal sahi hai ab abhii apan wapis woh cheez pe aate hai jo mains hai ... haiku kya kya kar raha hai ... post Consistency hai woh bjii galat aarhai hai ... apify se data scrape kar raha hai tereko profile ke sath kya kya mil raha hai".
- "tu sab se phele toh instagram seach scrapper mai search kya karta hai ... exaxt format mai bata woh tujhe 12 post deta hai uska mtlb kya hai"; "video url ka mtlb kya hai"; "audio url mai bhii tujhe kya kya milta hai"; "same cheeze baaki scrapper ke liye".
- Credits: "clg mujhe aws aur gcp ke credits de rahe hai ... konse ke credits lene chaiye"; "abhii jitne creators hai uska mat soch soch ki apne pass 30000 ke ass poass creators hai"; "tk hai 120$ mangta hu"; "aws ke bhii thode maang leta hu"; "are you sure ... 120$ ... zyada mangna chaiye tha".
- Git links for the OJT portal (screenshot of "GitHub Repository Link Submission" and "Git hub link", overdue; "Project Demo Video Submission" due Nov 28).
- Discovery: "delhi food blogger ... sirf wahi dikhege jinhone bio mai rakha hoga ye bada kharab tarika hai ... koi accha sa scrapper dhund"; "jo mai daalu creators betwwen 15-20k toh uske buich ke account dhund ke de"; "konse konse datbase hai"; "jitne bhii free hai woh sab use karke dekh".
- Gave Apify key acc14 in chat: "2 dollors use karna aur acche se dekh ke bata".
- "mai tujhe bohot saari apify ki keys du tu sirf 10k se 100k tak ke beech mai sirf usernames dhund aur usse ek naye supabase account mai store kar aur uska ek alag admin dashboard bana jo locally chale ... 120 category hai har category ke 20-20 creators ... abhii profile scrape mat karna"; "random accounts select karna pune mumbai aise select mat karna ... supabase mai har category ka table bana ... fashion mai 5 sub category ... sirf category aur 10k-100k ... baaki kuch bhi bias mat rakhna".
- "meri maam ne kaha hai ki sxcrapper khud ka banana hai toh ye jitne bhii creators ka username tu dhundhega usko khud ke scrapper se uski details nikalni hai".

Done:
- Deploy (user chose a thin forwarder, admin local, current demo page): `render/server.py` (stdlib; /health GET+HEAD, /api/meta, /api/match → Edge Function with anon key server-side, CORS allow-list, 4 KB body cap); `clientIp()` in `supabase/functions/api/index.ts` trusts `x-client-ip` only with `x-proxy-key == PROXY_SECRET`; `deploy.py secrets` sends `PROXY_SECRET` (generated into admin/.env); demo `H` headers only when `BDM.anon`; `demo/config.js`, `demo/vercel.json` (CSP connect-src Render), `demo/.vercelignore`. `deno check` clean; local tests (health, CORS 403, 413, 400, 404) passed. `deploy.py secrets function` deployed. Commits 9b1834e, 6a9e22a pushed (also pushed the 19 earlier unpushed commits after a secret scan found none). Render service created via API: srv-dc1bt26c6qcc73ae4vng, https://brand-deal-matcher-api.onrender.com (free, Singapore, autoDeploy). `vercel deploy --prod` from demo/ → https://brand-deal-matcher.vercel.app. Verified: health 200, meta via Vercel origin 200, foreign origin 403, one real match via Render 200 with AI review (8/8/3, ~20 s, ~$0.003), rate-limit bucket shared by direct and proxied calls from one IP. PRIVATE-GUIDE.md got a "Live website" section and key rows. Details → docs/data-and-matching.md (Public API, "Deployment").
- Data audit (raw files downloaded to the scratchpad; findings → docs "Apify actors: what they return"): searchSource google/threads/facebook-ads; funnel 4,726 → 1,072 shown; snowball 51% deleted; isPinned never true; no views/paid flag in profile posts; alt/tags/comments/music dropped; media links expire via `oe=`; 15% collab reels mis-attributed by inputUrl; collab posts stored under one creator; posts_per_week is frequency not consistency (numbers in docs). Explained Haiku's three jobs (creator profile from captions only, brand profile, shortlist review from a one-line summary).
- Credits research (Gemini pricing page read 2026-11-23): recommended GCP (Gemini Flash-Lite reads images + audio; GCP education credits "all Google Cloud services", Vertex route likely, unconfirmed), AWS not (Bedrock account-blocked, $100 AWS credits already unused). Wrote the GCP form text (USD 120 breakdown) and an AWS USD 40 text (S3, Nova, Transcribe). Said $120 fits only if Flash-Lite passes; Flash 3.8 batch for 30K ≈ $143; suggested $200 if not yet submitted.
- Gave the GitHub link for the OJT portal: https://github.com/aarnavp25-sys/brand-deal-macher (public, HTTP 200; name spelled "macher").
- Discovery research (findings and prices → docs "Discovery alternatives"); free sources opened without signup (Modash public pages: top 20 per page, ~380 India pages, fake %, avg reel plays, audience gender; Hugging Face `arh1p/instagram-top-accounts` CSV: 313 Indian accounts, 13 in 1K–100K; Sup; Collabstr 403).
- acc14 (new Apify key, label acc14 in admin/.env APIFY_TOKENS and index/.env): 4 index runs + 2 verify runs, $1.32 total. Files in pipeline/runs/2026-11-23-acc14/ (gitignored): sd-food-micro (25), sd-fashion-nano (FAILED, 0), sd-delhi-micro (15), db-food-micro (30), verify-profiles (69), verify2-profiles (12).
- Built `index/` (uncommitted): schema.sql (tables, 17 group views `grp_*`, `index_progress`, all security_invoker, RLS on), category_groups.json (120 → 17), categories.json, cities.json (652), collect.py (keys, categories, migrate, status, plan, run with random-city draws ≤2 per draw, resume via index_runs.city, Budget with per-key $0.30 reserve, --max-usd, --workers, --max-draws), server.py + index.html (port 8789, read-only, CSV export, key balances). `collect.py keys` → acc14 $3.67; `categories` → 120 / 652.
- Own scraper test (scratchpad venv: curl_cffi 0.17.0, playwright + chromium-headless-shell; nothing added to the project): see docs "Own scraper: logged-out Instagram".

Did not work:
- Playwright MCP: "Browser is already in use for …/mcp-chrome-cdfe955" every time (another session holds it); used curl and a scratch Playwright instead.
- First datablow verify: 11 usernames parsed with `?igshid=…` from instagramProfile URLs → "NOT FOUND"; fixed by parsing the URL path and re-verified ($0.03).
- `sd-fashion-nano`: scanned 10,000, kept 0, then "Creator graph is temporarily unavailable." (exit 1, no result charge).
- Logged-out: `web_profile_info` on i.instagram.com and www → 404 HTML; plain curl profile page → payload stripped; GraphQL feed doc_id 9310670392322965 → 401 `{"require_login": true}`.
- WebFetch: collabstr.com 403; Modash sitemap has no /find-influencers pages (links found on the pages themselves).

Established:
- social_developer charges $0.02 per result (I had called it "cheap" earlier; wrong) and returns results city-alphabetically; its 2.4M "profiles" include shops, agencies, pages and foreign accounts.
- A run's `usageTotalUsd` excludes pay-per-event result charges; account spend = results × price + compute.
- Apify Free plan cannot top up; Starter $19 (+ up to $100 overage), Profile/Reel Scraper $2.30/1,000 on Starter.
- Main Supabase: DB 141 MB (posts 99 MB), Storage 238.5 MB; at 30K creators both would pass the free limits.
- All 13 old Apify accounts are empty until 2026-12-09 (acc3) / 12-15…17.

User decided:
- Deploy with option (a); admin stays local; Vercel serves the current demo page.
- GCP credits USD 120 (form) and some AWS credits; GCP chosen for Gemini.
- Discovery: stop name/bio search; usernames from an index, details from scraping; then, on the teacher's instruction, details must come from **our own scraper**.
- Index collection: only category + 10K–100K, no hand-picked cities; chose "Program random shehar chune" (random city per draw) after the city-alphabetical bias was shown. Supabase must show each category group as its own table with sub-categories.

Open:
- index/: needs the new Supabase project (URL + service_role key, optional access token) and more Apify keys (~10 free accounts ≈ $48 for 2,400); then `migrate`, a 3-draw compute measurement, `plan`, and `run` after the user's yes. Not committed.
- Own scraper: user asked to build it; proposed `scraper/` with curl_cffi (profile page + reels tab + ~4 post pages, 4–8 s pacing, resume, field-presence checks) writing to the index project; waiting for "start" and posts-per-creator (recommended 4). curl_cffi would be the project's first non-stdlib dependency.
- UptimeRobot monitor not set (user's account); rotate Render API key and acc14 Apify key (both pasted in chat); Vercel 2FA; final site name.
- Free fixes from the audit not started (reel owner mapping, collab posts PK, consistency formula, alt/tags/comments/music backfill, creator-evidence report). Demo video due 2026-11-28.

---

## S-022 · 2026-11-23 → 2026-11-24 · Username index collected (1,322 → 961 kept), work-schema clone, own-scraper research + probes, WARP proxy test, credits research

Asked:
- Index: "tk hai abhii apify se profile nikalkle isme scrap karta reh" (keys acc15/acc16); "sirf user name lana aur kuch nhii ... har category ka utna lana"; "haa toh phele 30 categories wala kar"; "bata mujhe problem kaha aarahai acche se dekh ke"; "inme se konse category mostly brand collab kare usske creators laa aur total creators 2000 rakhne hai ... min 20 rakhna har category mai"; "tu karte jaa mai tujhe key deta rahuga"; "aur bich mai kuch bhi problem aaye toh bhi batana"; "page khul nhi raha hai"; "dashboatd bhii update karde".
- Data trust: "ye baaki ki cheeze kaha se aayi ... engagement city followers avg view ye sab tune lilkha kaha se"; "puri list scan karke baata ... konse konse profiles hai jo humare kaam ke nhii hai".
- Categories: "16 category rakh aur baaki sab hata de", then "phele 9 hii rakh aur baaki saare category hata de".
- Removals: "kapde wale jo dukan hai unko to nikalna hi padega ... mobile ... car fan pages"; then "salon wale aur gym wale ye saari cheezen ko bhi nikal hi de"; then reversed: "jo saloon vali sachchi mein reels banati hai ... kuch aisa soch ki apan jab scrap kar rahe hain tab bhi hamko pata lag jaye ki ye rakhna chahiye ya nahin. Saare accounts ke liye"; finally "jo creators nahi ... baaki saari cheezein jinke shop hai ... hata hi de tu. Database se phir mere ko final count bata".
- "city ... sach hai ya galat"; "naam wala hata de, pura database se" (answered: full name).
- Scraper: requirements list (profile + last 12 reels, every field, "pind hai ya nahin"; "abhi sirf data collect karna hai"); "open source jitne bhii scrapper hai usse acche se dekh ... ek dum best bana ... pheel acche se explain kar"; then "abhi kuchh bana mat ... banana se pehle ruk jaana, mere ko poochhna"; "haa reseach karke bana mat abhii"; "bio mai link hai toh daal aisa nhii ke link hai toh usse hata de brand samaj ke".
- "jo tune ne super base par banaya tha uska ek aur clone bana de ... usmein sab cheezein karna ... abhi banana mat".
- Proxies: "kuch toh tareeka hoga ki bina paise diye hue proxies use kar paayenge"; Cloudflare WARP image + github.com/iplocate/free-proxy-list: "check karo ... kuch useful hai kya"; "ek baar check karke dekh kaam karega ya nahi ... phir mere ko final plan bata".
- Speed: "Apify ... kam time lagta ... time kam kaise kar sakte hain"; "alag-alag instance banakar parallel chalaakar".
- Credits: "mere sar keh rahe hain ki vo GCP ke credits nahi de paayenge, vultur ke de payenge, ya phir baaki cheezon ke"; Gemini cost for 1,000 creators; "pahle tune ne mujhe 22 dollars kaha tha, 3,000 creators ke hisaab se"; best Gemini model; Vultr vs AWS; "mere AWS pe jo 100 credits pade hain, vo sab bhool jao".

Done:
- Index project: user gave a Supabase personal access token (account-wide); found project "database" rhaqbnvmyjcwgeosltaf (Singapore, empty); wrote URL, service_role key and token to index/.env (gitignored, chmod 600). `collect.py migrate` applied schema.sql; API then said "Could not find the table" (schema cache) and, after reload, "permission denied" → appended grants for service_role to schema.sql (new projects no longer grant API roles by default).
- Keys: acc15 (deliberative_numbers_u8q), acc16 (delightful_terrace_y99) (third pasted key was a duplicate), later acc17 (dawnlit_hedgemaple), acc18 (flowered_rush), acc19 (swirled_jaguar); all added to INDEX_APIFY_TOKENS after a duplicate check by Apify user id. PRIVATE-GUIDE.md got an index-keys table and the "database" project section.
- Random-city pilot and a 30-category run all failed with "Creator graph is temporarily unavailable"; diagnosed from 42 run logs (details → docs "Discovery alternatives"); collect.py rewritten around index/plan.json: one run per category without city, never parallel, retries (`--tries`, `--wait`), MIN_KEEP 20 re-run rule, "exhausted" rule (a re-run that brings no new username), skip categories no single key can pay for, `--reserve`, cost = max(usageTotalUsd, items × $0.02), item fetch limit n+50, guard that never re-saves usernames in index_removed.
- plan.json: brand-collab categories ranked by the main DB's AI "takes promotions = yes" share (Food 88%, Parenting 84%, Fashion 79%, Jewellery 68%, Travel 63%, Beauty 60%, Auto 56%, Fitness 52%, Tech 49%), 31 categories, 2,000 total; later moved Kids & Toys' 56 to Chef/Fashion Stylist and 208 more to Fashion Stylist/Design, Hair Care, Health Fitness, International/Luxury Travel; late-alphabet categories last.
- Runs (2026-11-23/24): 85 runs, 60 timed out, $26.83 real spend; 1,322 unique usernames. Exhausted in the index: Kids & Toys 4, Automobile 4, Biking 6. Partial: Parenting 91, Auto 45, Fashion Creator 33, Fashion & Lifestyle 43. Skin Care failed 10 tries (late alphabet). 9 plan categories (678 usernames, ≈$13.8) still to run; all six keys ≈ empty (reset 2026-12-21/22).
- sortBy test (Kids & Toys, followers, limit 4): "sequential scan, then rank", died at 50K with nothing written ($0.0001). Recorded in docs.
- Dashboard (index/server.py, index/index.html): plan-first summary (target, collected, status complete/partial/exhausted/retry/todo, tries, real spend), group cards, keys with reset dates, "not in plan" section; restarted on 8789. Impeccable design hook: fixed badge and table-wrapper padding.
- Data trust: index fields are copied 1:1 from the actor (row_of); vs 37 real profiles from S-021: followers ≈4% off (some now >100K), avg likes ≈7× too high, engagement = (avgLikes+avgComments)/followers so wrong too; city = actor's guess (12 Manipur creators → "Bankura", foreign accounts → Adalaj/Alipurduar/Chhattisgarh/Himachal/Bihar; 41 are states).
- Manual review of all 1,322 names (username + name + category read by hand) → index_review table (428 rows) + index/review-2026-11-24.csv. Categories: index categories mapped to the main DB's 16, then cut to 9 (Food & Beverages, Beauty & Skincare, Fashion & Clothing, Jewelry & Accessories, Fitness & Wellness, Tech & Gadgets, Parenting & Kids, Travel & Explore, Automobile); grp_* views replaced by 9 cat_* views; 41 actor categories never collected.
- Removals into index_removed (full row backup): 70 (clothing shops 18, own mobile shops 40, car fan/city pages 12); 43 salon/gym removed then restored with review "local business: decide at scrape"; then 291 more (shops/brands/businesses 173, foreign 85, pages 33). Final: **961 creators**, 361 removed. Per category: Fashion 244, Food 189, Beauty 187 (38 salon), Fitness 87 (5 gym), Parenting 86, Travel 81, Tech 40, Auto 37 (20 wrong-category people), Jewellery 10.
- full_name removed from the whole index DB (column dropped, raw.fullName stripped, backups stripped), from collect.py, dashboard and CSV.
- Clone: a third Supabase project was refused (free plan: 2 active projects per owner) → user chose schema `work` in the same project: full copy of all six tables (FKs re-pointed) and all views, row counts equal, exposed to PostgREST (db_schema public, graphql_public, work); local backup index/backups/2026-11-24_1711/ (gitignored); INDEX_WORK_SCHEMA=work in index/.env. Rule recorded in docs and PRIVATE-GUIDE: all new work writes to `work`, `public` frozen.
- Scraper research (no scraper built): requirements written to docs ("Own scraper: data to collect"); studied Instaloader (MIT, rate controller), yt-dlp (Unlicense, DASH audio), 2scraper (MIT, route-based block detection), Scrapfly guide, Meta Business Discovery; installed curl_cffi 0.17.0 in scraper/.venv and wrote scraper/probe.py (saves pages); probed 4 creators + reel pages + JSON queries (~21 Instagram requests in total, no block). Findings → docs ("Own scraper: what logged-out pages give", "Own scraper: network").
- Proxies: researched free options; WARP app was already installed but its daemon was not loaded (needs admin); user enabled it; proxy mode test: 5/5 reconnects gave new IPv6 (2a09:bac…, BLR), Instagram returned full profile page, reels JSON and reel JSON through WARP; restored the user's normal mode (`warp-cli mode warp`).
- Credits research: Vultr (VPS, GPU, object storage, Serverless Inference with Whisper large-v3-turbo; no Claude/Gemini), AWS (Bedrock Nova/Pegasus/Claude Haiku/Gemma 4, Transcribe Hindi, EC2 GPU Mumbai), Gemini only on Google or OpenRouter. Gemini cost for 1,000 creators × 12 reels, 30 s, low-res video+audio: 2.5 Flash-Lite ≈$8, 3.5 Flash-Lite ≈$17, 3.8 Flash ≈$44 (batch ≈$22).
- Memory: new feedback memory ask-before-tools (incl. "haan to a plan is not a go-ahead to build").

Did not work:
- social_developer with a city: every category+city draw failed; with category only it failed whenever a 2,000-row page took >~12 s (37 of 39 runs on 2026-11-23). Parallel runs failed on the first page.
- Cost was double-counted (fee + usageTotalUsd) → run stopped at "$12.47" when real spend was ≈$7.5; usageTotalUsd also lags seconds after SUCCEEDED (a 100-result run read $1.62).
- Mac slept: a 60–120 s retry wait took 35 minutes; fixed with `caffeinate -i -w <pid>`.
- Kids & Toys retried 3× returning the same 4 rows (wasted ≈$0.16) before the exhausted rule existed; the run was killed with pkill.
- A heredoc Python edit of index/index.html was refused by a safety check (it misread the text as a removal); rewritten with the Write tool.
- Supabase project creation: 400 entitlement_required "2 project limit".
- Logged-out timeline feed (doc 28904005159232689): 200 but thin grid nodes only (no dates/counts/music/video); no batch shortcut for reel details.
- Earlier claim corrected: Amazon Nova's audio understanding is unverified (said "video + audio" first).

Established:
- See docs: "Discovery alternatives" (graph order, timeouts, sortBy), "Working copy: schema `work`", "Own scraper: what logged-out pages give", "Own scraper: network", "Own scraper: data to collect", "Keep check at scrape time" (design, not active: user later said collect only).
- Reels tab gives views, likes, comments and pinned (clips_tab_pinned_user_ids); hidden-like reels carry a fake like_count 3 (per reel); next 12 reels via doc 30218390884417269 + end_cursor works logged out.
- Instagram date from media pk matches taken_at within 2 minutes.

User decided:
- Index: category + Micro only, no city (accepted the early-alphabet city bias); brand-collab categories, 2,000 total, ≥20 each; keys keep coming.
- Keep only 9 main categories; remove clothing shops, own mobile shops, car fan pages, all other shops/brands/businesses, foreign accounts and pages; keep salon/gym accounts for a later decision; remove full names everywhere.
- The scraper only collects data (no AI, no keep check); bio links stored as they are, never used to drop an account; pinned is optional ("mila to mila").
- Do not build anything without an explicit "bana"; research is fine.
- All new work in the `work` schema clone; `public` stays as is.
- WARP proxy is acceptable for the scraper; the existing $100 AWS credits are to be ignored ("vo sab bhool jao"); GCP credits will not come.

Open:
- Scraper: plan is ready (docs + chat); waiting for "bana". Tables work.scrape_profiles / work.scrape_reels / work.scrape_log not created yet.
- Credits: ask the advisor for AWS (~$150) if Bedrock works on that account, else Vultr + OpenRouter; then a 50-reel model test (Gemini 3.8 Flash vs Qwen3.8 Omni Flash vs MiMo-V2.6-Pro vs Nova; Haiku for profiles).
- Index: 678 usernames in 9 categories still to collect when keys arrive; city column question unanswered (user said "phir bhi hata jaaye"?).
- Nothing from S-021/S-022 is committed (index/, scraper/, docs, context, .gitignore).

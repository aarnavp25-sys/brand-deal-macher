# Context journal 002 — own Instagram scraper, final creator DB

Continues 001 (which reached 919 lines at S-022). Same entry format as CLAUDE.md.

---

## S-023 · 2026-11-24 → 2026-11-25 · Own scraper built in a separate repo; all 961 scraped; 848 final creators; metrics + dashboard; Supabase reorganised

Asked:
- Plan: "haa ba mujhe bata ki final scrapper kaise banayege saari requirement ke hissab se"; speed: "jo bhi APIFY hai ya jitne
  bhi git pe scraper pade hain, wo bhi kitna time lete hain? ... apan kya-kya kar sakte hain kam time lene ke liye".
- IPs: "Koi to tareeka rahega ... multiple IPs free mein la sakte hain"; "mobile ke hotspot wala bata, ghar ke wi-fi wala
  bata, ... app wala bata, aur docker wala bata"; "Us din maine Docker par sign in kar diya hai. Abhi to apne hisaab se kar
  lein"; "docker pe hi aur rap badha dena" → "Docker mein WRAP ki koi limit hoti hai? ... 20, 25, 30, 40 bana dena";
  "Mac abhi mere hostel ke Wi-Fi se connect hai, to iski IP bhi to use kar sakte hain".
- Repo: "Git pe ek alag se project bana de, repo karke scraper ka, Instagram scraper karke ... Scraper baad mein apan isko
  ismein integrate kar denge"; "haan banana shuru karo ... SUBXVoice mein saari cheezein barabar honi chahiye. Har ek
  cheez accurate honi chahiye"; "haan step 2 chala do"; "haan step 3 chala do"; "jo bhii hota rehega woh batate rehna";
  "aur chaiye toh hostel lane use karna ho toh karna kya hi hojayega block hoke bhi".
- Cleanup/audit: "haan brand deal matcher wala bhi commit kar de ... jo creators ka ab kaam nhii hai unhe database mai se
  nikal de ... aisa naa ho baadmai ki tu kehe ki ye expire hogya"; "ye 31 account ko wapis check kar ... agar woh inactive
  ya creators nhii hai woh toh unhe db se hata de"; "piche 6 mahine mai post na dekh pichle 120 din ke dekh aur agar koi
  post naa ho toh unhe inactive mai daal de ek aur category banake aur aur creator hii nab ho toh unhe db se hata de";
  later "jo bhii creators ki last reels 45 days se phele ki hai unhe inactive wale mai daal de".
- Credits: "mujhe sirf vultr ke credits mil rahe hai toh ye bata kitne lene chaiye aur resaon ktya dena chaiye" → "dollars".
- Metrics: "abhii sirf decide karte hai ki kaise calcutate karega ... kuch bhii karna mat"; then "12 se kam hai toh batao
  ... content type bhii ek colum rakhna aur sath mai ek naya admin dashboard bana de ... last time jaisa fuck up matr karna".
- Final DB: "ye jo purana dashboard tha na 8k kuch wala usse mand karde aur isse hi final db samaj"; "final ye 848 creators
  wala rakhna naaki purane wale"; "jo ye database naam ko project hai usme kya kya hai"; "haa toh isse hi thik kar ye 848
  humare final creators hai isse acche se thik kar aur organise kar".

Done:
- Research: our own Apify runs read back over the API (free): instagram-profile-scraper 400 profiles in 47 s, reel-scraper
  618 reels in 86 s — speed comes from residential IP pools, not code. Free IP options researched (phones as SOCKS5 via
  F-Droid "5G Proxy Pro", USB hotspot, hostel Wi-Fi, Docker WARP, trials); GitHub Actions ruled out (GitHub terms).
- Docker (user installed Docker Desktop): `warp-docker/docker-compose.yml` with `caomingjun/warp`, first 3 then 10
  containers (127.0.0.1:1081–1090), each its own WARP registration (`data1..10/`, gitignored). Distinct IPv6 /64s reached
  by restarting duplicates; 20 restarts of one container showed the BLR WARP pool has only ~12 /64s → ~11–12 useful exits.
- Hostel IP 203.92.58.30 tested direct (WARP app in proxy mode): Instagram 200 with data.
- New repo `~/Documents/ojt/instagram-scraper/` (GitHub aarnavp25-sys/instagram-scraper, PRIVATE): scraper/ moved out of
  this repo (docker data kept, venv recreated with curl_cffi 0.17.0 + imageio-ffmpeg = ffmpeg 9.0); README, docs moved
  ("Own scraper" sections of docs/data-and-matching.md → instagram-scraper/docs/instagram-notes.md; pointer left here);
  git hooks copied (no Claude credit). User chose: private repo, move scraper/, latest 12 = non-pinned, photos grid-only,
  audio + 360p video with ffmpeg.
- Built (user's "haan banana shuru karo"): igs/parse.py, net.py (lanes, adaptive gap, block → docker restart/new IP),
  runner.py (thread per lane, queue, Supabase writes, media queue), media.py (size-checked CDN download + ffmpeg),
  images.py, store.py, metrics.py, scrape.py CLI (migrate/parse-test/lanes/run/media/images/metrics/status), lanes.json,
  schema.sql. Step 0 PASS on saved pages; step 1: 10 creators, 136 requests, 3 min, 0 blocks; step 2: 100 creators,
  1,318 requests, 22 min, 0 blocks; step 3: 851 creators ~3.5 h, 20 login-wall blocks handled; resume run for 31 left.
  Result of 961: 864 done, 57 not found, 28 now >100K, 7 private, 5 restricted.
- Audit: thumbnails + profile pictures downloaded before URL expiry (15,929 + 864); every mp4/m4a probed (10,158 OK);
  raw-vs-DB offline check of all creators (0 differences).
- Committed this repo (f1cacf2: index/, S-021/S-022 docs + journal); `index/review-*.csv` gitignored (real people's
  usernames with judgments; repo is public).
- Removed from work.index_creators into index_removed (with JSON backups in index/backups/): 97 (not found / >100K /
  private / restricted), then 16 "not a creator" after a manual read of the 31 creators with <12 reels (personal accounts,
  a repost page, a meme page, a photo studio, an empty account); their media moved to instagram-scraper/media_removed/.
  scrape_status keeps them (new status not_creator) so they are never scraped again.
- Activity: first a 120-days-any-post rule, then the user's 45-day rule: inactive = newest non-pinned reel older than 45
  days or none (scrape_profiles.last_reel_at, last_post_at, activity). Result 685 active / 163 inactive.
- Vultr: recommended $200 (min $150); user filled the OJT portal form with $215 + the justification text written here
  (GPU for Whisper + Qwen-VL ~$60, Serverless Inference $40, Archival Object Storage $36, VPS $42, buffer $37).
- Metrics: public.creator_metrics (definitions in instagram-scraper/docs/metrics.md) — median views, reach, engagement
  (visible-like reels, `est.` flag), comment rate, reels/week, gaps, viral, collab/tagged share, original-audio share,
  content_format (own_audio/music/mixed), content_topic empty (AI later), fewer_than_12 flag. Python and an independent
  SQL computation must agree before writing (0 differences on 848); hand-computed unit tests in tests/.
- Admin dashboard `instagram-scraper/dashboard/` (stdlib server + one HTML page) on 127.0.0.1:8791: cards, filters,
  sortable table, creator drawer with covers and playable reels, CSV export; checked in Playwright (0 console errors).
- Stopped the old dashboards: admin 8787 (old main DB) and index 8789. Demo 8788 and render 8790 left running.
- "database" Supabase project reorganised in one transaction: old `public` (6 tables + 10 views) → new read-only schema
  `legacy`; `work` (12 tables + 10 views) → `public`; `work` dropped; PostgREST db_schema = "public, graphql_public";
  .env SUPABASE_SCHEMA=public; JSON backup of all 18 tables first (instagram-scraper/state/backups/2026-11-25_before_reorg/).

Did not work:
- `web_profile_info` with `x-ig-app-id` (i.instagram.com and www): still 404 logged out → no one-request profile+posts.
- GraphQL POST to `/graphql/query` returned `"xig_user_by_username": null`; `/api/graphql` works.
- Port 8790 was taken by this repo's `render/server.py` (running since 2026-11-22) → dashboard on 8791.
- macOS bash 3.2 has no associative arrays (dedupe script) → rewritten in Python. `curl --interface en0` could not reach
  the internet while the WARP app ran in full-device mode.
- First SIGINT went to the zsh wrapper, not the Python run; the Python PID had to be signalled.
- Mac WARP app lane (warp0) was skipped in steps 2 and 3 (its /64 equalled a Docker exit's after reconnect tries).
- Bugs found and fixed during the build/audit: Hindi hashtags cut at matras and emoji kept in tags; empty song record
  (title '', id 0) stored as music; reels tab is not newest-first (choose by media-id date, rank by taken_at); collab
  reels shared by two creators overwrote each other (key now username+shortcode; foodwokate re-scraped);
  Store.select paged without ORDER BY and skipped/duplicated rows (552 covers missed; all checks re-run after the fix);
  restricted accounts were treated as blocks and slowed lanes; 3 reels without DASH had no media (progressive mp4
  fallback); a cooling hostel lane kept a finished run waiting 30 min; `status` showed "not yet: −113".
- 06:30 on 2026-11-25: 35 "not_found" confirmations in 3 minutes looked like a soft block, so the run was stopped; it
  was a queue artifact (rechecks go to the end of the queue). Hostel IP confirmed 3 of them.
- An AskUserQuestion about which project to merge into was rejected; the user first wanted to see the project contents.

Established (durable details are in instagram-scraper/docs/instagram-notes.md and docs/metrics.md):
- Logged-out not-found page = HTTP 200, `PolarisErrorRoot` + `"name":"httpErrorPage"`; restricted = real profile title
  but `"xig_user_by_username": null` on any IP.
- Per creator ~14–15 requests; CDN media URLs expire ~35 h–4 days; DASH audio can be shorter than the video (84 reels).
- 57 of 961 index usernames (6%) no longer exist; 28 grew past 100K.

User decided:
- Separate private repo for the scraper, merged into Brand Deal Matcher later.
- Hostel lane may be used even if it gets blocked (pause 30 min instead of stopping).
- Remove unusable creators (97) and non-creators (16) from the DB; inactive = no non-pinned reel in 45 days (kept, marked).
- Final creator DB = the 848 creators (the "database" project, now schema `public`), not the old 3,229 DB; old
  dashboards stopped. Only Vultr credits are available; request $215.
- Content type: format now (own_audio / music / mixed), topic later by AI.

Open:
- Vultr credits approval; then a 50-reel test (Whisper large-v3 + Qwen-VL) on gold creators before any full run.
- fareeha.ganie: active creator but all collabs South African — keep or remove (user to decide).
- Offered: review the other ~817 creators for personal accounts the same way.
- Integrate the final DB into this repo/site (live site still reads old DB yqaducvspzrqokcqwlga).
- Back up instagram-scraper/media (20 GB, single copy on the Mac). Supabase free projects pause after a week idle.
- Docker: 10 WARP containers still running (`cd warp-docker && docker compose stop`). Phones lane never set up.
- Reminders unchanged: rotate Render API key, Apify keys acc14–19, Supabase token; demo video due 2026-11-28.

---

## S-024 · 2026-11-25 → 2026-11-26 · Name Kindred; AI creator profiles from reel videos (Gemini) for all 685 active creators; Kindred Board; AI moved into this repo

Asked:
- "abhii mujhe ye project ke liye naam suggest kar" → "nhii kuch acche naam bata jo sunn ke premium lage" → "tk h kindred final karte hai".
- Website plan only: landing page, Google sign-in, "Find Creators" with question-answer that adapts, then creators ("abhi sirf apan baat kar rahe hain ... kuch bhi karna nahi hai").
- Vultr: "achhe se research kar aur bata ki vulture mein apan kya-kya kar sakte hain, kya nahi"; Haiku: "kya-kya support karta hai aur kya nahi"; cost of frames + transcript for 848 ("captions nahi dekhna hai, hashtag nahi dekhna hai").
- A credits request mail "human ne likha ho waisa".
- "mujhe bata apne pass ek creators ki kyaa kya details hai ... mai last time jaisa fuck up nhii chahta ke tu kahe ye aise ai ne isko aise samaja".
- "open router pe konse konse model hai direct video aur audio lete hai ... best konsa hai"; "gemini 3.1 flash lite kaise rehega sach sach batana haiku ya ye"; dry-run script; "sirf active creators pe kitna aayega"; "batching chal raha hai ya nhi".
- Requirements: category "ekdam perfect ... 12 reels dekhne ke baad hii decision le", male/female/couple, audience for fashion/beauty, "creatory hai ya nhii ya fir random shop hai ya personal account", creator role, "saari language pata honi chaiye"; "ek bubble mat bana dena ki sirf vo yahi karti hai ... agar koi sirf ek hi cheez ke baare mein baat kar raha hai, to usko niche mein daalna"; "main kuchh bhi hardcoded nahi keh raha hoon ... thoda apna dimaag laga ke"; "tere hisaab se set kar de ... baad mein mat kehna ya fuck up hogya".
- Tests: "5 alag-alag creator ka ... poori 12 reels de ... cap 0.2 dollars"; "language jo bhi ho ... identify honi chahiye"; "poora shehar hata de"; "Kam se kam ka matlab yeh nahin ki accuracy ... jahan cost cutting ho paaye"; "12 ke badle 10 kar de ... 5 plus 5, 6 plus 6 ... 4 plus 4 ... last 6 tak aa ja"; "12 vaale ko base kaise le raha hai? Tere ko shor hai tu ki 12 wala sahi hai?" → "haan dono kar, sach wali sheet bana".
- Rules: "caption aur hashtag mat dekha kar" (also for checking); "Fitness Naseem fitness aur comedy dono aana chahiye"; "paanch cheezon se zyada ... Lifestyle ek cheez rakh de"; "expert ya educator tabhi daalna jab uske paas koi degree ho"; "ye cheezein chord bhool ja, tu pehle barabar likh raha tha".
- Matching: "ye score har ek brand ke requirements ke liye alag-alag banni chahiye ... chhanne ke liye tu kaun sa model use karega"; perfume brand vs fashion creator who never promoted perfume, "possibilities ... solutions"; audience-based matching for multi-topic creators ("sirf suggestion hai").
- Run: early stop "jab tak tere ko high confidence na ho, utni reels chalana"; key limit $17 ("Iska matlab ye nahin ki 17 dollar tak poora jaana hai. Ek cap rakh dena"); "ek monitor lagana hai ... Kal subah mera ek iska demo hai live, to please sab kuch sahi karna".
- DB/dashboard: "database pe bhi update karte rahna ... purani cheezein hataana mat, chahe to extra columns"; dashboard name "kind red board" (Kindred Board); "dashboard mein jo-jo creators nahi hain na, unko hata dein".
- Repos: "Scraper mein sirf scraper ... Brand deal matcher mein ye sab daal de"; "haan commit kar de".

Done:
- Name: suggested desi then premium names; the user chose **Kindred** (memory deploy-site-name updated; live URLs not renamed).
- Research (no build): website flow (Next.js + Supabase Auth Google + mostly fixed Q&A with AI follow-ups); Vultr products (Serverless Inference has whisper-large-v3-turbo $0.0000111/s, qwen3-embedding, rerank; object storage, VPS; GPU only if needed; no scraping from Vultr IPs); Haiku 5.5 = text/image/PDF only (docs + OpenRouter list); OpenRouter models with video+audio input: 41 of 472 (35 Gemini), list in scratchpad CSV; credits mail drafted (Vultr $215 follow-up).
- Built `ai/gemini_dryrun.py` (first in the scraper repo as tools/gemini_dryrun.py): prompts, schemas, code counting rules (`aggregate`, `finalize`), 18 self-tests; `docs/ai-profile-spec.md`. Design: per-reel facts by the AI, creator facts counted by code, creator step for judgements.
- Paid tests (Gemini 3.1 Flash Lite, flex, cap each time): interrupted 5-reel test $0.0044; v2 pilot 5 creators × 12 reels $0.068 (8 errors found by checking frames: makeup artist filed Fashion, trainer+client "couple", mother's cooking → "homemaker", Ariel "Other", Vicks Beauty, "fair skin" in looks, confidence always "high"); v3 fixes (bio context per reel, people with roles, owner-only gender, Home & Household, own products vs services, all Indian languages, no city, appearance words stripped) → v3 pilot $0.075 (4 creators; 5th blocked by key limit).
- Method comparison `ai/gemini_compare.py` (5 creators; 1x12, 10in1, 5+5, 6+6, 4x3, 8in1, 4+4, 6in1, 1x10/1x8/1x6): $0.34. Noise run (fresh 1x12 + 4x3) $0.108 (stopped at 3 creators, see below). Hand-checked truth sheet of 60 reels (`ai/state/ai_truth/truth_v1.json`) scored by `ai/gemini_truth.py`: creator level 4x3 46/46 and 27/27, 1x12 45/46 and 27/27, 6+6 44/46, 10in1/1x10/1x8 43/46, 5+5/1x6 42/46, 4+4 41/46, 6in1 39/46; reel level 96–99% for all; self-agreement 1x12 97–99%, 4x3 97–100%. Chosen: 12 reels as 4+4+4.
- Rule changes after the user's corrections (v3.1→v3.4): niche/near_niche/not_niche; Hindi family; low-confidence languages flagged; collabs decided by code from promoted non-own brands; expert shown only with a credential quoted from bio/speech and matching a credential regex (8 creators have one; all checked in their bios); category = subject, comedy/dance style as the reel's secondary_category; main category counted from reel main categories only; Lifestyle when > 5 real (≥2-reel) categories or no leader; 7-creator v3.4 test incl. 2 pure-comedy controls (no Fitness added) $0.088.
- `ai/gemini_run.py`: groups ≤ 18 MB, 180 s trim, early stop after each group, single-reel fallback, resume, spend cap, writes `creator_ai` (json + flat columns), `reel_ai`, view `creator_overview` (`--migrate`, `--flatten`). 12-creator test $0.27. Full run 2026-11-26 01:35–03:05 (three parts: 10 workers, then 20, then resumed after the workspace budget): **685/685 active creators: 662 done, 23 stopped_non_creator (salons, nail studios, shops, brands, restaurant, agency, repost pages), 0 failed, $8.80 stored cost**; 139 need review; categories Lifestyle 133, Beauty 102, Food 100, Fashion 73, Travel 64, Comedy 59, Fitness 46; female 380 / male 242 / unclear 40; main language Hindi family 390, none 93, English 62, Malayalam 21.
- Dashboard → **Kindred Board** (`kindred_board/`, 8791): AI columns, filters, AI profile + per-reel notes in the drawer, CSV AI fields; active by default; the 23 non-creators hidden (kept in DB).
- Moved everything AI out of the scraper repo into this repo: `ai/`, `kindred_board/`, `docs/ai-profile-spec.md`; AI data `ai/state/` (372 MB, gitignored); scripts read the scraper's `igs/store.py`, `.env`, `media/` via `../instagram-scraper` (run with its `.venv`). Verified from the new place (self-test, dry run, truth scoring, resume skip, board + video). Commits: scraper 50b6d6e then 1257bfe (removal, README); this repo 0f67cc3, 0a5f6a3 (not pushed). Memories: examples-mean-principles, no-captions-hashtags.

Did not work:
- My first "$6.5 for 685" was a guess for one request per creator; after switching to one reel per request the estimate rose to $12–13 and I did not say clearly why; the user asked and I explained (instructions repeated per request).
- 12 reels in one request is impossible: Gemini takes ≤ 10 videos per request.
- v3 pilot: @iamasish_tripura 12/12 reels HTTP 402 "requires at least $1.00 in balance for video" (key limit $5, $0.80 left).
- Method test: two flex requests hung ~15 min (one video group, one text-only creator step) → 900 s timeout; later 240 s + retry.
- Noise run stopped instantly then after 3 creators: per-call reserve × parallel calls exceeded the small cap (8×$0.05 > $0.25; later 0.02). Same cause stopped the 12-creator script test at $0.11 (cap $0.30).
- Full-run script first version failed creators that have fewer than 6 reels in total ("only 5 reel notes") → fixed to accept all available reels.
- v3.4 first versions: one-off categories made a Marathi comedy creator "Lifestyle"; counting secondary categories equally made a makeup artist "Fashion" main → both fixed and self-tested.
- I misread the user twice (proposed tips_howto/skill_showcase roles and "creator title"; the user wanted the original roles plus two category rules) and built a truth sheet using captions (user: never use captions).
- Full run: 10 workers ≈ 5 h projected → restarted with 20; **OpenRouter workspace daily budget $5 → HTTP 403 for every request at creator 279/648** (separate from the key limit; S-016 had noted it, I did not check before starting); stopped, user raised it to $12, resumed. One request of 29.2 MB → HTTP 413 "exceeds the 20000000 byte limit for Google AI Studio" (@trivago_expedition_ kept 11/12 reels). PROGRESS lines show a wrong denominator (skipped subtracted twice).
- Prompt caching via cache_control: 25% then 7% cached.

Established:
- Durable details are in `docs/ai-profile-spec.md` (rules, method, run, platform limits).
- Gemini through OpenRouter bills ~66–70 tokens per video second and ~20–25 per audio second; flex endpoints are half price and synchronous; `:batch` (Vertex) may take up to 96 h.
- After the run the OpenRouter key showed no limit (`limit_remaining` null); the run's own cap protected spend.
- INDEX had said the OpenRouter key had ~$0.95; it actually had $14.44 (account $18.50 credits).

User decided:
- Product name Kindred. Model Gemini 3.1 Flash Lite (flex), 12 reels as 4+4+4, accuracy before cost ("jahan cost cutting ho paaye" only).
- Never captions/hashtags, not even when checking; no city/location at all; every spoken language identified.
- Category = what the creator makes content about (gym comedy = Fitness + Comedy); > 5 different things = Lifestyle; niche only for one-topic creators; expert only with a stated degree/certificate; roles stay expert_educator/reviewer/entertainer/lifestyle.
- Early stop for clear non-creators only at high confidence; cap below the key limit.
- AI work and the dashboard live in Brand Deal Matcher; the scraper repo holds only the scraper. Dashboard named Kindred Board, non-creators hidden.

Open:
- Matching on the new data (score per brand, adjacency "never promoted but fits", embeddings, Haiku review; persona idea) is designed, not built; live site still reads the old DB.
- Push both repos (this one is PUBLIC; asked, not answered). Review the 139 flagged and 23 stopped creators (salons: creator or business?). 163 inactive not analysed. @trivago_expedition_ missing reel. User's language check of the 5 pilot creators pending. Fix the PROGRESS denominator.
- Set an OpenRouter key limit again; workspace budget now $12/day.

---

## S-025 · 2026-11-26 · Kindred website built in web/ (Next.js 16 + Supabase): conversational 5-question chat, no sign-in, top 20 by Kindred Score; AI matching built but off

Asked:
- "ab user dashboard banate hain, jahan pe user aaye, login kare, and then usko apne need ke hisaab se creators dekh paaye";
  "backend ka kya ha kuch"; "pheal muje stucture sama complete repo ha kha kya reha ga and request kha sa kasha".
- Wanted (pasted): landing → sign in → chatbot that asks questions → "model ke through database dekh ke ... sahi creators";
  "Purple color bilkul nahi ... AI-generated bilkul nahi"; full end-to-end test with 3-4 brands + security audit + "Ekdum
  complete visual diagram ... anpadh-champda aadmi bhi dekhe"; "Vercel pe frontend ho jaye, Render pe backend ... pehle mere
  ko bata hi de ki kya approach apne hisaab se sahi rahegi".
- "Git pe push karna. Vercel pe abhi deploy mat karna. main wahan se use deploy kar dunga"; "versal pe ek tha. Pehle se maine
  wo delete kar diya. Project naya project banana hai, kyunki purane wale creators nahi lene."
- "Abhi OpenRouter se kuch bhi credits use mat karna"; "abhi tu sirf pehle bana ke de mere ko ek website app ... LLM ko kya
  batana hai, kya nahi karna hai, wo saari cheezein apan baad mein main batata hoon".
- "category select karein ... to wo categories ke saare creators dikh jaayen. Abhi sirf wahi rakh."
- Questions: 1. "Tell me about your brand: What do you make? ... cool way mein", 2. product, 3. "Which creative would you
  like? ... category ke saare", 4. "Who buys it mostly?", 5. female/male creator "with 'Do you have any language
  preferences?'"; "Thoda cool way mein, fun Gen Z likho"; "yeh question-answer type nahi lagna chahiye. yeh conversation
  type lagna chahiye".
- "ek harness bhi daal dena" → "harness ki zarurat hai ya nahi hai?" → "Chal harness jaane de, wo baad mein dekhte hain."
- "Google se sign in ... wo poora option abhi hata de ... Abhi demo ke liye sign in mat rakh."
- LLM: "LLM ko kaise train karna hai"; "pehle bhi chats jab kiye the, tab kya decide kiya tha ... kaun sa model";
  "ye saari cheezein nahi dekhni ... kis umar ka hai ... faltu ka bigaad mat"; "Kaun kharid sakta hai, wo probably brand
  bata dega ... apne paas jo creators ki list hai, unmein se kaun bech sakta hai ... lifestyle creator ... fashion ki cheez
  bech sakta hai ya nahi"; "mere ko ek LLM dhoondh ke aur is pe daal, aur phir mere ko test karke bata".
- Then: "Abhi ke liye ... options se jo last ke creators bach rahe hain, un creators mein se best creators, top 20 ... LLM se
  ekdum hi zyada personalized mat karwa ... brand ke hisaab se candidate score banana hai ... sirf demo ke liye".
- Checks on localhost: a designer's showcase page "creator kam lag raha hai"; a nail-art account "isme yeh aana hi nahi
  chahiye"; "ye dono hi galtiyan thi. baaki saare creators sahi the ... jaldi theek kar de".

Done:
- Architecture (recommended, accepted): one Next.js 16 app on Vercel holds pages + API route handlers; Supabase "database"
  holds creators, website tables and sessions; Render not used (it only hid a key for the static demo/, and its free plan
  sleeps). Choices via AskUserQuestion: Next.js + Supabase, Google-only sign-in (later removed), paywall later, website first.
- web/ created (create-next-app 16.4.6, React 19.3, Tailwind 4); libraries approved by the user: @supabase/ssr,
  @supabase/supabase-js, zod. Read the bundled Next 16 docs first: middleware is now src/proxy.ts; cookies()/params are
  async; the starter's cacheComponents/partialPrefetching were removed (every page reads the session).
- DB (web/db/migrations/001_website.sql, 002_llm_kinds.sql, applied with web/db/migrate.py via the Management API):
  brand_searches (chat, brief, results; RLS: select own), llm_calls (no browser access), explicit service_role grants,
  creator_overview set security_invoker, stray anon TRUNCATE/TRIGGER grants on creator_ai/reel_ai revoked; private bucket
  creator-photos with 662 profile photos (web/db/upload_photos.py). ai/gemini_run.py now creates the view security_invoker.
- Design: Archivo (wide cut for headings), one coral accent #ff5a36 with dark ink text on it, no purple, Instagram
  story-ring around photos, light + dark; landing numbers come live from the DB (598 creators, 18 categories).
- Chat evolved in four steps on the user's orders: 10 fixed questions + brief card + "all creators of one category" →
  5 questions (casual Gen Z copy) with filters (lib/filters.ts, shared by results and a live "N creators fit" count) →
  conversation (lib/conversation.ts: reactions per category, product name echoed, 2-3 short bubbles with typing pauses,
  typed answers to choice questions read with keywords, errors as a Kindred bubble, no progress bar) → results = top 20 by
  Kindred Score (lib/rank.ts).
- No sign-in: login page, Google button and account menu removed; a private anonymous Supabase session is created when a
  chat starts (POST /api/searches in lib/api.ts), never on a page view; Supabase anonymous sign-ins on, 100 new anonymous
  users/hour/IP, email sign-up off, Google off.
- Explained the LLM plan several times; looked up the 2026-11-20 decisions (memory + docs/data-and-matching.md): Haiku 5.5
  via OpenRouter for text, Gemini only for video, embeddings never decided. Fetched OpenRouter prices (free call): Haiku
  5.5 $0.10/$0.50 per M, Gemini 3.1 Flash Lite $0.25/$1.50, GPT-5 mini $0.25/$2.00, Sonnet 5.5 $2/$10.
- AI matching built and left OFF (LLM_ENABLED=false, LLM_REVIEW=false): lib/llm.ts (Haiku 5.5, strict JSON, daily cap,
  every call logged), lib/product.ts (product type, words, same-shopping-world words, made_for, categories), lib/review.ts
  (40-creator shortlist, Haiku reads 12 reel notes per creator: strong/good/weak + why + idea + cited reels; code checks the
  citations; specialists/category/lifestyle groups), web/db/ai_check.py. One paid pilot (men's watch): 5 calls, $0.0055,
  9 s, automatic rules passed.
- Demo ranking lib/rank.ts (no LLM): product relevance 35 (product's own category x1, fixed close category x0.8, Lifestyle
  x0.5, + reels naming the product), audience 15, engagement 15, reach 10, on camera 10, language 5, regularity 4, brand
  ready 3, quality 3; no-relevance creators and portfolio pages never in the top 20. Durable description: docs/website.md.
- Tests: web/db/e2e_test.py (6 test brands incl. one typing every answer, anonymous visitors, security, bundle scan),
  92/92 passing at the end; web/db/test_login.py (one-time sign-in links via admin API for test users on
  kindred-test.example.com). Browser checks with Playwright (light/dark, mobile, console 0 errors).
- Visual diagram published as a private artifact (https://claude.ai/artifact/FNjYEvRJMr9BPb7fq5gvwL, version 3: big
  picture, 21 request steps, security locks, tests); it predates the top-20 ranking.
- Commits pushed to GitHub (public repo): 7e04453 (website; also pushed the S-024 commits 0f67cc3, 0a5f6a3, 54c4707),
  78b57c4 (5 questions), b20f712 (conversation), 1fdb0a2 (no sign-in), 9cf88f8 (top 20 + AI off), 8be9d22 (relevance fix).
  Memory added: deploy-via-github. CLAUDE.md (gitignored) build/run lines updated.

Did not work:
- PostgREST "permission denied for table brand_searches" for the secret key: this project does not grant new tables to
  service_role by default; fixed with explicit grants in the migration.
- Playwright profile locked by a stale Chrome from 2026-11-25 16:27; killed it.
- supabase-js client typed as never (ReturnType<typeof createClient>); fixed with SupabaseClient.
- Plain CSS component classes overrode Tailwind utilities (textarea border); moved them into @layer components.
- Bundle scan "secret key in browser JS" was a false alarm: supabase-js contains the literal prefix "sb_secret_".
- Build failed on stale .next/dev types for a deleted route; rm -rf .next.
- Anonymous session in proxy.ts created accounts on link prefetches: Next 16 strips next-router-prefetch and similar
  headers before the proxy (docs: skipProxyUrlNormalize); moved session creation to POST /api/searches.
- Playwright cannot open file:// pages, so the diagram was published without a local preview.
- Pre-push scan found 4 creator handles in pushed content from S-024 (journal 002, INDEX, ai/gemini_dryrun.py help text);
  the help text was changed to placeholders, the append-only journal was left (2 handles were already on GitHub from S-023).
- AI pilot: the review put outfit reels into "product seen" for a watch (two accounts with no watch in any reel note);
  prompt narrowed and code now verifies cited reels name the product. Not re-run after the fix.
- Ranking v1 rewarded the category label: "All categories" put automobile/dance creators first for a coffee brand, and
  product words like "starter"/"500g" counted; then a nail-art studio and a fashion designer's showcase page reached a
  watch brand's top 20 (user's check). Fixed with product relevance + portfolio exclusion (docs/website.md).
- In one LLM-plan answer I left out the 2026-11-20 decisions (field/account questions, three columns, "no AI = no unchecked
  results"); the user had to ask what was decided before.

Established:
- Supabase "database" project ref rhaqbnvmyjcwgeosltaf: keys default publishable/secret (sb_*) available via
  /api-keys?reveal=true; auth site_url http://localhost:3000, redirect list http://localhost:3000/**.
- Reel notes (reel_ai.note) carry products with item/type/for/brand/level, owner_on_screen, owner_speaks, format,
  sponsored_signs; e.g. "watch" appears in 14 creators' notes, "candle" 17, "protein" 29.
- 30 of 598 creators are portfolio pages (26 beauty/makeup studios).
- OpenRouter: $18.50 credits, $13.85 used before this session's $0.0055 pilot; key has no limit.

User decided:
- Next.js + Supabase on Vercel only; user deploys from GitHub (never CLI); old Vercel project deleted, old creators unused.
- No LLM and no credits until the user explains personalisation; demo = top 20 by candidate score from the chat choices.
- Five questions, casual Gen Z tone, must feel like a conversation; who buys comes from the brand; do not judge age,
  persona or mood; the AI's job later is "who among our creators can sell this product".
- No sign-in for the demo (Google later); harness later.
- A showcase/portfolio page and an unrelated nail-art studio are wrong results; the rest of that watch search was right.

Open:
- User to deploy web/ on Vercel (Root Directory web; NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  SUPABASE_SECRET_KEY); then set Supabase site URL to the live domain.
- Personalisation/AI: user will explain; before switching on, re-run web/db/ai_check.py (the product_seen fix is untested).
- Decide: music-only creators pass every language filter (currently yes). Old Render API still serves the old DB.
- Diagram artifact does not show the top-20 ranking. Test users on kindred-test.example.com exist
  (python3 web/db/test_login.py --delete-all). Scraper repo still 2 commits ahead of origin (not pushed).

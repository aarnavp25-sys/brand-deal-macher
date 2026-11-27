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

---

## S-026 · 2026-11-26 · Kindred live on Vercel (kindred-eta-black.vercel.app) with AI on and a $1 total cap; name question; Singapore region; deck and viva explanations

Asked:
- Deploy: "aap isko Vercel pe deploy karte ho. Mere ko final link de, jo main share kar paaun, to meri mam iska demo le
  paaye ... aur us pe $1 ka cap rakhna. Agar searches ki costing $1 se zyada ho rahi hai, to searches rok dena apne aap
  hi." Picked "AI ON + $1 cap (Recommended)" in a question. Then: "Git pe sab push karne ke baad Vercel pe deploy
  karna, samjha?"
- Presentation: "mujhebye project ka pos banake de abhii presentation hai"; "jaldi bana"; later "pos kya hota hai".
- Viva prep, each answered in chat only (no files): "apna scrapper kaise kaam kara raha hu ekdum details mai bata" →
  "english mai bata sab" → "short nhii ekdum detail"; "ye Instagram block kaise nahi kar raha hai?"; "wrap jo hai, wo
  IPv4 dete hain, aur uska IPv6 kaise ho raha hai?"; curl_cffi / "each request looks like real Chrome ... hinglish mai";
  "apne ko apna kuch ka scraper banane ki need kya padi?"; "website mein jo bhi buttons hain ... uska backend kya hai";
  "problem statement achhe se bata"; "how homegrown startups are there and how many creators are there"; "ai back and
  forth question kaise kar raha hai aur ai ye scroe kaise bana raha hai"; "mujhe apne database ka link de".
- "ek baar dekh aur bata ki website barbar kaam kar rahi hai na"; "find creators likhta hu tab itna time kyu lag raha
  hai load hone mai"; "isme google auth daalne mai kitna time lagega".
- "find creators click karne ke baad user ka naam puchna hai woh daal aur ye bata past hiostory kaise save ho rahi
  hai"; then "haa xhange karde" (push + Singapore region + deploy).

Done:
- /context-read: INDEX matched the code; noted CLAUDE.md said e2e "63 checks" while INDEX said 92.
- Spend cap (commit f520d1e): `web/src/lib/llm.ts` daily cap `LLM_DAILY_CAP_USD` replaced by a TOTAL cap
  `LLM_TOTAL_CAP_USD` (default 1) summed over all `llm_calls` rows, `budgetReached()` stops $0.01 early;
  `createSearch()` in `lib/searches.ts` refuses new chats with 503 when reached. Tested locally with cap 0.005 →
  POST /api/searches answered 503 with no AI call. e2e with AI off: 92/92.
- AI check (paid, approved ~$0.03): `python3 web/db/ai_check.py 1 2 3` with LLM on → 3/3 brands passed the rules,
  $0.0054–0.0055 per brand; the product_seen fix held (watch brand: 1 strong creator, real watch-unboxing reels; outfit
  reels no longer counted). Candle brand had 2–3 stretched picks (bridal makeup artists). One more search driven
  through the API with the rendered results page checked (charcoal face wash): page shows groups, score, why, idea.
- Pushed both repos (brand deal matcher; instagram-scraper's 2 pending commits). Vercel: `vercel project add kindred`
  (team dragon-44d8); root directory `web`, framework nextjs, node 22 set via the REST API (token read from
  ~/Library/Application Support/com.vercel.cli/auth.json, never printed); env vars set via API from web/.env.local:
  Supabase URL / publishable (plain), SUPABASE_SECRET_KEY (sensitive), OPENROUTER_API_KEY (sensitive, production only),
  LLM_ENABLED=true and LLM_REVIEW=true (production only), LLM_TOTAL_CAP_USD=1. Deployed with `vercel deploy --prod` from
  a `git archive HEAD` export in the scratchpad (so only committed files upload). Live:
  https://kindred-eta-black.vercel.app (public, 200, security headers present). Supabase Auth site_url set to it and
  `https://kindred-eta-black.vercel.app/**` added to the redirect list (localhost kept) via the Management API.
  One live AI search (pickle brand) worked. Memory `deploy-via-github` updated (deploy only when asked; push first).
- Deck: Slides artifact https://claude.ai/artifact/Wses6ZjK7eCxJSCZrtoKuV (private; 12 slides: cover, problem, idea,
  4-step flow, data, AI profiles, chat, score formula, real watch result, stack/security/cost, next, live demo;
  Hinglish speaker notes; no creator usernames). Not rendered or previewed by Claude. Slide 7's "212 creators" is a
  made-up example number (said so in its notes). "pos" was taken to mean PPT; the user later asked what POS means.
- Market research for the viva (web search, 2026-11-26): DPIIT-recognised startups ~1.98 lakh (Oct 2025), ~2.23 lakh
  (Mar 2026); ~800 funded D2C brands vs 50,000+ consumer brands (broad, Inc42); ~7.3 crore Udyam MSMEs; Indian
  Instagram creators 18–23 lakh (Kofluence 2025), ~18.9 lakh (HypeAuditor 2026). Vendor numbers are estimates.
- Live health check: pages 200, CSRF 403 for no/foreign Origin, one full live search 22 creators in ~47 s, 40 AI calls
  so far with 0 failures, total spend $0.0433 (≈$0.96 of the cap left); no Vercel error logs in the last 30 min.
- Slow "Find creators" diagnosed: Vercel functions ran in `iad1` (Washington, the default) while Supabase is
  ap-southeast-1 (Singapore); start chat 2.8–4.5 s + chat page 1.7–2.1 s (5–7 s total). Fixed later (below).
- Name question (commit 8b98edb): `lib/brief.ts` new first step `name` (text, max 40) with `TypedName` rule (letters,
  spaces, . ' - only) and `name` in `BriefSchema` (lenient); `lib/conversation.ts` asks it ("First things first, what
  should I call you?"), answers "Nice to meet you, <first name>!", greets a returning visitor "Hey <name>, good to see
  you again." and ends "Here are your top N, <name>."; `answer()` saves it to the Supabase user's
  `user_metadata.name`; `createSearch(userId, brand.name)` pre-fills it (account names, e.g. Google later, taken as
  they are); dashboard says "Hi <name>!". The name is never sent to the AI. e2e gained 7 name checks → 102/102 with
  LLM_ENABLED=false (env override on `npm run start`); `ai_check.py` answers the name first. docs/website.md updated.
- "haa xhange karde": pushed; Vercel `resourceConfig.functionDefaultRegions = ["sin1"]`; redeployed from a fresh
  `git archive` export. Live after: start chat 0.55–0.84 s, chat page 0.50–0.68 s (first request after idle ~2–3 s);
  name flow and "good to see you again" verified live. README (ba03ef4) and docs/website.md (d2bd5e9) record the
  region rule and the AI-on/$1-cap state.

Did not work:
- `vercel git connect` → "You need to add a Login Connection to your GitHub account first. (400)". The Vercel account
  has no GitHub login connection, so pushes do not auto-deploy; deploys are CLI from a git export until the user adds it.
- `vercel link` silently created `.env.local` (a VERCEL_OIDC_TOKEN) at the repo root and appended `.vercel` / `.env*`
  to the root .gitignore; both reverted, the `.vercel` link folder kept only in the scratchpad export.
- Playwright MCP: "Browser is already in use for .../mcp-chrome-..." (another session held it); UI checked by fetching
  the rendered HTML with the API-driven script instead.
- Vercel PATCH with both `serverlessFunctionRegion` and `resourceConfig.functionDefaultRegions` → 400 "Cannot specify
  both"; only `resourceConfig.functionDefaultRegions` worked.
- `vercel logs --since 6h` → Hobby plan keeps runtime logs only ~30 min.
- First e2e after the name step: 9 fails (409) because the test brands' account name "Test Brand 1" has a digit and
  failed the typed-name regex, so they were asked the name; after taking account names as they are: 5 fails (500,
  ZodError at the final `BriefSchema.parse`) because the regex was still in BriefSchema. Fixed by moving the strict rule
  to `TypedName` (typed answers only).

Established:
- Vercel creates new projects in `iad1`; with Supabase in Singapore each DB round trip cost ~250 ms. Region must be
  `sin1` (Project Settings → Functions).
- One AI search = 5 Haiku calls, ~$0.0055, ~45–47 s live; OpenRouter credits 18.5 total, 13.85 used (~$4.65 left) on
  2026-11-26 before the demo searches.
- Live search history is per browser (anonymous Supabase user in a cookie); clearing cookies / another device = a new
  user and the name is asked again. Google sign-in (linkIdentity) is the fix; estimate ~2.5–3 h incl. ~20–30 min of
  the user's Google Cloud Console work; `/auth/callback`, `/auth/signout`, `safeNext` already exist.

User decided:
- AI ON for the demo with a $1 TOTAL cap; searches must stop by themselves when it is reached.
- This time Claude deploys, but only after pushing everything to GitHub first.
- Ask the visitor's name after "Find creators"; move functions to Singapore.

Open:
- Vercel GitHub Login Connection (user, in Vercel → Account Settings → Authentication) to get auto-deploys on push.
- Google sign-in: not started; recommended after the 2026-11-28 demo.
- Deck: the user should page through it (not previewed), share it from the page's Share menu if others need it.
- Tell the demo audience a search takes ~45 s. Anonymous test users and abandoned chats accumulate in the
  "database" project (test_login.py --delete-all removes only the test brands).
- Personalisation of the AI still to be explained by the user. Old Render API still up. Earlier reminders unchanged.

---

## S-027 · 2026-11-27 · Google sign-in, dashboard + name pop-up, AI brand summary, follower slider, Let Kindred decide, richer creator cards; 20-brand stress test (fixes on hold); all live

Asked:
- Data questions: "apne pass kya koi niche creator hai jaise koi sirf watch pe bat karta ho"; "how many creators do we
  have more than 50k"; "apne db mai apne pass user ka kya kya hai".
- "google auth dalna hai google se sign in ke baad hi kuch bhii search kar sakta hai" (home page public; name still
  asked: "Naam phir bhi poochho").
- "Sign in karne ke baad jo ek chatbot aata hai, wo chatbot khulna nahi chahiye ... sirf 'What is your name?'
  poochega ... ek pop-up type ... Sign in ke baad ek user dashboard type bana de"; wording "thoda cool way mein",
  example "Aarnav".
- Account menu: "maine is pe click kara ... ye abhi hat nahi raha". Chat box: "jo chatbot pe box sa aa raha hai na,
  wo hata dein".
- First question: "what's your brand, what is its spirit" → then "What's your brand? What do you make? Spill it" →
  later "What's your vibe hata de question mein se".
- AI summary flow: "apna AI jo samajh raha hai, wo dikhna chahiye ... Is this what you mean?"; one re-explain only:
  "No dega to 'Could you explain it again?' ... pehli baar yahan pe hi samajh jaani hai"; product question only for a
  brand with several products ("resume bana ke deti hai ... usko thodi pooch sakta hai ... which product").
- Followers: "ek range dena hai ... dono side se scroll"; "Slider mein 5K mat rakh, 1K rakh".
- Categories: "hamesha tick hata de ... tu kuch bhi select mat karo ... ek aur option 'let Kindred decide'".
- AI agent search: "tech creators aa rahe the ... phone promote karte hain ya hardware ... check kar ki wo kyun ho raha
  tha" and "kuch bhi change karne se pehle poochna"; then a 20-question stress test and "ek proper report".
- Cards: "followers, average views, reach, engagement, comment ... brand collabs ... bio mein collab email ya number".
- "isko deploy kar de ... jo tu teen suggestions keh raha tha na, wo abhi hold pe rakh ... sakht banana ... ruk".

Done:
- Read-only answers: 167 of 611 active creators are "niche" (topics, not single products; no watch-only creator);
  247 of 848 creators have ≥50K followers (199 showable); auth users 50 (45 anonymous, 5 test), 80 searches, two real
  outside visitors who typed ideas/services rather than products.
- Google sign-in (12bdcbd): restored /login, GoogleButton, browser client from 1fdb0a2^; proxy protects /find,
  /dashboard, /results; anonymous sessions count as signed out; API 401 without Google. The user created the Google
  Cloud project "kindred" (OAuth consent External, published) and the Web client (origins live + localhost, redirect
  https://<ref>.supabase.co/auth/v1/callback) and pasted the id/secret in Supabase; Claude verified the provider via the
  Management API (enabled, id format ok). Deployed, then Supabase `external_anonymous_users_enabled=false`.
- Dashboard + name pop-up (4001473, 1f7a983): sign-in lands on /dashboard (from "Find creators" too); `NamePopup`
  ("Hey there! What should we call you?", placeholder "e.g. Aarnav") until `user_metadata.kindred_name` is set (kept
  apart from Google's `name`); `POST /api/profile/name`; `createSearch` refuses 409 without a name; the chat no longer
  asks it. Dashboard: "Hi <name>!", Start a new search card, 3 numbers, saved searches.
- Fixes: account menu became `AccountMenu` (closes on outside click / Escape / page change) (f05aab4); inner focus
  outline in the chat composer removed (`.composer-input`) (26772b8).
- Brand understanding (27fd584, f2044dc, 3eb1b32): `understandBrand()` in lib/product.ts (one Haiku call: summary,
  kind single|range, product words); steps confirm / more / focus in lib/brief.ts with a branching `nextStep`;
  `MAX_EXPLAINS` = 1 ("Could you explain it again?" then "Got it. This is what we have understood now:" and straight
  on); range brands get "Are you planning to promote a particular product, or your brand in general?"; prompt forbids
  internal words ("single"/"range") in the summary. First question: "What's your brand? What do you make? Spill it all."
- Follower range (4b413bc): step `followers` after buyers; `RangeAnswer` two-handle slider 10K–100K, 1K steps, live
  count; typed ranges ("20k to 50k", "under 30k", "50k+"); `followers_min/max` in `passes()`; ends = no limit.
- Categories (38da2bd): nothing pre-ticked (Lifestyle was always forced before); "Let Kindred decide" below the chips
  (AI main + close categories, said back as "Kindred picked … for you").
- AI agent investigation: both "AI agent" searches were understood correctly; only 7 showable Tech creators (mostly
  phones) and 1 finance creator exist; the localhost search had 10K–50K + Hindi/English, leaving 2 creators.
- Stress test: `scratchpad/hard.py` ran 20 brands through the local chat with AI (cost $0.068) → report doc
  "Kindred — Matching Stress Test (20 brands)" https://claude.ai/artifact/Mav7LbwJsy26j7GhNHXsb4 (verdict, table of 20,
  causes, coverage chart, 5 suggestions). Findings and the hold → docs/website.md "Known matching limits".
- Demo: headless Chrome screenshots of every screen (name pop-up → results) opened in Preview; found the categories
  screen heavy, a red "Nobody fits this combo yet" when nothing is ticked (bug from the no-pre-tick change), and a
  results header line contradicting the cards. Proposed 3 UX fixes — on hold.
- Creator cards (02dc661): migration 003 view `creator_card_stats` (mean_views, avg_comments over reel_rank 1–12,
  bio, bio_links; service_role only, ends with `notify pgrst, 'reload schema'`); `lib/contact.ts` (email, Indian
  mobile, wa.me link from the bio); `components/CreatorStats.tsx` on all three result layouts: Followers · Avg views ·
  Reach · Engagement (est.) · Avg comments · Speaks · Audience · all brand collabs · Contact (from their bio).
- e2e now 125 checks (AI off). Pushed and deployed four times; last deploy = 02dc661, verified live (cards, AI summary
  + Yes/No buttons). Spend: total ~$0.15 of the $1 cap.

Did not work:
- Google login first attempt → Supabase `{"code":400,"msg":"Unsupported provider: provider is not enabled"}`: the user
  had not yet enabled Google in Supabase (first opened the Email provider panel by mistake).
- e2e after Google: 9 then 5 failures — test brands' names "Test Brand 1" have digits (typed-name regex), and the
  regex sat in BriefSchema (500 ZodError at the final parse). Fixed with `TypedName` for typed names only and
  letter-only test names.
- `npx tsc` after restoring /login: TS2344 '"/login"' not in AppRoutes → `npx next typegen` regenerated route types.
- React lint `set-state-in-effect` on the account menu's close-on-route effect → keyed open state by pathname instead.
- Migration 003 applied but PostgREST answered 404 until `notify pgrst, 'reload schema'`.
- Demo run: final step 500 — Mac network blip ("LLM review failed: fetch failed" ×4, then Supabase fetch failed);
  retry succeeded. Not a code bug.
- Playwright MCP stayed locked by another session all day; screenshots via headless Chrome instead.
- A test brand ("brand1") showed the name pop-up live: it simply never had a name saved (e2e uses brands 2–7).

Established:
- Supabase Google provider and anonymous sign-ins are set in the dashboard / Management API; anon-off needs ~10 s to
  apply (one anonymous user slipped in and was deleted).
- Results are a snapshot: searches saved before 02dc661 show "-" for avg views, reach, avg comments, contact.
- Bios: 116 of 848 have an email, 91 an Indian mobile number, 42 a WhatsApp link.
- Showable creators by category (603): Lifestyle 126, Food 92, Beauty 87, Fashion 67, Comedy 58, Travel 58, Fitness
  41, Music 23, Automobile 17, Tech 7, Parenting 7, Gaming 6, Home & Household 5, Jewelry 3, Decor 2, Finance 1,
  Sports 1, Pets 1.

User decided:
- Google sign-in required for everything but the home page; the name is still asked once, in a pop-up after sign-in,
  never in the chat; after sign-in the dashboard, never the chat.
- AI summary + confirm, one re-explain only; product question only for brands with several products; nothing
  pre-ticked in categories, "Let Kindred decide" offered; follower slider in 1K steps.
- Cards show followers, avg views, reach, engagement, avg comments, languages, brand collabs and bio contact.
- ON HOLD (2026-11-27, "abhi hold pe rakh ... baad mein discuss"): the 3 UX fixes (categories screen, merging buyers +
  followers + gender/language, results header line) and making the AI stricter (stress-test suggestions).
- Ask before changing anything in matching ("kuch bhi change karne se pehle poochna").

Open:
- The hold list above; ask before starting any of it.
- Optional: overlay live card numbers on old saved searches (offered, not answered).
- Contact is free for every signed-in brand until a paywall exists.
- Old Render API, key rotations, scraper backups: unchanged reminders.

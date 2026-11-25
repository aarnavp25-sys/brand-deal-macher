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

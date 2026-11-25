# AI creator profile: spec (video-v3, set 2026-11-25)

What the AI must find for every creator, how, and which parts are allowed to drive matching. The owner left the
design to Claude on 2026-11-25 ("tere hisaab se set kar de") with one bar: no silent fuck-up. The principle is
**the AI labels, the code decides**: the model answers small, concrete questions per reel; creator-level facts are
counted by fixed rules in code, so every result can be traced to reels.

Model: `google/gemini-3.1-flash-lite` on OpenRouter, `service_tier: "flex"` (half price, synchronous; batch can take
up to 96 h on Google Vertex). It watches the 360p video at ~1 frame/s and hears the audio. Haiku 5.5 cannot take
video or audio (checked 2026-11-25).

## Two steps

1. **Reel step** (one request per reel; ~1–3 MB each, so request size is never a problem). Input: the reel's details
   (date, length, audio type + song, Instagram topic labels, Instagram's image description without the display
   name, collab partner, tagged accounts, location) and the video with audio. No captions/hashtags (owner's choice),
   no views/likes/followers. Output: facts about that reel only (schema `REEL_SCHEMA` in tools/gemini_dryrun.py).
2. **Creator step** (one text request per creator, cheap). Input: username, bio (emails/phones removed), bio-link
   domains, profile picture, all reel notes from step 1, and the code's counts. Output: only the judgements that
   cannot be counted (account type, role, what they do, journeys, audience estimate, collab status).

## What the creator gets, and who decides it

| Field | Tier | Decided by | Rule |
|---|---|---|---|
| account_type (creator / personal / repost_or_meme_page / shop_or_brand / organization / professional / celebrity) + reason + evidence | A | AI (creator step), checked by code | review if AI says creator but the main person is on screen in < 3 reels and speaks in < 3 |
| sells_own_products | A | AI | a creator with her own boutique stays a creator |
| content_mix (category -> reel count) | A | code | count of reel categories |
| category / secondary | A | code | most reels; secondary needs >= 3 reels (>= 25% when fewer than 12); top share < 40% -> scope "broad" |
| niche + niche_creator | A | AI proposes, code verifies | niche_creator only if the AI's niche reels are >= 75% of analysed reels and >= 6 reels; otherwise not niche (owner: "ek bubble mat bana dena") |
| creator_gender (male / female / couple / group / unclear) | A | code | >= 70% of reels with a main person agree, else unclear -> review |
| content_made_for (men / women / everyone -> reel count) and products_for (men / women / unisex -> count) | A | code | who the CONTENT is aimed at, judged per reel from what is shown, said and sold, not from the creator's gender. Matching uses these: a men's perfume brand gets creators whose content is aimed at men; a woman appears only if her reels really are for men (e.g. gifts for him). Owner, 2026-11-25: examples are examples, the rule is "understand what the content is for" |
| spoken_languages with counts | A | code | speech only (lip-sync songs do not count); Hindi and Urdu are one value (indistinguishable in speech) |
| what_they_do (<= 40 words) and journeys (transformation, before/after, launch, pregnancy, wedding, achievement, recurring series) with evidence | B | AI | only what reels show or say |
| products (type, item, promoted / shown, reels) | B | code merges reel notes | promoted = brand named/tagged/code/review; shown = used on camera as the point |
| brand_collabs (yes / maybe / no) + brands | B | AI from notes, tags, co-authors | promoting own shop/product is not a collab |
| creator_role (expert_educator / reviewer / entertainer / lifestyle) | B | AI | 4 values instead of 7 (humans disagree on finer ones) |
| audience_gender_estimate, audience_age_estimate + reason | B | AI | always shown as estimated; never a hard filter |
| apparent_age_group (teen_college / 20s_30s / 40_plus / unclear) | B | code (majority of reel guesses) | soft only |
| life_context (student, working, parent, pregnant, pet_owner, homemaker, business_owner) | B | code (>= 2 reels) | only when said or clearly shown; "married" is not collected |
| beard (male), on_camera_share, speaks_on_camera_share, repost_share | B | code | counts |
| quality (good / ok / weak), brand_safe | B | AI / code (any unsafe reel -> review) | 3 levels, not 1–10 |

**v3 changes after the v2 pilot (2026-11-25, 5 creators, $0.068):** the reel step also gets the account's bio as
context (a makeup artist's bridal reels were filed as Fashion); every person on screen gets a role (account_owner /
client_or_model / co_actor_or_friend / family_member), and gender, age look, beard and life context come only from
the account owner (a trainer + client skit had become "couple", a mother's cooking had made the creator a
"homemaker"); the bio's stated audience ("female plan") outranks the estimate; new category "Home & Household"
(Ariel had become "Other"), medicines go to Fitness & Wellness; sells_own_products (physical) is split from
offers_services; spoken languages cover every Indian language, with the name kept when it is not in the list;
skin colour and body words are banned in the prompt and stripped by code; the model's per-reel confidence was
dropped (it said "high" for everything) and confidence now comes from agreement counts; city and location are not
collected at all (owner: "shehar dekhne ki zaroorat nahi").

**Owner's rules added 2026-11-26 (v3.4):**
- Categories as before (main + second with >= 3 reels), with two changes: a reel's subject is its category and a
  comedy/dance telling style is its secondary category, and both are counted, so a trainer's gym comedy makes the
  creator **Fitness AND Comedy**, never only Comedy; a creator spread over **more than 5 different categories** gets one
  category, **Lifestyle** (the full content_mix is kept).
- Roles stay expert_educator / reviewer / entertainer / lifestyle. A creator is **shown as an expert only with a
  stated credential** (degree, certificate, licence: Dr., MBBS, Dermatologist, Dietitian, CA, "Certified ..."),
  quoted word for word from the bio or the owner's own speech and checked by code; job titles are not credentials
  ("personal trainer", "makeup artist", "nutritionist", "founder").
- **Method (v3 method test 2026-11-25/26, 5 creators, hand-checked truth):** 12 reels per creator, sent as 4+4+4
  (three requests). Creator level 100% right in two runs, reel level 97-99%, same as one-reel-per-request (98-100%) at
  ~2/3 of the cost; 10, 8 or 6 reels made niche and collab calls worse.

**Not collected:** body type as a label, skin colour, religion, caste, health, "married", price level, city/location. Body-related
fit comes only from what the creator does on camera (e.g. a fitness transformation, plus-size styling as a topic).

Tier A may become a hard filter only after it passes the gold test. Tier B only moves the score a little and never
removes a creator. Every field has an on/off switch (`FIELD_SWITCHES`) so a field that fails is turned off without a
re-run.

## Gold test (before any full run)

30–40 creators labelled by the owner by hand first, chosen to include hard cases: male comedians playing women,
creators with their own boutique, meme/repost pages, collab-heavy creators, music-only creators, family pages.
Pass marks: account_type >= 95%, category >= 90%, creator_gender >= 95%, main language >= 90%, Tier B fields >= 80%.
Run twice to check the same answers come back. A field that fails is switched off; no arguing with the numbers.

## Known limits (told to the owner 2026-11-25)

360p: small text, logos and price tags often unreadable. 1 frame/s: very fast cuts can be missed. The model cannot
match a face to a small profile picture reliably, so "the creator" = the person who appears across most reels.
Collab reels show the partner. Gemini may block some reels (safety); a blocked reel is marked and skipped. About half
the reels are songs, so they give no spoken language. Audience is a guess: real demographics are private. Token
counts via OpenRouter are unverified until a 5-reel paid test reads usage back.

## Cost (dry run 2026-11-25, estimates)

Per reel the ~4,500-token instructions are sent again, so text is ~57K tokens per creator. Without caching: 685
active ~$12.5, 163 inactive ~$2.7 (flex). Gemini caches a repeated prompt prefix automatically (cache read $0.0125/M on
these endpoints); if that works through OpenRouter, the active run drops to ~$7. The 5-reel paid test checks
`usage` for cached tokens before any bigger run.

## How it is run (ai/gemini_run.py)

12 latest reels per creator, sent as 4+4+4 (a group is split further so one request stays under 18 MB of base64
video); videos longer than 180 s are cut to their first 180 s with a stream copy and the model is told so. After each
group, until the account is clearly a creator, a text-only check asks whether it is a personal account, a shop/brand or
a repost page; the account is stopped only when the AI says so with high confidence AND the code's own count agrees
(status `stopped_non_creator`, kept in the DB, hidden on Kindred Board). A reel the group answer leaves out is retried
alone. Resumable (creators finished with the same prompt version are skipped); hard spend cap; 20 creators at a time
gave ~7 creators/min. Results: `creator_ai` (json + flat columns), `reel_ai` (one note per reel), view
`creator_overview`. First full run 2026-11-26, prompt video-v3.4: 685 active creators, 662 profiled, 23 stopped as
not creators, 0 failed, $8.80 (about $0.013 per creator).

## Platform limits found while running (keep in mind before any paid run)

- OpenRouter has two separate limits: the **key limit** and a **workspace daily budget** (it stopped the run at
  $5.00 with HTTP 403 "Workspace daily budget ... exceeded"; it resets at 00:00 UTC = 05:30 IST). A video request also
  needs at least $1.00 left on the key (HTTP 402 otherwise). Check both before starting.
- Gemini takes at most 10 videos per request. Through OpenRouter the Google AI Studio route rejects request bodies
  over 20,000,000 bytes (HTTP 413); the Vertex route accepted 25.5 MB. Hence the 18 MB group limit.
- Flex requests sometimes hang ~15 min: 240 s timeout + retry. Batch on Vertex may take up to 96 h, so flex (same
  half price, synchronous) is used.
- Prompt caching through OpenRouter was unreliable (7–25% of prompt tokens cached); costs are planned without it.
- `igs/metrics.py` (scraper) writes `content_topic = None` on every recompute, so the AI category is kept only in
  `creator_ai`, never in `creator_metrics`.

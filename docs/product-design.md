# Brand Deal Matcher — Product Design

Durable product knowledge: what the product is and why it is shaped this way.
Source of every decision here: the planning session recorded in
`context/001-project-genesis-and-context-setup.md` (S-001), whose raw transcript
is `A.txt`. Nothing below is implemented yet. Items marked **UNCONFIRMED**
were proposed by Claude but not accepted by the user; do not build on them
without asking.

## Problem and positioning

Small and homegrown Indian brands (handmade, skincare, food, clothing, decor)
have no agency or marketing team. Their founders find Instagram creators by
scrolling hashtags. Nano/micro creators (1K–100K) usually have higher
engagement than big creators, cost less, and want their first brand collabs.

The product is a **website** where a brand searches and gets the best
**growing** creators for its niche and city. The brand pays to unlock the
results, then contacts the creator itself. The user treats this as a real
product, not only an OJT/college project.

Framing that matters for the pitch: the platform does not give the brand an
"edge". The edge comes from the right small creator (engaged, local, cheap);
the platform finds that creator quickly.

## Out of scope by user decision (binding)

- **Budget and price.** No budget field, no price estimate, no budget-fit
  score. The brand negotiates price with the creator directly. User's words:
  "budget jane de buget ka kya woh brand apne aap hi creator se baat kar ke
  dekh legi bas hum usse best creator dhund ke dge".
- **Manual / concierge / WhatsApp flow.** No Google Form + spreadsheet +
  WhatsApp matching stage. User's words: "mujhe ye watsapp wala aur ye sab nhii
  karna hau mujhe ek website banani hai".
- **Big creators.** Creators above 100K followers are never stored.

## Brand flow

1. Landing page.
2. Sign up / login.
3. Search form: niche, city/state, follower range (1K–10K, 10K–50K,
   50K–100K), target audience (age, gender), optional "only fast-growing" toggle.
4. Free preview: match count ("18 creators found"), top results blurred
   (handle hidden), score and basic stats visible.
5. Payment (Razorpay, UPI).
6. Unlocked results: ranked list, match score 0–100, Instagram handle, contact
   (if any), growth stats, AI explanation.
7. Brand contacts the creator itself via DM or email.
8. Dashboard: past searches and unlocked creators.

Pricing models discussed: pay per search unlock (example ₹99), credit pack
(example ₹399 for 5), subscription (example ₹999/month). Suggested start: pay
per search plus credit pack. The amounts are examples, not decisions.

Weak point: the Instagram handle is public. The brand is paying for the
shortlist, the data and the contact, so matching quality is the real product.
Contact exists only when the creator put an email in the bio.

## Creator side (later, optional)

"Claim your profile": the creator signs up, edits email/niche/city, gets a
"Verified" badge and ranks higher. An opt-out/delete option is required
because scraped data is shown behind a paywall.

## Data pipeline

The pipeline runs offline (once, then on a schedule). **Never scrape when a
brand submits a search.** Searches always run against the own database.

Discovery (decided: Apify):
1. One-time manual list of about 50 hashtags (for example #punefoodie,
   #skincareindia, #homegrownbrand).
2. Apify Instagram Hashtag Scraper (reels mode): owner usernames, location
   name, reel views.
3. Apify Instagram Profile Scraper on those usernames.
4. `relatedProfiles` from each profile feeds back into step 3 (snowball).
   Creators tagged by homegrown brands are the best seed: already collab-friendly.
5. Auto-filter: 1K–100K followers, posted in the last 30 days, not fake, not a
   brand/meme page.
6. Save the raw JSON so nothing is paid for twice.

Apify fields, as read from the actor pages in S-001 (not yet checked against
real output):
- Hashtag Scraper: `ownerUsername`, `ownerFullName`, `ownerId`, caption,
  hashtags, mentions, timestamp, URL, likes, comments, `locationName`,
  `locationId`, reels: `videoPlayCount`, `sharesCount`, duration, music.
  Inputs: hashtags, `resultsType` ("posts" or "reels", not both per run),
  `resultsLimit`. Free plan returns only the first page.
- Profile Scraper: `username`, `fullName`, `biography`, `followersCount`,
  `followsCount`, `postsCount`, `isBusinessAccount`, `businessCategoryName`,
  `verified`, `private`, `externalUrl`, `relatedProfiles`, `latestPosts` (12),
  per post: type, caption, hashtags, mentions, `likesCount`, `commentsCount`,
  `videoViewCount`, `timestamp`, `taggedUsers`, `isPinned`. `likesCount` is
  -1 when likes are hidden. The "about" section is paid-plan only.

Not available from scraping: audience age/gender/city, email/phone (unless in
bio), follower history, posts older than the latest 12.

Derived metrics:
- Engagement rate = (avg likes + avg comments) / followers, over 12 posts.
- Reel reach = avg reel views / followers (above 1 means Instagram is pushing
  the content to non-followers: strongest growth signal).
- Consistency = posts per week from the 12 timestamps.
- Engagement trend = older 6 posts vs newest 6 posts.
- Follower growth = weekly `followersCount` snapshots; needs 3–4 weeks of data.
- Niche, city, language, "open to collab" (bio hints such as "DM for collabs",
  "PR friendly") = LLM over bio, captions, hashtags, location names.
- Fake-follower flag = very low engagement for the size, odd
  follower/following ratio, generic comments.
- Fields that are estimates (audience) must be marked "estimated" in DB and UI.

Weekly refresh tool: **UNCONFIRMED.** Last proposal: Apify for discovery,
Instaloader running locally for the weekly followers-count refresh, with code
that can fall back to Apify. Graph API Business Discovery was the earlier
proposal and is deferred.

Instagram Graph API is deferred until either Apify cost becomes a problem or
brands need real audience data (creator OAuth + Insights). It works only on
Business/Creator accounts, needs a known username, needs a Meta developer app,
Facebook Page and App Review.

## Matching engine

Deterministic and explainable. The LLM never produces the score.

1. Filter: niche, city, follower range.
2. Score 0–100: niche match 25, growth 25, engagement 20, location 15,
   audience fit 10, consistency 5.
3. Rank, highest first.
4. After unlock only: the LLM writes 2–3 lines explaining the score breakdown
   it is given (it cannot invent facts). Cache explanations per search+creator.

Zero-result searches should relax filters and show near matches.

## Stack (agreed in S-001)

Next.js (frontend + backend), Supabase (Postgres + auth), Razorpay, Apify, an
LLM API, Vercel. A Python script was implied for the scraping/enrichment side;
language for the pipeline is not formally decided.

## Build order (agreed in S-001)

1. Scrape creators with Apify into the database.
2. Growth + engagement calculation script.
3. Matching engine (filter, score, rank).
4. Search form + results page.
5. Login.
6. Blurred preview + payment.
7. AI explanation.
8. Dashboard.
9. Creator claim-profile page.

## Legal and compliance (India)

- Scraping is against Instagram's terms (Apify and local alike). Use only
  public data; keep an opt-out/delete path.
- DPDP Act 2023: collect only what is needed, consent, deletion.
- ASCI influencer guidelines: every paid or barter collab needs disclosure
  (#ad / #collab).
- Tax (TDS/GST, e.g. Section 194R) matters only once payments flow between
  parties; confirm with a CA then.

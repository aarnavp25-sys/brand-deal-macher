# Data collection and matching — how it works and why

Durable knowledge from S-003 (2026-11-16/17). Supersedes the Apify field list,
the `relatedProfiles` snowball and the scoring weights in `product-design.md`.

## Apify facts (verified with real runs on 2026-11-16)

- Account: FREE plan, $5/month, cycle resets on the 16th (2026-11-16 → 2026-12-15).
  Free plan stops runs at the limit instead of charging.
- Prices on FREE tier: $0.0026 per result (profile, hashtag, reel), $0.0027 (search),
  followers-count scraper $0.0026 + $0.001 start — no cheaper than a full profile.
- **No actor can filter by followers, location or niche.** Only date filters exist
  (`onlyPostsNewerThan` on reel/api scrapers). The 1K–100K rule is applied after
  scraping, so out-of-range profiles are paid for.
- **Search Scraper, `searchType: user`** is the best discovery source: one result
  = full profile (followers, bio, category, business flag, external URL) + 12
  `latestPosts` (likes, comments, timestamps, location, hashtags, coauthors).
  `searchLimit` max 250 per term; comma-separated terms in one run.
- **Profile Scraper** returns the same profile shape. It has **no reel views** in
  `latestPosts` and **no `relatedProfiles`** (0 of 21 profiles) — the snowball plan
  from S-001 does not work.
- **Reel Scraper** is the only source of views (`videoPlayCount`), plus
  `taggedUsers`, `paidPartnership`. It also returns collab reels owned by brands.
- **Hashtag Scraper** returns top (viral, 1–2.5 months old) reels with views,
  `sharesCount`, `coauthorProducers`, but no follower counts; many owners are
  businesses. `resultsType` = posts/reels/stories; `keywordSearch` option exists.
- Private and age-restricted profiles come back with `error: "Restricted profile"`.
- Broad terms ("… influencer india") return mostly >100K or <1K accounts.
  City + niche terms ("pune home decor", "tech tips marathi") yield far more
  1K–100K creators. Observed keep rates: 33%, 24%, 33% across rounds.
- **Collab snowball beats search (rounds 12–13, 2026-11-18).** Usernames that our creators tag as
  coauthors (collab posts) or @mention are free candidates already in `posts`. Profile Scraper on 768
  coauthor candidates kept 40% (search: 24–33%) and cost ~$0.012 per new usable creator incl. reels
  (city+niche search: ~$0.016). Candidates inherit the source creator's category, so picking them from
  thin categories fills those. Mentions alone are mostly brands (Flipkart, Nykaa); prefer coauthors.
  New creators add new candidates, so the pool grows each round (~3,300 coauthor candidates left).
- Polling/downloading through flaky networks needs retries; a crashed client does
  not stop the Apify run — re-attach by run id (`apify_run.py … <run_id>`).

## Pipeline (pipeline/)

Search (user) → filter (`passes`: 1K–100K, public, ≥3 posts, posted ≤60 days,
not a business category, not follow-for-follow) → Reel Scraper (2 reels, last
90 days, no pinned) → `process.py build` → Supabase upsert → raw JSON to Storage
bucket `raw-scrapes` (multi-MB jsonb rows hit Postgres statement_timeout 57014).

Metrics: engagement = (median likes + median comments) / followers (mean was
skewed to 591% by one viral post); reel reach = median reel views / followers;
posts/week = recent posts / weeks since the oldest of them (Apify gives only 12
posts, so a fixed 60-day window capped everyone at 1.4); fake flag = followers
≥10K and ER <0.5% **and** reach <0.3 (low ER alone flagged viral accounts);
bios that read like shops (`BRANDISH` regex) get `status = review`.
Known defect: `cmd_build` uses `(avg_views or 0)`, so a creator with no reel data
counts as reach 0 and is flagged on low ER alone (6 of 166 flagged creators on
2026-11-18). Fix: no reel data → `status = review`, not `fake_flag`.

Every fake-flagged creator gets `creators.fake_reason`: the rule in plain words with the creator's own
numbers (shown in admin). Creators loaded without reel data (reel runs that ran out of credit, or no reels in
90 days) get reels later with `process.py reels <reels.json>`, which updates views, reach, the fake check and
reel posts for creators already in the DB (category/products are not re-run). About half of the usable
creators without reel data simply post no reels; re-scraping them returns nothing.

Classification `keyword-v1`: category = keyword share across posts + bio + search
term; products = keyword hits per post. Category level is usable; product level
is noisy ("chain" on biker posts, "ring" ceremony) — needs the LLM step
(`classification_method = 'llm'`), which also fills `creator_gender_est` and
`content_quality_est`.

## Taxonomy

16 categories (`pipeline/taxonomy.py`): Food, Beauty, Fashion, Jewelry &
Accessories, Home Decor, Fitness, Sports, Tech, Gaming, Entertainment & Comedy,
Music & Dance, Education & Finance, Parenting, Travel, Automobile, Pets.
"Lifestyle" is never a main category (it matches everything). Gaming is separate
from Tech and Sports from Fitness (different audiences and brands). 42 product
types with keywords. Fixed lists only — free-text labels break search.

## Matching (demo/server.py, design agreed in S-003)

1. Brief → product types + categories + city + audience (keywords now, LLM later).
   Categories are ranked by keyword hits so "gaming accessories" → Gaming.
2. Product fit per creator: proven product (posts show it) > category match >
   possible. Proven evidence counts fully only if the creator's **primary**
   category is relevant; single-post evidence is discounted.
3. Labels: Specialist (≥50% of posts on the product, or ≥60% in the category),
   Wider reach (proven but less), Potential (possible only).
4. Score 0–100. Goal "sales": product 30, engagement 20, reach 15, quality 15,
   growth 10, consistency 5, location 5. Goal "reach": reach 30, product 20.
   Engagement is percentile within the follower tier. Signals without data
   (quality, growth) are dropped and weights re-normalised. Followers never score
   directly — a strong 8K creator can beat an average 80K one.
5. Keep score ≥50; show ~20 mixed: ~40% specialists, ~50% wider, ~10% potential.
6. Explanation is built only from the breakdown numbers (LLM later).

Specialist vs wider: specialists convert (intent, trust); wider creators give
reach. A fashion creator's audience interest in a product is measured by
engagement on that product's posts vs their average.

## Why the database, not live scraping

A live search would take 5–10 minutes and ~$1–2 per search, can fail mid-demo,
cannot compute growth (needs history) and cannot rank against the whole pool.
Live calls are only for: refreshing the ~25 unlocked creators after payment, and
a background discovery job when a search returns <10 matches.

## LLM / AWS notes

Claude prices (cached 2026-11-03): Opus 5.5 $4/$20 per MTok, Sonnet 5.5 $2/$10,
Haiku 5.5 $0.10/$0.50; Message Batches 50% off. On Amazon Bedrock the model id
is `anthropic.claude-opus-5-5` and Anthropic Message Batches are not available;
Claude Platform on AWS has batches but bills through AWS Marketplace.
AWS account: Free plan, $100 credits until 2027-05-16. Credits cannot pay Apify
or Supabase. Do not run scrapers on AWS (IPs blocked).

**Chosen LLM: Amazon Nova 2 Lite on Bedrock** (`global.amazon.nova-2-lite-v1:0`,
Sydney `ap-southeast-2`), decided 2026-11-18 after the tests below. Reasons: best
balance on our data (category 100%, product ~79%, shop 95% on the 20-creator
test), fastest (~1.7 s), takes images, and it is Amazon's own model so the AWS
credits certainly pay for it. Weakness: `global` routing (data may leave the
region) — the in-region fallback would be Claude Haiku 4.5 (`au.`) if DPDP needs it.

What Bedrock allows on this account (verified 2026-11-17/18 with Bedrock API keys):
- The API key works only in `ap-southeast-2`; other regions return
  `not authorized to perform: bedrock:CallWithBearerToken` (explicit deny).
- 47 of 73 text models answer. Blocked with "not available for this account":
  Claude 5.x (Haiku/Sonnet/Opus 5.5, Opus 5, Sonnet 5, Fable 5–5.2), Claude Opus
  4.7/4.8, OpenAI GPT-5.x/6.x, xAI Grok, GLM-5.3 — third-party Marketplace-billed
  models, which the Free plan blocks.
- Claude 4.x (Haiku 4.5, Sonnet 4.6, Opus 4.5/4.6) needs the one-time "Anthropic use
  case details" form in the Bedrock console (HTTP 404 until then). Claude models are
  absent from AWS's public Bedrock price list, i.e. billed via Marketplace; whether
  the credits cover them is unverified.
- Under ~12 parallel requests the key intermittently returns
  `403 Authentication failed`; retry with backoff and ≤2–3 parallel calls.
- Official per-MTok prices (Sydney, public price list
  `pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrock/current/ap-southeast-2/index.json`):
  Nova 2 Lite $0.32/$2.63 (global), Nova Lite $0.063/$0.252, gpt-oss-120b
  $0.15/$0.62, DeepSeek V3.2 $0.64/$1.91, Kimi K2.5 $0.62/$3.09, Kimi K3 $3/$15
  (global); Kimi K3.1 not listed.

Model test (same prompt, same 20 creators, gold labels written by reading each
creator; 10–20 creators per model because of the 403s): per creator ~2,030 input
and ~110 output tokens. Top results: gpt-oss-safeguard-20b/120b 94% category /
94% product, gpt-oss-120b 90/90 (text only), DeepSeek V3.2 100/83, Kimi K3 100/83
(~$20 for 1,356 creators, 7 s), Nova 2 Lite 100/79 (~$1.25), Kimi K2.5 100/75,
Kimi K3.1 100/70 (10 creators). Worst: Gemma 3 4B (product 21%), Kimi K2 Thinking
(category 58%, 19 s). Big "reasoning" models did not beat small ones on this
fixed-list task. Keyword-v1 on the same 20: category 17/20, a wrong product on
~17/20, 0 of 4 shops caught (a bakery, a furniture store, a gym and an arcade were
all "usable creators").

## Load gotchas (found 2026-11-17)

- Upsert `posts` in batches of 100, not 500: 500 posts with captions timed out
  (`TimeoutError`). Upserts are idempotent, so `upsert()` retries on timeout.
- A collab reel can appear under two creators with the same post id. Postgres
  rejects duplicate keys inside one upsert (`21000 ON CONFLICT DO UPDATE command
  cannot affect row a second time`); `cmd_load` dedupes posts by id first.
- Load only creators that are new: rebuilding an existing creator from search
  data without reels would overwrite `avg_reel_views` with null. Round scripts
  filter by usernames already in `creators`.
- Generate round search terms from an explicit per-round dict (`ROUND5_TERMS` …
  `ROUND8_TERMS`), never by slicing the merged `EXTRA_SEARCH_TERMS` (it flattens
  by category and mixes rounds).
- Multiple free Apify accounts work the same way; each has its own $5/month.
- Parallel runs (found 2026-11-17): a FREE account allows 5 concurrent jobs and 16 GB
  actor memory. Search Scraper runs use 1 GB, Reel Scraper runs 4 GB, so at most 3 reel
  runs fit at once; a 4th/5th start returns `HTTP 402 Payment Required` (memory, not
  credit). Splitting terms or usernames across parallel runs costs the same per result
  and cut a round from ~20 to ~8 minutes. Merge the reel outputs before `process.py build`.
- PostgREST returns at most 1000 rows per request; `limit=10000` silently stops at 1000.
  Page with `order=id&limit=1000&offset=…` (pipeline scripts and admin `apiAll`). A
  truncated "existing creators" list would treat known creators as new.
- A dataset download can fail mid-stream (`ValueError: invalid literal for int() with
  base 16`); `apify_run.py` retries GETs, and a finished run can be re-downloaded for free
  by passing its run id.
- Term yield (rounds 9–11): city + niche terms returned ~13 profiles/term; content-style
  terms ("room makeover india", "golden retriever india") returned ~4.5/term. Home decor
  city terms return mostly shops.
- City/niche search yields: round 5 241/636, round 7 350/727 kept; small-city
  terms for thin categories (round 8) returned few results (174 for 19 terms).

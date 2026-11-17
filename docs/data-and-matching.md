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
AWS account: Free plan, $100 credits until 2027-05-16; whether the free plan
allows Anthropic models on Bedrock is unverified (Amazon Nova is the fallback).
Credits cannot pay Apify or Supabase. Do not run scrapers on AWS (IPs blocked).

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
- City/niche search yields: round 5 241/636, round 7 350/727 kept; small-city
  terms for thin categories (round 8) returned few results (174 for 19 terms).

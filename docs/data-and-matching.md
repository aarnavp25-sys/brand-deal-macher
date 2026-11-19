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
  Rounds 12–37 (2026-11-18/19, 13 free accounts, ~$65): 1,356 → 6,224 creators, 5,399 usable; snowball
  keep rate 39–49%, pool grew to ~10,000 candidates. Thin categories (Tech, Home Decor, Jewelry,
  Education, Parenting) ran out of collab candidates first; topic terms ("lippan art", "neet aspirant
  creator", "mobile photography tips india") filled them at ~30–60% keep.
- **Billing lag.** Reel Scraper charges post minutes after a run ends (runs often show `$0.001`), so the
  balance read before the next round is too high. One account went to $5.195 of $5 that way: Free plan
  cannot charge without a card, but the account cannot start runs until its cycle resets. Leave ~$0.3
  unspent before the last round on an account. `maxTotalChargeUsd` caps one run, not the account.
- Polling/downloading through flaky networks needs retries; a crashed client does
  not stop the Apify run — re-attach by run id (`apify_run.py … <run_id>`).

## Pipeline (pipeline/)

Round driver: `pipeline/round.py` (one account per run; plans within the balance minus $0.30).

Search (user) → filter (`passes`: 1K–100K, public, ≥3 posts, posted ≤60 days,
not a business category, not follow-for-follow) → Reel Scraper (2 reels, last
90 days, no pinned) → `process.py build` → Supabase upsert → raw JSON to Storage
bucket `raw-scrapes` as `.json.gz` (multi-MB jsonb rows hit Postgres statement_timeout 57014;
uncompressed files reached 1.1 GB, over the free 1 GB Storage quota — gzip cut them to 223 MB on 2026-11-19).

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

## Matching (supabase/functions/api/index.ts; redesigned 2026-11-20 on the user's request)

The user's goal (2026-11-20): small brands with small budgets need the *right* creators, not a list sorted by one
score. So the AI first understands the brand, the creators are understood in depth (how they talk, price level,
whose products, values), and results come in three columns, each creator reviewed for this brand.

1. **Brand profile.** Haiku 5.5 reads the brand's text → summary, niche, products, categories, customers
   (men/women/unisex + age), price level (budget/mid/premium), values, the creator roles that would sell it best
   (supplements → expert/reviewer; snacks → lifestyle/entertainer) and what the brand needs. Shown to the brand as
   "How we understood your brand"; the brand can override customers, price, category, product. Keyword parser
   when the LLM is unavailable.
2. **Creator profile** (`creator_llm`, prompt v4): niche (specific), creator_role (expert / reviewer / educator /
   enthusiast / entertainer / lifestyle / aspirational — a cricket fan page is "enthusiast", a state player who
   trains on camera is "expert"), credibility + reason, price_segment, products_for (whose products they feature —
   a woman styling men's shirts = "men"), content_values (healthy vs indulgent, value-for-money vs luxury...),
   scope (niche / category / broad), brand_fit note, plus the v3 audience fields.
3. **Formula score 0–100** (deterministic). Sales: product 25, brand fit ("style") 20, audience 15, engagement 15,
   reach 10, quality 7, growth 5, consistency 3, location 5. Reach goal and the trending column: reach 30.
   - Product fit: proven product (posts show it) > category match > possible (`can_promote`).
   - Brand fit = mean of price fit (same 1, mixed 0.7, one step 0.55, budget vs premium 0.15), values
     (overlap; clashing values 0.1), role (brand's first ideal role 1, other ideal 0.85, else 0.45), credibility
     when the brand needs trust (professional 1 / experienced 0.8 / casual 0.45), audience age.
   - Audience fit = best of the creator's audience gender and products_for (same 1 / 0.9, unisex 0.6, opposite 0.1).
   - Engagement is percentile within the follower tier; missing signals are dropped and weights re-normalised.
4. **Three columns**, each creator in one: *niche* (already posted this product), *trending* (scope broad or a
   lifestyle/entertainer/aspirational role, reel reach in the top 40%; possible-only creators need the top 25%),
   *category* (talks about the category). Score ≥50 to enter; top 12 per column go to review.
5. **AI review** (one Haiku call, ~36 creators): the brand profile + each creator's profile line → verdict
   strong/good/weak, a reason specific to the brand, and a reel idea. Order in a column = verdict, then score;
   weak fits are hidden when a column has ≥4 others; 8 shown per column. The LLM changes the order and the advice,
   never the score, and cannot add creators. Without an AI brand profile or on failure the order is the score.
6. Cost per search ≈ $0.002 (profile ~$0.0003 + review ~$0.0017). Rate limit 30 searches / 10 min per client.

Before 2026-11-20 the result was one list mixed as ~40% specialists / ~50% wider / ~10% potential, and the LLM
only parsed the brief. The user rejected "just a matching score in descending order".

## Public API (Supabase Edge Function `api`)

The demo page calls `POST /functions/v1/api/match` and `GET /functions/v1/api/meta`; `demo/server.py` only
serves the page and `/config.js` (URL + public anon key). Security: the service-role key and
`ANTHROPIC_API_KEY` live only in Supabase secrets; tables have RLS on with no policies, so the anon key reads
nothing directly; CORS allow-list (`ALLOWED_ORIGINS`); JWT check (anon key); body ≤4 KB, brief ≤600
chars, enum checks; per-client rate limit 30 matches / 10 min via `api_hit()` (salted IP hash,
`api_rate_limit`, execute revoked from anon); responses never include email or bio; errors are generic.
Verified 2026-11-18: no key → 401, foreign origin → 403, bad input → 400, anon table read → `[]`, anon
`rpc/api_hit` → permission denied. Deploy: `python3 supabase/deploy.py [migrate|anon|secrets|function]`
(needs `SUPABASE_ACCESS_TOKEN`; the CLI refuses to deploy in agent mode without `--yes`).

## Coverage target

Coverage is planned per category × follower tier × audience, never per city (creators can be anywhere
in India; city is optional data and a filter for local brands). Launch target: ~5,000 usable
(16 × 3 × 2 groups × ~50). Reached 2026-11-19 (5,399). Weak spot: mid tier (50K–100K) has only ~316
usable, ~20 per category — next rounds should favour it.

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

**Bedrock blocked (2026-11-18).** Every model on the account (Nova, gpt-oss, DeepSeek) returned
`400 Error 002: Access to Bedrock models is not allowed for this account`; listing models still worked,
so it is an account-level block, not the key. Only fix reported by others: an AWS Support case
(Account and billing). A later key returned `403 Authentication failed` (expired/revoked). Plan instead:
**Claude Haiku 5.5 via the Anthropic API with Message Batches** (~$0.05/$0.25 per MTok batched) —
~$0.70 for 6,224 creators; brief parsing per search ~$0.0001. Not yet run: needs `ANTHROPIC_API_KEY`
in `admin/.env`, then a 20-creator check against the gold labels before the full batch.
Prompt v2 (`pipeline/llm_classify.py`, `PROMPT_VERSION v2`) adds `audience_gender`, `audience_age`,
`audience`, `can_promote`. Measured size: ~1,000 tokens fixed instructions + ~1,000 per creator
(14 posts, captions ≤450 chars) + ~180 out. Hashtags are sent twice (in the caption and as a list) —
dropping the duplicate saves ~10–15%. Keep thinking off / effort low on Haiku 5.5 (on by default; its
tokens bill as output).

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
- macOS `/bin/bash` is 3.2: no `declare -A` (associative arrays). Round scripts use `case` functions.
- A dataset download can fail mid-stream (`ValueError: invalid literal for int() with
  base 16`); `apify_run.py` retries GETs, and a finished run can be re-downloaded for free
  by passing its run id.
- Term yield (rounds 9–11): city + niche terms returned ~13 profiles/term; content-style
  terms ("room makeover india", "golden retriever india") returned ~4.5/term. Home decor
  city terms return mostly shops.
- City/niche search yields: round 5 241/636, round 7 350/727 kept; small-city
  terms for thin categories (round 8) returned few results (174 for 19 terms).

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
Fixed 2026-11-20 (was a known defect): low engagement without reel data no longer marks a creator fake. Such
creators get `status = review` (183 moved from fake to review); `process.py reels` sets them back to active or
fake once reel views exist. Only low engagement AND low reel reach marks fake.

Every fake-flagged creator gets `creators.fake_reason`: the rule in plain words with the creator's own
numbers (shown in admin). Creators loaded without reel data (reel runs that ran out of credit, or no reels in
90 days) get reels later with `process.py reels <reels.json>`, which updates views, reach, the fake check and
reel posts for creators already in the DB (category/products are not re-run). About half of the usable
creators without reel data simply post no reels; re-scraping them returns nothing.

Business accounts (2026-11-20, user: "kya pata woh brand ho"; also saves LLM credit): `process.py build` sets
`status = 'business'` when the Instagram business category is clearly a shop, venue, company, school, team or agency
(`BUSINESS_CATEGORIES`, or a name ending in Store/Shop/Dealership/Wholesaler) and the bio/username (NFKC-normalised)
has no creator words (creator, influencer, I/my, promotion, collab, comedy, coach, athlete, doctor, parent...).
Ambiguous categories (Education, Nonprofit, NGO, Charity, Gym, Event Planner, Interior Design Studio, Travel Company,
Comedy club...) are left to the LLM, because individual rescuers, coaches and fans pick them too. Applied to the DB on
2026-11-20: 173 accounts moved; business accounts are never shown and never sent to the LLM. The LLM still catches the
rest (`is_shop`, `creator_type = organization`, `in_india = no`).

Deleted shops (2026-11-21, user's order): the 560 accounts the AI profile called a shop/brand page (`is_shop`, not a
creator) that do not take promotions were deleted from `creators` (posts, AI profile, snapshots and products went
with them by cascade). The 95 shops with `takes_promotions = yes` were kept (still hidden from search). Full rows are
in storage `raw-scrapes/backups/removed-2026-11-21-shops.json.gz` (local copy in `pipeline/runs/`). Their usernames
are in `removed_creators`, which `round.py` treats as already known, so a later round never scrapes or profiles them
again (the search/profile scrape that finds them is still paid; reels and the LLM are not).
Same day, same way: of the 553 fake-flagged accounts (never AI-profiled), a manual read of bio and captions found
170 real creators (kept, still fake-flagged) and 383 non-creators (159 business/shop, 110 pages, 57 outside India,
33 personal/professional, 24 organisations), which were deleted; backup `removed-2026-11-21-fake-noncreators.json.gz`
(it holds each account's label). Labels came from a quick read, not the AI profile; check the backup if one is missed.
Then (user: "jitne bhii non usable creators mai se sach mai creators hai unhe rakh aur baaki saare db mai se nikal de")
1,432 more were deleted on existing labels, no new reading: organisations 519, outside India 278 (incl. 125 creators
abroad: an Indian brand never sees them), AI account check personal 260 and own shop 107, `status = business` 173,
and the 95 shops that take promotions. Backup `removed-2026-11-21-noncreators.json.gz` (each account's group).
`removed_creators` holds every deleted username.
Last, on the user's order ("review wale saare creators ko db se hata de"), all 286 `status = review` accounts were
deleted: 182 without reel data (about 78 looked like creators), 89 with shop-like bios, 15 without posts; none had an
AI profile. Backup `removed-2026-11-21-review.json.gz`. They are in `removed_creators` too, so December rounds skip
them; delete a username from that table to let a round pick it up again. After this: 3,563 creators, 3,231 shown,
169 fake-flagged (real creators), 163 professionals; no account is in review.
Then the 163 professionals/celebrities with no sign of promotions (AI profile, no collab line) were deleted on the
user's order too (films/theatre ~68, politicians ~16, doctors ~16, artists ~20...); backup
`removed-2026-11-21-professionals.json.gz`. After this: 3,399 creators = 3,230 shown + 169 fake-flagged.
(@anuuuuuuuuuuu__47, a shown comedy creator, disappeared in the same window but not by these scripts: not in any
backup or in `removed_creators`; most likely the admin's Delete button.)

**Account check** (`pipeline/account_check.py`, user 2026-11-20: "saare 10k se niche wala account ko haiku se check
karwa aur un sab ko review mai daal"). Every search-visible account under 10K followers gets one Haiku question:
creator / personal / own shop / unclear, from its saved AI profile + bio + 8 recent captions (no new scraping;
~$0.00011 per account). Creator = a clear topic or format an outsider would follow (craft professionals such as
makeup artists and trainers count; so do accounts that make paid promos for other shops); personal = own life,
friends, greetings, reposts with no theme; own shop = mainly advertises its own store/product/service/event.
`apply` moves personal and own shop to `status = 'review'` with `review_reason`; admin shows the AI note and a
"Keep as creator" button. First run 2026-11-20: 2,424 checked ($0.27), 2,047 creator, 260 personal, 109 own shop,
8 unclear; 2 own-shop labels contradicted their own note (they promote other brands) and were set to creator by
hand; 367 moved to review (search-visible 3,598 → 3,231). Samples read by hand looked right; the gray zone is
makers selling their own craft (potters, mural artists) and advocacy pages. `round.py` runs the check + apply for
new creators after their AI profile. Every `status = 'review'` row now carries a `review_reason` (pipeline rules
write one too: shop-like bio, low engagement without reel data, no posts).

Classification `keyword-v1`: category = keyword share across posts + bio + search
term; products = keyword hits per post. Category level is usable; product level
is noisy ("chain" on biker posts, "ring" ceremony) — needs the LLM step
(`classification_method = 'llm'`), which also fills `creator_gender_est` and
`content_quality_est`. (That column was never filled; since prompt v5 the LLM gives `creator_llm.content_quality`
1-10 + `quality_note`, which the API uses as the quality signal.)

## Taxonomy

16 categories (`pipeline/taxonomy.py`): Food, Beauty, Fashion, Jewelry &
Accessories, Home Decor, Fitness, Sports, Tech, Gaming, Entertainment & Comedy,
Music & Dance, Education & Finance, Parenting, Travel, Automobile, Pets.
"Lifestyle" is never a main category (it matches everything). Gaming is separate
from Tech and Sports from Fitness (different audiences and brands). 82 product
types with keywords (42 until 2026-11-20; added masala, pickles, mithai, chocolates, ready-to-cook, organic
staples, cookware, body/nail care, ayurvedic beauty, salons, men's ethnic, innerwear, toys, kids clothing, furniture,
bedding, cleaning, stationery, fitness equipment, cycles, academies, appliances, cameras, esports, events, OTT,
books, insurance, tours, camping, bikes/cars, car care, pet services...). Without a type, the AI had to pick a
wrong neighbour for such brands. Both prompts show each type with its category and 4 example words so close
types are not confused. `product_types` in the DB is synced by migration 20261120000002. Keyword-v1 tags exist
only for the first 42; the LLM profiles cover all 82. Fixed lists only — free-text labels break search.

## Matching (supabase/functions/api/index.ts; redesigned 2026-11-20 on the user's request)

The user's goal (2026-11-20): small brands with small budgets need the *right* creators, not a list sorted by one
score. So the AI first understands the brand, the creators are understood in depth (how they talk, price level,
whose products, values), and results come in three columns, each creator reviewed for this brand.

1. **Brand profile.** Haiku 5.5 reads the brand's text → summary, niche, products, categories, customers
   (men/women/unisex + age), price level (budget/mid/premium), values, the creator roles that would sell it best
   (supplements → expert/reviewer; snacks → lifestyle/entertainer) and what the brand needs. Shown to the brand as
   "How we understood your brand"; the brand can override customers, price, category, product. Keyword parser
   when the LLM is unavailable.
2. **Creator profile** (`creator_llm`, prompt v5): niche (specific), creator_role (expert / reviewer / educator /
   enthusiast / entertainer / lifestyle / aspirational — a cricket fan page is "enthusiast", a state player who
   trains on camera is "expert"), credibility + reason, price_segment, products_for (whose products they feature —
   a woman styling men's shirts = "men"), content_values (healthy vs indulgent, value-for-money vs luxury...),
   scope (niche / category / broad), brand_fit note, plus the v3 audience fields. v5 adds `settings` (the places and
   situations they film), `natural_fits` (see 5c) and `content_quality` 1-10 + `quality_note` (original vs reposts,
   effort, hook, format, audience response; capped at 3 if not brand-safe or mostly reposts).
3. **Formula score 0–100** (deterministic). Weights (supabase/functions/api/index.ts `WEIGHTS`): sales = product 22,
   audience 15, price 12, brand fit 12, engagement 12, reach 10, quality 9, growth 5, location 5, consistency 3;
   reach goal and the wider column = reach 25, audience 15, product 15, quality 11, price 10, brand fit 10,
   engagement 10. Content quality ≤3 never enters the wider column (user, 2026-11-20: "content quality bhii dhyaan
   mai rkhna").
   - Product fit: proven product (posts show it) > category match > natural fit 0.42 (5c) > possible 0.3
     (`can_promote`, a guess from the audience).
   - Brand fit = mean of price fit (same 1, mixed 0.7, one step 0.55, budget vs premium 0.15), values
     (overlap; clashing values 0.1), role (brand's first ideal role 1, other ideal 0.85, else 0.45), credibility
     when the brand needs trust (professional 1 / experienced 0.8 / casual 0.45), audience age.
   - Audience fit = best of the creator's audience gender and products_for (same 1 / 0.9, unisex 0.6, opposite 0.1).
   - Engagement is percentile within the follower tier; missing signals are dropped and weights re-normalised.
**Search rules, consolidated 2026-11-20 after one-off fixes kept breaking other searches** (user: "saari cheeze
ek baar re think kar sab properly fix kar"). `pipeline/eval_search.py` runs 16 fixed briefs against the live API and
checks R1–R9; run it after every matching change (first full pass: 0 violations).
- R1 Category column = creators whose main category is the product's own category, or a fixed close neighbour the
  brand AI also picked (`CAT_NEIGHBOURS`: jewellery/watches ↔ fashion, beauty ↔ fashion, fitness ↔ sports, tech ↔
  gaming), or who posted the product. The brand AI's other categories (it added Entertainment to men's jewellery,
  Parenting/Travel to instant chai) never open the category column.
- R1b Inside that, the creator's own products must touch the product's world (`relevance`: 3 posted it, 2.5 it fits
  a scene they film, 2 the AI guesses they could promote it, or they posted/film a same-category product such as
  watches for men's chains, 1.5 a same-category product only guessed, 1 any product of those categories, 0 = only the
  category label, which the profile AI got wrong for
  dermatology-exam, vegan-advocacy and mural-art pages labelled "Beauty"). Relevance 0 never enters the column, and
  the 12 review slots go to the most relevant first (reach-led scores used to fill them with photographers). For a
  men's or women's product, creators whose audience matches come first (2026-11-21: men's perfume showed 2 of many
  men's fashion creators because unisex photographers with "perfume" as a guessed product took the slots).
  A token-gated `debug` field (secret DEBUG_TOKEN) returns the whole pool with column, relevance, fit and score.
- R2 Review answers field + account; "other field" is out of the category column; "related" stays.
- R3 Weak is never shown. R4 Personal / own-shop accounts never shown (account check + review).
- R5 A shop that sells only at its counter: its city only. R6 Wider reach: ≥3,000 followers.
- R7 Niche: product evidence or (local store) shop-visit creator. R8 One column per creator.
- R9 A men's product never shows a creator whose audience is women and who features women's products (and back);
  a woman styling men's products stays.
- R0 No AI check, no results: if the brand profile or the review fails (2026-11-20: OpenRouter's workspace daily
  budget of $4.00 stopped every call and search silently fell back to keywords, showing a woman's page, a comedian
  and a doctor for men's perfume), `/match` returns 503 "The AI check is not available right now" instead of
  unchecked creators. Cached searches keep working. OpenRouter has a workspace daily budget separate from the key limit.
Known gaps (data, not rules): no men's jewellery or perfume specialists; premium men's perfume falls back to premium
photographers/filmmakers; Haiku varies run to run on borderline creators (cache keeps a repeated search stable).

4. **Three columns**, each creator in one (user's definitions, 2026-11-20):
   - *niche* = specialists: the product is ≥20% of their recent posts (~3 of 14), or they come from its field (LLM
     role expert or credibility professional in the product's category, and they show or naturally fit it); for a
     local-store brand also creators who film inside shops in its city. A creator who posted the product once or
     twice is not a specialist.
   - *category* = make content in this category in general: their MAIN category is one the brand needs, or they
     showed the product (occasional product posters inside the category land here). A secondary-category match alone
     is not enough (2026-11-20: a box-cricket creator with secondary "Fashion" topped a men's jewellery search on
     one viral reel's reach).
   - *trending* ("Wider reach" in the UI) = big reach and the product can believably appear in their content:
     scope broad or a lifestyle/entertainer/aspirational role with reel reach in the top 40%; natural fits and
     occasional posters outside the category also need the top 40%; possible-only creators the top 25%; always
     ≥3,000 followers and content quality >3.
   Score ≥50 to enter; top 12 per column go to review. Measured on keyword-v1 data (2026-11-20): only ~9 of 106
   perfume posters are specialists, so the perfume niche column is thin (3 shown) until LLM profiles and more
   perfume creators exist.
5. **AI review** (one Haiku call, ~36 creators): the brand profile + each creator's profile line → verdict
   strong/good/weak, a reason specific to the brand, and a reel idea. Order in niche and category = verdict, then
   score. Order in trending (wider reach) = score only (reach-weighted), the verdict there only removes creators who
   cannot believably promote the product (user, 2026-11-20: a hostel student fits instant tea perfectly but has small
   reach; a travel vlogger who can sell it as "time saving, easy to make" with big reach must rank higher there;
   engagement, reach and content quality count in all three columns);
   The review also answers two plain questions per creator, and code applies the user's rules to them (2026-11-20,
   after a men's jewellery search showed cricket players, watch reviewers and personal accounts: "kaha se ye
   personalized hai"; prose rules alone did not work, Haiku called nearly everyone "good"): `field` (own field /
   related / other field: is their usual content where buyers look for this product?) and `account` (creator /
   personal / own shop). Personal accounts and own-shop pages are weak everywhere; "other field" is weak in the
   category column ("related" stays: an "own field only" rule tried on 2026-11-20 emptied the column for a men's
   watch brand, whose men's fashion creators the AI rated "good, related"). "Entertainment & Comedy" is a
   reach category: it qualifies a creator for the category column only when the product itself belongs there
   (the brand AI sometimes adds it, e.g. to a men's jewellery brand) (niche creators got there on product evidence; the wider column allows props). Niche and
   category are ordered by verdict, then field, then product fit (0.1 steps), then score, so one viral reel cannot
   lift a weaker fit above a closer one. Formula side: a specialist in another product of the brand's product
   category (watch reviewer for a chain brand) never enters the category column; an account with no sign of brand
   work, no product shown and content quality ≤4 is hidden as a personal account.
   Weak fits are never shown in any column (an empty group says so; before 2026-11-20 they filled columns with
   fewer than 4 good fits, e.g. 8 restaurant reviewers for an instant chai premix); 8 shown per column. The LLM changes the order and the advice,
   never the score, and cannot add creators. Without an AI brand profile or on failure the order is the score.
5a. **Price level and relevance** (user, 2026-11-20: "1000 ke perfumes" and "10000 ke" must not get the same
   creators; no wider-audience creators without a relation, e.g. a doctor for a perfume brand). Price is its own
   signal (sales 12, reach 10, local 8): same level 1, mixed 0.6, one step 0.45, budget vs premium 0.05. The brand
   prompt judges price against the product's usual Indian price (perfume ~₹1,000 budget, ₹5,000+ premium) and keeps
   ₹ amounts in `price_note`; keyword fallback reads ₹/Rs/k amounts (<₹1,500 budget, ≤₹5,000 mid, else premium).
   The creator prompt uses the same price scale. Brand categories must be ones whose creators naturally talk about
   the product; the review marks unrelated high-reach creators "weak", and weak fits are never shown in trending.
5c. **Natural fits: think like the brand** (user, 2026-11-20: a travel creator who makes chai in the mountains can
   be good for an instant tea brand; the model must look from the brand's side at every possible shot, give a short
   reason for each creator, and show such creators in the wider column when their reach is good). The creator prompt
   lists up to 8 `natural_fits` = product types (any category) that fit a scene the creator already films, each with
   the `moment` from the posts ("brews chai on cold mountain treks", "late-night study chai in the hostel room" →
   beverages); only scenes really seen, never generic guesses. The mountain example was only one example: the user
   wants every such angle (hostel/college, office, home, commute, travel...). The brand prompt lists up to 8
   `moments` where every kind of buyer uses the product ("late-night study in hostel", "office tea break"). A natural fit with reel reach in the top 40% (and ≥3,000 followers) enters the wider ("trending")
   column even if the creator is a niche travel creator; the explanation says "Has not promoted X yet, but already
   films: …". The review prompt makes Haiku the brand owner: imagine where the product appears in what the creator
   already films; reason ≤20 words naming the decisive point (shot, trust, audience or price); idea = a reel inside
   their own usual scenes; no believable shot = "weak", which is never shown in the wider column.
5d. **Who is shown at all** (user, 2026-11-20). Hidden: `status = 'business'` accounts (see Pipeline); LLM
   `is_shop` unless the account is creator-type; `in_india = no`; `creator_type = organization` unless it takes
   paid promotions (`takes_promotions = yes`, seen in its posts; a "DM for collab" bio line is not required — that
   rule hid 107 meme/community pages and rider/run clubs that do brand collabs); professionals/celebrities only when
   `takes_promotions = unlikely` and not `collab_open` ("woh kyu hii promotion karega": a TVF director or a CEO does
   not make paid reels; "maybe" stays because a creator with no collab yet can still say yes). Web checks of
   professionals were deferred: ~$0.01–0.02 per search, ask after the full run.
5b. **Local shops** (user, 2026-11-20: a local store should see creators who make reels inside shops). The brand
   profile has `sales_channel` (online / local store / both; brand can override with "Where you sell"). The creator
   profile has `store_visits` (often / sometimes / never: shop tours, market hauls, "where to buy", cafe/salon or
   factory visits; specific shop location tags are strong evidence) + `store_visit_note`. For a shop brand, creators
   who film in shops (often/sometimes) in the brand's city go into the niche column and the "local" weights apply:
   product 20, shop-visit reels 20, location 20, brand fit 10, audience 10, engagement 10, reach 5, quality 3,
   growth 1, consistency 1. A brand that sells only at its own shop (no online) with a city sees only creators
   in that city, in every column (viewers elsewhere cannot walk in; before 2026-11-20 a Jaipur mithai shop got
   out-of-city comedians in the wider column). "Both" (shop + online) keeps all cities. Keyword matching on captions alone was too noisy (mall ads, quotes, festivals), so this
   signal comes only from the LLM reading captions + location tags.
6. Cost per search ≈ $0.002 (profile ~$0.0003 + review ~$0.0017). Rate limit 30 searches / 10 min per client.
   Both answers are cached in `llm_cache` for 7 days: the brand profile by the normalised brief, the review by the
   exact prompt (brand profile + shortlist with its numbers). Changing filters or repeating a search reuses them;
   any change in the shortlist or creator data makes a new key, so a cached answer is never stale.

Before 2026-11-20 the result was one list mixed as ~40% specialists / ~50% wider / ~10% potential, and the LLM
only parsed the brief. The user rejected "just a matching score in descending order".

## Public API (Supabase Edge Function `api`)

The demo page calls `POST /functions/v1/api/match` and `GET /functions/v1/api/meta`; `demo/server.py` only
serves the page and `/config.js` (URL + public anon key). Security: the service-role key and
`OPENROUTER_API_KEY` live only in Supabase secrets; tables have RLS on with no policies, so the anon key reads
nothing directly; CORS allow-list (`ALLOWED_ORIGINS`); JWT check (anon key); body ≤4 KB, brief ≤600
chars, enum checks; per-client rate limit 30 matches / 10 min via `api_hit()` (salted IP hash,
`api_rate_limit`, execute revoked from anon); responses never include email or bio; errors are generic.
Verified 2026-11-18: no key → 401, foreign origin → 403, bad input → 400, anon table read → `[]`, anon
`rpc/api_hit` → permission denied. Deploy: `python3 supabase/deploy.py [migrate|anon|secrets|function]`
(needs `SUPABASE_ACCESS_TOKEN`; the CLI refuses to deploy in agent mode without `--yes`).

**Deployment (2026-11-22).** Site: https://brand-deal-matcher.vercel.app (Vercel serves `demo/` as static files;
`demo/config.js` points at the Render API, `demo/vercel.json` sets CSP/headers, `demo/.vercelignore` keeps `server.py`
out). API: https://brand-deal-matcher-api.onrender.com (Render free web service `srv-dc1bt26c6qcc73ae4vng`, Singapore,
auto-deploys from GitHub `main`, start `python3 render/server.py`). `render/server.py` is a thin forwarder: `/health`
(GET/HEAD) for UptimeRobot, `/api/meta` and `/api/match` forwarded to the Edge Function with the anon key added
server-side (the public page carries no key), its own CORS allow-list (`ALLOWED_ORIGINS` env on Render). Rate limit:
every request would reach Supabase from Render's IP, so the forwarder sends the visitor IP in `x-client-ip` with
`x-proxy-key: PROXY_SECRET`; `clientIp()` in index.ts trusts it only when the secret matches (verified: direct and
proxied calls from one IP land in the same `api_rate_limit` bucket). Names are placeholders until the user picks one.

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
(Account and billing). A later key returned `403 Authentication failed` (expired/revoked).
**Decision 2026-11-20 (user): forget AWS; use OpenRouter.** Model `anthropic/claude-haiku-5.5` ($0.10/$0.50 per
MTok, cache reads $0.01; structured outputs supported per OpenRouter's public model list, 2026-11-20). A
`:batch` variant is listed at half price but its mechanics are untested, so runs are real-time.
**Measured on real calls (2026-11-20, prompt v7–v10).** Per creator: ~11,400 cached input tokens (fixed
instructions + JSON schema with the 82-product enums; the earlier "~2,100" guess was wrong), ~1,900 uncached
(bio + 14 posts), ~670 out → **~$0.00064–0.0007 per creator**, ~$3.3–3.5 for ~5,100 creators (the first estimate of
$1.5 assumed 300 output tokens and a 500-token schema). Cost shares: answer 52%, creator data 30%, cached
instructions 18%. One request per creator on purpose: batching 10 creators per call would save at most ~$0.50 for
the whole run (only the cached 18% shrinks) and risks mixing posts across creators and losing 10 profiles per
cut-off. The first call of a run goes alone so it writes the prompt cache; then 6 run in parallel (~1 hour for
5,000). `estimate`/`run` print a "measured" line from saved `cost_usd` once ≥20 replies exist.
API gotchas found on the first paid calls: Haiku 5.5 rejects any non-default `temperature` (HTTP 400), so none is
sent and replies vary slightly run to run; OpenRouter's Haiku 5.5 endpoints on Claude Platform on AWS and Amazon
Bedrock list no `structured_outputs`, so `provider.only/order = anthropic, azure, google-vertex` (Anthropic first
keeps cache hits); the Edge Function sends the same. `max_tokens` is 1500 per profile and 140/creator for reviews
(a cut-off reply is paid but unusable). `llm_classify.py compare --model X` runs any model on the 20 gold creators
without saving. Run so far: `credits` → `test` (v5, v6, v7) → pilot 100 (v8, v9, v10) → compare.
**Jev Router ruled out (2026-11-20, user asked "kum cost me ache se"):** `typesafe/jev-router` on the same 20 gold
creators and prompt: category 10/20, product 13/20, shop 18/20, 11/20 replies cut off by its reasoning tokens,
$0.0043 per creator (6x Haiku), and it switched between GPT-6 Luna, Gemini 4 Hydrogen and DeepSeek V4.1 Flash, so
profiles would not be comparable. Haiku on the same run: 16/20, 16/20, 19/20, 0 cut off, $0.0007.

**Creator profile lessons (prompt v5 → v10, `pipeline/llm_classify.py`).**
- Products: the model kept treating activities as products (squats → fitness equipment, a home recipe →
  ready-to-cook, a pilgrimage → tour package) even with those exact counter-examples in the prompt. What fixed it
  (gold product 9/20 → 18/20): every product must carry `item`, the exact thing seen ("Anveshan A2 ghee jar"), and
  `clean()` drops a product whose item is empty or admits nothing concrete (`NOT_A_PRODUCT`: greeting, recipe,
  no specific, not shown, not...). The item is shown in explanations ("e.g. Bella Vita Oud").
- Gold set (`pipeline/gold20.py`) was written for the 42-type taxonomy; its allowed products were extended for the
  82 types only where the evidence posts were read.
- Role: people with professional standing in what they post (director, chef, founder) are expert/educator.
  Store visits exclude stadiums, event venues, offices, temples, gyms and their own studio.
- Content quality 1-10 bunches at 4–7 (the model reads captions, not video), so search uses its percentile.
- `creator_type` creator / professional / celebrity / organization, `takes_promotions` yes/maybe/unlikely (own
  company posts are not promotions), `in_india` yes/no/unclear. A person making content about their own craft
  (makeup artist, coach, dancer, esports player, DJ, photographer) is a creator; meme/city/fan pages that sell
  promotions are creators; `is_shop` only for pages selling physical products or running a venue (v9 over-hid
  these: a makeup artist became a shop, a meme page and a coach became organizations).
- Pilot findings on the first 100 by id: ~11% foreign accounts (Italy, UK, Chile, Australia, Hong Kong), ~10%
  organisations, ~12% shops/own-business pages.
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

## Apify actors: what they return and what we keep (checked on raw files 2026-11-22/23)

- **Search Scraper does not search Instagram.** Each result carries `searchSource`: google 3,360 / threads 1,260 /
  facebook-ads 305 of 5,065. It matches the term against names and bios found there, then opens the profile. Inputs
  were `searchType: user`, `searchLimit: 15`, 533 city+niche terms. Of 4,726 unique profiles: 50% outside 1K–100K
  (paid anyway), 312 inactive, 171 business, ~503 deleted later; 1,072 (23%) shown.
- **Collab snowball** (Profile Scraper on `coauthorProducers`) brings friends, family, venues and brands: 2,304 of
  4,487 loaded (51%) were deleted on 2026-11-21 vs 30% for search; shown snowball creators have brand-work "yes"
  46% vs 68%, bio collab line 24% vs 52%, under 3K followers 39% vs 22%. 66% of shown creators came from it.
- `latestPosts` = the first page of the grid (12 items; median span 42 days, p90 346 days). **`isPinned` is never
  true** (0 of 6,093 profiles; Instaloader docs say Instagram stopped exposing it), so the pinned filter does nothing.
  No views and no `paidPartnership` in profile posts (0 of 36,692 stored). ~14% of posts hide likes (-1).
- Reel Scraper (`resultsLimit 2`, `onlyPostsNewerThan 90 days`): the only source of `videoPlayCount`; also
  `paidPartnership` (7 of 612 true), `taggedUsers`, `latestComments` (text, ≤12), `musicInfo`
  (`uses_original_audio` 57% true), `videoDuration`. **15% of returned reels belong to another account** (collab
  reels): `process.py` maps reels by `inputUrl`, so their views count toward the input creator's reach (bug).
- Dropped at load: `alt` (Instagram's own image description, "May be an image of shawl, poncho and text" on ~60% of
  posts), `taggedUsers`, comments, `musicInfo`, `videoDuration`, carousel children. All still in raw files.
- Media links (`displayUrl`, `videoUrl`, `audioUrl`, profile pics) are signed CDN URLs with an `oe=` hex expiry
  1–3 days after the scrape (403 after); anything visual or audio must be processed at scrape time.
- `posts` has primary key `id`; a collab post shared by two creators is stored under one of them only
  (e.g. drnoorbutt: 12/week from 1 stored post). `posts_per_week` = posts ÷ weeks since the oldest of the 12: it is
  frequency, not regularity; 165 creators got full marks with all posts inside 3 days; 1,231 of 3,229 differ from
  their last-4-weeks rate by >1/week. Only 103 creators have ≥2 snapshots, so growth is empty for 97%.

## Discovery alternatives (researched 2026-11-23; prices read from the Apify API, Free-plan rates)

- No tool lists "all accounts with N followers"; only pre-built indexes filter by followers. India-claimed sizes
  (vendor claims): Modash 787,425 Indian Instagram (≤500K), Reelax 1M+, Qoruz 0.3–4M, Kofluence 750K, GCC 500K+,
  Dexfluence 136,421 or 43,000 (two pages disagree); market estimate ~1.99M Indian Instagram influencers. None
  exports a bulk list for free; copying their data breaks their terms. Modash public pages show top 20 per page.
- `social_developer` India index (Apify): 2,412,880 "indexed profiles", 120 categories, 652 cities, brackets
  Nano <10K / Micro 10K–99.9K; $0.02 per result. Returns username, name, category, followers (rounded), city, posts,
  engagement, avg likes/comments/views; no bio or posts. The graph is ordered **category A→Z, then city A→Z**, and
  every run scans it from row 0 in 2,000-row pages (no offset/random option). `sortBy` = sequential (default) /
  followers / views / engagement / likes; tested 2026-11-24 (Kids & Toys, limit 4, followers): the log says "sequential
  scan, then rank", it did not stop when the 4 known matches were passed ("kept 0" at 50,000) and died at the
  ~50K wall with nothing written ($0.0001). Ranked modes must read the whole graph and write only at the end, so on
  this backend they fail and return nothing, while sequential returns what it found before a timeout. Keep sequential.
  So a category's rows are contiguous (Food Blogging + Micro: first match at row 38,733, 25 matches by row 38,787),
  later categories need more pages, and the same input always returns the same first rows. Each page fetch has a
  ~12 s timeout; one slow page ends the run with "Creator graph is temporarily unavailable" (exit 1, rows written so
  far kept and billed; a 0-row failure costs ~$0.001). Page failure rate 3% on 2026-11-22, 11% on 2026-11-23; parallel
  runs failed on the first page. City filters scan past the category block when a city has no match → near-certain
  failure (Food Blogging + Delhi and 3 small cities all failed). Delhi + Micro without category showed ~700 rows per
  category block, so the real graph is likely ~100K rows, not the claimed 2.4M (estimate). Test 2026-11-23:
  ~64% real active Indian creators; Delhi + Micro without category ~2–3 of 15; Fashion Influencer + Nano 0 in 10,000,
  then "Creator graph is temporarily unavailable". `datablow` ($0.01, TheMediaAnt listings with ad rates): 33% inactive,
  follower counts stale. Index ≠ creators: it holds shops, agencies, pages, foreign accounts.
- Cheaper discovery: "Suggested for you" — deepmine $0.00089/profile with followers, bio, category, free follower
  filter, depth ≤11 (Free plan returns only 50 per run); data-slayer $0.0025 (names only); brand-tagged posts —
  thescrappa $0.000375/post, instagram-scraper $0.001, Apify official $0.0027; keyword content search $0.0025.
- Paid databases with export: Impulze Solo $29 (200 exports), Pro $199 (5,000/mo), Lifetime Pro $549 (unlimited);
  CreatorDB API $0.01–0.04 per credit (profile = 2); Bright Data datasets $250 minimum (~$0.0025/record).

## Own scraper (moved 2026-11-25 to its own repo)

**Final creator DB since 2026-11-25 (owner's decision):** the scraper's data in the index project, schema `public`
(848 creators with per-reel data and `creator_metrics`), dashboard on 127.0.0.1:8791. This project's main DB
(yqaducvspzrqokcqwlga, 3,229 creators) and the index `public` schema are legacy and no longer the source for new work;
the admin (8787) and index (8789) dashboards were stopped. The live site still reads the old DB until the merge.

The logged-out Instagram scraper is a separate project: `~/Documents/ojt/instagram-scraper/` (GitHub
`aarnavp25-sys/instagram-scraper`, private). What it collects, its rules and lanes are in that repo's `README.md`; the
page/JSON fields, network tests (WARP app, 10 Docker WARP exits, hostel IP, phones) and media findings are in its
`docs/instagram-notes.md`. It writes to schema `public` of the index project (schema `work` until the 2026-11-25 reorganisation). It will be merged back into this project later.

## Keep check at scrape time (design, 2026-11-24; applies to every account)

User, 2026-11-24: a salon aunty who makes reels with tanning tips, home remedies and product advice is worth keeping
("log unki sunte bhi hai"); one who only shows her makeovers is not; followers, reach and reels count too; decide this
while scraping, for every account. So no account is removed for its name or type (salon, gym, home baker, boutique):
the scraper decides from what the account posts. (Exception: 70 accounts the user removed by type on 2026-11-24 —
clothing shops, own mobile shops, car fan pages — stay in `index_removed`.)

Stage 1, numbers (free, from the scrape; thresholds are first guesses to tune on a hand-checked pilot):
- live followers 10K–100K (index counts are stale; above 100K is never stored);
- active: ≥2 posts in the last 30 days;
- makes reels: ≥4 of the latest 12 grid items are reels;
- reach: median views of the latest 12 reels ≥ 15% of followers and ≥ 1,000 (low = audience not watching or bought);
- real engagement: median likes on opened posts ≥ 1% of followers.
Failing a gate → `drop` with the reason (or `review` when just under a threshold).

Stage 2, content (AI reads bio + 12 captions + alt text + brand tags + music + the stage-1 numbers; one call per account):
- account: creator / business that makes content / business catalogue / page without a person / personal / foreign;
- what most reels do: teach, recommend, review, entertain, vlog **vs** sell or show its own service (before/after,
  price lists, offers, "book now", "DM to order"), or repost others;
- keep when it is a creator, or a business whose reels mostly teach or recommend to an audience (the salon-aunty case);
  drop when it is a catalogue, a page with no person, personal, or not in India; `review` when unsure;
- returns keep / drop / review + a one-line reason + one quoted caption as evidence.
Results go to the index project (verdict per account, shown in the dashboard; `review` rows get a human pass).

## Working copy: schema `work` (2026-11-24; reorganised 2026-11-25)

**2026-11-25:** the index project was reorganised: the old `public` tables and views moved to a read-only schema
`legacy`, everything in `work` moved to `public` (now the final data), and `work` was dropped. The text below describes
the 2026-11-24 state.


User: make a clone and do all new work there, so a mistake can never damage the collected data. A third Supabase
project was refused (free plan: 2 active projects per owner), so the clone is a second schema in the same index project:
`work.*` = full copy of every `public.*` table (index_creators, index_creator_categories, index_runs, index_review,
index_removed, index_category_groups; same columns, keys, RLS, the two FKs re-pointed inside `work`) and every view
(cat_* and index_progress, reading `work` tables only). Row counts matched exactly (961 creators). `work` is exposed to
the REST API (PostgREST db_schema = public, graphql_public, work); select it with the header `Accept-Profile: work`
(reads) / `Content-Profile: work` (writes). **All new code (the scraper, any change) writes to `work` only; `public` is
the frozen original.** A JSON backup of all six tables + schema.sql is in index/backups/2026-11-24_1711/ (gitignored).

## Creator username index (`index/`, separate Supabase project)

Usernames only (no profile scrape) from the `social_developer` index, Micro bracket, rows kept only when
10,000 ≤ followers < 100,000. The planned random-city draws were dropped on 2026-11-23 (city filters fail, see
"Discovery alternatives"): each category gets **one** run without a city, with its final count from `index/plan.json`
(user: brand-collab categories only, 2,000 total, ≥20 each; 31 categories ranked by the main DB's "takes promotions"
share: Food 88%, Parenting 84%, Fashion 79%, Jewellery 68%, Travel 63%, Beauty 60%, Auto 56%, Fitness 52%, Tech 49%).
Results lean to early-alphabet cities (accepted by the user). Runs go one at a time; a 0-row failure is retried
(`--tries`, `--wait`); a category that returned rows is never run again (same rows would be billed twice), unless it
holds fewer than 20 (re-running re-buys only those few). Cost per run = max(`usageTotalUsd`, items × $0.02):
`usageTotalUsd` now includes the result fees but lags a few seconds after the run ends. Keep the Mac awake
(`caffeinate -i -w <pid>`): sleep pauses the retry waits. Tables `index_creators`, `index_creator_categories`, `index_runs` (with `city`), `index_category_groups`
(the actor's categories → 9 of the main DB's categories, user's choice on 2026-11-24: Food & Beverages, Beauty & Skincare, Fashion & Clothing, Jewelry & Accessories, Fitness & Wellness, Tech & Gadgets, Parenting & Kids, Travel & Explore, Automobile; every other actor category is never collected), `index_review` (manual review: not_useful / check with kind and reason) and views `cat_<category>` (one per kept category, with the review) + `index_progress`, all `security_invoker` with RLS on and no
policies. `python3 index/collect.py keys|categories|migrate|status|plan|run [--plan index/plan.json]`; dashboard `python3 index/server.py`
(127.0.0.1:8789, read-only, CSV export). Keys in `index/.env` (`INDEX_APIFY_TOKENS`, gitignored).

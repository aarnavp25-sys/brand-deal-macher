# Kindred website: how it works and why

Durable knowledge about the brand-facing website in `web/` (built 2026-11-26). Setup and deploy steps are in
`web/README.md`.

## What a brand does

1. Landing page (`/`) → "Find creators".
2. **Google sign-in is required for everything except the home page** (user, 2026-11-27: "google auth dalna hai google
   se sign in ke baad hi kuch bhii search kar sakta hai"; home page stays public). `proxy.ts` sends a signed-out
   visitor on `/find`, `/dashboard` or `/results` to `/login?next=<path>`; `/login` has one "Continue with Google"
   button (`components/GoogleButton.tsx`, Supabase `signInWithOAuth`, PKCE); Google returns through Supabase to
   `/auth/callback`, which sets the session cookies and goes on to `next` (same-site paths only, `safeNext`). A
   signed-in brand on `/login` goes to `/find`. Every API route answers 401 without a Google session; pages check the
   user again on the server (`requireBrand`). The header has the brand's Google photo, name, email and Sign out.
   **History:** anonymous Supabase sessions were used from 2026-11-26 (demo without sign-in) until 2026-11-27; those
   users and their searches stay in the database, but an anonymous session now counts as signed out (`currentBrand`
   returns null for `is_anonymous`), so they cannot be reached from a browser. Supabase anonymous sign-ins are switched
   off once this code is live. Test brands sign in with a one-time link (`web/db/test_login.py`, secret key needed).
3. **After sign-in: the dashboard** (`/dashboard`), never a chat (user, 2026-11-27: "Sign in karne ke baad jo ek
   chatbot aata hai, wo chatbot khulna nahi chahiye ... Sign in ke baad ek user dashboard type bana de"). Signing in
   from "Find creators" or `/login` lands there; a link to a saved chat or results page still returns to that page.
   **First visit: a pop-up "Hey there! What should we call you?"** (user's wording request 2026-11-27: "thoda cool way mein"; placeholder "e.g. Aarnav") (`components/NamePopup.tsx`, shown by `(app)/layout.tsx` while
   `user_metadata.kindred_name` is empty; cannot be skipped; letters, spaces and . ' - only, max 40; saved by
   `POST /api/profile/name` → `saveName()`). It is asked even though Google already gives a name ("Naam phir bhi
   poochho") and kept apart from `name` / `full_name`, which Google rewrites on every sign-in. Until it is given,
   `POST /api/searches` answers 409. Dashboard: "Hi <name>!", a "Start a new search" card with Find creators, three
   numbers (searches done, creators found, chats not finished) and every saved search (open / continue / delete).
4. Chat (`/find/<id>`), opened only from the dashboard's Find creators or New search. It starts "Hey <name>! Let's
   find you some creators." The name is stored in the search's brief, used in the last line and never sent to the AI.
   Then five fixed questions, one at a time, in a casual Gen Z tone (user, 2026-11-26):
   1. "What's your brand? What do you make? What's the vibe behind it? Spill it all." (typed; user, 2026-11-27: "what's your brand, what is its spirit" wording)
   2. "Love that. Which product should creators hype first?" (typed)
   3. "Which creators are you vibing with?" categories, several at once or "All of them"; the category guessed
      from the brand's words is pre-picked
   4. "Who's actually buying it?" Mostly men / Mostly women / Everyone
   5. "Last one. What kind of creator, and any language preference?" Female / Male / Either works + languages
   From question 3 on, every option shows how many creators it leaves, and a live "N creators match so far" line
   uses the same rule as the results (`lib/filters.ts`), so the number always equals what the results page shows.
   **It must read like a conversation, not a form** (user, 2026-11-26). Without an LLM (`lib/conversation.ts`):
   Kindred reacts to the brand's own words (a line per category its words point to, the product name echoed back,
   the live creator count said in a sentence), sends two or three short bubbles with a typing pause before each,
   shows the brand's message at once, and every choice question can also be answered by typing ("mostly girls in
   college", "female, hindi ya english"), read with keywords. If a typed answer is not understood, Kindred says so
   in a bubble and asks the brand to tap instead. No progress bar.
5. After question 5 the creators are found at once (`/results/<id>`), biggest first, with sort by followers /
   typical reel views / engagement / posting frequency and tabs per category.
5b. **Results for the demo (user, 2026-11-26): the top 20 by a candidate score, no LLM** (`lib/rank.ts`). From the
   creators that pass the brand's choices: category fit 25 (share of the last 12 reels in the chosen categories; with
   "All categories", in the product's own category guessed from the brand's words), product seen 15 (reels whose
   products/topic name the product's own words, filler words like "starter", "500g" removed), audience fit 15,
   engagement 15 and reach 10 (percentiles on Kindred), language 5, regularity 5, brand-collab ready 5, content
   quality 5. Every card shows the score and up to four reasons taken from the data.
   **Fixed the same day after the user's check of a watch search** (two wrong creators): (1) a nail-art studio got in
   because the brand had ticked Beauty and the score rewarded the category label; now product relevance leads (35:
   the product's own category x1, a fixed close category x0.8, Lifestyle x0.5, other categories 0) and creators with
   no link to the product never reach the top 20; (2) a fashion designer's showcase page (owner on camera in 5 of 12
   reels, never speaks, clients wearing his designs) got in; now "on camera" is 10 points and portfolio pages (owner
   on camera in under half the reels + sells own work/services + 3+ work-showcase reels; 30 such accounts, 26 of them
   makeup/beauty studios) are never in the top 20. Studios that are on camera keep a "Runs their own studio" label.
   **AI matching is ON on the live site since 2026-11-26** (user chose "AI ON + $1 cap" for the teachers' demo;
   `LLM_ENABLED=true`, `LLM_REVIEW=true` on Vercel production only; local `.env.local` has them too): `lib/product.ts` (Haiku reads
   what the product is, its words and its shopping world) and `lib/review.ts` (Haiku judges, from each creator's 12
   reel notes, whether they can sell it, citing reels; code checks every cited reel really names the product; weak
   and non-creators hidden; Kindred Score; specialists / category / lifestyle groups). One pilot on a men's watch
   brand on 2026-11-26: $0.0055, 9 s, rules passed; it showed the AI counted outfit reels as "watch seen", fixed in
   the prompt and by the code check; a re-check on 3 brands (watch, pickle, candle) the same day passed the rules
   (only real watch-unboxing reels counted as "watch seen"). One search = 5 calls (1 product + 4 review batches of 10),
   about $0.0055 and ~45 s end to end on the live site. If the AI fails or the budget is used up, the code-only top 20
   (`lib/rank.ts`) is shown instead. Personalisation (how the user wants AI to tailor results) is still to be designed.
   **Spend cap (user, 2026-11-26: "us pe $1 ka cap rakhna ... searches rok dena apne aap hi"):** `LLM_TOTAL_CAP_USD`
   (default 1) is a TOTAL cap over every row ever logged in `llm_calls` (tests included), checked before every AI call
   and before a new chat starts (`budgetReached()` in `lib/llm.ts`, stopping $0.01 early). When reached, new chats get
   503 "demo search budget is used up"; chats already open finish with the code-only ranking. It replaced the old
   per-day cap `LLM_DAILY_CAP_USD`.
6. The dashboard (`/dashboard`) lists the brand's past searches; each can be reopened or deleted.

**Brand understanding (user, 2026-11-27; `lib/product.ts` `understandBrand`, one Haiku call):** after the first
answer the AI writes a 1–2 sentence summary of the brand and decides `kind`: "single" (one website, app, service or
product, e.g. a resume-builder site) or "range" (several products). Kindred shows "This is what we have understood: …" and
asks "Is this what you mean?" (Yes / No). "No, not quite" → "Could you explain it again?" → the extra text is appended
to the description and understood again ONCE (`MAX_EXPLAINS` = 1): Kindred shows "Got it. This is what we have
understood now: …" and goes straight on, without asking again (user, 2026-11-27). Range brands are asked "Are you planning to promote a particular product, or your brand in general?"
(product → the product question; brand → no product question); single brands get no product question. Without AI
(off, budget used up) the old flow runs: product question right after the brand. The first question no longer asks
for the vibe ("What's your brand? What do you make? Spill it all.").

**Categories (user, 2026-11-27):** nothing is pre-ticked any more (before, the AI's categories plus "Lifestyle &
Daily Vlog" were always ticked, which looked wrong for most brands). The question is "Which kinds of creators would you
like? Pick as many as you want, or let Kindred decide." Below the chips sits **Let Kindred decide**: the AI's main
category plus its 0–2 close ones (without AI: the keyword guess; nothing found = all), told back as "Kindred picked …
for you." It can also be typed ("you decide").

**Follower range (user, 2026-11-27):** after "who buys it", a two-handle slider from 10K to 100K in 1K steps
(`RangeAnswer` in `components/Chat.tsx`: two native range inputs on one track, keyboard and touch work), with the
live creator count; it can also be typed ("20k to 50k", "under 30k", "50k+"). The ends mean "no limit on that side",
so creators who dropped just under 10K still show when the lower handle stays at 10K. Stored as `followers_min` /
`followers_max`; the same `passes()` rule filters the results.

**Creator cards (user, 2026-11-27; `components/CreatorStats.tsx`, the same block on every results layout):**
Followers · Avg views (mean of the last 12 reels) · Reach (typical views ÷ followers) · Engagement ("est." when many
reels hide likes) · Avg comments (mean per reel, last 12) · Speaks · Audience (est.) · Brand collabs (all named
brands, 8 shown then "+N more") · **Contact (from their bio)**: an email, an Indian mobile number and/or a WhatsApp
bio link, read only from the creator's own bio and bio links (`lib/contact.ts`; on 2026-11-27: 116 of 848 bios had an
email, 91 a phone, 42 a WhatsApp link). Numbers and bio come from the server-only view `creator_card_stats`
(migration 003). A saved search keeps the cards it was made with, so searches from before this change show "-" for
the new numbers. Contact is visible to every signed-in brand for now; the planned paywall would put it behind unlock.

**Filter rule (lib/filters.ts):** main category in the chosen ones (none = all); creator gender matches unless
"Either works"; speaks at least one chosen language, where creators with no speech in their reels (music only)
pass every language; "Mostly men" hides creators whose audience is mostly women and back, "Everyone" hides nobody.
Who counts as a creator on the site: `creator_overview` rows with `ai_status = done`, `activity = active`,
`account_type` creator or professional (shops, brands, personal accounts and repost pages are never shown),
`in_india` not "no", `quality` not "weak", no "not brand-safe" flag. On 2026-11-26 that was 598 of 662 profiled
creators. Thin categories: Home Decor & Handmade 2, Jewelry 3, Home & Household 5, Parenting & Kids 7.

## Known matching limits (stress test of 20 brands, 2026-11-27)

Report: "Kindred — Matching Stress Test (20 brands)" (private Claude Doc, https://claude.ai/artifact/Mav7LbwJsy26j7GhNHXsb4).
Result 10 right / 6 partly / 4 wrong; brand understanding was right for all 20. Hardware brands never got software
creators. Software, finance and service brands (AI agent, resume site, tax filing, SIP app, spoken-English app) got
phone and gadget creators, always as "good", never "strong". Causes, biggest first:
1. **Database gaps:** of 603 showable creators, 1 finance, 1 pets, 7 tech (mostly phones), 0 business, software,
   career or women's-health. The 961 usernames came from 9 broad Apify index categories.
2. **"Good" is too easy for non-physical products** ("has promoted an app, so a tax tool fits").
3. **No score for a niche match:** the one stock-market creator ranked below a gadget reviewer.
4. **Shortlist only from the picked categories:** student and career creators sit in Lifestyle and Travel.
Fixes proposed in the report (form + buyer in brand understanding, stricter "good", niche bonus, topic specialists
across categories, new collection round) are ON HOLD by the user's decision of 2026-11-27.

## Where things run

Everything runs in one Next.js app on Vercel: pages and the API (route handlers) live on the same domain. No Render.
Live: Vercel project `kindred` (team dragon-44d8), https://kindred-eta-black.vercel.app, Root Directory `web`.

- **Functions must run in Singapore (`sin1`)**, next to the Supabase project (ap-southeast-1). The project was first
  created with Vercel's default Washington (`iad1`): every database call then crossed the Pacific (~250 ms each) and
  "Find creators" took 5–7 s to show the chat (start chat 2.8–4.5 s + chat page 1.7–2.1 s, measured 2026-11-26).
  After moving to `sin1`: start chat 0.55–0.84 s, chat page 0.50–0.68 s (first request after idle ~2–3 s).

- Render was needed only for the old static `demo/` page, which could not hide a key; Next.js server code hides keys
  itself. Render's free plan also sleeps after 15 minutes (about a minute for the first request), and a split
  frontend/backend would need cross-domain login cookies and CORS.
- Supabase project "database" holds the creator data, the website tables and the sessions (Supabase Auth, Google sign-in).

## Request flow

```
Browser ── every request ──► proxy.ts (Vercel)
                              ├─ POST/PUT/DELETE without our own Origin header → 403 (CSRF)
                              ├─ refreshes the Supabase session cookies
                              └─ signed out on /find, /dashboard, /results → /login?next=…; signed in on /login → /find
Sign-in:  /login → Google → Supabase → /auth/callback?code=… → session cookies → next page
Chat:     POST /api/searches                    no Google session → 401; else a brand_searches row
                                                (max 25 per brand per day)
          POST /api/searches/:id/answer          {step, value} → validated → next question; after question 5 the
                                                 creators that pass the filter are saved in results
Pages:    /results/:id reads the saved results + signs photo links (1 hour) from the private bucket
```

Every route handler and page checks the user again with `supabase.auth.getUser()` (lib/auth.ts) and reads rows with
`user_id = <that user>`; the proxy check is only the quick first gate.

## Security model

- Browser holds only the publishable key. Grants: `anon` and `authenticated` have **no** access to creator tables or
  views; `authenticated` may only SELECT its own `brand_searches` rows (RLS policy). `llm_calls` has no policy.
- The server uses the secret key (`SUPABASE_SECRET_KEY`, never `NEXT_PUBLIC_`), which bypasses RLS, so `lib/searches.ts`
  filters every query by the signed-in user's id. `import "server-only"` makes a build fail if that code reaches the
  browser bundle.
- This project does **not** grant new tables to `service_role` by default (2026-11-26: "permission denied for table
  brand_searches"); the migration grants it explicitly. Remember this for every new table.
- `creator_overview` is `security_invoker = true` (it used to run with its owner's rights).
- Profile photos: private bucket `creator-photos`, served only through signed links created for a signed-in brand.
- Input: JSON bodies ≤ 8 KB, every answer validated against the question's own options (zod for text), answers must
  come in order, open redirects blocked (`safeNext`).
- Headers: CSP, X-Frame-Options DENY, nosniff, Referrer-Policy, Permissions-Policy, HSTS; no X-Powered-By.
- `web/db/e2e_test.py` checks all of the above plus five test brands end to end (one types every answer) (92 checks, all passing on
  2026-11-26).

## Design

One accent (Instagram's warm coral `#ff5a36`, dark ink text on it for contrast), neutral off-white / off-black, no
purple (user: "Purple color bilkul nahi"). Font: Archivo only, its wide cut for headings. Creator photos sit in an
Instagram-style story ring (amber → coral → pink). Light and dark follow the visitor's system setting. Cards 16px
radius, inputs 12px, buttons and chips pills.

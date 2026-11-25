# Kindred website: how it works and why

Durable knowledge about the brand-facing website in `web/` (built 2026-11-26). Setup and deploy steps are in
`web/README.md`.

## What a brand does

1. Landing page (`/`) → "Find creators".
2. Sign in with Google (`/login`). Email/password sign-up is switched off in Supabase, so Google is the only way in.
3. Chat (`/find/<id>`): ten fixed questions, one at a time: about the brand, the product, its category (suggested from
   the brand's own words), who buys it, buyer ages, creator gender, languages, creator size, goal, video styles.
   Each answer is a tap on an option or typed text. At the end a "Your brief" card shows every answer and lets the
   brand change any of them.
4. "Show creators" → results (`/results/<id>`): **every creator whose main category is the chosen category**,
   biggest first, with sort by followers / typical reel views / engagement / posting frequency.
5. "My searches" (`/dashboard`) lists the brand's past searches; each can be reopened or deleted.

**Current rule (user, 2026-11-26):** no LLM anywhere on the site yet, and results = all creators of the category. The
other answers are stored in `brand_searches.brief` for the matching that comes later. Consequence seen in testing: a
men's face-wash brand that asked for male creators still sees all 87 beauty creators, mostly women makeup artists.

Who counts as a creator on the site: `creator_overview` rows with `ai_status = done`, `activity = active`,
`account_type` creator or professional (shops, brands, personal accounts and repost pages are never shown),
`in_india` not "no", `quality` not "weak", no "not brand-safe" flag. On 2026-11-26 that was 597 of 662 profiled
creators. Thin categories: Home Decor & Handmade 2, Jewelry 3, Home & Household 5, Parenting & Kids 7.

## Where things run

Everything runs in one Next.js app on Vercel: pages and the API (route handlers) live on the same domain. No Render.

- Render was needed only for the old static `demo/` page, which could not hide a key; Next.js server code hides keys
  itself. Render's free plan also sleeps after 15 minutes (about a minute for the first request), and a split
  frontend/backend would need cross-domain login cookies and CORS.
- Supabase project "database" holds the creator data, the website tables and the logins (Supabase Auth, Google).

## Request flow

```
Browser ── every request ──► proxy.ts (Vercel)
                              ├─ POST/PUT/DELETE without our own Origin header → 403 (CSRF)
                              ├─ refreshes the Supabase login cookies
                              └─ /dashboard, /find, /results without a login → /login
Sign in:  /login → Google → Supabase Auth → /auth/callback (code → session cookies) → /find
Chat:     POST /api/searches                    create a brand_searches row (max 25 per brand per day)
          POST /api/searches/:id/answer          {step, value} → validated → next question
          POST /api/searches/:id/run             {brief} → validated (zod) → creators of the category saved in results
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
- `web/db/e2e_test.py` checks all of the above plus three test brands end to end (63 checks, all passing on
  2026-11-26).

## Design

One accent (Instagram's warm coral `#ff5a36`, dark ink text on it for contrast), neutral off-white / off-black, no
purple (user: "Purple color bilkul nahi"). Font: Archivo only, its wide cut for headings. Creator photos sit in an
Instagram-style story ring (amber → coral → pink). Light and dark follow the visitor's system setting. Cards 16px
radius, inputs 12px, buttons and chips pills.

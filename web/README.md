# Kindred website (`web/`)

The brand-facing site: landing page, Google sign-in, a short question-and-answer chat about the brand, and the
creators of the category the brand picks. Next.js 16 (App Router) + Supabase ("database" project). How it works and
why: `../docs/website.md`.

## Run locally

```bash
cd web
cp .env.example .env.local      # fill in the values (Supabase dashboard -> Project Settings -> API Keys)
npm install
npm run dev                     # http://localhost:3000
```

Production check: `npm run build && npm run start`.

## Database

`db/migrations/*.sql` holds the website's tables (`brand_searches`, `llm_calls`), their RLS and grants, and the private
`creator-photos` bucket. Creator data itself (`creator_overview`, `creator_ai`, ...) is made by the scraper and `ai/`.

```bash
python3 web/db/migrate.py            # apply migrations (idempotent); --check only prints the state
python3 web/db/upload_photos.py      # copy creator profile photos into the private bucket (skips existing)
```

## Tests

```bash
python3 web/db/e2e_test.py [base_url]     # 3 test brands end to end + security checks (63 checks)
python3 web/db/test_login.py 1            # one-time sign-in link for test brand 1 (no Google needed)
python3 web/db/test_login.py --delete-all # remove all test brands and their searches
```

Test sign-in uses the Supabase admin API (secret key), so only the project owner can do it.

## Deploy on Vercel (from GitHub)

1. Vercel -> Add New -> Project -> import this GitHub repository.
2. **Root Directory: `web`**. Framework preset: Next.js (detected). Build and output settings: leave the defaults.
3. Environment Variables (Production and Preview):

   | Name | Value |
   |---|---|
   | `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL of the "database" project |
   | `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | the `sb_publishable_...` key |
   | `SUPABASE_SECRET_KEY` | the `sb_secret_...` key (server only, never `NEXT_PUBLIC_`) |

   `SUPABASE_ACCESS_TOKEN` is for the local scripts only. Never add it to Vercel.
4. Deploy, then put the production URL into Supabase (Authentication -> URL Configuration): Site URL =
   `https://<your-domain>`, Redirect URLs = `https://<your-domain>/**`.

## Google sign-in

Google Cloud Console -> APIs & Services -> Credentials -> Create OAuth client ID -> Web application:

- Authorized JavaScript origins: `https://<your-domain>` and `http://localhost:3000`
- Authorized redirect URI: `https://<supabase-project-ref>.supabase.co/auth/v1/callback`

Then Supabase -> Authentication -> Sign In / Providers -> Google: paste the Client ID and Client Secret and enable it.

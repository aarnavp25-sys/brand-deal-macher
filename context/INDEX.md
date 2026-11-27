# Context INDEX

The only mutable file in `context/`. Rewritten in full by every `/context-write`. Read it every session; read
numbered files only when the topic map points to them or the user asks for full history.

Last rewritten: 2026-11-27 (S-027).

> **Auto-compact is OFF** (`~/.claude/settings.json`). Run `/context-write` at ~70–80% context.
> **Git: never credit Claude** (user's order 2026-11-18; hooks block it in both repos).
> **Do not build or install anything without the user's explicit go**; research is fine. **Ask before changing
> anything in matching** (2026-11-27). Paid LLM calls only with the user's yes (live searches are covered by the $1 cap).
> **Never use reel captions or hashtags** for AI profiles or when checking results.
> **This repo is PUBLIC:** no keys and no creator usernames in pushed files (journal included). Scan before every push.
> **Deploy:** push first, deploy only when the user asks: `git archive HEAD` into the scratchpad, keep the `.vercel` link
> folder, `vercel deploy --prod --yes --scope dragon-44d8` (Vercel has no GitHub connection).
> Two repos: this one and `~/Documents/ojt/instagram-scraper/` (PRIVATE). Network git needs
> `-c credential.helper= -c credential.helper='!gh auth git-credential'`.

## Where things stand

**Kindred is live at https://kindred-eta-black.vercel.app** (Vercel project `kindred`, functions in Singapore `sin1`,
Supabase "database" ref rhaqbnvmyjcwgeosltaf). Last deploy = commit 02dc661 (2026-11-27), verified live.

Flow today: public home page → **Google sign-in** (required for everything else; anonymous sign-ins are off) →
**dashboard** ("Hi <name>!", Start a new search, 3 numbers, saved searches). First visit shows a **name pop-up** ("Hey
there! What should we call you?", saved as `user_metadata.kindred_name`). Chat (`/find`): "What's your brand? What do
you make? Spill it all." → **AI summary** ("This is what we have understood: …" + "Is this what you mean?" Yes/No; No →
"Could you explain it again?" once, then the new summary and straight on) → for brands with several products "a
particular product or your brand in general?" (+ product question) → **categories** (nothing pre-ticked, or "Let
Kindred decide") → buyers → **follower slider** (10K–100K, 1K steps) → gender + language → results. AI (Haiku 5.5)
understands the brand and reviews a 40-creator shortlist; code checks every claim and sets the Kindred Score. **Cards**
show Followers, Avg views, Reach, Engagement, Avg comments, languages, audience, all brand collabs and **Contact from
the bio** (email / phone / WhatsApp; view `creator_card_stats`, migration 003). Saved searches from before 02dc661
show "-" for the new numbers. AI spend ~$0.15 of the $1 total cap. e2e: 125 checks (AI off).

Data: 848 creators, 662 AI-profiled, 603 showable. A 20-brand **stress test** (report:
https://claude.ai/artifact/Mav7LbwJsy26j7GhNHXsb4) graded 10 right / 6 partly / 4 wrong: hardware brands are fine;
software, finance and service brands get phone/gadget creators because the database has 1 finance, 1 pet, 7 tech and
no business/software/career creators; the AI's "good" is also too lenient and niche specialists get no bonus (details
in docs/website.md "Known matching limits"). The user put every fix **on hold**.

S-027 ended right after the deploy of 02dc661 and this context write. Demo / viva with teachers: 2026-11-28.

## Continue from here

1. Wait for the user. **On hold, ask before touching:** (a) categories screen (big "Let Kindred decide", no red
   "Nobody fits" when nothing is ticked — that red line is a known bug from the no-pre-tick change), (b) buyers +
   followers + gender/language on one screen, (c) results header "None of our creators shows…" contradicting the cards,
   (d) stricter AI / niche bonus / topic specialists (stress-test suggestions), (e) new collection round for empty niches.
2. Offered, not answered: overlay live card numbers on old saved searches.
3. Older: Vercel GitHub Login Connection; old Render API; rotate keys; back up `instagram-scraper/media` (20 GB).

## Topic -> file

| Topic | File |
|---|---|
| Website flow: sign-in, dashboard, name pop-up, chat steps, AI summary, slider, categories, cards, contact, hosting | docs/website.md; 002 (S-025–S-027) |
| Matching limits, stress test of 20 brands, coverage by category | docs/website.md "Known matching limits"; report artifact above; 002 (S-027) |
| Setup, env vars, Vercel (region sin1), Google OAuth setup, tests | web/README.md |
| Google sign-in setup and its failures; anonymous-off | 002 (S-027) |
| AI matching (brand/product understanding, review, Kindred Score, $1 cap) | docs/website.md; web/src/lib/product.ts, review.ts, llm.ts |
| Live deploy details and what failed (git connect, region, logs retention) | 002 (S-026) |
| Presentation deck + viva explanations | 002 (S-026) |
| LLM model choice + prices | docs/data-and-matching.md; 002 (S-025) |
| Product idea, brand flow, paywall; refused budget/WhatsApp | docs/product-design.md; 001 (S-001) |
| Old pipeline, Apify audit (why our own scraper) | docs/data-and-matching.md; 001 (S-016–S-022) |
| Own scraper, lanes, WARP, 848 final creators, metrics | instagram-scraper/README.md, docs/; 002 (S-023) |
| AI creator profiles, Kindred Board (127.0.0.1:8791) | docs/ai-profile-spec.md; 002 (S-024) |
| Accounts, keys by name, live URLs, project refs | ~/Documents/ojt/PRIVATE-GUIDE.md |

## Open decisions

1. The on-hold list (Continue from here, item 1) — each needs the user's go.
2. Contact chips are free for every signed-in brand; paywall / unlock later?
3. Raise or keep the $1 AI cap after the demo.
4. Music-only creators in every language filter; old Render API; salon/studio accounts as creators.

## Ruled out

- Budget fields, WhatsApp flow, creators >100K (S-001); live scraping at search time; city as a requirement; buyer
  age / persona / mood (S-025); captions and hashtags as AI input or evidence (S-024).
- Anonymous sessions (replaced by Google sign-in, S-027); the chat asking the name (pop-up instead, S-027); forced
  "Lifestyle" pre-tick and any pre-ticked categories (S-027); more than one re-explain (S-027).
- Render backend, split hosting (S-025); Vercel region `iad1` (S-026).
- Fine-tuning an LLM; Sonnet for live searches (S-025); Haiku for video; fewer than 12 reels (S-024).
- Name/bio search, collab snowball, copying Modash/Qoruz, login scraping (S-021); cloud IPs, Tor, >11 WARP exits (S-023).
- Claude as git co-author.

## Sessions

| # | Date | Summary | File |
|---|---|---|---|
| S-001 | ≤ 2026-11-16 | Product planning chat (A.txt) | 001 |
| S-002–S-012 | 2026-11-16 → 19 | Context system, Apify pipeline, admin/demo, Edge Function, rounds, private guide | 001 |
| S-013–S-020 | 2026-11-19 → 22 | Brand-first matching, OpenRouter, eval, account check, credits | 001 |
| S-021–S-022 | 2026-11-22 → 24 | Deploy; Apify audit; index (961); scraper research; WARP | 001 |
| S-023 | 2026-11-24 → 25 | Own scraper repo; 848 final creators; metrics; Supabase reorganised | 002 |
| S-024 | 2026-11-25 → 26 | Kindred name; Gemini video AI profiles; Kindred Board | 002 |
| S-025 | 2026-11-26 | Website in web/: chat, top 20 by Kindred Score; AI built but off | 002 |
| S-026 | 2026-11-26 | Live on Vercel (AI on, $1 cap), name question, Singapore region, deck | 002 |
| S-027 | 2026-11-27 | Google sign-in, dashboard + name pop-up, AI summary, slider, Let Kindred decide, richer cards; stress test (fixes on hold); live | 002 |

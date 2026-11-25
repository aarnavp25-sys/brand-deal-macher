-- Kindred website tables in the "database" Supabase project (schema public).
-- Idempotent: safe to run again. Apply with: python3 web/db/migrate.py
--
-- Security model:
--   * The browser holds only the publishable (anon) key. It can read a brand's own searches (RLS below) and nothing
--     else: no creator table or view is granted to anon/authenticated.
--   * Every write and every creator read happens in the Next.js server with the secret key, after the server has
--     checked the signed-in user.

-- One row per "Find creators" conversation: the chat, the brief the AI built from it, and the final results.
create table if not exists public.brand_searches (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  title       text,
  status      text not null default 'chatting'
              check (status in ('chatting', 'ready', 'searching', 'done', 'failed')),
  messages    jsonb not null default '[]'::jsonb,   -- [{role: 'user'|'assistant', content, at}]
  brief       jsonb,                                -- the brand brief (validated by the server)
  results     jsonb,                                -- columns + creators + AI reasons, frozen at search time
  error       text,
  ai_cost     numeric not null default 0,           -- USD, real cost reported by OpenRouter
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index if not exists brand_searches_user_idx on public.brand_searches (user_id, created_at desc);

-- Every AI call the website makes: used for per-user limits and a site-wide daily spend cap.
create table if not exists public.llm_calls (
  id          bigserial primary key,
  user_id     uuid references auth.users(id) on delete set null,
  search_id   uuid references public.brand_searches(id) on delete set null,
  kind        text not null check (kind in ('chat', 'review')),
  ok          boolean not null,
  cost        numeric not null default 0,
  tokens_in   integer,
  tokens_out  integer,
  created_at  timestamptz not null default now()
);
create index if not exists llm_calls_user_idx on public.llm_calls (user_id, created_at desc);
create index if not exists llm_calls_time_idx on public.llm_calls (created_at desc);

alter table public.brand_searches enable row level security;
alter table public.llm_calls enable row level security;

-- Supabase's default privileges grant everything on new tables to anon/authenticated; take it all back.
revoke all on table public.brand_searches from anon, authenticated;
revoke all on table public.llm_calls from anon, authenticated;
revoke all on sequence public.llm_calls_id_seq from anon, authenticated;
grant select on table public.brand_searches to authenticated;
-- The server (secret key = service_role) does all writes. This project does not grant new tables to service_role
-- by default (found 2026-11-26: "permission denied for table brand_searches"), so grant it explicitly.
grant select, insert, update, delete on table public.brand_searches, public.llm_calls to service_role;
grant usage, select on sequence public.llm_calls_id_seq to service_role;

drop policy if exists "brand reads own searches" on public.brand_searches;
create policy "brand reads own searches" on public.brand_searches
  for select to authenticated using (user_id = (select auth.uid()));
-- llm_calls: no policy = no browser access at all.

-- Creator data is server-only. The view ran with its owner's rights (bypassing RLS); make it respect the caller,
-- and remove stray privileges anon/authenticated had on the AI tables.
alter view public.creator_overview set (security_invoker = true);
revoke all on table public.creator_ai, public.reel_ai, public.creator_overview from anon, authenticated;

-- Private bucket for creator profile pictures (served to signed-in brands through short-lived signed URLs).
insert into storage.buckets (id, name, public)
values ('creator-photos', 'creator-photos', false)
on conflict (id) do update set public = false;

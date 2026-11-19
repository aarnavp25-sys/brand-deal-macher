-- 2026-11-20: cache of search-time LLM answers (brand profile per brief, shortlist review per brand+shortlist).
-- The same brief, or the same brief with other filters, reuses the answer instead of paying again; 7-day expiry
-- is enforced by the Edge Function. Service role only (RLS on, no policies).
create table if not exists llm_cache (
  key        text primary key,          -- 'brand:<sha256>' / 'review:<sha256>'
  value      jsonb not null,
  created_at timestamptz not null default now()
);
alter table llm_cache enable row level security;

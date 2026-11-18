-- 2026-11-18: LLM classification (Amazon Nova 2 Lite) and the public match API.
-- keyword-v1 labels in `creators` / `creator_products` are never overwritten; the LLM writes here.
-- RLS on, no policies: only the service role (pipeline + Edge Function) can read/write.

create table if not exists creator_llm (
  creator_id     text primary key references creators(id) on delete cascade,
  model          text not null,                 -- e.g. global.amazon.nova-2-lite-v1:0
  prompt_version text not null,                 -- bump when the prompt changes; reruns skip same version
  category       text references categories(name),
  secondary      text references categories(name),
  products       jsonb not null default '[]',   -- [{"type": "...", "evidence_posts": 2, "specialization": 0.17}]
  gender_est     text,                          -- estimated: male / female / mixed/brand / unknown
  is_shop        boolean,                       -- account mainly sells its own products
  city           text,
  content_style  text,
  language       text,
  confidence     numeric,
  posts_seen     int,
  invalid        text[] not null default '{}',  -- validation problems; values outside the fixed lists are dropped
  input_tokens   int,
  output_tokens  int,
  raw            text,                          -- model reply, kept so the same call is never paid for twice
  classified_at  timestamptz not null default now()
);
create index if not exists creator_llm_category_idx on creator_llm (category);
alter table creator_llm enable row level security;

-- Per-client rate limit for the public Edge Function. Clients are stored as a salted SHA-256 hash, never raw IPs.
create table if not exists api_rate_limit (
  client       text not null,
  window_start timestamptz not null,
  hits         int not null default 0,
  primary key (client, window_start)
);
alter table api_rate_limit enable row level security;

create or replace function api_hit(p_client text, p_window_seconds int, p_max int)
returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  w timestamptz := to_timestamp(floor(extract(epoch from now()) / p_window_seconds) * p_window_seconds);
  n int;
begin
  insert into api_rate_limit (client, window_start, hits) values (p_client, w, 1)
  on conflict (client, window_start) do update set hits = api_rate_limit.hits + 1
  returning hits into n;
  delete from api_rate_limit where window_start < now() - interval '1 day';
  return n <= p_max;
end;
$$;
revoke all on function api_hit(text, int, int) from public, anon, authenticated;
grant execute on function api_hit(text, int, int) to service_role;

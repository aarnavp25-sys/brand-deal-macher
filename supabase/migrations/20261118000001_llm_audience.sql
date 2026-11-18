-- 2026-11-18: audience profile per creator from the LLM (prompt v2). All values are estimates.
alter table creator_llm add column if not exists audience_gender text;            -- men / women / unisex
alter table creator_llm add column if not exists audience_age    text;            -- teens / 18-24 / 25-34 / 35+ / mixed
alter table creator_llm add column if not exists audience_desc   text;            -- <=10 words
alter table creator_llm add column if not exists can_promote     text[] not null default '{}';  -- fixed product types

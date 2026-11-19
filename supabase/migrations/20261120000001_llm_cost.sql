-- 2026-11-20: LLM calls go through OpenRouter; keep the real cost and cache hits of every profile call.
alter table creator_llm add column if not exists cached_tokens int;      -- prompt tokens served from the cache
alter table creator_llm add column if not exists cost_usd      numeric;  -- cost OpenRouter reported for the call

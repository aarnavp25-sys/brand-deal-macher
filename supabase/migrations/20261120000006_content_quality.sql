-- 2026-11-20 (user: "content quality bhii dhyaan mai rkhna"): content quality read by the LLM from the posts.
-- creators.content_quality_est was never filled (keyword-v1 cannot judge it), so the quality signal was missing.
alter table creator_llm add column if not exists content_quality int;   -- 1-10
alter table creator_llm add column if not exists quality_note    text;  -- <=12 words: why

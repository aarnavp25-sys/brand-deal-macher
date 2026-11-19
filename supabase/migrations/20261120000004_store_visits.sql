-- 2026-11-20 (user: local stores should see creators who make reels inside shops): LLM-read store-visit content.
alter table creator_llm add column if not exists store_visits     text;  -- often / sometimes / never
alter table creator_llm add column if not exists store_visit_note text;  -- <=15 words: what kind of places and where

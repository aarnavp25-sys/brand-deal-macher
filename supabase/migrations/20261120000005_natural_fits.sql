-- 2026-11-20 (user: think like the brand; a travel creator who makes chai in the mountains can suit an instant tea
-- brand): products that fit naturally into scenes a creator already films, even if never promoted.
alter table creator_llm add column if not exists settings     text;   -- <=12 words: real places/situations they film
alter table creator_llm add column if not exists natural_fits jsonb;  -- [{type, moment}] up to 6; moment <=12 words

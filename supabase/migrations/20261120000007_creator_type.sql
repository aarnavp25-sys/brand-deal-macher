-- 2026-11-20 (user: a TVF director or a company CEO is not a reels creator; "woh kyu hii promotion karega"):
-- is Instagram this person's creator work, and do they take brand promotions?
alter table creator_llm add column if not exists creator_type     text;  -- creator / professional / celebrity
alter table creator_llm add column if not exists takes_promotions text;  -- yes / maybe / unlikely
alter table creator_llm add column if not exists collab_note      text;  -- <=12 words: the evidence

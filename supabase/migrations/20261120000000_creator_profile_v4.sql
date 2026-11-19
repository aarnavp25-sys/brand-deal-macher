-- 2026-11-20: deeper creator profile from the LLM (prompt v4). All values are estimates read from public posts.
-- Asked by the user: know HOW a creator talks (fan vs expert), at what price level, whose products, which values,
-- and whether they are niche, category-wide or broad lifestyle creators, so each brand gets creators that fit it.
alter table creator_llm add column if not exists niche            text;   -- <=8 words, e.g. "healthy high-protein home recipes"
alter table creator_llm add column if not exists creator_role     text;   -- expert / reviewer / educator / enthusiast / entertainer / lifestyle / aspirational
alter table creator_llm add column if not exists credibility      text;   -- professional / experienced / casual
alter table creator_llm add column if not exists credibility_note text;   -- <=15 words: why (e.g. "state-level cricketer, coaches juniors")
alter table creator_llm add column if not exists price_segment    text;   -- budget / mid / premium / mixed: price level of what they show
alter table creator_llm add column if not exists products_for     text;   -- men / women / unisex: whose products they feature (not the creator's gender)
alter table creator_llm add column if not exists content_values   text[] not null default '{}';  -- fixed list, up to 4
alter table creator_llm add column if not exists scope            text;   -- niche / category / broad
alter table creator_llm add column if not exists brand_fit        text;   -- <=25 words: which brands fit and how

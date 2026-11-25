-- Creator username index (separate Supabase project from the main app).
-- Holds only what the Apify India index returns: usernames + basic counts per category. No profile scrape.
-- Run once in the new project's SQL editor, or: python3 index/collect.py migrate (needs INDEX_SUPABASE_ACCESS_TOKEN).

create table if not exists index_creators (
  username          text primary key,          -- lower-case Instagram handle
  followers         integer,
  follower_bracket  text,
  city              text,
  posts_count       integer,
  engagement_rate   numeric,                    -- 0-1 ratio as the source gives it
  avg_likes         integer,
  avg_comments      integer,
  avg_views         integer,
  verified          boolean,
  country           text,
  source            text not null default 'apify:social_developer',
  first_seen        timestamptz not null default now(),
  last_seen         timestamptz not null default now(),
  raw               jsonb                       -- the source row as returned, so nothing is paid for twice
);

-- one creator can be found under several of the 120 categories
create table if not exists index_creator_categories (
  username   text not null references index_creators(username) on delete cascade,
  category   text not null,
  run_id     text,
  found_at   timestamptz not null default now(),
  primary key (username, category)
);
create index if not exists index_creator_categories_category on index_creator_categories (category);

-- every Apify run: what was asked, what came back, what it cost, which account paid
create table if not exists index_runs (
  run_id          text primary key,
  category        text not null,
  city            text,                        -- random city the program drew for this run (no city is ever hand-picked)
  account         text not null,               -- key label only, never the token
  requested       integer not null,
  received        integer,
  kept            integer,                     -- rows inside 10K-100K that were saved
  new_usernames   integer,                     -- not seen before in this index
  cost_usd        numeric,                     -- results x price (the actor's per-result charge)
  status          text,
  status_message  text,
  started_at      timestamptz not null default now()
);

create or replace view index_progress with (security_invoker = true) as
  select category, count(*)::int as creators from index_creator_categories group by category;

-- RLS on, no policies: only the service key (local scripts and the local dashboard) can read or write.
alter table index_creators enable row level security;
alter table index_creator_categories enable row level security;
alter table index_runs enable row level security;

-- 2026-11-24: manual review of every collected username (name, username, category read by hand).
-- verdict: not_useful (shop/brand/business, foreign, page) or check (wrong category, person may still be useful).
create table if not exists index_review (
  username    text primary key references index_creators(username) on delete cascade,
  verdict     text not null,              -- not_useful / check
  kind        text not null,              -- shop / brand / business · foreign account · page, not a person · wrong category
  reason      text,
  reviewed_at timestamptz not null default now()
);
alter table index_review enable row level security;
grant all on index_review to service_role;

-- 2026-11-24 (user): the display name is removed from the whole index database: the column, the stored source rows
-- (raw.fullName) and the removal backups. collect.py no longer saves it. Views are dropped first (they used it).
do $$ declare v record; begin for v in select table_name from information_schema.views where table_schema='public'
  and table_name like 'cat\_%' loop execute format('drop view if exists %I', v.table_name); end loop; end $$;
alter table index_creators drop column if exists full_name;
update index_creators set raw = raw - 'fullName' where raw ? 'fullName';
update index_removed set row = (row - 'full_name') || jsonb_build_object('raw', (row->'raw') - 'fullName')
  where row ? 'full_name' or (row->'raw') ? 'fullName';

-- Categories (2026-11-24, user: keep only the 9 main-DB categories that have creators; Home Decor & Handmade,
-- Sports, Gaming, Entertainment & Comedy, Music & Dance, Education & Finance and Pets removed). index_category_groups
-- maps the actor's categories into the 9 (generated from index/category_groups.json); every other actor category
-- is never collected. Each of the 9 gets a view cat_<name> listed like a table in Supabase, with the manual review.
create table if not exists index_category_groups (category text primary key, group_name text not null);
delete from index_category_groups;
insert into index_category_groups (category, group_name) values
  ('Food Blogging', 'Food & Beverages'),
  ('Food Drink', 'Food & Beverages'),
  ('Chef', 'Food & Beverages'),
  ('Beauty', 'Beauty & Skincare'),
  ('Make Up', 'Beauty & Skincare'),
  ('Skin Care', 'Beauty & Skincare'),
  ('Hair Care', 'Beauty & Skincare'),
  ('Nail Art', 'Beauty & Skincare'),
  ('Fashion', 'Fashion & Clothing'),
  ('Fashion & Lifestyle', 'Fashion & Clothing'),
  ('Fashion Creator', 'Fashion & Clothing'),
  ('Fashion Design', 'Fashion & Clothing'),
  ('Fashion Influencer', 'Fashion & Clothing'),
  ('Fashion Stylist', 'Fashion & Clothing'),
  ('Modeling', 'Fashion & Clothing'),
  ('Jewellery', 'Jewelry & Accessories'),
  ('Gym & Fitness', 'Fitness & Wellness'),
  ('Gym Training', 'Fitness & Wellness'),
  ('Fitness Training', 'Fitness & Wellness'),
  ('Fitness Modeling', 'Fitness & Wellness'),
  ('Health', 'Fitness & Wellness'),
  ('Health Fitness', 'Fitness & Wellness'),
  ('Yoga', 'Fitness & Wellness'),
  ('Ayurveda', 'Fitness & Wellness'),
  ('Nutrition', 'Fitness & Wellness'),
  ('Doctor', 'Fitness & Wellness'),
  ('Psychotherapy', 'Fitness & Wellness'),
  ('Technology', 'Tech & Gadgets'),
  ('Gadget Review', 'Tech & Gadgets'),
  ('Coding', 'Tech & Gadgets'),
  ('Parenting', 'Parenting & Kids'),
  ('Kids & Toys', 'Parenting & Kids'),
  ('Fertility Expert', 'Parenting & Kids'),
  ('Travel', 'Travel & Explore'),
  ('Budget Travel', 'Travel & Explore'),
  ('International Travel', 'Travel & Explore'),
  ('Luxury Travel', 'Travel & Explore'),
  ('Wildlife Travel', 'Travel & Explore'),
  ('Auto', 'Automobile'),
  ('Automobile', 'Automobile'),
  ('Biking', 'Automobile');
alter table index_category_groups enable row level security;
do $$ declare v record; begin for v in select table_name from information_schema.views where table_schema='public' and (table_name like 'grp\_%' or table_name like 'cat\_%') loop execute format('drop view if exists %I', v.table_name); end loop; end $$;
create or replace view cat_food_beverages with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Food & Beverages';
create or replace view cat_beauty_skincare with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Beauty & Skincare';
create or replace view cat_fashion_clothing with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Fashion & Clothing';
create or replace view cat_jewelry_accessories with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Jewelry & Accessories';
create or replace view cat_fitness_wellness with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Fitness & Wellness';
create or replace view cat_tech_gadgets with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Tech & Gadgets';
create or replace view cat_parenting_kids with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Parenting & Kids';
create or replace view cat_travel_explore with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Travel & Explore';
create or replace view cat_automobile with (security_invoker = true) as
  select cc.category as sub_category, c.username, 'https://www.instagram.com/' || c.username || '/' as instagram_url,
         c.followers, c.city, c.posts_count, r.verdict as review, r.kind as review_kind, r.reason as review_reason,
         c.first_seen
  from index_creator_categories cc
  join index_creators c on c.username = cc.username
  join index_category_groups g on g.category = cc.category
  left join index_review r on r.username = c.username
  where g.group_name = 'Automobile';

-- New Supabase projects (late 2026) no longer grant API roles on new tables by default. Only the local collector
-- and dashboard (service_role) read or write; anon and authenticated get nothing.
grant usage on schema public to service_role;
grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
notify pgrst, 'reload schema';


notify pgrst, 'reload schema';

-- 2026-11-24 (user): clothing shops, own mobile/gadget shops and car fan pages are removed from the index. Full rows are
-- kept here as a backup, and collect.py never saves these usernames again.
create table if not exists index_removed (
  username    text primary key,
  reason      text not null,
  categories  text[],
  row         jsonb not null,               -- the full index_creators row at removal time (incl. raw)
  removed_at  timestamptz not null default now()
);
alter table index_removed enable row level security;
grant all on index_removed to service_role;
notify pgrst, 'reload schema';

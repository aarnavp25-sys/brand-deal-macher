-- Brand Deal Matcher: creator data schema (Supabase / Postgres 17)
-- First schema (2026-11-16, was pipeline/schema.sql). RLS on, no policies: only the service role can read/write.
-- The website will get explicit read policies later.

create table if not exists raw_scrapes (
  id          bigint generated always as identity primary key,
  actor       text not null,
  run_id      text,
  input       jsonb,
  items       jsonb,                                 -- unused: big payloads timed out; see storage_path
  storage_path text,                                 -- Supabase Storage object with the raw run JSON
  item_count  int,
  cost_usd    numeric,
  created_at  timestamptz not null default now()
);

create table if not exists categories (
  name      text primary key,
  sub_tags  text[] not null default '{}',
  demo_rank int
);

create table if not exists product_types (
  name      text primary key,
  category  text references categories(name),
  keywords  text[] not null default '{}'
);

create table if not exists creators (
  id                    text primary key,            -- Instagram user id
  username              text not null unique,
  full_name             text,
  bio                   text,
  followers             int,
  following             int,
  posts_count           int,
  follower_tier         text,                        -- nano / micro / mid
  is_business           boolean,
  ig_category           text,                        -- Instagram's own category
  verified              boolean,
  external_url          text,
  profile_pic_url       text,
  niche_primary         text references categories(name),
  niche_secondary       text references categories(name),
  niche_share           numeric,                     -- share of recent posts matching niche_primary
  sub_tags              text[] not null default '{}',
  city                  text,
  email                 text,
  collab_open           boolean,
  engagement_rate       numeric,                     -- %, (avg likes + avg comments) / followers
  avg_reel_views        numeric,
  reel_reach            numeric,                     -- avg reel views / followers
  posts_per_week        numeric,
  last_post_at          timestamptz,
  fake_flag             boolean not null default false,
  creator_gender_est    text,                        -- filled by LLM step later
  content_quality_est   numeric,                     -- filled by vision step later
  classification_method text,                        -- 'keyword-v1' now, 'llm' later
  source_keyword        text,
  status                text not null default 'active',
  scraped_at            timestamptz,
  updated_at            timestamptz not null default now()
);
create index if not exists creators_niche_idx on creators (niche_primary, follower_tier);
create index if not exists creators_city_idx on creators (city);

create table if not exists creator_snapshots (
  creator_id text references creators(id) on delete cascade,
  taken_at   date not null,
  followers  int,
  following  int,
  primary key (creator_id, taken_at)
);

create table if not exists posts (
  id               text primary key,
  creator_id       text references creators(id) on delete cascade,
  shortcode        text,
  url              text,
  type             text,
  source           text,                             -- 'profile' | 'reel'
  posted_at        timestamptz,
  likes            int,                              -- null when hidden (-1 from Apify)
  comments         int,
  views            int,
  caption          text,
  hashtags         text[] not null default '{}',
  mentions         text[] not null default '{}',
  location         text,
  is_pinned        boolean,
  paid_partnership boolean,
  coauthors        text[] not null default '{}',
  product_labels   text[] not null default '{}',
  thumbnail_url    text
);
create index if not exists posts_creator_idx on posts (creator_id, posted_at desc);

create table if not exists creator_products (
  creator_id     text references creators(id) on delete cascade,
  product_type   text references product_types(name),
  kind           text not null,                      -- 'proven' | 'possible'
  evidence_posts int not null default 0,
  specialization numeric,                            -- evidence_posts / recent posts
  paid_posts     int not null default 0,
  last_seen      timestamptz,
  primary key (creator_id, product_type)
);

alter table raw_scrapes       enable row level security;
alter table categories        enable row level security;
alter table product_types     enable row level security;
alter table creators          enable row level security;
alter table creator_snapshots enable row level security;
alter table posts             enable row level security;
alter table creator_products  enable row level security;

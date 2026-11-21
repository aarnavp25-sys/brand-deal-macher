-- 2026-11-21: accounts deleted from `creators` on the user's order, kept here only so a later scraping round
-- does not scrape and profile them again (round.py treats these usernames as already known).
-- The full rows (creator, posts, AI profile, snapshots, products) are backed up in storage raw-scrapes/backups/.
create table if not exists removed_creators (
  username    text primary key,          -- lower-case Instagram username
  creator_id  text,                      -- the old creators.id (Instagram user id)
  reason      text not null,
  removed_at  timestamptz not null default now()
);
alter table removed_creators enable row level security;

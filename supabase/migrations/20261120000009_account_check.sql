-- 2026-11-20 (user, after a men's jewellery search showed personal accounts: "saare 10k se niche wala account ko
-- haiku se check karwa aur un sab ko review mai daal"): Haiku checks each account under 10K followers: is it a
-- creator a brand can hire, a personal account, or a page that mainly promotes its own shop? Personal and own-shop
-- accounts move to status = 'review' (hidden from search, kept in the DB, visible in admin with the reason).
alter table creators add column if not exists account_type       text;         -- creator / personal / own shop / unclear
alter table creators add column if not exists account_note       text;         -- <= 15 words: why (from the AI)
alter table creators add column if not exists account_checked_at timestamptz;
alter table creators add column if not exists review_reason      text;         -- why status = 'review' (any source)

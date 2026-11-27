-- Numbers and contact lines for the creator cards (user, 2026-11-27: followers, average views, reach, engagement,
-- comments, languages, brand collabs, and the collab email / phone from the bio).
-- avg_comments = mean comments over the creator's latest non-pinned reels (reel_rank 1..12), the same reels the
-- metrics use. Server-only, like the other creator data.
create or replace view public.creator_card_stats with (security_invoker = true) as
select
  p.username,
  m.mean_views,
  m.median_views,
  m.reach_ratio,
  (select round(avg(r.comments))::int
     from public.scrape_reels r
    where r.username = p.username and r.reel_rank between 1 and 12 and r.comments is not null) as avg_comments,
  p.bio,
  p.bio_links
from public.scrape_profiles p
left join public.creator_metrics m using (username);

revoke all on table public.creator_card_stats from anon, authenticated;
grant select on table public.creator_card_stats to service_role;

-- Make the API see the new view right away.
notify pgrst, 'reload schema';

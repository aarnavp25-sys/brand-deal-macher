-- 2026-11-18: why a creator is fake-flagged, in plain words with the creator's own numbers (shown in admin).
alter table creators add column if not exists fake_reason text;

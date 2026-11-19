-- 2026-11-19 cleanup: raw_scrapes.items was never used (multi-MB jsonb rows timed out; raw JSON lives in
-- Storage bucket raw-scrapes as .json.gz, path in storage_path). 0 of 174 rows had it filled.
alter table raw_scrapes drop column if exists items;

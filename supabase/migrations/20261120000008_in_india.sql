-- 2026-11-20 pilot: ~11% of profiled accounts were not in India (Italy, UK, Chile, Australia...) and ~10% were
-- organisations (colleges, NGOs, teams, event organisers). in_india lets search drop foreign accounts.
alter table creator_llm add column if not exists in_india text;  -- yes / no / unclear

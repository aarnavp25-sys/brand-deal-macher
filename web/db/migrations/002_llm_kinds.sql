-- llm_calls.kind: the website's AI calls are "product" (understand the brand's product) and "review" (judge creators).
alter table public.llm_calls drop constraint if exists llm_calls_kind_check;
alter table public.llm_calls add constraint llm_calls_kind_check check (kind in ('chat', 'product', 'review'));

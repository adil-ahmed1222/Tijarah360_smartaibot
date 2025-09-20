-- Supabase schema for bilingual FAQs
-- Creates table `faqs` with English and Arabic fields, tags, and basic FTS support

create table if not exists public.faqs (
  id integer primary key,
  question_en text not null,
  answer_en text not null,
  question_ar text not null,
  answer_ar text not null,
  tags text[] default array[]::text[],
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Trigger to auto-update updated_at
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_faqs_updated_at on public.faqs;
create trigger set_faqs_updated_at
before update on public.faqs
for each row execute function public.set_updated_at();

-- Basic full-text search index (simple config, covers both languages as plain text)
create index if not exists faqs_fts_idx on public.faqs using gin (
  to_tsvector('simple', coalesce(question_en,'') || ' ' || coalesce(answer_en,'') || ' ' || coalesce(question_ar,'') || ' ' || coalesce(answer_ar,''))
);

-- Helpful btree indexes
create index if not exists faqs_tags_idx on public.faqs using gin (tags);

-- RLS: enable and allow anonymous read, service role full access
alter table public.faqs enable row level security;

-- Drop existing policies if re-running
do $$ begin
  if exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'faqs' and policyname = 'faqs_select_public') then
    drop policy faqs_select_public on public.faqs;
  end if;
  if exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'faqs' and policyname = 'faqs_all_service_role') then
    drop policy faqs_all_service_role on public.faqs;
  end if;
end $$;

-- Public read-only
create policy faqs_select_public on public.faqs
for select
to anon, authenticated
using (true);

-- Service role full access
create policy faqs_all_service_role on public.faqs
for all
to service_role
using (true)
with check (true);




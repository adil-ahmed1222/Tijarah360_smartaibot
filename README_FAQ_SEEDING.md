### Bilingual FAQ in Supabase

This backend includes a schema and scripts to seed a bilingual (English + Arabic) FAQ into Supabase.

#### Files
- `supabase_schema.sql`: Creates `public.faqs` with EN/AR fields, tags, FTS index, and RLS.
- `faq_data.csv`: Existing English source (ID, Question, Answer, Tags).
- `faq_data_ar.json`: Arabic mapping from ID → `question_ar`, `answer_ar`.
- `scripts/seed_faqs_bilingual.py`: Merges EN+AR and upserts to Supabase.

#### 1) Apply schema to Supabase
Run this SQL in Supabase SQL editor (or via psql):
- Open `supabase_schema.sql` and execute its contents.

#### 2) Configure environment
Ensure these env vars are set (e.g., in `.env`):
- `SUPABASE_URL`
- `SUPABASE_KEY` (service role preferred for seeding)

#### 3) Seed data
From `src/backend` directory:
```bash
python -m scripts.seed_faqs_bilingual
```

The script will:
- Read `faq_data.csv` (EN) and `faq_data_ar.json` (AR)
- Normalize tags
- Upsert into `public.faqs` by `id`

#### Notes
- Missing Arabic rows will fall back to English text to avoid nulls.
- You can re-run the seeder safely; it uses upsert on `id`.





# Inst Content Intelligence

Instagram analysis service for reels/carousel/posts with Russian-language insights.

## What Is Implemented

- Single URL analysis with structured output:
  - hook (`захват`)
  - retention (`удержание`)
  - transfer (`перелив`)
  - CTA detection
  - audience reaction from comments
- Engagement metrics with fallback:
  - `by_views` when views are available
  - bounded proxy metric when views are unavailable
- Local exports:
  - `TXT`
  - `DOCX`
- Google export:
  - Sheets-only mode
  - retries and detailed export diagnostics in `insights.exports`
- Batch pipeline:
  - up to 30 URLs per batch
  - retries per URL
  - retry failed-only workflow
  - CSV export of batch results
- UI panel:
  - KPI cards
  - single-analysis actions
  - history table with search/filters/actions
  - batch table, summary, file upload (`.txt/.csv`)
  - clear history button

## Project Structure

- `app/main.py` - API endpoints + embedded UI page
- `app/services/instagram_client.py` - Instagram ingestion/auth
- `app/services/analyzer.py` - scoring and insight generation
- `app/services/exporters.py` - Google Sheets export
- `app/services/report_export.py` - TXT/DOCX export
- `app/entities.py` - DB models (`analysis_records`, `batch_jobs`, `batch_job_items`)
- `tests/test_analyzer.py` - analysis tests
- `start_inst_analyzer.bat` - one-click local launcher

## Quick Start

1. Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

1. Configure env:

```bash
copy .env.example .env
```

1. Set required variables in `.env` or `env.txt`:

- `INSTAGRAM_USERNAME`
- `INSTAGRAM_PASSWORD`

Optional but recommended:

- `INSTAGRAM_SESSIONID` (if password login is blocked)
- `REPORTS_DIR` (default `reports`)
- `GOOGLE_CREDENTIALS_FILE` (recommended) or `GOOGLE_CREDENTIALS_JSON`
- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_EXPORT_RETRIES` (default `2`)

1. Run:

```bash
python -m uvicorn app.main:app --reload
```

or double-click:

- `start_inst_analyzer.bat`

1. Open:

- `http://127.0.0.1:8000` (UI)
- `http://127.0.0.1:8000/docs` (OpenAPI)

## API Reference

### Single Analysis

- `POST /api/analyze`
  - body:
    - `url`
    - `comments_limit` (10..1000, default 200)
    - `include_comment_replies` (bool)
    - `export_google` (bool)
- `GET /api/analysis/{analysis_id}`
- `GET /api/analysis`
  - query:
    - `limit` (1..200)
    - `q` (search in url/shortcode/author)
    - `author` (author contains)
    - `media_type` (`1` photo, `2` video/reel, `8` carousel)
- `POST /api/analysis/clear`
- `GET /api/analysis/{analysis_id}/export/txt`
- `GET /api/analysis/{analysis_id}/export/docx`

### Batch Analysis

- `POST /api/batch/analyze`
  - `urls` (1..30 URLs)
  - `comments_limit`
  - `include_comment_replies`
  - `export_google`
  - `max_retries` (1..5)
- `GET /api/batch/{batch_job_id}`
- `GET /api/batch`
- `POST /api/batch/{batch_job_id}/retry-failed`
- `GET /api/batch/{batch_job_id}/export/csv`

## Current Product Decisions

- Google Docs export is disabled.
- Google export target is Google Sheets only.
- Batch max size is 30 URLs.
- Primary human-readable exports are local `TXT/DOCX`.

## Known Limits

- Instagram does not reliably provide per-post subscriber conversion.
- Some posts return `view_count=0`; proxy engagement is used in this case.
- If Instagram login challenges occur, use `INSTAGRAM_SESSIONID`.

## Troubleshooting

- `POST /api/analyze` returns auth errors:
  - verify credentials
  - set `INSTAGRAM_SESSIONID`
  - restart server after env changes
- Google export is partial:
  - inspect `insights.exports` in response
  - verify Sheets ID and service account access
- UI seems stale:
  - hard refresh (`Ctrl+F5`)
  - restart server

## Delivery Status

- Core MVP: complete
- Single analysis flow: complete
- Batch flow with retry/csv: complete
- UI mini-dashboard: complete
- Docs export: intentionally excluded

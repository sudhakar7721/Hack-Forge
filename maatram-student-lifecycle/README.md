# Maatram Student Lifecycle Platform (MH26-05)

A local prototype connecting admissions, student lifecycle events, alumni career history, and secure document uploads.

## Stack
- React + Vite frontend
- FastAPI backend
- SQLAlchemy relational models; SQLite by default for easy local setup, MySQL/MariaDB via `DATABASE_URL`
- S3-compatible presigned uploads (MinIO supported)
- Docker Compose
- Pytest backend tests

> Uses synthetic/demo data only. Do not enter real student personal information in a public demo.

## Run locally (Python + Node)
### Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### Frontend
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173. The Vite dev server proxies `/api` to the backend.

## Run with Docker Compose
```bash
docker compose up --build
```
Open http://localhost:5173. Compose starts the React app, FastAPI, MariaDB, and MinIO. MinIO console: http://localhost:9001 (minioadmin / minioadmin123).

## Tests
```bash
cd backend
pip install -r requirements.txt
pytest -q
```

## Features
- **Admission cycles:** create drafts, submit applications, filter by cycle, shortlist, bulk select/reject, rejection reasons, audit history.
- **Student lifecycle event log:** append-only event records; event and state changes commit together; duplicate `event_id` is idempotent; chronological replay and replay-from-time.
- **Alumni career tracker:** career records retain source, normalized company names, and employment dates; query current alumni by company.
- **Smart uploads:** server-side MIME/size checks and short-lived S3 presigned PUT URLs. If object storage is not configured, the API returns a clear configuration error.
- **Linked records:** selected applicants are linked to a student record and an `ApplicantSelected` lifecycle event.

## API highlights
- `GET /api/health`
- `GET/POST /api/cycles`
- `GET/POST /api/applications`
- `POST /api/applications/{id}/submit`
- `POST /api/applications/bulk-review`
- `GET /api/applications/{id}/audit`
- `POST /api/events`, `GET /api/students/{id}/events`, `GET /api/students/{id}/replay?from_time=...`
- `GET/POST /api/careers`, `GET /api/careers/search?company=...`
- `POST /api/uploads/presign`, `POST /api/uploads/confirm`

## Design notes / prototype limits
- Event rows are append-only at the application layer. Production deployments should enforce append-only permissions at the database layer and use a transactional outbox if external side effects are added.
- Replay returns reconstructed event-derived state. Events are ordered by `occurred_at`, then database ID to make ties deterministic; clients should supply stable event IDs and timestamps.
- Company matching uses a small configurable alias map plus lowercase punctuation/whitespace normalization. Review aliases before production use.
- Configure `MAX_UPLOAD_BYTES`, `ALLOWED_CONTENT_TYPES`, `S3_ENDPOINT_URL`, `S3_BUCKET`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, and `S3_REGION` using environment variables.
- For production: add authentication/role-based authorization, CSRF/CORS policy, rate limits, malware scanning, retention policy, backups, monitoring, and formal privacy review.

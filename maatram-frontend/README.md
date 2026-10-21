# Maatram Student Lifecycle – React Frontend
Pages: Apply (drafts/submit), Staff Review (filter by cycle/status, bulk shortlist/select/reject with reason, audit trail, year comparison),
Event Log (append with idempotency key, replay from beginning / point in time / bookmark), Alumni Careers (history, source, company search), Documents (presigned S3/MinIO upload).

## Run
    npm install
    cp .env.example .env     # set VITE_API_URL to your FastAPI backend
    npm run dev              # http://localhost:3000

## Expected backend endpoints (FastAPI)
GET/POST /cycles · GET /cycles/compare?years= · GET/POST /applications · PUT /applications/{id} · POST /applications/{id}/submit
POST /applications/bulk {ids, action: shortlist|select|reject, reason} · GET /applications/{id}/audit
GET/POST /students/{id}/events · POST /students/{id}/replay {mode, from_time}
POST /alumni/{id}/careers · GET /alumni/{id}/profile · GET /alumni/search?company=
POST /uploads/presign {student_id, filename, content_type, size} -> {url, key} · POST /uploads/confirm {key} · GET /students/{id}/documents
Enable CORS for http://localhost:3000 on the backend.

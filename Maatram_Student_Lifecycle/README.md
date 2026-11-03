# MH26-05 – Maatram Student Lifecycle Platform

A unified React + FastAPI + MySQL starter implementation for the Maatram HackForge 2026–27 brief. It includes role-aware authentication, admission applications, student/alumni records, append-only lifecycle events, dashboard analytics, secure document upload, CSV export, Alembic migration scaffolding and optional Docker Compose.

> Security note: this is a hackathon-ready development baseline, not a security-certified production deployment. OTP is deliberately in development-adapter mode and prints a test code to the backend console. No SMS delivery is configured. Use synthetic data until privacy, legal, security, backup and deployment reviews are complete.

## Requirements
- Python 3.11+
- Node.js 20+
- MySQL 8+
- Optional: Docker Desktop

## Quick start (Windows PowerShell)

### 1. Database
Create a MySQL database:
```sql
CREATE DATABASE maatram_student_lifecycle CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Copy `backend/.env.example` to `backend/.env` and set your local database password and a long random `JWT_SECRET`.

### 2. Backend
```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### 3. Frontend
Open another terminal:
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## First admin account
For a clean development database, create an account using the registration endpoint is intentionally disabled for privileged roles. Create the first admin from the backend shell:
```powershell
cd backend
python -m app.seed_admin
```
The script prompts for username, email and password. Keep the password private.

Students can register from the UI. Admins can create Core Member accounts from Swagger using `POST /api/users` with an admin JWT.

## Development OTP
`OTP_MODE=console` prints the OTP in the backend terminal. This is only for local testing. For real OTP, implement a provider adapter in `app/services/otp.py`, configure provider credentials only in environment variables, and set `OTP_MODE=provider`. Do not claim SMS delivery unless a real provider is configured.

## Main API groups
- `/api/auth` – register, login, OTP request/verify, forgot-password reset
- `/api/users` – admin user management
- `/api/applications` – admission workflow and history
- `/api/students` – student lifecycle records
- `/api/alumni` – alumni career profiles
- `/api/events` – append-only lifecycle events and replay
- `/api/documents` – private document upload/list/download
- `/api/dashboard` – role-aware metrics
- `/api/reports/applications.csv` – application CSV export

## Architecture
- Frontend: React, Vite, React Router, Axios
- Backend: FastAPI, SQLAlchemy 2, Pydantic v2, JWT, Argon2
- Database: MySQL via PyMySQL
- Migrations: Alembic
- Uploads: private local directory outside frontend public assets
- Event history: append-only records with unique event UUID and SHA-256 hash chain

## Important implementation notes
- The app intentionally avoids shipping demo passwords or real personal data.
- Salary fields are not exposed in general dashboard responses.
- Document download requires authentication and ownership/admin permission.
- Event history is append-only at the API layer; production database users should also be granted INSERT/SELECT (not UPDATE/DELETE) on `event_logs`.
- Redis/Celery are not enabled by default because the core workflow does not require background jobs. Add them only when real notification/report workloads justify them.
- `docker-compose.yml` starts MySQL and the API; frontend can be run locally or containerized separately.

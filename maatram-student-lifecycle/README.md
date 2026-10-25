# Maatram - Student Lifecycle

A full-stack starter platform for managing the student journey from application to alumni.

## Stack
- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: SQLAlchemy + SQLite by default (change `DATABASE_URL` for PostgreSQL/MySQL)
- Authentication: demo role-based login; passwords are hashed in the database
- Theme: yellow, black, white

> Important: Demo credentials and OTP flow are for local demonstration only. The forgot-password OTP is a development demo (OTP `123456`); it does not send SMS. Before real use, integrate an SMS provider, add verified phone ownership, rate limits, secure deployment, backups, privacy consent, and professional security review. Use synthetic data while testing.

## Demo logins
| Role | Username | Password |
|---|---|---|
| Student | `student` | `student-50` |
| Alumni | `alumni` | `alumni-100` |
| Admin | `admin` | `admin-5` |
| Core Members | `core` | `core-12` |

## Run on Windows (PowerShell)
### 1. Backend
Open terminal:
```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

### 2. Frontend (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the URL Vite prints (normally http://localhost:5173).

If Node/Vite reports native-binding errors, use Node.js 22 LTS, delete `frontend/node_modules`, then run `npm install` again.

## Database
SQLite database is created automatically at `backend/maatram.db`. Set `DATABASE_URL` before starting FastAPI to use another SQL database, for example:
`DATABASE_URL=sqlite:///./maatram.db`

## Features in this starter
- Four role-specific sign-in types and dashboards
- Demo credentials above
- Forgot password demo flow (phone number + demo OTP)
- Student profile, application, admission, academics, mentoring, fee, activities and volunteering fields
- Alumni placement/company information and linked student details
- Admin and core team workspaces with management summaries
- Student list and create/update APIs
- SQL persistence and hashed demo passwords
- Responsive yellow/black/white UI

This is a practical foundation, not yet a production-hardened student information system.

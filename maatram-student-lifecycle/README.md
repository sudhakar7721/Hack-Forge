# Maatram - Student Lifecycle

A full-stack Maatram student and alumni community platform. Existing lifecycle, admin, core-team and career features are retained while adding academic profiles and zone communication.

## Stack
- Frontend: React + Vite
- Backend: Python + FastAPI
- Database: SQLAlchemy + SQLite by default (change `DATABASE_URL` for PostgreSQL/MySQL)
- Authentication: demo role-based login; passwords are hashed in the database
- Theme: yellow, black, white

> Important: Demo credentials and OTP flow are for local demonstration only. The forgot-password OTP is a development demo (OTP `123456`); it does not send SMS. Before real use, integrate an SMS provider, add verified phone ownership, rate limits, secure deployment, backups, privacy consent, and professional security review. Use synthetic data while testing.

## Demo logins
The full 55-account demo credential list is supplied in `Maatram_Login_Credentials.pdf` at the project root. There are 40 student accounts, 5 admin accounts (4 zone admins plus 1 system admin), and 10 core-team accounts. The legacy alumni demo account remains available: `alumni` / `alumni-100`.

The credentials are predictable demo credentials intended only for local testing. Change them before any shared deployment.

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

The frontend dependencies are declared in `frontend/package.json`; run `npm install` before `npm run dev`. The Maatram Foundation logo is included in `frontend/public/maatram-logo-4k.png` and links to https://www.maatramfoundation.com/. Student CGPA and academic entries currently shown as samples are demonstration data, not verified academic results.

If Node/Vite reports native-binding errors, use Node.js 22 LTS, delete `frontend/node_modules`, then run `npm install` again.

## Database
SQLite database is created automatically at `backend/maatram.db`. Set `DATABASE_URL` before starting FastAPI to use another SQL database, for example:
`DATABASE_URL=sqlite:///./maatram.db`

## Features in this starter
- Four role-specific sign-in types and dashboards
- Demo credentials above
- Forgot password demo flow (phone number + demo OTP)
- Expanded student academic profile: registration number, college, department, passed-out year, semester marks, CGPA, courses/certificates, internship, skills, resume, projects and social profiles
- Student zone information, shared document/link notices, feedback to zone incharge and volunteering updates
- Alumni/student directory, zone information broadcasts, zone feedback view and editable student-to-zone/team assignments
- Existing application/admission records remain available to admin/core team; the student navigation no longer displays Application & Admission
- Alumni placement/company information and linked student details
- Admin and core team workspaces with management summaries
- Student list and create/update APIs
- SQL persistence and hashed demo passwords
- Responsive yellow/black/white UI

This is a practical foundation, not yet a production-hardened student information system.

## Added zone and academic features
- Student menu: Dashboard, My Details, Academics, Volunteering, Informations, Notifications and Feedback. Application & Admission is hidden from the student workspace; existing admin/core application management remains.
- Academic profile fields can be edited from the student Academics page. Semester subject/mark entries can be added; resume and course certificate uploads are limited to 4 MB per file in the browser.
- Zone messages support a title, message, external URL (Google Forms/Meet/group links) and one attached file. Attachments are stored as Base64 in SQLite in this demo, so use small files and configure production object storage before deployment.
- Feedback is saved in the database and can be viewed by zone. Student notifications currently display in the app; actual phone SMS/push delivery is **not configured**. Integrate and verify an SMS/push provider before promising phone notifications.
- Zone/team assignment is editable in Assign Students. Assignments appear in the student academic/profile details.
- The API is a development starter, not production-secure: add authenticated role/zone authorization, audit logs, secure file storage, backups, HTTPS, consent and privacy review before using real student data. Demo login and OTP credentials must be replaced.

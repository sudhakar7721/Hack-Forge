# Maatram Student Lifecycle Platform — cleaned & repaired

This package contains the original frontend and backend, with the source files retained and the broken field mappings repaired. Generated dependency/cache folders and the private `.env` file are not included.

## Requirements

- Windows 10/11
- Python 3.12 recommended
- Node.js 20+ and npm
- MySQL Server 8.x (or another compatible MySQL version)

## 1. Prepare MySQL

Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE IF NOT EXISTS maatram_student_lifecycle
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. Start the backend

Open a terminal in `backend`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env` and replace `YOUR_MYSQL_PASSWORD` with your MySQL password. Keep this private; never share the `.env` file.

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

The API documentation is at `http://127.0.0.1:8000/docs` and health check at `http://127.0.0.1:8000/api/health`.

The app upgrades existing tables additively on startup. It does not intentionally drop tables or records. Back up your database before first startup against an existing database.

## 3. Start the frontend

Open a second terminal in `frontend`:

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`.

## Demo login

Choose the matching role in the login page:

| Role | Username | Password |
|---|---|---|
| Student | `student` | `student-50` |
| Alumni | `alumni` | `alumni-100` |
| Admin | `admin` | `admin-5` |
| Core Member | `core` | `core-12` |

The demo seed also includes zone admins, more core-member accounts, and student accounts. Demo passwords and the fixed OTP are for local testing only. Real SMS OTP, production authentication, and authorization protections must be integrated before deployment.

## SQLite-to-MySQL migration (optional)

If you have a legacy SQLite database and want to copy it into an empty MySQL target, configure `.env` first and run this from the backend folder:

```powershell
python migrate_sqlite_to_mysql.py path\to\maatram.db
```

The script refuses to copy into target tables that already contain data.

## Modules retained

- Role-based login (Student, Alumni, Admin, Core Members)
- Student profiles and directory
- Application / admission details and verification notes
- Academic records, semester marks, course certificates, internship, skills, projects, resume and profile links
- Volunteering (PV, TV, school visits and other activities)
- Alumni career directory and placement fields
- Zone assignment
- Zone information, notices and attachments
- Student feedback
- Dashboard, reports, activities and event-log placeholder pages

Some pages are existing demonstration/placeholder modules and are not described as production-complete.


## Alumni Association & Projects (new)

The Alumni workspace now includes:

- **My Alumni Profile** — signed-in account details plus linked student education/career information.
- **Alumni Association** — alumni can publish skills, project interests, availability status, start date and contact details.
- **Alumni Projects** — submit Palm Tree Plantation, School Visit, Koodukal (Sittu Kuruvi Project), Technical Team and Other Contribution activities. Activity records support date, time, place, participant/seed/unit count, GPS latitude/longitude and an optional photo (up to 3 MB).
- **Admin – Alumni Association Management** — a consolidated view of alumni career records, availability posts and project contributions.

New API routes:

- `GET/POST /api/alumni/availability`
- `GET/POST /api/alumni/projects`

The new `alumni_availability` and `alumni_projects` tables are created automatically at backend startup. Existing tables and records are not dropped. The new project and availability records are stored in the configured MySQL database.

**Important deployment note:** This starter's existing API does not enforce per-record authorization. Before public/production deployment, add authenticated ownership checks, admin-only access controls, file storage controls and consent/privacy rules. The GPS feature requires browser location permission and HTTPS outside localhost.

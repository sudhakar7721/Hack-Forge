from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from passlib.context import CryptContext
from .database import Base, engine, get_db, SessionLocal
from .models import User, Student, Alumni, ZoneInformation, StudentFeedback
from .schemas import LoginIn, StudentIn, AlumniIn

app = FastAPI(title="Maatram - Student Lifecycle API", version="1.0.0",
              description="Role-based student lifecycle and alumni management starter API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
Base.metadata.create_all(bind=engine)
# Lightweight migration for databases created before blood_group was added.
with engine.begin() as conn:
    columns = [row[1] for row in conn.execute(text("PRAGMA table_info(students)"))]
    if "blood_group" not in columns:
        conn.execute(text("ALTER TABLE students ADD COLUMN blood_group VARCHAR(10) NOT NULL DEFAULT ''"))

# Demo credentials are for local testing only. Do not use these passwords in production.
# 40 students are split evenly across four zones. Four zone admins each own exactly one zone;
# the fifth admin is a system-wide admin. Ten core-team accounts are provided.
def credential_sets():
    admins = [("admin", "admin-5", "System Admin", "9000000005", "")]
    for zone in range(1, 5):
        admins.append((f"admin{zone:02d}", f"MaatramAdm{zone:02d}!", f"Zone {zone} Admin", f"90000001{zone:02d}", f"Zone {zone}"))
    cores = [("core", "core-12", "Core Team Member 01", "9000000012")]
    for i in range(2, 11):
        cores.append((f"core{i:02d}", f"MaatramCore{i:02d}!", f"Core Team Member {i:02d}", f"90000002{i:02d}"))
    students = [("student", "student-50", "Demo Student", "9000000050", 1)]
    for i in range(2, 41):
        students.append((f"student{i:02d}", f"MaatramStu{i:02d}!", f"Student {i:02d}", f"9000001{i:03d}", i))
    return admins, cores, students

ADMINS, CORES, STUDENTS = credential_sets()

def get_or_create_user(db, username, password, role, name, phone):
    user = db.scalar(select(User).where(User.username == username))
    if not user:
        user = User(username=username, password_hash=pwd.hash(password), role=role,
                    display_name=name, phone=phone, active=True)
        db.add(user)
        db.flush()
    else:
        # Ensure all bundled demo accounts can sign in after upgrading an existing local DB.
        user.role = role
        user.display_name = name
        user.phone = phone
        user.active = True
        if not user.password_hash or not pwd.verify(password, user.password_hash):
            user.password_hash = pwd.hash(password)
    return user

def seed():
    db = SessionLocal()
    try:
        get_or_create_user(db, "alumni", "alumni-100", "alumni", "Demo Alumni", "9000000100")
        for username, password, name, phone, _zone in ADMINS:
            get_or_create_user(db, username, password, "admin", name, phone)
        for username, password, name, phone in CORES:
            get_or_create_user(db, username, password, "core", name, phone)
        student_users = {}
        for username, password, name, phone, number in STUDENTS:
            student_users[number] = get_or_create_user(db, username, password, "student", name, phone)
        db.flush()

        # Make exactly 40 sample student profiles, with 10 students assigned to each zone.
        # Existing records are retained and connected to the matching login where possible.
        for number in range(1, 41):
            user = student_users[number]
            student = db.scalar(select(Student).where(Student.user_id == user.id))
            if student is None and number == 1:
                student = db.scalar(select(Student).where(Student.application_number == "MTR-2026-0001"))
                if student and student.user_id is None:
                    student.user_id = user.id
            zone = ((number - 1) // 10) + 1
            zone_admin = next(a[2] for a in ADMINS if a[4] == f"Zone {zone}")
            if student is None:
                student = Student(user_id=user.id)
                db.add(student)
            student.user_id = user.id
            student.full_name = user.display_name
            student.age = 18 + (number % 4)
            student.dob = f"200{number % 6 + 2}-{(number % 12)+1:02d}-{(number % 27)+1:02d}"
            student.phone = user.phone
            student.email = f"student{number:02d}@example.test"
            student.parent_name = f"Parent of {user.display_name}"
            student.address = f"Sample Street, Zone {zone}, Chennai, Tamil Nadu"
            student.blood_group = ["A+", "B+", "O+", "AB+", "A-", "O-"][number % 6]
            student.previous_school = f"Zone {zone} Higher Secondary School"
            student.tenth_mark = float(400 + (number % 90))
            student.tenth_percentage = round(75 + (number % 24) * 0.9, 1)
            student.twelfth_mark = float(430 + (number % 120))
            student.twelfth_percentage = round(78 + (number % 21) * 0.9, 1)
            student.higher_secondary_group = ["Computer Science", "Biology-Maths", "Commerce", "Arts"][number % 4]
            student.applied_domain = "Arts & Science" if number % 2 else "Engineering"
            student.application_number = f"MTR-2026-{number:04d}"
            student.application_status = "Approved" if number % 3 else "Waiting List"
            student.college = "Demo Arts & Science College" if student.application_status == "Approved" else ""
            student.course = "B.Sc. Computer Science" if student.application_status == "Approved" else ""
            student.academic_year = "2026-27"
            student.residence_type = "Day Scholar"
            student.mentor_name = f"Mentor Zone {zone}"
            student.anchor_name = f"Anchor Zone {zone}"
            student.zone_incharge = zone_admin
            student.academic_details = f"Sample semester CGPA: {7.2 + (number % 15) / 10:.1f}/10; status: Demo data"
            student.self_learning_details = "Python basics; communication skills (sample)"
            student.activities = "Orientation and peer learning (sample)"
            student.pv_volunteering = f"PV completed: {number % 4}; sample records"
            student.tv_volunteering = f"TV completed: {number % 3}; sample records"
            student.school_visits = f"School visits: {number % 5}; sample records"
        # Remove only the old duplicate sample applicant, if present.
        db.query(Student).filter(Student.application_number == "MTR-2026-0002", Student.user_id.is_(None)).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()
# Additive SQLite migration for expanded profile fields; existing student data is retained.
with engine.begin() as conn:
    existing = {row[1] for row in conn.execute(text("PRAGMA table_info(students)"))}
    additions = {
        "registration_number":"VARCHAR(80) NOT NULL DEFAULT ''", "department":"VARCHAR(150) NOT NULL DEFAULT ''",
        "passed_out_year":"VARCHAR(20) NOT NULL DEFAULT ''", "semester_details":"TEXT NOT NULL DEFAULT '[]'",
        "current_cgpa":"VARCHAR(20) NOT NULL DEFAULT ''", "completed_courses":"TEXT NOT NULL DEFAULT '[]'", "certificate_files":"TEXT NOT NULL DEFAULT '[]'",
        "internship_details":"TEXT NOT NULL DEFAULT ''", "skills":"TEXT NOT NULL DEFAULT ''",
        "resume_url":"TEXT NOT NULL DEFAULT ''", "project_details":"TEXT NOT NULL DEFAULT ''",
        "linkedin_url":"TEXT NOT NULL DEFAULT ''", "github_url":"TEXT NOT NULL DEFAULT ''",
        "volunteering_details":"TEXT NOT NULL DEFAULT '[]'", "zone_name":"VARCHAR(100) NOT NULL DEFAULT ''",
        "spoc_name":"VARCHAR(150) NOT NULL DEFAULT ''"
    }
    for col, definition in additions.items():
        if col not in existing:
            conn.execute(text(f"ALTER TABLE students ADD COLUMN {col} {definition}"))

seed()

def student_dict(s):
    return {c.name: getattr(s, c.name) for c in s.__table__.columns}
def alumni_dict(a):
    return {c.name: getattr(a, c.name) for c in a.__table__.columns}

@app.get("/api/health")
def health():
    return {"status":"ok","service":"Maatram - Student Lifecycle API"}

@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username, User.active == True))
    if not user or not pwd.verify(data.password, user.password_hash):
        raise HTTPException(401, "Username or password is incorrect")
    if user.role != data.role:
        raise HTTPException(403, "Choose the correct login type for this account")
    return {"id":user.id,"username":user.username,"role":user.role,"display_name":user.display_name,
            "phone":user.phone,"message":"Demo login successful"}

@app.post("/api/auth/forgot-password")
def forgot_password(payload: dict):
    phone = str(payload.get("phone","")).strip()
    if len(phone) < 8:
        raise HTTPException(400, "Enter a valid phone number")
    # Demo only: real SMS integration must be configured before production.
    return {"message":"Demo OTP generated. SMS is not configured.","demo_otp":"123456"}

@app.post("/api/auth/reset-password")
def reset_password(payload: dict, db: Session = Depends(get_db)):
    username = str(payload.get("username","")).strip()
    otp = str(payload.get("otp","")).strip()
    new_password = str(payload.get("new_password",""))
    if otp != "123456":
        raise HTTPException(400, "Invalid demo OTP")
    if len(new_password) < 8:
        raise HTTPException(400, "New password must be at least 8 characters")
    user = db.scalar(select(User).where(User.username == username))
    if not user: raise HTTPException(404, "Username not found")
    user.password_hash = pwd.hash(new_password)
    db.commit()
    return {"message":"Password reset. Please sign in again."}

@app.get("/api/dashboard/{role}")
def dashboard(role: str, db: Session = Depends(get_db)):
    role = role.lower()
    if role not in {"student","alumni","admin","core"}: raise HTTPException(404,"Unknown role")
    return {"role":role, "students":db.scalar(select(func.count(Student.id))) or 0,
            "approved":db.scalar(select(func.count(Student.id)).where(Student.application_status=="Approved")) or 0,
            "waiting":db.scalar(select(func.count(Student.id)).where(Student.application_status=="Waiting List")) or 0,
            "alumni":db.scalar(select(func.count(Alumni.id))) or 0,
            "placed_alumni":db.scalar(select(func.count(Alumni.id)).where(Alumni.placed==True)) or 0}

@app.get("/api/students")
def list_students(q: str = Query(default=""), db: Session = Depends(get_db)):
    stmt = select(Student).order_by(Student.id.desc())
    records = db.scalars(stmt).all()
    if q:
        ql=q.lower()
        records=[s for s in records if ql in s.full_name.lower() or ql in s.application_number.lower() or ql in s.email.lower()]
    return [student_dict(s) for s in records]

@app.get("/api/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    s=db.get(Student,student_id)
    if not s: raise HTTPException(404,"Student not found")
    return student_dict(s)

@app.post("/api/students")
def create_student(data: StudentIn, db: Session = Depends(get_db)):
    fields=data.model_dump()
    if not fields["application_number"]:
        fields["application_number"] = f"MTR-{2026}-{(db.scalar(select(func.count(Student.id))) or 0)+1:04d}"
    if db.scalar(select(Student).where(Student.application_number==fields["application_number"])):
        raise HTTPException(409,"Application number already exists")
    s=Student(**fields); db.add(s); db.commit(); db.refresh(s)
    return student_dict(s)

@app.put("/api/students/{student_id}")
def update_student(student_id: int, data: StudentIn, db: Session = Depends(get_db)):
    s=db.get(Student,student_id)
    if not s: raise HTTPException(404,"Student not found")
    for k,v in data.model_dump().items(): setattr(s,k,v)
    db.commit(); db.refresh(s)
    return student_dict(s)

@app.get("/api/alumni")
def list_alumni(db: Session = Depends(get_db)):
    return [alumni_dict(a) for a in db.scalars(select(Alumni).order_by(Alumni.id.desc())).all()]

@app.post("/api/alumni")
def create_alumni(data: AlumniIn, db: Session = Depends(get_db)):
    a=Alumni(**data.model_dump()); db.add(a); db.commit(); db.refresh(a)
    return alumni_dict(a)

@app.put("/api/alumni/{alumni_id}")
def update_alumni(alumni_id: int, data: AlumniIn, db: Session = Depends(get_db)):
    a=db.get(Alumni,alumni_id)
    if not a: raise HTTPException(404,"Alumni not found")
    for k,v in data.model_dump().items(): setattr(a,k,v)
    db.commit(); db.refresh(a)
    return alumni_dict(a)


@app.get("/api/informations")
def get_informations(zone: str = Query(default=""), db: Session = Depends(get_db)):
    stmt = select(ZoneInformation).order_by(ZoneInformation.created_at.desc())
    if zone: stmt = stmt.where(ZoneInformation.zone_name == zone)
    return [{c.name:getattr(x,c.name) for c in x.__table__.columns} for x in db.scalars(stmt).all()]

@app.post("/api/informations")
def post_information(payload: dict, db: Session = Depends(get_db)):
    required = str(payload.get("title","")).strip()
    if not required: raise HTTPException(400,"Information title is required")
    item = ZoneInformation(zone_name=str(payload.get("zone_name","")).strip(),
        sender_name=str(payload.get("sender_name","")), sender_role=str(payload.get("sender_role","")),
        title=required, message=str(payload.get("message","")), link=str(payload.get("link","")),
        attachment_name=str(payload.get("attachment_name","")), attachment_data=str(payload.get("attachment_data","")))
    db.add(item); db.commit(); db.refresh(item)
    return {c.name:getattr(item,c.name) for c in item.__table__.columns}

@app.get("/api/feedback")
def get_feedback(zone: str = Query(default=""), db: Session = Depends(get_db)):
    stmt = select(StudentFeedback).order_by(StudentFeedback.created_at.desc())
    if zone: stmt = stmt.where(StudentFeedback.zone_name == zone)
    return [{c.name:getattr(x,c.name) for c in x.__table__.columns} for x in db.scalars(stmt).all()]

@app.post("/api/feedback")
def post_feedback(payload: dict, db: Session = Depends(get_db)):
    message = str(payload.get("message","")).strip()
    student_id = payload.get("student_id")
    if not message or not student_id: raise HTTPException(400,"Feedback message and student ID are required")
    student = db.get(Student, int(student_id))
    if not student: raise HTTPException(404,"Student not found")
    item = StudentFeedback(student_id=student.id, zone_name=student.zone_name or student.zone_incharge,
        student_name=student.full_name, message=message)
    db.add(item); db.commit(); db.refresh(item)
    return {"id":item.id,"message":"Feedback sent to your zone team"}

@app.put("/api/students/{student_id}/assignment")
def assign_student(student_id: int, payload: dict, db: Session = Depends(get_db)):
    student=db.get(Student,student_id)
    if not student: raise HTTPException(404,"Student not found")
    for key in ["zone_name","zone_incharge","college","department","anchor_name","mentor_name","spoc_name"]:
        if key in payload: setattr(student,key,str(payload[key] or ""))
    db.commit(); db.refresh(student)
    return student_dict(student)

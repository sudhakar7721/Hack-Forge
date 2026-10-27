from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from passlib.context import CryptContext
from .database import Base, engine, get_db, SessionLocal
from .models import User, Student, Alumni
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

DEMO_USERS = [
    ("student", "student-50", "student", "Demo Student", "9000000050"),
    ("alumni", "alumni-100", "alumni", "Demo Alumni", "9000000100"),
    ("admin", "admin-5", "admin", "System Admin", "9000000005"),
    ("core", "core-12", "core", "Core Team Member", "9000000012"),
]
def seed():
    db = SessionLocal()
    try:
        for username, password, role, name, phone in DEMO_USERS:
            user = db.scalar(select(User).where(User.username == username))
            if not user:
                db.add(User(username=username, password_hash=pwd.hash(password), role=role, display_name=name, phone=phone))
        db.commit()
        # Keep the starter demo to one unified student record, not a separate sample applicant.
        db.query(Student).filter(Student.application_number == "MTR-2026-0002").delete(synchronize_session=False)
        if db.scalar(select(func.count(Student.id))) == 0:
            db.add(Student(full_name="Demo Student", phone="9000000050", email="student@example.test",
                           parent_name="Demo Parent", application_number="MTR-2026-0001",
                           applied_domain="Arts & Science", application_status="Approved",
                           college="Demo Arts & Science College", course="B.Sc. Computer Science",
                           academic_year="2026-27", residence_type="Day Scholar", mentor_name="Demo Mentor",
                           anchor_name="Demo Anchor", zone_incharge="Zone 1", tenth_percentage=88.0,
                           twelfth_percentage=91.0, previous_school="Demo Higher Secondary School",
                           blood_group="Not added"))
        db.commit()
    finally:
        db.close()
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

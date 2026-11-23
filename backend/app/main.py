from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text, inspect, Text
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from .database import Base, engine, get_db, SessionLocal
from .models import User, Student, Alumni, ZoneInformation, StudentFeedback
from .schemas import LoginIn, StudentIn, AlumniIn

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Existing databases are upgraded additively: no table or record is dropped.
def migrate_schema():
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    aliases = {
        "students": {
            "dob": "date_of_birth", "previous_school": "school_name",
            "tenth_mark": "tenth_marks", "twelfth_mark": "twelfth_marks",
            "applied_domain": "domain", "college": "college_name",
            "application_status": "admission_status", "academic_details": "academic_performance",
            "self_learning_details": "self_learning", "zone_name": "zone", "fees_details": "fees",
        },
        "alumni": {
            "current_company": "company_name", "job_title": "job_role", "work_location": "current_location",
        },
        "zone_information": {"message": "description", "sender_name": "zone_incharge"},
        "student_feedback": {"message": "feedback"},
    }

    # Add any model columns missing from a previously-created table.
    added_columns = {}
    preparer = engine.dialect.identifier_preparer
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in table_names:
                continue
            existing = {c["name"] for c in inspector.get_columns(table.name)}
            added_columns[table.name] = set()
            for column in table.columns:
                if column.name in existing:
                    continue
                col_type = column.type.compile(dialect=engine.dialect)
                default_sql = ""
                if column.server_default is not None:
                    default_sql = f" DEFAULT {column.server_default.arg}"
                elif column.default is not None and not callable(column.default.arg) and not isinstance(column.type, Text):
                    value = column.default.arg
                    if isinstance(value, str):
                        value = "'" + value.replace("'", "''") + "'"
                    elif isinstance(value, bool):
                        value = "1" if value else "0"
                    default_sql = f" DEFAULT {value}"
                table_sql = preparer.quote(table.name)
                column_sql = preparer.quote(column.name)
                conn.execute(text(f"ALTER TABLE {table_sql} ADD COLUMN {column_sql} {col_type}{default_sql}"))
                existing.add(column.name)
                added_columns[table.name].add(column.name)

    # Transfer values from the legacy column names into the current UI/API fields.
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table_name, mapping in aliases.items():
            if table_name not in inspector.get_table_names():
                continue
            existing = {c["name"] for c in inspector.get_columns(table_name)}
            table_sql = preparer.quote(table_name)
            for target, source in mapping.items():
                if target in existing and source in existing:
                    target_sql, source_sql = preparer.quote(target), preparer.quote(source)
                    if target in added_columns.get(table_name, set()):
                        where_sql = f"{source_sql} IS NOT NULL"
                    else:
                        where_sql = f"({target_sql} IS NULL OR {target_sql} = '') AND {source_sql} IS NOT NULL"
                    conn.execute(text(f"UPDATE {table_sql} SET {target_sql} = {source_sql} WHERE {where_sql}"))
        # Translate older application statuses into labels expected by the UI.
        if "students" in inspector.get_table_names():
            conn.execute(text("UPDATE students SET application_status='Waiting List' WHERE lower(application_status)='pending'"))
            conn.execute(text("UPDATE students SET application_status='Approved' WHERE lower(application_status)='approved'"))
            conn.execute(text("UPDATE students SET application_status='Declined' WHERE lower(application_status) IN ('rejected','declined')"))
        if "alumni" in inspector.get_table_names() and "placement_status" in {c["name"] for c in inspector.get_columns("alumni")}:
            conn.execute(text("UPDATE alumni SET placed=1 WHERE lower(placement_status) IN ('placed','yes','true')"))
            conn.execute(text("UPDATE alumni SET placed=0 WHERE lower(placement_status) IN ('not_placed','not placed','no','false')"))
        if "student_feedback" in inspector.get_table_names() and "student_name" in {c["name"] for c in inspector.get_columns("student_feedback")}:
            conn.execute(text("UPDATE student_feedback SET student_name=(SELECT full_name FROM students WHERE students.id=student_feedback.student_id) WHERE student_name IS NULL OR student_name=''"))


def safe_verify(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return pwd.verify(password, hashed)
    except (ValueError, TypeError):
        return False


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
        user.role, user.display_name, user.phone, user.active = role, name, phone, True
        if not safe_verify(password, user.password_hash):
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

        for number in range(1, 41):
            user = student_users[number]
            student = db.scalar(select(Student).where(Student.user_id == user.id))
            if student is None:
                student = db.scalar(select(Student).where(Student.application_number == f"MTR-2026-{number:04d}"))
                if student and student.user_id is None:
                    student.user_id = user.id
            zone = ((number - 1) // 10) + 1
            zone_admin = next(a[2] for a in ADMINS if a[4] == f"Zone {zone}")
            if student is None:
                status = "Approved" if number % 3 else "Waiting List"
                student = Student(
                    user_id=user.id, full_name=user.display_name, age=18 + number % 4,
                    dob=f"200{number % 6 + 2}-{(number % 12)+1:02d}-{(number % 27)+1:02d}",
                    phone=user.phone, email=f"student{number:02d}@example.test",
                    parent_name=f"Parent of {user.display_name}", address=f"Sample Street, Zone {zone}, Chennai, Tamil Nadu",
                    blood_group=["A+", "B+", "O+", "AB+", "A-", "O-"][number % 6],
                    previous_school=f"Zone {zone} Higher Secondary School",
                    tenth_mark=float(400 + number % 90), tenth_percentage=round(75 + (number % 24) * .9, 1),
                    twelfth_mark=float(430 + number % 120), twelfth_percentage=round(78 + (number % 21) * .9, 1),
                    higher_secondary_group=["Computer Science", "Biology-Maths", "Commerce", "Arts"][number % 4],
                    applied_domain="Arts & Science" if number % 2 else "Engineering",
                    application_number=f"MTR-2026-{number:04d}", application_status=status, admission_status=status.lower().replace(" ", "_"),
                    college="Demo Arts & Science College" if status == "Approved" else "",
                    course="B.Sc. Computer Science" if status == "Approved" else "", academic_year="2026-27",
                    residence_type="Day Scholar", mentor_name=f"Mentor Zone {zone}", anchor_name=f"Anchor Zone {zone}",
                    zone_incharge=zone_admin, zone_name=f"Zone {zone}", zone=f"Zone {zone}",
                    school_name=f"Zone {zone} Higher Secondary School",
                    tenth_marks=float(400 + number % 90), twelfth_marks=float(430 + number % 120),
                    domain="Arts & Science" if number % 2 else "Engineering",
                    college_name="Demo Arts & Science College" if status == "Approved" else "",
                    academic_performance=f"Sample semester CGPA: {7.2 + (number % 15) / 10:.1f}/10; status: Demo data",
                    self_learning="Python basics; communication skills (sample)",
                    academic_details=f"Sample semester CGPA: {7.2 + (number % 15) / 10:.1f}/10; status: Demo data",
                    self_learning_details="Python basics; communication skills (sample)",
                    activities="Orientation and peer learning (sample)",
                    pv_volunteering=f"PV completed: {number % 4}; sample records",
                    tv_volunteering=f"TV completed: {number % 3}; sample records",
                    school_visits=f"School visits: {number % 5}; sample records",
                    certificate_files="[]",
                )
                db.add(student)
            elif student.user_id is None:
                student.user_id = user.id
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_schema()
    seed()
    yield


app = FastAPI(title="Maatram - Student Lifecycle API", version="1.1.0",
              description="Role-based student lifecycle and alumni management API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


def student_dict(student: Student):
    return {column.name: getattr(student, column.name) for column in student.__table__.columns}


def alumni_dict(alumni: Alumni):
    return {column.name: getattr(alumni, column.name) for column in alumni.__table__.columns}


def info_dict(item: ZoneInformation):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


def feedback_dict(item: StudentFeedback):
    return {column.name: getattr(item, column.name) for column in item.__table__.columns}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Maatram - Student Lifecycle API"}


@app.post("/api/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == data.username, User.active.is_(True)))
    if not user or not safe_verify(data.password, user.password_hash):
        raise HTTPException(401, "Username or password is incorrect")
    if user.role != data.role:
        raise HTTPException(403, "Choose the correct login type for this account")
    return {"id": user.id, "username": user.username, "role": user.role, "display_name": user.display_name,
            "phone": user.phone, "message": "Demo login successful"}


@app.post("/api/auth/forgot-password")
def forgot_password(payload: dict, db: Session = Depends(get_db)):
    phone = str(payload.get("phone", "")).strip()
    if len(phone) < 8:
        raise HTTPException(400, "Enter a valid phone number")
    user = db.scalar(select(User).where(User.phone == phone, User.active.is_(True)))
    if not user:
        raise HTTPException(404, "No active account is linked to this phone number")
    # Demo-only OTP. Replace with a real SMS provider before production deployment.
    return {"message": "Demo OTP generated. SMS is not configured.", "demo_otp": "123456"}


@app.post("/api/auth/reset-password")
def reset_password(payload: dict, db: Session = Depends(get_db)):
    username = str(payload.get("username", "")).strip()
    otp = str(payload.get("otp", "")).strip()
    phone = str(payload.get("phone", "")).strip()
    new_password = str(payload.get("new_password", ""))
    if otp != "123456":
        raise HTTPException(400, "Invalid demo OTP")
    if len(new_password) < 8:
        raise HTTPException(400, "New password must be at least 8 characters")
    user = db.scalar(select(User).where(User.username == username, User.active.is_(True)))
    if not user:
        raise HTTPException(404, "Username not found")
    if not phone or user.phone != phone:
        raise HTTPException(403, "Phone number does not match this account")
    user.password_hash = pwd.hash(new_password)
    db.commit()
    return {"message": "Password reset. Please sign in again."}


@app.get("/api/dashboard/{role}")
def dashboard(role: str, db: Session = Depends(get_db)):
    role = role.lower()
    if role not in {"student", "alumni", "admin", "core"}:
        raise HTTPException(404, "Unknown role")
    return {
        "role": role,
        "students": db.scalar(select(func.count(Student.id))) or 0,
        "approved": db.scalar(select(func.count(Student.id)).where(Student.application_status == "Approved")) or 0,
        "waiting": db.scalar(select(func.count(Student.id)).where(Student.application_status == "Waiting List")) or 0,
        "alumni": db.scalar(select(func.count(Alumni.id))) or 0,
        "placed_alumni": db.scalar(select(func.count(Alumni.id)).where(Alumni.placed.is_(True))) or 0,
    }


@app.get("/api/students")
def list_students(q: str = Query(default=""), db: Session = Depends(get_db)):
    records = db.scalars(select(Student).order_by(Student.id.desc())).all()
    if q.strip():
        ql = q.strip().lower()
        records = [s for s in records if any(ql in (value or "").lower() for value in (s.full_name, s.application_number, s.email, s.registration_number, s.college, s.department))]
    return [student_dict(s) for s in records]


@app.get("/api/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    return student_dict(student)


def student_payload(data: StudentIn) -> dict[str, Any]:
    values = data.model_dump()
    for key in values:
        if isinstance(values[key], str) and values[key] == "":
            values[key] = None
    values["full_name"] = data.full_name.strip()
    values["application_status"] = data.application_status or "Waiting List"
    values["admission_status"] = values["application_status"].lower().replace(" ", "_")
    values["certificate_files"] = data.certificate_files or "[]"
    # Keep the previous schema's columns populated for compatibility with older deployments.
    legacy_map = {
        "dob": "date_of_birth", "previous_school": "school_name",
        "tenth_mark": "tenth_marks", "twelfth_mark": "twelfth_marks",
        "applied_domain": "domain", "college": "college_name",
        "academic_details": "academic_performance", "self_learning_details": "self_learning",
        "zone_name": "zone",
    }
    for current, legacy in legacy_map.items():
        values[legacy] = values.get(current)
    fees_value = values.get("fees_details")
    try:
        values["fees"] = float(fees_value) if fees_value not in (None, "") else None
    except (TypeError, ValueError):
        values["fees"] = None
    return values


@app.post("/api/students")
def create_student(data: StudentIn, db: Session = Depends(get_db)):
    fields = student_payload(data)
    if not fields["full_name"]:
        raise HTTPException(400, "Student name is required")
    if not fields["application_number"]:
        next_number = (db.scalar(select(func.count(Student.id))) or 0) + 1
        while db.scalar(select(Student.id).where(Student.application_number == f"MTR-2026-{next_number:04d}")):
            next_number += 1
        fields["application_number"] = f"MTR-2026-{next_number:04d}"
    if db.scalar(select(Student.id).where(Student.application_number == fields["application_number"])):
        raise HTTPException(409, "Application number already exists")
    student = Student(**fields)
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Student record conflicts with an existing application number")
    return student_dict(student)


@app.put("/api/students/{student_id}")
def update_student(student_id: int, data: StudentIn, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    fields = student_payload(data)
    for key, value in fields.items():
        setattr(student, key, value)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Application number is already assigned to another student")
    return student_dict(student)


@app.get("/api/alumni")
def list_alumni(db: Session = Depends(get_db)):
    return [alumni_dict(a) for a in db.scalars(select(Alumni).order_by(Alumni.id.desc())).all()]


@app.post("/api/alumni")
def create_alumni(data: AlumniIn, db: Session = Depends(get_db)):
    fields = data.model_dump()
    if not fields["student_id"]:
        raise HTTPException(400, "Link an alumni record to a student ID")
    linked_student = db.get(Student, fields["student_id"])
    if not linked_student:
        raise HTTPException(404, "Linked student not found")
    if not fields["full_name"].strip():
        fields["full_name"] = linked_student.full_name
    fields["placement_status"] = "placed" if fields["placed"] else "not_placed"
    fields["company_name"] = fields["current_company"] or None
    fields["job_role"] = fields["job_title"] or None
    fields["current_location"] = fields["work_location"] or None
    alumni = Alumni(**fields)
    db.add(alumni)
    try:
        db.commit()
        db.refresh(alumni)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This student is already linked to an alumni record")
    return alumni_dict(alumni)


@app.put("/api/alumni/{alumni_id}")
def update_alumni(alumni_id: int, data: AlumniIn, db: Session = Depends(get_db)):
    alumni = db.get(Alumni, alumni_id)
    if not alumni:
        raise HTTPException(404, "Alumni not found")
    fields = data.model_dump()
    if not fields["student_id"]:
        raise HTTPException(400, "Link an alumni record to a student ID")
    linked_student = db.get(Student, fields["student_id"])
    if not linked_student:
        raise HTTPException(404, "Linked student not found")
    if not fields["full_name"].strip():
        fields["full_name"] = linked_student.full_name
    fields["placement_status"] = "placed" if fields["placed"] else "not_placed"
    fields["company_name"] = fields["current_company"] or None
    fields["job_role"] = fields["job_title"] or None
    fields["current_location"] = fields["work_location"] or None
    for key, value in fields.items():
        setattr(alumni, key, value)
    try:
        db.commit()
        db.refresh(alumni)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "This student is already linked to another alumni record")
    return alumni_dict(alumni)


@app.get("/api/informations")
def get_informations(zone: str = Query(default=""), db: Session = Depends(get_db)):
    stmt = select(ZoneInformation).order_by(ZoneInformation.created_at.desc())
    if zone.strip():
        stmt = stmt.where((ZoneInformation.zone_name == zone) | (ZoneInformation.zone_name == ""))
    return [info_dict(x) for x in db.scalars(stmt).all()]


@app.post("/api/informations")
def post_information(payload: dict, db: Session = Depends(get_db)):
    title = str(payload.get("title", "")).strip()
    if not title:
        raise HTTPException(400, "Information title is required")
    item = ZoneInformation(
        zone_name=str(payload.get("zone_name", "")).strip(),
        sender_name=str(payload.get("sender_name", "")), sender_role=str(payload.get("sender_role", "")),
        title=title, message=str(payload.get("message", "")), link=str(payload.get("link", "")),
        attachment_name=str(payload.get("attachment_name", "")), attachment_data=str(payload.get("attachment_data", "")),
        zone_incharge=str(payload.get("sender_name", "")), description=str(payload.get("message", "")), active=True,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return info_dict(item)


@app.get("/api/feedback")
def get_feedback(zone: str = Query(default=""), db: Session = Depends(get_db)):
    stmt = select(StudentFeedback).order_by(StudentFeedback.created_at.desc())
    if zone.strip():
        stmt = stmt.where(StudentFeedback.zone_name == zone)
    return [feedback_dict(x) for x in db.scalars(stmt).all()]


@app.post("/api/feedback")
def post_feedback(payload: dict, db: Session = Depends(get_db)):
    message = str(payload.get("message", "")).strip()
    student_id = payload.get("student_id")
    if not message or not student_id:
        raise HTTPException(400, "Feedback message and student ID are required")
    try:
        student = db.get(Student, int(student_id))
    except (TypeError, ValueError):
        student = None
    if not student:
        raise HTTPException(404, "Student not found")
    item = StudentFeedback(student_id=student.id, student_name=student.full_name,
                           zone_name=student.zone_name or student.zone_incharge or "", message=message,
                           feedback=message, feedback_type="general", submitted_by=student.full_name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "message": "Feedback sent to your zone team"}


@app.put("/api/students/{student_id}/assignment")
def assign_student(student_id: int, payload: dict, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(404, "Student not found")
    for key in ["zone_name", "zone_incharge", "college", "department", "anchor_name", "mentor_name", "spoc_name"]:
        if key in payload:
            value = str(payload[key] or "")
            setattr(student, key, value)
            if key == "zone_name":
                student.zone = value
    db.commit()
    db.refresh(student)
    return student_dict(student)

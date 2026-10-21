import os, re, uuid, unicodedata
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from .database import Base, engine, get_db
from .models import Cycle, Application, Student, LifecycleEvent, CareerRecord, UploadRecord, ApplicationAudit, utcnow
from .schemas import CycleIn, ApplicationIn, BulkReviewIn, EventIn, CareerIn, PresignIn

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Maatram Student Lifecycle Platform", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

ALLOWED_TYPES = set(os.getenv("ALLOWED_CONTENT_TYPES", "application/pdf,image/jpeg,image/png").split(","))
MAX_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
ALIASES = {"google inc": "google", "google llc": "google", "tcs": "tata consultancy services", " tata consultancy services ": "tata consultancy services", "amazon web services": "amazon"}

def company_key(name: str) -> str:
    raw = unicodedata.normalize("NFKC", name).lower().strip()
    raw = re.sub(r"[.,'’()]", "", raw)
    raw = re.sub(r"\s+", " ", raw)
    return ALIASES.get(raw, raw).strip()

def event_out(e):
    return {"id": e.id, "event_id": e.event_id, "student_id": e.student_id, "event_type": e.event_type, "occurred_at": e.occurred_at.isoformat(), "payload": e.payload}

def application_out(a):
    return {"id": a.id, "cycle_id": a.cycle_id, "applicant_name": a.applicant_name, "email": a.email, "phone": a.phone, "education": a.education, "statement": a.statement, "status": a.status, "rejection_reason": a.rejection_reason, "student_id": a.student_id, "created_at": a.created_at.isoformat()}

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "maatram-student-lifecycle"}

@app.get("/api/cycles")
def list_cycles(db: Session = Depends(get_db)):
    return [{"id": c.id, "name": c.name, "year": c.year, "active": c.active} for c in db.scalars(select(Cycle).order_by(Cycle.year.desc())).all()]

@app.post("/api/cycles")
def create_cycle(data: CycleIn, db: Session = Depends(get_db)):
    if db.scalar(select(Cycle).where(Cycle.name == data.name)):
        raise HTTPException(409, "A cycle with this name already exists")
    c = Cycle(**data.model_dump())
    db.add(c); db.commit(); db.refresh(c)
    return {"id": c.id, "name": c.name, "year": c.year, "active": c.active}

@app.get("/api/applications")
def list_applications(cycle_id: int | None = None, status: str | None = None, db: Session = Depends(get_db)):
    q = select(Application)
    if cycle_id is not None: q = q.where(Application.cycle_id == cycle_id)
    if status: q = q.where(Application.status == status)
    return [application_out(a) for a in db.scalars(q.order_by(Application.created_at.desc())).all()]

@app.post("/api/applications")
def create_application(data: ApplicationIn, db: Session = Depends(get_db)):
    if not db.get(Cycle, data.cycle_id): raise HTTPException(404, "Admission cycle not found")
    if data.status not in ("draft", "submitted"): raise HTTPException(422, "New applications must be draft or submitted")
    if data.status == "submitted":
        cycle = db.get(Cycle, data.cycle_id)
        if not cycle.active: raise HTTPException(400, "This admission cycle is closed")
    a = Application(**data.model_dump())
    db.add(a); db.flush()
    db.add(ApplicationAudit(application_id=a.id, old_status=None, new_status=a.status, reason="Application created"))
    if a.status == "submitted":
        db.add(ApplicationAudit(application_id=a.id, old_status="draft", new_status="submitted", reason="Submitted by applicant"))
    db.commit(); db.refresh(a)
    return application_out(a)

@app.post("/api/applications/{application_id}/submit")
def submit_application(application_id: int, db: Session = Depends(get_db)):
    a = db.get(Application, application_id)
    if not a: raise HTTPException(404, "Application not found")
    if a.status == "submitted": return application_out(a)
    if a.status != "draft": raise HTTPException(400, "Only drafts can be submitted")
    c = db.get(Cycle, a.cycle_id)
    if not c or not c.active: raise HTTPException(400, "Admission cycle is closed")
    old = a.status; a.status = "submitted"; a.updated_at = utcnow()
    db.add(ApplicationAudit(application_id=a.id, old_status=old, new_status=a.status, reason="Submitted by applicant"))
    db.commit(); db.refresh(a)
    return application_out(a)

@app.post("/api/applications/bulk-review")
def bulk_review(data: BulkReviewIn, db: Session = Depends(get_db)):
    if data.action not in ("shortlist", "select", "reject"):
        raise HTTPException(422, "Action must be shortlist, select, or reject")
    if data.action == "reject" and not (data.reason or "").strip():
        raise HTTPException(422, "A rejection reason is required")
    targets = db.scalars(select(Application).where(Application.id.in_(data.application_ids))).all()
    if len(targets) != len(set(data.application_ids)): raise HTTPException(404, "One or more applications were not found")
    # Keep all state changes, linked student creation, audit and lifecycle events in one DB transaction.
    for a in targets:
        if a.status not in ("submitted", "shortlisted"):
            raise HTTPException(400, f"Application {a.id} is not ready for review (status: {a.status})")
        old = a.status
        if data.action == "shortlist":
            a.status = "shortlisted"
        elif data.action == "reject":
            a.status = "rejected"; a.rejection_reason = data.reason.strip()
        else:
            if a.student_id is None:
                s = Student(application_id=a.id, display_name=a.applicant_name, email=a.email)
                db.add(s); db.flush(); a.student_id = s.id
                ev = LifecycleEvent(event_id=f"app-selected-{a.id}", student_id=s.id, event_type="ApplicantSelected", occurred_at=utcnow(), payload={"application_id": a.id, "cycle_id": a.cycle_id})
                db.add(ev)
            a.status = "selected"
        a.updated_at = utcnow()
        db.add(ApplicationAudit(application_id=a.id, old_status=old, new_status=a.status, reason=data.reason or data.action))
    db.commit()
    return {"updated": len(targets), "applications": [application_out(a) for a in targets]}

@app.get("/api/applications/{application_id}/audit")
def application_audit(application_id: int, db: Session = Depends(get_db)):
    if not db.get(Application, application_id): raise HTTPException(404, "Application not found")
    rows = db.scalars(select(ApplicationAudit).where(ApplicationAudit.application_id == application_id).order_by(ApplicationAudit.created_at, ApplicationAudit.id)).all()
    return [{"id": r.id, "old_status": r.old_status, "new_status": r.new_status, "reason": r.reason, "actor": r.actor, "created_at": r.created_at.isoformat()} for r in rows]

@app.get("/api/students")
def list_students(db: Session = Depends(get_db)):
    return [{"id": s.id, "display_name": s.display_name, "email": s.email, "application_id": s.application_id, "enrolled_at": s.enrolled_at.isoformat()} for s in db.scalars(select(Student).order_by(Student.id.desc())).all()]

@app.post("/api/events")
def record_event(data: EventIn, db: Session = Depends(get_db)):
    if not db.get(Student, data.student_id): raise HTTPException(404, "Student not found")
    existing = db.scalar(select(LifecycleEvent).where(LifecycleEvent.event_id == data.event_id))
    if existing:
        if existing.student_id == data.student_id and existing.event_type == data.event_type:
            return {"duplicate": True, **event_out(existing)}
        raise HTTPException(409, "event_id already used for a different event")
    e = LifecycleEvent(event_id=data.event_id, student_id=data.student_id, event_type=data.event_type, occurred_at=data.occurred_at.replace(tzinfo=None), payload=data.payload)
    db.add(e)
    try:
        db.commit()
    except Exception:
        db.rollback()
        existing = db.scalar(select(LifecycleEvent).where(LifecycleEvent.event_id == data.event_id))
        if existing and existing.student_id == data.student_id and existing.event_type == data.event_type:
            return {"duplicate": True, **event_out(existing)}
        raise HTTPException(409, "Could not record event; retry with the same event_id")
    db.refresh(e)
    return {"duplicate": False, **event_out(e)}

@app.get("/api/students/{student_id}/events")
def student_events(student_id: int, from_time: datetime | None = None, db: Session = Depends(get_db)):
    if not db.get(Student, student_id): raise HTTPException(404, "Student not found")
    q = select(LifecycleEvent).where(LifecycleEvent.student_id == student_id)
    if from_time: q = q.where(LifecycleEvent.occurred_at >= from_time.replace(tzinfo=None))
    rows = db.scalars(q.order_by(LifecycleEvent.occurred_at, LifecycleEvent.id)).all()
    return [event_out(e) for e in rows]

@app.get("/api/students/{student_id}/replay")
def replay_student(student_id: int, from_time: datetime | None = None, db: Session = Depends(get_db)):
    events = student_events(student_id, from_time, db)
    state = {"student_id": student_id, "events_applied": 0, "history": [], "current": {}}
    for e in events:
        state["events_applied"] += 1
        state["history"].append(e)
        # Simple generic projection: latest payload values win; event_type is preserved in history.
        state["current"].update(e.get("payload", {}))
        state["current"]["last_event_type"] = e["event_type"]
        state["current"]["last_event_at"] = e["occurred_at"]
    return state

@app.get("/api/careers")
def list_careers(db: Session = Depends(get_db)):
    rows = db.scalars(select(CareerRecord).order_by(CareerRecord.created_at.desc())).all()
    return [{"id": r.id, "student_id": r.student_id, "company_name": r.company_name, "company_key": r.company_key, "job_title": r.job_title, "source": r.source, "started_at": r.started_at.isoformat() if r.started_at else None, "ended_at": r.ended_at.isoformat() if r.ended_at else None, "is_current": r.is_current} for r in rows]

@app.post("/api/careers")
def add_career(data: CareerIn, db: Session = Depends(get_db)):
    if not db.get(Student, data.student_id): raise HTTPException(404, "Student not found")
    if data.source not in ("self-reported", "referral", "placement"): raise HTTPException(422, "Source must be self-reported, referral, or placement")
    r = CareerRecord(student_id=data.student_id, company_name=data.company_name.strip(), company_key=company_key(data.company_name), job_title=data.job_title.strip(), source=data.source, started_at=data.started_at.replace(tzinfo=None) if data.started_at else None, ended_at=data.ended_at.replace(tzinfo=None) if data.ended_at else None, is_current=data.is_current)
    db.add(r)
    # Record the career change as a lifecycle event in the same transaction.
    db.flush()
    db.add(LifecycleEvent(event_id=f"career-{uuid.uuid4()}", student_id=r.student_id, event_type="CareerRecordAdded", occurred_at=utcnow(), payload={"career_record_id": r.id, "company_name": r.company_name, "company_key": r.company_key, "job_title": r.job_title, "source": r.source, "is_current": r.is_current}))
    db.commit(); db.refresh(r)
    return {"id": r.id, "student_id": r.student_id, "company_name": r.company_name, "company_key": r.company_key, "job_title": r.job_title, "source": r.source, "is_current": r.is_current}

@app.get("/api/careers/search")
def search_careers(company: str = Query(min_length=1), current_only: bool = True, db: Session = Depends(get_db)):
    key = company_key(company)
    q = select(CareerRecord, Student).join(Student, Student.id == CareerRecord.student_id).where(or_(CareerRecord.company_key == key, CareerRecord.company_key.like(f"%{key}%")))
    if current_only: q = q.where(CareerRecord.is_current == True)
    return [{"student_id": s.id, "student_name": s.display_name, "company_name": r.company_name, "job_title": r.job_title, "source": r.source, "is_current": r.is_current} for r, s in db.execute(q.order_by(Student.display_name)).all()]

@app.post("/api/uploads/presign")
def presign_upload(data: PresignIn, db: Session = Depends(get_db)):
    if data.content_type not in ALLOWED_TYPES: raise HTTPException(415, f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_TYPES))}")
    if data.size_bytes <= 0 or data.size_bytes > MAX_BYTES: raise HTTPException(413, f"File must be between 1 byte and {MAX_BYTES} bytes")
    endpoint = os.getenv("S3_ENDPOINT_URL")
    if not endpoint: raise HTTPException(503, "Object storage is not configured. Set S3_ENDPOINT_URL and S3 credentials.")
    try:
        import boto3
        client = boto3.client("s3", endpoint_url=endpoint, aws_access_key_id=os.getenv("S3_ACCESS_KEY"), aws_secret_access_key=os.getenv("S3_SECRET_KEY"), region_name=os.getenv("S3_REGION", "us-east-1"))
        bucket = os.getenv("S3_BUCKET", "maatram-documents")
        try: client.head_bucket(Bucket=bucket)
        except Exception: client.create_bucket(Bucket=bucket)
        key = f"{data.owner_type}/{data.owner_id}/{uuid.uuid4().hex}-{re.sub(r'[^a-zA-Z0-9._-]', '_', data.filename)[:120]}"
        url = client.generate_presigned_url("put_object", Params={"Bucket": bucket, "Key": key, "ContentType": data.content_type}, ExpiresIn=300)
        public_endpoint = os.getenv("S3_PUBLIC_ENDPOINT_URL")
        if public_endpoint and endpoint != public_endpoint:
            url = url.replace(endpoint, public_endpoint)
        rec = UploadRecord(owner_type=data.owner_type, owner_id=data.owner_id, filename=data.filename, content_type=data.content_type, size_bytes=data.size_bytes, object_key=key, status="pending")
        db.add(rec); db.commit(); db.refresh(rec)
        return {"upload_id": rec.id, "upload_url": url, "object_key": key, "expires_in_seconds": 300, "method": "PUT", "required_headers": {"Content-Type": data.content_type}}
    except HTTPException: raise
    except Exception as exc:
        raise HTTPException(503, f"Unable to prepare upload. Check S3/MinIO configuration. ({type(exc).__name__})")

@app.post("/api/uploads/confirm/{upload_id}")
def confirm_upload(upload_id: int, db: Session = Depends(get_db)):
    rec = db.get(UploadRecord, upload_id)
    if not rec: raise HTTPException(404, "Upload not found")
    endpoint = os.getenv("S3_ENDPOINT_URL")
    try:
        import boto3
        client = boto3.client("s3", endpoint_url=endpoint, aws_access_key_id=os.getenv("S3_ACCESS_KEY"), aws_secret_access_key=os.getenv("S3_SECRET_KEY"), region_name=os.getenv("S3_REGION", "us-east-1"))
        head = client.head_object(Bucket=os.getenv("S3_BUCKET", "maatram-documents"), Key=rec.object_key)
        if head.get("ContentLength", 0) != rec.size_bytes: raise HTTPException(400, "Uploaded file size does not match the declared size")
        if head.get("ContentType") != rec.content_type: raise HTTPException(400, "Uploaded content type does not match")
        rec.status = "uploaded"; db.commit()
        return {"upload_id": rec.id, "status": rec.status}
    except HTTPException: raise
    except Exception:
        raise HTTPException(400, "Upload could not be verified in object storage")

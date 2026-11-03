import os, uuid, hashlib, json, csv, io, secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .config import settings
from .database import Base, engine, get_db
from .models import User, Application, Student, Alumni, LifecycleEvent, Document
from .schemas import RegisterIn, LoginIn, ApplicationIn, StatusIn, AlumniIn, UserCreate
from .security import hash_password, verify_password, create_token
from .dependencies import current_user, require_roles
from .services.otp import issue_otp, deliver_otp

app = FastAPI(title=settings.APP_NAME, version="1.0.0", description="Maatram student lifecycle REST API")
origins = [x.strip() for x in settings.CORS_ORIGINS.split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(bind=engine)
UPLOAD_ROOT = Path(settings.UPLOAD_DIR).resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg"}
def serialize_user(u): return {"id":u.id,"username":u.username,"email":u.email,"full_name":u.full_name,"role":u.role,"phone":u.phone}
def add_event(db, student_user_id, event_type, previous_value, new_value, actor_id):
    last = db.scalar(select(LifecycleEvent).where(LifecycleEvent.student_user_id==student_user_id).order_by(LifecycleEvent.version.desc()).limit(1))
    version = (last.version + 1) if last else 1
    prev_hash = last.event_hash if last else ""
    stamp = datetime.now(timezone.utc).isoformat()
    event_uuid = str(uuid.uuid4())
    payload = "|".join([event_uuid,str(student_user_id),event_type,previous_value,new_value,str(actor_id),stamp,str(version),prev_hash])
    digest = hashlib.sha256(payload.encode()).hexdigest()
    db.add(LifecycleEvent(event_uuid=event_uuid,student_user_id=student_user_id,event_type=event_type,previous_value=previous_value,new_value=new_value,actor_user_id=actor_id,version=version,previous_hash=prev_hash,event_hash=digest))

@app.get("/")
def root(): return {"name":settings.APP_NAME,"docs":"/docs","status":"ok"}
@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/api/auth/register")
def register(data: RegisterIn, db: Session=Depends(get_db)):
    if db.scalar(select(User).where((User.username==data.username)|(User.email==data.email))):
        raise HTTPException(409,"Username or email already exists")
    u=User(username=data.username,email=data.email,password_hash=hash_password(data.password),full_name=data.full_name,phone=data.phone,role="student")
    db.add(u); db.commit(); db.refresh(u)
    return {"message":"Account created","user":serialize_user(u)}

@app.post("/api/auth/login")
def login(data: LoginIn, db: Session=Depends(get_db)):
    u=db.scalar(select(User).where((User.username==data.username)|(User.email==data.username)))
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Invalid username/email or password")
    if not u.is_active: raise HTTPException(403,"Account is disabled")
    return {"access_token":create_token(u.id,u.role),"token_type":"bearer","user":serialize_user(u)}

@app.get("/api/auth/me")
def me(user: User=Depends(current_user)): return serialize_user(user)

@app.post("/api/auth/otp/request")
def request_otp(destination: str=Form(...)):
    code=issue_otp()
    # Development-only response intentionally returns code to UI for local test flow.
    delivered=deliver_otp(destination,code,settings.OTP_MODE)
    return {"message":"Development OTP generated. Check backend terminal.","development_code":code if settings.OTP_MODE=="console" else None,"delivered":delivered}

@app.post("/api/users")
def create_user(data: UserCreate, db: Session=Depends(get_db), admin: User=Depends(require_roles("admin"))):
    if data.role not in {"student","alumni","core","admin"}: raise HTTPException(400,"Invalid role")
    if db.scalar(select(User).where((User.username==data.username)|(User.email==data.email))): raise HTTPException(409,"User already exists")
    u=User(username=data.username,email=data.email,password_hash=hash_password(data.password),full_name=data.full_name,role=data.role)
    db.add(u); db.commit(); db.refresh(u); return serialize_user(u)

@app.get("/api/users")
def list_users(role: str|None=None, db: Session=Depends(get_db), admin: User=Depends(require_roles("admin"))):
    q=select(User)
    if role: q=q.where(User.role==role)
    return [serialize_user(x) for x in db.scalars(q.order_by(User.id.desc()).limit(500)).all()]

@app.post("/api/applications")
def create_application(data: ApplicationIn, db: Session=Depends(get_db), user: User=Depends(current_user)):
    appno="MHT-"+datetime.now().strftime("%y%m%d")+"-"+secrets.token_hex(3).upper()
    row=Application(**data.model_dump(),user_id=user.id,application_number=appno,status="Submitted")
    db.add(row); db.flush()
    add_event(db,user.id,"APPLICATION_SUBMITTED","",appno,user.id)
    db.commit(); db.refresh(row)
    return {"id":row.id,"application_number":row.application_number,"status":row.status}
@app.get("/api/applications")
def applications(status: str|None=None, q: str|None=None, skip:int=0, limit:int=100, db:Session=Depends(get_db), user:User=Depends(current_user)):
    stmt=select(Application)
    if user.role=="student": stmt=stmt.where(Application.user_id==user.id)
    if status: stmt=stmt.where(Application.status==status)
    if q: stmt=stmt.where(Application.full_name.like(f"%{q}%")|Application.application_number.like(f"%{q}%"))
    rows=db.scalars(stmt.order_by(Application.created_at.desc()).offset(skip).limit(min(limit,200))).all()
    return [application_dict(x) for x in rows]
def application_dict(x):
    return {"id":x.id,"application_number":x.application_number,"user_id":x.user_id,"full_name":x.full_name,"phone":x.phone,"email":x.email,"domain":x.domain,"course_preference":x.course_preference,"college_preference":x.college_preference,"academic_year":x.academic_year,"status":x.status,"created_at":x.created_at.isoformat(),"tele_comments":x.tele_comments,"physical_comments":x.physical_comments,"assigned_verifier":x.assigned_verifier}
@app.patch("/api/applications/{application_id}/status")
def update_application(application_id:int, data:StatusIn, db:Session=Depends(get_db), actor:User=Depends(require_roles("admin","core"))):
    allowed={"Draft","Submitted","Initial Review","Tele-verification","Physical Verification","Admin Review","Approved","Rejected","Waiting List","Admission Confirmation"}
    if data.status not in allowed: raise HTTPException(400,"Invalid application status")
    row=db.get(Application,application_id)
    if not row: raise HTTPException(404,"Application not found")
    old=row.status; row.status=data.status
    if actor.role=="core" and data.comment: row.tele_comments=data.comment
    elif data.comment: row.physical_comments=data.comment
    add_event(db,row.user_id,"APPLICATION_STATUS_CHANGED",old,data.status,actor.id)
    if data.status=="Approved":
        student=db.scalar(select(Student).where(Student.user_id==row.user_id))
        if not student:
            db.add(Student(user_id=row.user_id,application_id=row.id,college=row.college_preference,course=row.course_preference,academic_year=row.academic_year))
    db.commit(); return application_dict(row)

@app.get("/api/students")
def students(db:Session=Depends(get_db), user:User=Depends(current_user)):
    stmt=select(Student,User).join(User,Student.user_id==User.id)
    if user.role=="student": stmt=stmt.where(Student.user_id==user.id)
    return [{"id":s.id,"user_id":u.id,"name":u.full_name,"email":u.email,"college":s.college,"course":s.course,"academic_year":s.academic_year,"mentor":s.mentor,"anchor":s.anchor} for s,u in db.execute(stmt).all()]
@app.patch("/api/students/me")
def update_student(data:dict, db:Session=Depends(get_db), user:User=Depends(require_roles("student","admin"))):
    allowed={"college","course","department","academic_year","residence_type","admission_date","anchor","mentor","zone_incharge"}
    if set(data)-allowed: raise HTTPException(400,"Unsupported fields")
    row=db.scalar(select(Student).where(Student.user_id==user.id))
    if not row: row=Student(user_id=user.id); db.add(row); db.flush()
    for k,v in data.items():
        old=str(getattr(row,k) or ""); setattr(row,k,str(v))
        add_event(db,user.id,"STUDENT_FIELD_UPDATED",old,str(v),user.id)
    db.commit(); return {"message":"Profile updated"}

@app.get("/api/alumni")
def alumni(db:Session=Depends(get_db), user:User=Depends(current_user)):
    stmt=select(Alumni,User).join(User,Alumni.user_id==User.id)
    if user.role=="alumni": stmt=stmt.where(Alumni.user_id==user.id)
    return [{"id":a.id,"user_id":u.id,"name":u.full_name,"email":u.email,"student_id":a.student_id,"graduation_year":a.graduation_year,"employment_status":a.employment_status,"company":a.company,"job_role":a.job_role,"industry":a.industry,"work_location":a.work_location,"skills":a.skills,"achievements":a.achievements} for a,u in db.execute(stmt).all()]
@app.put("/api/alumni/me")
def update_alumni(data:AlumniIn, db:Session=Depends(get_db), user:User=Depends(require_roles("alumni","admin"))):
    row=db.scalar(select(Alumni).where(Alumni.user_id==user.id))
    if not row: row=Alumni(user_id=user.id); db.add(row)
    for k,v in data.model_dump().items():
        if k=="salary_private" and user.role!="admin": continue
        setattr(row,k,v)
    db.commit(); return {"message":"Alumni profile saved"}

@app.get("/api/events/{student_user_id}")
def event_history(student_user_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    if user.role=="student" and user.id!=student_user_id: raise HTTPException(403,"Not your lifecycle")
    rows=db.scalars(select(LifecycleEvent).where(LifecycleEvent.student_user_id==student_user_id).order_by(LifecycleEvent.version)).all()
    return [{"event_uuid":e.event_uuid,"event_type":e.event_type,"previous_value":e.previous_value,"new_value":e.new_value,"actor_user_id":e.actor_user_id,"version":e.version,"occurred_at":e.occurred_at.isoformat(),"previous_hash":e.previous_hash,"event_hash":e.event_hash} for e in rows]
@app.get("/api/events/{student_user_id}/verify")
def verify_events(student_user_id:int, db:Session=Depends(get_db), user:User=Depends(require_roles("admin","core"))):
    rows=db.scalars(select(LifecycleEvent).where(LifecycleEvent.student_user_id==student_user_id).order_by(LifecycleEvent.version)).all()
    previous=""
    for e in rows:
        payload="|".join([e.event_uuid,str(e.student_user_id),e.event_type,e.previous_value,e.new_value,str(e.actor_user_id),e.occurred_at.isoformat(),str(e.version),previous])
        if e.previous_hash!=previous or hashlib.sha256(payload.encode()).hexdigest()!=e.event_hash: return {"valid":False,"failed_version":e.version}
        previous=e.event_hash
    return {"valid":True,"events_checked":len(rows)}

@app.post("/api/documents")
async def upload_document(category:str=Form("Other"), file:UploadFile=File(...), db:Session=Depends(get_db), user:User=Depends(current_user)):
    ext=Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT: raise HTTPException(400,"Only PDF, PNG and JPG files are allowed")
    content=await file.read(settings.MAX_UPLOAD_MB*1024*1024+1)
    if len(content)>settings.MAX_UPLOAD_MB*1024*1024: raise HTTPException(413,"File too large")
    if not content: raise HTTPException(400,"Empty file")
    if ext==".pdf" and not content.startswith(b"%PDF"): raise HTTPException(400,"Invalid PDF content")
    if ext in {".jpg",".jpeg"} and not content.startswith(b"\xff\xd8"): raise HTTPException(400,"Invalid JPEG content")
    if ext==".png" and not content.startswith(b"\x89PNG\r\n\x1a\n"): raise HTTPException(400,"Invalid PNG content")
    stored=f"{uuid.uuid4().hex}{ext}"; path=UPLOAD_ROOT/stored
    path.write_bytes(content)
    doc=Document(owner_user_id=user.id,original_name=Path(file.filename or "document").name,stored_name=stored,content_type=file.content_type or "application/octet-stream",size_bytes=len(content),category=category)
    db.add(doc); db.commit(); db.refresh(doc)
    return {"id":doc.id,"original_name":doc.original_name,"category":doc.category,"size_bytes":doc.size_bytes,"verification_status":doc.verification_status}
@app.get("/api/documents")
def documents(db:Session=Depends(get_db), user:User=Depends(current_user)):
    stmt=select(Document)
    if user.role=="student": stmt=stmt.where(Document.owner_user_id==user.id)
    return [{"id":d.id,"original_name":d.original_name,"category":d.category,"size_bytes":d.size_bytes,"verification_status":d.verification_status,"uploaded_at":d.uploaded_at.isoformat()} for d in db.scalars(stmt.order_by(Document.uploaded_at.desc())).all()]
@app.get("/api/documents/{doc_id}/download")
def download_document(doc_id:int, db:Session=Depends(get_db), user:User=Depends(current_user)):
    d=db.get(Document,doc_id)
    if not d: raise HTTPException(404,"Document not found")
    if user.role=="student" and d.owner_user_id!=user.id: raise HTTPException(403,"Forbidden")
    path=UPLOAD_ROOT/d.stored_name
    if not path.is_file() or path.parent!=UPLOAD_ROOT: raise HTTPException(404,"File unavailable")
    return FileResponse(path,filename=d.original_name,media_type=d.content_type)

@app.get("/api/dashboard")
def dashboard(db:Session=Depends(get_db), user:User=Depends(current_user)):
    def count(model, *criteria): return db.scalar(select(func.count()).select_from(model).where(*criteria)) if criteria else db.scalar(select(func.count()).select_from(model))
    if user.role=="student":
        mine=count(Application,Application.user_id==user.id)
        return {"role":"student","my_applications":mine,"my_documents":count(Document,Document.owner_user_id==user.id),"my_events":count(LifecycleEvent,LifecycleEvent.student_user_id==user.id)}
    if user.role=="alumni":
        a=db.scalar(select(Alumni).where(Alumni.user_id==user.id))
        return {"role":"alumni","employment_status":a.employment_status if a else "Not Placed","company":a.company if a else "","career_profile_complete":bool(a and a.job_role)}
    return {"role":user.role,"total_users":count(User),"students":count(User,User.role=="student"),"alumni":count(User,User.role=="alumni"),"core_members":count(User,User.role=="core"),"applications":count(Application),"pending":count(Application,Application.status.in_(["Submitted","Initial Review","Tele-verification","Physical Verification","Admin Review"])),"approved":count(Application,Application.status=="Approved"),"rejected":count(Application,Application.status=="Rejected"),"documents":count(Document),"events":count(LifecycleEvent)}
@app.get("/api/reports/applications.csv")
def export_applications(db:Session=Depends(get_db), user:User=Depends(require_roles("admin","core"))):
    rows=db.scalars(select(Application).order_by(Application.created_at.desc())).all()
    stream=io.StringIO(); writer=csv.writer(stream)
    writer.writerow(["Application No","Name","Phone","Email","Domain","Course","Status","Created"])
    for x in rows: writer.writerow([x.application_number,x.full_name,x.phone,x.email,x.domain,x.course_preference,x.status,x.created_at.isoformat()])
    stream.seek(0)
    return StreamingResponse(iter([stream.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=maatram_applications.csv"})

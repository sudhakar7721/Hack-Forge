from datetime import datetime, timezone
import uuid
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(25), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student", index=True)
    full_name: Mapped[str] = mapped_column(String(160), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    application_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    dob: Mapped[str] = mapped_column(String(20), default="")
    gender: Mapped[str] = mapped_column(String(30), default="")
    phone: Mapped[str] = mapped_column(String(25), default="")
    email: Mapped[str] = mapped_column(String(180), default="")
    parent_name: Mapped[str] = mapped_column(String(160), default="")
    parent_phone: Mapped[str] = mapped_column(String(25), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    district: Mapped[str] = mapped_column(String(100), default="")
    state: Mapped[str] = mapped_column(String(100), default="Tamil Nadu")
    school_name: Mapped[str] = mapped_column(String(180), default="")
    tenth_details: Mapped[str] = mapped_column(String(300), default="")
    twelfth_details: Mapped[str] = mapped_column(String(300), default="")
    higher_secondary_group: Mapped[str] = mapped_column(String(120), default="")
    domain: Mapped[str] = mapped_column(String(80), default="Arts and Science")
    course_preference: Mapped[str] = mapped_column(String(180), default="")
    college_preference: Mapped[str] = mapped_column(String(180), default="")
    academic_year: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(40), default="Draft", index=True)
    tele_comments: Mapped[str] = mapped_column(Text, default="")
    physical_comments: Mapped[str] = mapped_column(Text, default="")
    assigned_verifier: Mapped[str] = mapped_column(String(160), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("applications.id"), nullable=True)
    college: Mapped[str] = mapped_column(String(180), default="")
    course: Mapped[str] = mapped_column(String(180), default="")
    department: Mapped[str] = mapped_column(String(150), default="")
    academic_year: Mapped[str] = mapped_column(String(20), default="")
    residence_type: Mapped[str] = mapped_column(String(30), default="Day Scholar")
    admission_date: Mapped[str] = mapped_column(String(20), default="")
    anchor: Mapped[str] = mapped_column(String(150), default="")
    mentor: Mapped[str] = mapped_column(String(150), default="")
    zone_incharge: Mapped[str] = mapped_column(String(150), default="")

class Alumni(Base):
    __tablename__ = "alumni"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    student_id: Mapped[str] = mapped_column(String(50), default="")
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    employment_status: Mapped[str] = mapped_column(String(40), default="Not Placed")
    company: Mapped[str] = mapped_column(String(180), default="")
    job_role: Mapped[str] = mapped_column(String(160), default="")
    industry: Mapped[str] = mapped_column(String(120), default="")
    work_location: Mapped[str] = mapped_column(String(160), default="")
    joining_date: Mapped[str] = mapped_column(String(20), default="")
    salary_private: Mapped[str] = mapped_column(String(80), default="")
    skills: Mapped[str] = mapped_column(Text, default="")
    achievements: Mapped[str] = mapped_column(Text, default="")

class LifecycleEvent(Base):
    __tablename__ = "event_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_uuid: Mapped[str] = mapped_column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    student_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    previous_value: Mapped[str] = mapped_column(Text, default="")
    new_value: Mapped[str] = mapped_column(Text, default="")
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    version: Mapped[int] = mapped_column(Integer)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    previous_hash: Mapped[str] = mapped_column(String(64), default="")
    event_hash: Mapped[str] = mapped_column(String(64))
    __table_args__ = (UniqueConstraint("student_user_id", "version", name="uq_student_event_version"),)

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(100), unique=True)
    content_type: Mapped[str] = mapped_column(String(100), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String(80), default="Other")
    verification_status: Mapped[str] = mapped_column(String(30), default="Pending")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

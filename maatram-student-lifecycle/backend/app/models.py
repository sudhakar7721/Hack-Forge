from sqlalchemy import String, Integer, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), index=True)
    phone: Mapped[str] = mapped_column(String(30), default="")
    display_name: Mapped[str] = mapped_column(String(150), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(150), index=True, default="")
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dob: Mapped[str] = mapped_column(String(20), default="")
    phone: Mapped[str] = mapped_column(String(30), default="")
    email: Mapped[str] = mapped_column(String(150), default="")
    parent_name: Mapped[str] = mapped_column(String(150), default="")
    address: Mapped[str] = mapped_column(Text, default="")
    previous_school: Mapped[str] = mapped_column(String(200), default="")
    tenth_mark: Mapped[float | None] = mapped_column(Float, nullable=True)
    tenth_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    twelfth_mark: Mapped[float | None] = mapped_column(Float, nullable=True)
    twelfth_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    higher_secondary_group: Mapped[str] = mapped_column(String(100), default="")
    applied_domain: Mapped[str] = mapped_column(String(100), default="")
    application_number: Mapped[str] = mapped_column(String(80), unique=True, index=True, default="")
    application_details: Mapped[str] = mapped_column(Text, default="")
    tele_verification_comment: Mapped[str] = mapped_column(Text, default="")
    physical_verification_comment: Mapped[str] = mapped_column(Text, default="")
    application_status: Mapped[str] = mapped_column(String(40), default="Waiting List")
    admission_date: Mapped[str] = mapped_column(String(20), default="")
    college: Mapped[str] = mapped_column(String(200), default="")
    course: Mapped[str] = mapped_column(String(150), default="")
    academic_year: Mapped[str] = mapped_column(String(30), default="")
    residence_type: Mapped[str] = mapped_column(String(30), default="")
    fees_details: Mapped[str] = mapped_column(Text, default="")
    anchor_name: Mapped[str] = mapped_column(String(150), default="")
    mentor_name: Mapped[str] = mapped_column(String(150), default="")
    zone_incharge: Mapped[str] = mapped_column(String(150), default="")
    academic_details: Mapped[str] = mapped_column(Text, default="")
    self_learning_details: Mapped[str] = mapped_column(Text, default="")
    activities: Mapped[str] = mapped_column(Text, default="")
    pv_volunteering: Mapped[str] = mapped_column(Text, default="")
    tv_volunteering: Mapped[str] = mapped_column(Text, default="")
    school_visits: Mapped[str] = mapped_column(Text, default="")
    other_volunteering: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Alumni(Base):
    __tablename__ = "alumni"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(150), default="")
    placed: Mapped[bool] = mapped_column(Boolean, default=False)
    current_company: Mapped[str] = mapped_column(String(200), default="")
    job_title: Mapped[str] = mapped_column(String(150), default="")
    work_location: Mapped[str] = mapped_column(String(150), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

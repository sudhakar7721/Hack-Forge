from datetime import datetime

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, synonym

from .database import Base

LargeText = Text().with_variant(LONGTEXT(), "mysql")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    display_name: Mapped[str] = mapped_column("full_name", String(160), default="", nullable=False)
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    username = synonym("email")
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash = synonym("hashed_password")
    role: Mapped[str] = mapped_column(String(30), default="student", nullable=False)
    active: Mapped[bool] = mapped_column("is_active", Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dob: Mapped[str | None] = mapped_column(String(20), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    parent_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    previous_school: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tenth_mark: Mapped[float | None] = mapped_column(Float, nullable=True)
    tenth_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    twelfth_mark: Mapped[float | None] = mapped_column(Float, nullable=True)
    twelfth_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    higher_secondary_group: Mapped[str | None] = mapped_column(String(150), nullable=True)
    applied_domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    application_number: Mapped[str | None] = mapped_column(String(50), unique=True, index=True, nullable=True)
    application_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    tele_verification_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    physical_verification_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    application_status: Mapped[str] = mapped_column(String(30), default="Waiting List", nullable=False)
    admission_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    college: Mapped[str | None] = mapped_column(String(200), nullable=True)
    course: Mapped[str | None] = mapped_column(String(150), nullable=True)
    academic_year: Mapped[str | None] = mapped_column(String(30), nullable=True)
    residence_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fees_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    anchor_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    mentor_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    zone_incharge: Mapped[str | None] = mapped_column(String(160), nullable=True)
    academic_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    self_learning_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    activities: Mapped[str | None] = mapped_column(Text, nullable=True)
    pv_volunteering: Mapped[str | None] = mapped_column(Text, nullable=True)
    tv_volunteering: Mapped[str | None] = mapped_column(Text, nullable=True)
    school_visits: Mapped[str | None] = mapped_column(Text, nullable=True)
    other_volunteering: Mapped[str | None] = mapped_column(Text, nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(80), nullable=True)
    department: Mapped[str | None] = mapped_column(String(150), nullable=True)
    passed_out_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    semester_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_cgpa: Mapped[str | None] = mapped_column(String(20), nullable=True)
    completed_courses: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_files: Mapped[str | None] = mapped_column(LargeText, nullable=True)
    internship_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    resume_url: Mapped[str | None] = mapped_column(LargeText, nullable=True)
    project_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    volunteering_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    zone_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    spoc_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    # Legacy column compatibility for existing databases created by earlier versions.
    date_of_birth: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    parent_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    school_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tenth_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    twelfth_marks: Mapped[float | None] = mapped_column(Float, nullable=True)
    domain: Mapped[str | None] = mapped_column(String(100), nullable=True)
    college_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    admission_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    verification_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    verification_comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    accommodation_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fees: Mapped[float | None] = mapped_column(Float, nullable=True)
    zone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    academic_performance: Mapped[str | None] = mapped_column(Text, nullable=True)
    self_learning: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class Alumni(Base):
    __tablename__ = "alumni"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int | None] = mapped_column(ForeignKey("students.id"), unique=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    placed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    work_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    # Legacy columns remain writable for databases with their original NOT NULL constraints.
    placement_status: Mapped[str] = mapped_column(String(50), default="not_placed", nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_role: Mapped[str | None] = mapped_column(String(150), nullable=True)
    current_location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    package: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class ZoneInformation(Base):
    __tablename__ = "zone_information"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_name: Mapped[str] = mapped_column(String(100), default="", nullable=False, index=True)
    sender_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    sender_role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(200), default="", nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    link: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attachment_data: Mapped[str | None] = mapped_column(LargeText, nullable=True)
    zone_incharge: Mapped[str | None] = mapped_column(String(160), nullable=True)
    contact_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class StudentFeedback(Base):
    __tablename__ = "student_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    student_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    zone_name: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    feedback_type: Mapped[str] = mapped_column(String(100), default="general", nullable=False)
    feedback: Mapped[str] = mapped_column(Text, default="", nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class AlumniProject(Base):
    __tablename__ = "alumni_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    alumni_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    alumni_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    activity_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    activity_time: Mapped[str | None] = mapped_column(String(30), nullable=True)
    place: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[str | None] = mapped_column(String(40), nullable=True)
    longitude: Mapped[str | None] = mapped_column(String(40), nullable=True)
    details: Mapped[str | None] = mapped_column(LargeText, nullable=True)
    participant_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photo_data: Mapped[str | None] = mapped_column(LargeText, nullable=True)
    photo_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class AlumniAvailability(Base):
    __tablename__ = "alumni_availability"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    alumni_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    alumni_name: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    skill_area: Mapped[str] = mapped_column(String(160), default="", nullable=False)
    available_for: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    availability_status: Mapped[str] = mapped_column(String(40), default="Available", nullable=False)
    available_from: Mapped[str | None] = mapped_column(String(30), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(160), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

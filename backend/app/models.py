
from datetime import datetime, date

from sqlalchemy import (
    String,
    Integer,
    Float,
    Boolean,
    Date,
    DateTime,
    Text,
    ForeignKey,
    func,
)

from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


# =====================================================
# USER MODEL
# =====================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    display_name: Mapped[str] = mapped_column(
        "full_name",
        String(160),
        default="",
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(160),
        unique=True,
        index=True,
        nullable=False
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="student",
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        "is_active",
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# =====================================================
# STUDENT MODEL
# =====================================================

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    application_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=True
    )

    full_name: Mapped[str] = mapped_column(
        String(160),
        nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    date_of_birth: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    parent_name: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    parent_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    school_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    tenth_marks: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    tenth_percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    twelfth_marks: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    twelfth_percentage: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    higher_secondary_group: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    domain: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    college_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    course: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    academic_year: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    admission_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    admission_status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False
    )

    verification_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    verification_comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    accommodation_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    fees: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    anchor_name: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    mentor_name: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    zone_incharge: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    zone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    academic_performance: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    self_learning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    activities: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    volunteering_details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# =====================================================
# ALUMNI MODEL
# =====================================================

class Alumni(Base):
    __tablename__ = "alumni"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        unique=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(160),
        nullable=False
    )

    email: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    graduation_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    placement_status: Mapped[str] = mapped_column(
        String(50),
        default="not_placed",
        nullable=False
    )

    company_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    job_role: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    current_location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    package: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# =====================================================
# ZONE INFORMATION MODEL
# =====================================================

class ZoneInformation(Base):
    __tablename__ = "zone_information"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    zone_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    zone_incharge: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    contact_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )


# =====================================================
# STUDENT FEEDBACK MODEL
# =====================================================

class StudentFeedback(Base):
    __tablename__ = "student_feedback"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False
    )

    feedback_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    feedback: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    submitted_by: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

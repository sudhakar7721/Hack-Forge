from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

class CycleIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    year: int = Field(ge=2000, le=2100)
    active: bool = True

class ApplicationIn(BaseModel):
    cycle_id: int
    applicant_name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=3, max_length=255)
    phone: str = ""
    education: str = ""
    statement: str = ""
    status: str = "draft"

class BulkReviewIn(BaseModel):
    application_ids: list[int] = Field(min_length=1)
    action: str
    reason: str | None = None

class EventIn(BaseModel):
    event_id: str = Field(min_length=4, max_length=100)
    student_id: int
    event_type: str
    occurred_at: datetime
    payload: dict[str, Any] = {}

class CareerIn(BaseModel):
    student_id: int
    company_name: str
    job_title: str
    source: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    is_current: bool = True

class PresignIn(BaseModel):
    owner_type: str = "application"
    owner_id: int
    filename: str
    content_type: str
    size_bytes: int

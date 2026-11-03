from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    full_name: str = Field(min_length=2, max_length=160)
    phone: str = Field(default="", max_length=25)
class LoginIn(BaseModel):
    username: str
    password: str
class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
class ApplicationIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    dob: str = ""; gender: str = ""; phone: str = ""; email: str = ""
    parent_name: str = ""; parent_phone: str = ""; address: str = ""
    district: str = ""; state: str = "Tamil Nadu"; school_name: str = ""
    tenth_details: str = ""; twelfth_details: str = ""; higher_secondary_group: str = ""
    domain: str = "Arts and Science"; course_preference: str = ""
    college_preference: str = ""; academic_year: str = ""
class StatusIn(BaseModel):
    status: str
    comment: str = ""
class AlumniIn(BaseModel):
    student_id: str = ""; graduation_year: Optional[int] = None
    employment_status: str = "Not Placed"; company: str = ""; job_role: str = ""
    industry: str = ""; work_location: str = ""; joining_date: str = ""
    salary_private: str = ""; skills: str = ""; achievements: str = ""
class UserCreate(BaseModel):
    username: str; email: EmailStr; password: str = Field(min_length=10)
    full_name: str; role: str

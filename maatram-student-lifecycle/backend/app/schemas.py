from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class LoginIn(BaseModel):
    username: str
    password: str
    role: str

class StudentIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    full_name: str = ""
    age: Optional[int] = None
    dob: str = ""
    phone: str = ""
    email: str = ""
    parent_name: str = ""
    address: str = ""
    blood_group: str = ""
    previous_school: str = ""
    tenth_mark: Optional[float] = None
    tenth_percentage: Optional[float] = None
    twelfth_mark: Optional[float] = None
    twelfth_percentage: Optional[float] = None
    higher_secondary_group: str = ""
    applied_domain: str = ""
    application_number: str = ""
    application_details: str = ""
    tele_verification_comment: str = ""
    physical_verification_comment: str = ""
    application_status: str = "Waiting List"
    admission_date: str = ""
    college: str = ""
    course: str = ""
    academic_year: str = ""
    residence_type: str = ""
    fees_details: str = ""
    anchor_name: str = ""
    mentor_name: str = ""
    zone_incharge: str = ""
    academic_details: str = ""
    self_learning_details: str = ""
    activities: str = ""
    pv_volunteering: str = ""
    tv_volunteering: str = ""
    school_visits: str = ""
    other_volunteering: str = ""

class AlumniIn(BaseModel):
    full_name: str = ""
    placed: bool = False
    current_company: str = ""
    job_title: str = ""
    work_location: str = ""
    student_id: Optional[int] = None

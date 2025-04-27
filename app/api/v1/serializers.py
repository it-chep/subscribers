from pydantic import BaseModel
from typing import Optional


class DoctorCreateBody(BaseModel):
    doctor_id: int
    instagram: Optional[str] = None
    telegram: Optional[str] = None


class DoctorUpdateBody(BaseModel):
    instagram: Optional[str] = None
    telegram: Optional[str] = None

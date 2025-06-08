from pydantic import BaseModel
from typing import Optional


class DoctorCreateBody(BaseModel):
    """
    {
        "doctor_id": "23",
        "instagram": "it_necheporuk",
        "telegram": "mysli_maxima"
    }
    """
    doctor_id: int
    instagram: Optional[str] = None
    telegram: Optional[str] = None


class DoctorUpdateBody(BaseModel):
    """
    {
        "instagram": "it_necheporuk",
        "telegram": "mysli_maxima"
    }
    """
    instagram: Optional[str] = None
    telegram: Optional[str] = None

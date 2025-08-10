from pydantic import BaseModel
from typing import Optional


class DoctorsFilterBody(BaseModel):
    """
        {
            "social_media": ["tg"],
            "min_subscribers": 0,
            "max_subscribers": 100_000_000,
            "limit": 30
            "sort": "asc:
            "current_page": 1
            "doctor_ids": [1,2,3,5,67,]
        }
        """

    social_media: list[str] = ["tg", "inst"]
    min_subscribers: Optional[int] = 100
    max_subscribers: Optional[int] = 4_000_000
    limit: Optional[int] = 30
    sort: Optional[str] = "desc"
    current_page: Optional[int] = 0
    doctor_ids: list[int]


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
        "is_active": true,
    }
    """
    instagram: Optional[str] = None
    telegram: Optional[str] = None
    is_active: Optional[bool] = None

from typing import Optional, List
from pydantic import BaseModel, Field


class DoctorsFilterBody(BaseModel):
    """
        {
            "social_media": ["tg"],
            "min_subscribers": 0,
            "max_subscribers": 100_000_000,
            "limit": 30
            "sort": "asc":
            "current_page": 1
            "doctor_ids": [1,2,3,5,67,]
        }
        """

    social_media: List[str] = Field(default=["tg", "inst"])
    min_subscribers: Optional[int] = Field(default=100, ge=0)
    max_subscribers: Optional[int] = Field(default=4_000_000, ge=0)
    limit: Optional[int] = Field(default=30, gt=0)
    sort: Optional[str] = Field(default="desc")
    current_page: Optional[int] = Field(default=0, ge=0)
    doctor_ids: List[int] = Field(default_factory=list)


class DoctorCreateBody(BaseModel):
    """
    {
        "doctor_id": "23",
        "instagram": "it_necheporuk",
        "telegram": "mysli_maxima",
        "youtube": "readydoctor",
        "vk": "readydoctor"
    }
    """
    doctor_id: int
    instagram: Optional[str] = None
    telegram: Optional[str] = None
    youtube: Optional[str] = None
    vk: Optional[str] = None


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
    youtube: Optional[str] = None


class SubscriberItem(BaseModel):
    """Модель одного элемента подписчиков"""
    key: str
    subs_count: int


class UpdateDoctorSubscribersBody(BaseModel):
    """
    Тело запроса для обновления подписчиков врача
    {
        "items": [
            {"key": "instagram", "subs_count": 10000},
            {"key": "telegram", "subs_count": 5000},
            {"key": "youtube", "subs_count": 20000},
            {"key": "vk", "subs_count": 15000}
        ]
    }
    """
    items: List[SubscriberItem]


class CheckTelegramInBlacklistRequest(BaseModel):
    """
    {
        "telegram": "mysli_maxima"
    }
    """
    telegram: Optional[str] = None

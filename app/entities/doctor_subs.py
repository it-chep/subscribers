from __future__ import annotations

import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel


class SocialNetworkType(str, Enum):
    """Типы социальных сетей для докторов"""
    ALL = "all"
    INSTAGRAM = "inst"
    TELEGRAM = "tg"
    VK = "vk"
    YOUTUBE = "youtube"


class DoctorSubs(BaseModel):
    _id: int
    doctor_id: int
    inst_last_updated_timestamp: Optional[datetime.datetime] = None
    inst_subs_count: int = 0
    instagram_channel_name: str = ""

    tg_last_updated_timestamp: Optional[datetime.datetime] = None
    tg_subs_count: int = 0
    telegram_channel_name: str = ""

from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class DoctorSubsDTO:
    doctor_id: int

    ### Instagram
    inst_last_updated_timestamp: Optional[datetime.datetime]
    # количество подписчиков
    inst_subs_count: int
    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    instagram_short: str
    # текст отображения "подписчика", "подписчиков"
    instagram_text: str

    ### Telegram
    tg_last_updated_timestamp: Optional[datetime.datetime]
    tg_subs_count: int
    telegram_short: str
    telegram_text: str

    ### YouTube
    youtube_last_updated_timestamp: Optional[datetime.datetime]
    youtube_subs_count: int
    youtube_short: str
    youtube_text: str

    ### Vk
    vk_last_updated_timestamp: Optional[datetime.datetime]
    vk_subs_count: int
    vk_short: str
    vk_text: str


@dataclass
class DoctorSubsFilterDTO:
    doctor_id: int
    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    inst_short: str
    telegram_short: str
    youtube_short: str
    vk_short: str

    # текст отображения "подписчика", "подписчиков"
    inst_text: str
    telegram_text: str
    youtube_text: str
    vk_text: str


@dataclass
class DoctorSubsByIDsDTO:
    doctor_id: int

    # количество подписчиков
    inst_subs_count: str = "0"
    tg_subs_count: str = "0"
    youtube_subs_count: str = "0"
    vk_subs_count: str = "0"

    # название аккаунта
    instagram_text: str = ""
    telegram_text: str = ""
    youtube_text: str = ""
    vk_text: str = ""

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
    # количество подписчиков
    tg_subs_count: int
    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    telegram_short: str
    # текст отображения "подписчика", "подписчиков"
    telegram_text: str

    ### YouTube
    youtube_last_updated_timestamp: Optional[datetime.datetime]
    # количество подписчиков
    youtube_subs_count: int
    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    youtube_short: str
    # текст отображения "подписчика", "подписчиков"
    youtube_text: str


@dataclass
class DoctorSubsFilterDTO:
    doctor_id: int
    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    inst_short: str
    # текст отображения "подписчика", "подписчиков"
    inst_text: str

    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    telegram_short: str
    # текст отображения "подписчика", "подписчиков"
    telegram_text: str

    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    youtube_short: str
    # текст отображения "подписчика", "подписчиков"
    youtube_text: str


@dataclass
class DoctorSubsByIDsDTO:
    doctor_id: int
    # количество подписчиков
    inst_subs_count: str = "0"
    # название аккаунта
    instagram_text: str = ""

    # количество подписчиков
    tg_subs_count: str = "0"
    # название аккаунта
    telegram_text: str = ""

    youtube_subs_count: str = "0"
    youtube_text: str = ""

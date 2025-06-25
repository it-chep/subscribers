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


@dataclass
class DoctorSubsFilterDTO:
    doctor_id: int
    inst_subs_count: int

    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    telegram_short: str
    # текст отображения "подписчика", "подписчиков"
    telegram_text: str
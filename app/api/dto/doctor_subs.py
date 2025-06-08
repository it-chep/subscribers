from __future__ import annotations

from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class DoctorSubsDTO:
    doctor_id: int
    inst_last_updated_timestamp: Optional[datetime.datetime]
    inst_subs_count: int

    tg_last_updated_timestamp: Optional[datetime.datetime]
    # количество подписчиков
    tg_subs_count: int
    # сокращенный вид количества подписчиков "1,3м", "300к", "9999", "10,3к"
    telegram_short: str
    # текст отображения "подписчика", "подписчиков"
    telegram_text: str

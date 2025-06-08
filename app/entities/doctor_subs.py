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
    # время последнего обновления подписчиков
    inst_last_updated_timestamp: Optional[datetime.datetime] = None
    # количество подписчиков
    inst_subs_count: int = 0
    # название аккаунта
    instagram_channel_name: str = ""

    # время последнего обновления подписчиков
    tg_last_updated_timestamp: Optional[datetime.datetime] = None
    # количество подписчиков
    tg_subs_count: int = 0
    # название аккаунта
    telegram_channel_name: str = ""

    @property
    def subs_short(self) -> str:
        """
        Форматирует количество подписчиков в сокращенный вид:
        - 1,3м (1.3 миллиона)
        - 300к (300 тысяч)
        - 10,3к (10.3 тысячи)
        - 9999 (менее 10 тысяч)
        """
        count = self.tg_subs_count

        if count >= 1_000_000:
            short = f"{count / 1_000_000:0.1f}".replace('.', ',') + 'м'
        elif count >= 100_000:
            short = f"{count // 1000}к"
        elif count >= 10_000:
            short = f"{count:,}".replace(',', ' ')
        else:
            short = str(count)

        return short

    @property
    def subs_text(self) -> str:
        """
        Возвращает правильную форму слова "подписчик" в зависимости от количества
        """
        count = self.tg_subs_count % 100
        if 11 <= count % 100 <= 19:
            text = "подписчиков"
        else:
            remainder = count % 10
            if remainder == 1:
                text = "подписчик"
            elif 2 <= remainder <= 4:
                text = "подписчика"
            else:
                text = "подписчиков"

        return text

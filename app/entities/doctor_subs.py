from __future__ import annotations

import datetime
from typing import Optional
from pydantic import BaseModel


def subs_text(count) -> str:
    """
    Возвращает правильную форму слова "подписчик" в зависимости от количества
    """
    # count = count % 100
    # if 11 <= count % 100 <= 19:
    #     text = "подписчиков"
    # else:
    #     remainder = count % 10
    #     if remainder == 1:
    #         text = "подписчик"
    #     elif 2 <= remainder <= 4:
    #         text = "подписчика"
    #     else:
    #         text = "подписчиков"

    return "подписчиков"


def subs_by_digits(count: int) -> str:
    if count is None:
        return ""
    return "{:,}".format(count).replace(",", " ")


def subs_short(count) -> str:
    """
    Форматирует количество подписчиков в сокращенный вид:
    - 1,3м (1.3 миллиона)
    - 300к (300 тысяч)
    - 10,3к (10.3 тысячи)
    - 9999 (менее 10 тысяч)
    """

    if count >= 1_000_000:
        short = f"{count / 1_000_000:0.1f} ".replace('.', ',') + 'млн'
    elif count >= 100_000:
        short = f"{count // 1000} тыс"
    elif count >= 10_000:
        short = f"{count:,}".replace(',', ' ')
    else:
        short = str(count)

    return short


class DoctorSubs(BaseModel):
    internal_id: int
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
    # подписан ли бот на этот тг канал
    tg_has_subscribed: Optional[bool] = False

    # время последнего обновления подписчиков
    youtube_last_updated_timestamp: Optional[datetime.datetime] = None
    # количество подписчиков
    youtube_subs_count: int = 0
    # название аккаунта
    youtube_channel_name: str = ""


class DoctorSubsByIDs(BaseModel):
    doctor_id: int
    # количество подписчиков
    inst_subs_count: int = 0
    tg_subs_count: int = 0
    youtube_subs_count: int = 0


class UpdatedSubsQueue(BaseModel):
    # id в базе
    _id: int
    # id доктора в базе subscribers
    id_in_subscribers: int
    # doctor_id доктора в базе subscribers
    last_updated_id: int
    # последнее время обновление
    last_updated_at: Optional[datetime.datetime] = None

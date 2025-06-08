from __future__ import annotations

from typing import List
from clients.telegram import TelegramClient

from app.entities.doctor_subs import SocialNetworkType, DoctorSubs
from app.exception.domain_error import RequiredFieldError, UnavailableTelegramChannel, DoctorNotFound
from app.api.dto.doctor_subs import DoctorSubsDTO


class ApiService(object):

    def __init__(self, repository, tg_client: TelegramClient):
        self.repository = repository
        self.tg_client = tg_client

    def get_doctor_subscribers(self, doctor_id: int) -> DoctorSubsDTO | None:
        try:
            doctor: DoctorSubs = self.repository.get_doctor_subscribers(doctor_id)
        except DoctorNotFound:
            return None

        return DoctorSubsDTO(
            doctor_id=doctor.doctor_id,

            inst_subs_count=doctor.inst_subs_count,
            inst_last_updated_timestamp=doctor.inst_last_updated_timestamp,

            tg_subs_count=doctor.tg_subs_count,
            telegram_short=doctor.subs_short,
            telegram_text=doctor.subs_text,
            tg_last_updated_timestamp=doctor.tg_last_updated_timestamp,
        )

    async def create_doctor(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> None:
        # todo пока фича только под тг работать будет
        if not telegram_channel_name:
            raise RequiredFieldError(field_name=telegram_channel_name)

        try:
            await self.tg_client.get_chat_subscribers(telegram_channel_name)
        except Exception as e:
            raise UnavailableTelegramChannel(channel_name=telegram_channel_name)

        return self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, telegram_channel_name)

    def get_filter_info(self) -> List[str]:
        return self.repository.get_filter_info()

    def doctors_filter(
            self,
            social_media: str,
            min_subscribers: int,
            max_subscribers: int,
            offset: int,
            limit: int,
    ):
        if not social_media or social_media == "" or social_media == SocialNetworkType.ALL:
            return self.repository.doctors_all_filter(
                min_subscribers,
                max_subscribers,
                offset,
                limit,
            )

        if social_media in (
                SocialNetworkType.VK,
                SocialNetworkType.YOUTUBE,
                SocialNetworkType.TELEGRAM,
                SocialNetworkType.INSTAGRAM
        ):
            return self.repository.doctors_filter(
                social_media,
                min_subscribers,
                max_subscribers,
                offset,
                limit,
            )

        return []

    async def update_doctor(self, ):
        # todo
        ...

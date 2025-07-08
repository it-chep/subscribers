from __future__ import annotations

from typing import List
from clients.telegram import TelegramClient

from app.entities.doctor_subs import DoctorSubs, subs_short, subs_text, DoctorSubsByIDs
from app.entities.messengers import SocialNetworkType, Messenger
from app.exception.domain_error import RequiredFieldError, UnavailableTelegramChannel, DoctorNotFound
from app.api.dto.doctor_subs import DoctorSubsDTO, DoctorSubsFilterDTO, DoctorSubsByIDsDTO


class ApiService(object):

    def __init__(self, repository, tg_client: TelegramClient, notification_client):
        self.repository = repository
        self.tg_client = tg_client
        self.notification_client = notification_client

    def get_doctor_subscribers(self, doctor_id: int) -> DoctorSubsDTO | None:
        try:
            doctor: DoctorSubs = self.repository.get_doctor_subscribers(doctor_id)
        except DoctorNotFound:
            return None

        return DoctorSubsDTO(
            doctor_id=doctor.doctor_id,

            inst_subs_count=doctor.inst_subs_count,
            inst_last_updated_timestamp=doctor.inst_last_updated_timestamp,
            instagram_short=subs_short(doctor.inst_subs_count),
            instagram_text=subs_text(doctor.inst_subs_count),

            tg_subs_count=doctor.tg_subs_count,
            telegram_short=subs_short(doctor.tg_subs_count),
            telegram_text=subs_text(doctor.tg_subs_count),
            tg_last_updated_timestamp=doctor.tg_last_updated_timestamp,
        )

    def get_all_subscribers_count(self):
        subs_count, last_updated = self.repository.get_all_subscribers_count()
        return subs_count, subs_text(subs_count), last_updated

    def get_subscribers_by_doctor_ids(self, doctor_ids: list[int]) -> list[DoctorSubsByIDsDTO]:
        result = []
        doctors: list[DoctorSubsByIDs] = self.repository.get_subscribers_by_doctor_ids(doctor_ids)
        for doctor in doctors:
            result.append(DoctorSubsByIDsDTO(
                doctor_id=doctor.doctor_id,
                inst_subs_count=subs_short(doctor.inst_subs_count),
                instagram_text=subs_text(doctor.inst_subs_count),
                tg_subs_count=subs_short(doctor.tg_subs_count),
                telegram_text=subs_text(doctor.tg_subs_count),
            ))

        return result

    async def create_doctor(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> None:
        # todo пока фича только под тг работать будет
        if not telegram_channel_name:
            raise RequiredFieldError(field_name=telegram_channel_name)

        try:
            members_count = await self.tg_client.get_chat_subscribers(telegram_channel_name)
            if members_count == 0:
                raise UnavailableTelegramChannel(channel_name=telegram_channel_name)
        except Exception as e:
            self.notification_client.send_warning_not_found_doctor(doctor_id, "Создание пользователя в Telegram")
            raise UnavailableTelegramChannel(channel_name=telegram_channel_name)

        return self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, telegram_channel_name)

    def get_filter_info(self) -> List[Messenger]:
        return self.repository.get_filter_info()

    def doctors_filter(
            self,
            social_media: list[str],
            min_subscribers: int,
            max_subscribers: int,
            offset: int,
    ) -> List[DoctorSubsFilterDTO]:
        doctors_dto, doctor_subs = list(), list()
        # todo переделать это убожество!!!!!!!!!!!!
        # костыль для запроса и инсты и тг, надо сделать какой-нибудь билдер чтобы собирать запрос из переданных фильров
        if len(social_media) == 2:
            social_media = SocialNetworkType.ALL

        if not social_media or social_media == [] or social_media == SocialNetworkType.ALL:
            doctor_subs: list[DoctorSubs] = self.repository.doctors_all_filter(
                min_subscribers,
                max_subscribers,
                offset,
            )
        if len(social_media) == 1:
            if social_media[0] == SocialNetworkType.TELEGRAM:
                doctor_subs: list[DoctorSubs] = self.repository.doctors_filter_tg(
                    min_subscribers,
                    max_subscribers,
                    offset,
                )
            elif social_media[0] == SocialNetworkType.INSTAGRAM:
                doctor_subs: list[DoctorSubs] = self.repository.doctors_filter_inst(
                    min_subscribers,
                    max_subscribers,
                    offset,
                )

        for doctor_sub in doctor_subs:
            doctors_dto.append(
                DoctorSubsFilterDTO(
                    doctor_id=doctor_sub.doctor_id,
                    inst_short=subs_short(doctor_sub.inst_subs_count),
                    inst_text=subs_text(doctor_sub.inst_subs_count),
                    telegram_short=subs_short(doctor_sub.tg_subs_count),
                    telegram_text=subs_text(doctor_sub.tg_subs_count),
                )
            )

        return doctors_dto

    async def update_doctor(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> bool:
        """Обновление данных о докторе по его ID, если ID нет, то просто создаем доктора"""
        try:
            self.repository.update_doctor(doctor_id, instagram_channel_name, telegram_channel_name)
            return True
        except DoctorNotFound:
            self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, telegram_channel_name)
            return False

    def migrate_instagram(self, doctor_id: int, instagram_channel_name: str) -> bool:
        """Обновление данных о докторе по его ID, если ID нет, то просто создаем доктора"""
        try:
            self.repository.migrate_instagram(doctor_id, instagram_channel_name)
            return True
        except DoctorNotFound:
            self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, None)
            return False


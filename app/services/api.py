from __future__ import annotations

from typing import List

from app.entities.sorted import SortedType
from clients.telegram import TelegramClient

from app.entities.doctor_subs import DoctorSubs, subs_short, subs_text, DoctorSubsByIDs, subs_by_digits
from app.entities.messengers import Messenger
from app.exception.domain_error import DoctorNotFound
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
        return subs_by_digits(subs_count), subs_text(subs_count), last_updated

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
        try:
            self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, telegram_channel_name)
        except Exception as e:
            self.notification_client.send_error_message(str(e), "service_create_doctor")

    def get_filter_info(self) -> List[Messenger]:
        return self.repository.get_filter_info()

    def doctors_filter_with_doctors_ids(
            self,
            social_media: list[str],
            sort_enum: SortedType,
            min_subscribers: int,
            max_subscribers: int,
            limit: int,
            doctor_ids: list[int]
    ):
        doctors_dto, doctor_subs = list(), list()
        doctor_subs: list[DoctorSubs] = self.repository.doctors_filter_with_doctors_ids(
            social_media, sort_enum, min_subscribers, max_subscribers, limit, doctor_ids
        )

        doctors_count, subs_count = self.repository.filtered_doctors_count_with_doctors_ids(
            social_media, min_subscribers, max_subscribers, doctor_ids
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

        return doctors_dto, doctors_count, subs_by_digits(subs_count)

    def doctors_filter(
            self,
            social_media: list[str],
            sort_enum: SortedType,
            min_subscribers: int,
            max_subscribers: int,
            current_page: int,
            limit: int,
    ):
        doctors_dto, doctor_subs = list(), list()
        doctor_subs: list[DoctorSubs] = self.repository.doctors_filter(social_media, sort_enum, min_subscribers,
                                                                       max_subscribers, current_page, limit)
        doctors_count, subs_count = self.repository.filtered_doctors_count(
            social_media, min_subscribers, max_subscribers
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

        return doctors_dto, doctors_count, subs_by_digits(subs_count)

    async def update_doctor(
            self, doctor_id: int,
            instagram_channel_name: str,
            telegram_channel_name: str,
            is_active: bool
    ) -> bool:
        """Обновление данных о докторе по его ID, если ID нет, то просто создаем доктора"""
        if instagram_channel_name or telegram_channel_name:
            try:
                self.repository.update_doctor(doctor_id, instagram_channel_name, telegram_channel_name)
                return True
            except DoctorNotFound:
                self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, telegram_channel_name)
                return False
            except Exception as e:
                self.notification_client.send_error_message(str(e), "service_update_doctor")
                return False
        elif is_active:
            try:
                self.repository.update_doctor_is_active(doctor_id=doctor_id, is_active=is_active)
                return True
            except Exception as e:
                self.notification_client.send_error_message(str(e), "service_update_doctor")
                return False
        return None

    # def migrate_instagram(self, doctor_id: int, instagram_channel_name: str) -> bool:
    #     """Обновление данных о докторе по его ID, если ID нет, то просто создаем доктора"""
    #     try:
    #         self.repository.migrate_instagram(doctor_id, instagram_channel_name)
    #         return True
    #     except DoctorNotFound:
    #         self.repository.create_doctor_subscriber(doctor_id, instagram_channel_name, None)
    #         return False

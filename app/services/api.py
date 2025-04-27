from typing import List
from app.entities.doctor_subs import DoctorSubs, SocialNetworkType


class ApiService(object):

    def __init__(self, repository):
        self.repository = repository

    def get_doctor_subscribers(self, doctor_id: int) -> DoctorSubs:
        return self.repository.get_doctor_subscribers(doctor_id)

    def create_doctor(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> None:
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
        if social_media == "" or social_media == SocialNetworkType.ALL:
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

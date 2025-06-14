from typing import List

from redis.commands.search import query

from clients.postgres import Database
from app.entities.doctor_subs import DoctorSubs
from app.exception.domain_error import DoctorNotFound


class ApiRepository:

    def __init__(self):
        self.db = Database()

    def get_doctor_subscribers(self, doctor_id: int) -> DoctorSubs:
        query = f"""
            select id, 
                doctor_id, 
                instagram_channel_name,
                inst_subs_count,
                inst_last_updated,
                telegram_channel_name,
                tg_subs_count,
                tg_last_updated
            from doctors 
            where doctor_id = %s;
        """
        result = self.db.select(query, (doctor_id,), True)

        try:
            doctor = DoctorSubs(
                internal_id=result[0],
                doctor_id=result[1],
                instagram_channel_name=result[2] or "",
                inst_subs_count=result[3] or 0,
                inst_last_updated_timestamp=result[4],
                telegram_channel_name=result[5] or "",
                tg_subs_count=result[6] or 0,
                tg_last_updated_timestamp=result[7],
            )
        except Exception as e:
            raise DoctorNotFound(doctor_id=doctor_id)

        return doctor

    def create_doctor_subscriber(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> None:
        query = f"""insert into doctors (
                doctor_id, 
                instagram_channel_name,
                telegram_channel_name
        ) 
        values (%s, %s, %s)
        on conflict (doctor_id) do nothing
        returning id;
        """

        try:
            self.db.execute(query, (doctor_id, instagram_channel_name, telegram_channel_name))
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)

    def get_filter_info(self) -> List[str]:
        query = f"""
            select name from social_media where enabled is true;
        """

        medias = list()
        try:
            results = self.db.select(query)
            for result in results:
                medias.append(result[0])
        except Exception as e:
            print("Ошибка при получении информации о фильтрах для соц.cетей", e)

        return medias

    def doctors_all_filter(
            self,
            min_subscribers: int,
            max_subscribers: int,
            offset: int,
    ) -> List[int]:
        query = f"""
            select 
                doctor_id
            from doctors
            where (inst_subs_count > %s and inst_subs_count < %s)
                or (tg_subs_count > %s and tg_subs_count < %s)
            offset %s 
        """

        doctor_ids = list()

        try:
            results = self.db.select(
                query,
                (min_subscribers, max_subscribers, min_subscribers, max_subscribers, offset)
            )
            for result in results:
                doctor_ids.append(result[0])

        except Exception as e:
            print("Ошибка при фильтрации всех каналов докторов", e)

        return doctor_ids

    def doctors_filter(
            self,
            social_media: str,
            min_subscribers: int,
            max_subscribers: int,
            offset: int,
    ):
        subs_count = f"{social_media}_subs_count"
        query = f"""
            select 
                doctor_id
            from doctors
            where {subs_count} > %s and {subs_count} < %s
            offset %s 
        """

        doctor_ids = list()

        try:
            results = self.db.select(
                query,
                (min_subscribers, max_subscribers, offset)
            )
            for result in results:
                doctor_ids.append(result[0])

        except Exception as e:
            print(f"Ошибка при фильтрации по {subs_count} докторов", e)

        return doctor_ids

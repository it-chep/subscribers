from typing import List

from redis.commands.search import query

from clients.postgres import Database
from app.entities.doctor_subs import DoctorSubs


class ApiRepository:

    def __init__(self):
        self.db = Database()

    def get_doctor_subscribers(self, doctor_id: int) -> DoctorSubs:
        query = f"""
            SELECT id, 
                doctor_id, 
                instagram_channel_name,
                inst_subs_count,
                inst_last_updated,
                telegram_channel_name,
                tg_subs_count,
                tg_last_updated
            FROM doctors 
            WHERE doctor_id = %s;
        """
        result = self.db.select(query, (doctor_id,), True)

        return DoctorSubs(
            _id=result[0],
            doctor_id=result[1],
            instagram_channel_name=result[2],
            inst_subs_count=result[3],
            inst_last_updated_timestamp=result[4],
            telegram_channel_name=result[5],
            tg_subs_count=result[6],
            tg_last_updated_timestamp=result[7],
        )

    def create_doctor_subscriber(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> None:
        query = f"""INSERT INTO doctors (
                doctor_id, 
                instagram_channel_name,
                telegram_channel_name
        ) 
        VALUES (%s, %s, %s)
        ON CONFLICT (doctor_id) DO NOTHING
        RETURNING id;
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
            limit: int,
    ) -> List[int]:
        query = f"""
            select 
                doctor_id
            from doctors
            where (inst_subs_count > %s and inst_subs_count < %s)
                or (tg_subs_count > %s and tg_subs_count < %s)
            offset %s 
            limit %s;
        """

        doctor_ids = list()

        try:
            results = self.db.select(
                query,
                (min_subscribers, max_subscribers, min_subscribers, max_subscribers, offset, limit)
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
            limit: int,
    ):
        channel = f"{social_media}_subs_count"
        query = f"""
            select 
                doctor_id
            from doctors
            where {channel} > %s and {channel} < %s
            offset %s 
            limit %s;
        """

        doctor_ids = list()

        try:
            results = self.db.select(
                query,
                ( min_subscribers, max_subscribers, offset, limit)
            )
            for result in results:
                doctor_ids.append(result[0])

        except Exception as e:
            print(f"Ошибка при фильтрации по {channel} докторов", e)

        return doctor_ids

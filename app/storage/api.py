from typing import List

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
    ) -> List[DoctorSubs]:
        query = f"""
            select 
                doctor_id,
                tg_subs_count,
                inst_subs_count
            from doctors
            where (inst_subs_count > %s and inst_subs_count < %s)
                or (tg_subs_count > %s and tg_subs_count < %s)
            offset %s 
        """

        doctors = []

        try:
            results = self.db.select(
                query,
                (min_subscribers, max_subscribers, min_subscribers, max_subscribers, offset)
            )
            for result in results:
                doctors.append(
                    DoctorSubs(
                        internal_id=0,
                        doctor_id=result[0],
                        tg_subs_count=result[1] or 0,
                        inst_subs_count=result[2] or 0,
                    )
                )

        except Exception as e:
            print("Ошибка при фильтрации всех каналов докторов", e)

        return doctors

    def doctors_filter(
            self,
            social_media: str,
            min_subscribers: int,
            max_subscribers: int,
            offset: int,
    ) -> List[DoctorSubs]:
        subs_count = f"{social_media}_subs_count"
        query = f"""
            select 
                doctor_id,
                {subs_count}
            from doctors
            where {subs_count} > %s and {subs_count} < %s
            offset %s 
        """

        doctor = []

        try:
            results = self.db.select(
                query,
                (min_subscribers, max_subscribers, offset)
            )
            for result in results:
                doctor.append(DoctorSubs(
                    internal_id=0,
                    doctor_id=result[0],
                    tg_subs_count=result[1] or 0,
                ))

        except Exception as e:
            print(f"Ошибка при фильтрации по {subs_count} докторов", e)

        return doctor

    def update_doctor(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str):
        query = f"""
        update doctors
        set 
            instagram_channel_name = %s,
            telegram_channel_name = %s
        where doctor_id = %s;
        """

        try:
            rows_count = self.db.execute_with_result(query, (instagram_channel_name, telegram_channel_name, doctor_id))
            if rows_count == 0:
                raise DoctorNotFound(doctor_id=doctor_id)
        except DoctorNotFound as e:
            raise e
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)

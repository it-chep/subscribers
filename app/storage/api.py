import datetime
from typing import List, Optional

from clients.postgres import Database
from app.entities.doctor_subs import DoctorSubs, DoctorSubsByIDs
from app.entities.messengers import Messenger, SocialNetworkType
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

    def get_subscribers_by_doctor_ids(self, doctor_ids: list[int]) -> list[DoctorSubsByIDs]:
        query = f"""
            select
                doctor_id, 
                inst_subs_count,
                tg_subs_count
            from doctors 
            where doctor_id = ANY(%s);
        """
        doctors = list()

        try:
            result = self.db.select(query, (doctor_ids,))

            for r in result:
                doctors.append(DoctorSubsByIDs(
                    doctor_id=r[0],
                    inst_subs_count=r[1] or 0,
                    tg_subs_count=r[2] or 0,
                ))

        except Exception as e:
            print("Ошибка при получении врачей по ids", e)

        return doctors

    def get_all_subscribers_count(self) -> (int, Optional[datetime.datetime]):
        query = f""" 
            select 
                sum(tg_subs_count) + sum(inst_subs_count) AS total_subscribers,
                least(min(tg_last_updated), min(inst_last_updated)) AS last_updated_timestamp
            from doctors;
        """

        try:
            result = self.db.select(query)[0]
            total_subscribers = result[0]
            last_updated_timestamp = result[1]

            return total_subscribers, last_updated_timestamp
        except Exception as e:
            print("Ошибка получения количества подписчиков", e)
            return 0, None

    def create_doctor_subscriber(self, doctor_id: int, instagram_channel_name: str, telegram_channel_name: str) -> None:
        query = f"""insert into doctors (
                doctor_id, 
                instagram_channel_name,
                telegram_channel_name,
                tg_has_subscribed
        ) 
        values (%s, %s, %s, false)
        on conflict (doctor_id) do nothing
        returning id;
        """

        try:
            self.db.execute(query, (doctor_id, instagram_channel_name, telegram_channel_name))
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)

    def get_filter_info(self) -> List[Messenger]:
        query = f"""
            select name, slug from social_media where enabled is true;
        """

        medias = list()
        try:
            results = self.db.select(query)
            for result in results:
                medias.append(
                    Messenger(
                        name=result[0],
                        slug=SocialNetworkType(result[1]),
                    )
                )
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

    # todo переделать это убожество!!!!!!!!!!!!
    def doctors_filter_inst(
            self,
            min_subscribers: int,
            max_subscribers: int,
            offset: int,
    ):
        query = f"""
            select 
                doctor_id,
                tg_subs_count,
                inst_subs_count
            from doctors
            where inst_subs_count > %s and inst_subs_count < %s
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
                    inst_subs_count=result[2] or 0,
                ))

        except Exception as e:
            print(f"Ошибка при фильтрации по ИНСТЕ докторов", e)

        return doctor

    # todo переделать это убожество!!!!!!!!!!!!
    def doctors_filter_tg(
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
            where tg_subs_count > %s and tg_subs_count < %s
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
                    inst_subs_count=result[2] or 0,
                ))

        except Exception as e:
            print(f"Ошибка при фильтрации по ТГ докторов", e)

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

    def migrate_instagram(self, doctor_id: int, instagram_channel_name: str):
        query = f"""
        update doctors
        set 
            instagram_channel_name = %s
        where doctor_id = %s;
        """

        try:
            rows_count = self.db.execute_with_result(query, (instagram_channel_name, doctor_id))
            if rows_count == 0:
                raise DoctorNotFound(doctor_id=doctor_id)
        except DoctorNotFound as e:
            raise e
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)
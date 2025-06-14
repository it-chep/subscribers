from typing import List
from clients.postgres import Database
from app.entities.doctor_subs import DoctorSubs, UpdatedSubsQueue


class UpdateSubscribersRepository:

    def __init__(self):
        self.db = Database()

    def get_instagram_channels(self) -> List[DoctorSubs]:
        """Получает список всех докторов с их Instagram-каналами"""
        query = """
                select id,
                       doctor_id,
                       instagram_channel_name,
                       inst_subs_count,
                       inst_last_updated
                from doctors
                where instagram_channel_name is not null
                  and instagram_channel_name != ''
                """

        try:
            result = self.db.select(query)
            return [
                DoctorSubs(
                    internal_id=row[0],
                    doctor_id=row[1],
                    instagram_channel_name=row[2],
                    inst_subs_count=row[3],
                    inst_last_updated_timestamp=row[4],
                ) for row in result
            ]
        except Exception as e:
            print(f"Error fetching Instagram channels: {str(e)}")
            raise

    def update_instagram_subscribers(self, doctor_id: int, subscribers: int):
        """Обновляет количество подписчиков в Instagram"""
        query = """
                update doctors
                set inst_subs_count   = %s,
                    inst_last_updated = now()
                where doctor_id = %s
                """
        self.db.execute(query, (subscribers, doctor_id))
        self.db.commit()

    def get_telegram_channels(self) -> List[DoctorSubs]:
        """Получает список всех докторов с их Telegram-каналами"""
        query = """
                select id,
                       doctor_id,
                       telegram_channel_name,
                       tg_subs_count,
                       tg_last_updated
                from doctors
                where telegram_channel_name is not null
                  and telegram_channel_name != ''
                """

        try:
            result = self.db.select(query)
            return [
                DoctorSubs(
                    internal_id=row[0],
                    doctor_id=row[1],
                    telegram_channel_name=row[2],
                    tg_subs_count=row[3] or 0,
                    tg_last_updated_timestamp=row[4]
                ) for row in result
            ]
        except Exception as e:
            print(f"Error fetching Instagram channels: {str(e)}")
            raise

    def get_telegram_channels_with_offset(self, offset: int) -> List[DoctorSubs]:
        """Получает список всех докторов с их Telegram-каналами с оффсетом и лимитом для обновления батчами"""
        query = """
                select id,
                       doctor_id,
                       telegram_channel_name,
                       tg_subs_count,
                       tg_last_updated
                from doctors
                where telegram_channel_name is not null
                  and telegram_channel_name != ''
                  and id > %s
                order by id
                limit 2
                """

        try:
            result = self.db.select(query, (offset,))
            return [
                DoctorSubs(
                    internal_id=row[0],
                    doctor_id=row[1],
                    telegram_channel_name=row[2],
                    tg_subs_count=row[3] or 0,
                    tg_last_updated_timestamp=row[4]
                ) for row in result
            ]
        except Exception as e:
            print(f"Error fetching telegram channels with offset: {str(e)}")
            raise

    def update_telegram_subscribers(self, doctor_id: int, subscribers: int):
        """Обновляет количество подписчиков в Telegram"""
        query = """
                update doctors
                set tg_subs_count   = %s,
                    tg_last_updated = now()
                where doctor_id = %s
                """
        self.db.execute(query, (subscribers, doctor_id))
        self.db.commit()

    def commit_update_subscribers(self, subscribers_id: int, doctor_id: int):
        """Коммитит обновление подписчиков в update_subscribers_queue"""
        query = """
                insert into update_subscribers_queue (id, last_updated_id, last_updated_at, id_in_subscribers)
                values (1, %s, now(), %s)
                on conflict (id) do update set last_updated_id   = excluded.last_updated_id,
                                               last_updated_at   = now(),
                                               id_in_subscribers = excluded.id_in_subscribers
                """
        self.db.execute(query, (doctor_id, subscribers_id))
        self.db.commit()

    def get_last_updated_doctor(self) -> List[UpdatedSubsQueue]:
        """Получение данных об обновлении подписчиков из update_subscribers_queue"""
        query = """
                select id, last_updated_id, id_in_subscribers, last_updated_at
                from update_subscribers_queue;
                """

        try:
            result = self.db.select(query)
            # если никого нет, значит это первое обновление
            if len(result) == 0:
                doctors = self.get_telegram_channels_with_offset(0)
                self.commit_update_subscribers(doctors[0].internal_id, doctors[0].doctor_id)
                return []

            return [
                UpdatedSubsQueue(
                    _id=row[0],
                    last_updated_id=row[1],
                    id_in_subscribers=row[2],
                    last_updated_at=row[3],
                ) for row in result
            ]
        except Exception as e:
            print(f"Error fetching last_updated_doctor: {str(e)}")
            raise

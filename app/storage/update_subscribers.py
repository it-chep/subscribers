from typing import List
from clients.postgres import Database
from app.entities.doctor_subs import DoctorSubs


class UpdateSubscribersRepository:

    def __init__(self):
        self.db = Database()

    def get_instagram_channels(self) -> List[DoctorSubs]:
        """Получает список всех докторов с их Instagram-каналами"""
        query = """
            select 
                id, 
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
                    _id=row[0],
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
            set 
                inst_subs_count = %s,
                inst_last_updated = now()
            where doctor_id = %s
        """
        self.db.execute(query, (subscribers, doctor_id))
        self.db.commit()

    def get_telegram_channels(self) -> List[DoctorSubs]:
        """Получает список всех докторов с их Telegram-каналами"""
        query = """
            select 
                id, 
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
                    _id=row[0],
                    doctor_id=row[1],
                    telegram_channel_name=row[2],
                    tg_subs_count=row[3],
                    tg_last_updated_timestamp=row[4]
                ) for row in result
            ]
        except Exception as e:
            print(f"Error fetching Instagram channels: {str(e)}")
            raise

    def update_telegram_subscribers(self, doctor_id: int, subscribers: int):
        """Обновляет количество подписчиков в Telegram"""
        query = """
            update doctors
            set 
                tg_subs_count = %s,
                tg_last_updated = now()
            where doctor_id = %s
        """
        self.db.execute(query, (subscribers, doctor_id))
        self.db.commit()

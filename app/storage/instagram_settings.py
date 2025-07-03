from datetime import datetime
from clients.postgres import Database
from app.entities.instagram_settings import InstagramSettings


class InstagramSettingsRepository:

    def __init__(self):
        self.db = Database()

    def get_instagram_settings(self) -> InstagramSettings:
        """Получает настройки для получения инстаграм"""
        query = """
                select 
                    req_capacity,
                    filled_capacity,
                    last_updated_time,
                    long_access_token,
                    short_access_token,
                    is_active
                from instagram_api_settings
                where id = 1
                """

        try:
            result = self.db.select(query, fetch_one=True)
            return InstagramSettings(
                req_capacity=result[0] or 0,
                filled_capacity=result[1] or 0,
                last_updated_time=result[2] or datetime.now(),
                long_access_token=result[3] or "",
                short_access_token=result[4] or "",
                is_active=result[5] or False,
            )
        except Exception as e:
            print(f"Error fetching Instagram Settings: {str(e)}")
            raise

    def update_token_info(self, long_lived_token: str):
        """Обновляет информацию о долгом токене, включает работу инстаграм"""
        query = """
                update instagram_api_settings
                set 
                    long_access_token = %s,
                    is_active = true
                where id = 1
                """
        self.db.execute(query, (long_lived_token,))
        self.db.commit()

    def turn_of_token(self):
        """Выключаем возможность получать подписчиков из инсты"""
        query = """
                update instagram_api_settings
                set 
                    is_active = false
                where id = 1
                """
        self.db.execute(query, ())
        self.db.commit()

    def increment_filled_capacity(self):
        """Инкрементит выполненные к инстаграм запрос"""
        query = """
                update instagram_api_settings 
                set 
                    filled_capacity = filled_capacity + 1 
                where id = 1;
                """

        self.db.execute(query, ())
        self.db.commit()

    def clear_filled_capacity(self):
        """Очищает параметр количества Выполненных запросов"""
        query = """
                update instagram_api_settings 
                set 
                    filled_capacity = 0,
                    last_updated_time = now()
                where id = 1;
                """

        self.db.execute(query, ())
        self.db.commit()

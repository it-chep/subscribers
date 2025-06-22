import requests

from config.config import app_config


class SaleBotClient:
    def __init__(self):
        self.SALEBOT_API_URL = f"https://chatter.salebot.pro/api/{app_config.salebot.api_key}/callback"

    def send_message(self, data):
        """Отправка сообщения ОБЯЗАТЕЛЬНО в data должны быть "message" и "client_id" """
        try:
            response = requests.post(self.SALEBOT_API_URL, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(e)

    def send_error_message(self, error_text: str, error_place: str):
        """Отправка сообщения об ошибке"""
        data = {
            "error_place": error_place,
            "error_message": error_text,
            "message": "subscribers_error",
            "client_id": app_config.salebot.admin_chat_id
        }

        try:
            response = requests.post(self.SALEBOT_API_URL, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(e)

    def send_warning_not_found_doctor(self, doctor_id: int, social_media: str, channel_name: str):
        """Отправка уведомления о том, что не удалось получить количество подписчиков доктора"""
        data = {
            "doctor_id": doctor_id,
            "social_media": social_media,
            "channel_name": channel_name,
            "message": "doctor_not_found",
            "client_id": app_config.salebot.admin_chat_id
        }

        try:
            response = requests.post(self.SALEBOT_API_URL, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(e)

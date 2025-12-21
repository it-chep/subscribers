from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.config import app_config


class YouTubeClient:
    def __init__(self):
        """
        Инициализация с API ключом
        """
        self.youtube = build('youtube', 'v3', developerKey=app_config.youtube.api_key)

    def get_subscribers_count(self, username: str) -> int:
        """
        Получить информацию о канале по username
        """
        try:
            # Ищем канал по username
            search_response = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                forHandle=username
            ).execute()

            if not search_response.get('items'):
                return 0

            channel_data = search_response['items'][0]

            return int(channel_data['statistics'].get('subscriberCount', 0))
        except HttpError as e:
            print(f"Ошибка при получении канала {username}: {e}")
            return 0

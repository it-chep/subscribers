import instagrapi
import instaloader

from instagrapi import Client
from instagrapi.exceptions import UserNotFound
from config.config import app_config


class AnonymousClient(object):
    client: instaloader.Instaloader

    def __init__(self):
        self.client = instaloader.Instaloader()
        self.client.request_timeout = (5, 60)
        self.client.sleep = True
        self.client.max_connection_attempts = 3

    def get_profile_subscribers(self, username: str) -> int:
        """Получение количества подписчиков профиля"""

        try:
            profile = instaloader.Profile.from_username(self.client.context, username)
            return profile.followers
        except Exception as e:
            print(f"Error getting subscribers in INSTAnonymousClient.get_profile_subscribers: {e}")
            raise


class WithLoginClient(object):
    client: instagrapi.Client

    def __init__(self):
        self.client = Client()
        session_file = "../instagram_session.json"
        try:
            self.client.load_settings(session_file)
            self.client.login(app_config.instagram.username, app_config.instagram.password)
        except Exception:
            # Если не получилось, логинимся заново
            self.client.login(app_config.instagram.username, app_config.instagram.password)
            self.client.dump_settings(session_file)

    def get_profile_subscribers(self, username: str) -> int:
        """Получение количества подписчиков профиля"""

        try:
            profile = self.client.user_info_by_username(username)
            if not profile:
                return 0
            return profile.follower_count
        except UserNotFound:
            return 0
        except Exception as e:
            raise e

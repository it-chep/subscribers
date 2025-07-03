import requests

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
        session_file = "/app/instagram_session.json"
        try:
            self.client.load_settings(session_file)
            self.client.login(app_config.instagrapi.username, app_config.instagrapi.password)
        except Exception:
            # Если не получилось, логинимся заново
            self.client.login(app_config.instagrapi.username, app_config.instagrapi.password)
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


class InstagramGraphApiClient:
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v23.0"
        self.app_id = app_config.instagramGraphApi.app_id
        self.app_secret = app_config.instagramGraphApi.app_secret
        self.fb_business_account_id = app_config.instagramGraphApi.fb_business_account_id

    def authenticate(self, short_lived_token: str) -> str:
        """Получаем long lived access token"""

        url = f"{self.base_url}/oauth/access_token"
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "fb_exchange_token": short_lived_token
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()["access_token"]
        return ""

    def _get_subscribers_count(self, username: str, token: str) -> int:
        """Получаем количество подписчиков"""

        params = {
            "fields": f"business_discovery.username({username}){{followers_count}}",
            "access_token": token
        }

        url = f"{self.base_url}/{self.fb_business_account_id}"

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 400:
            return 0
        if response.status_code == 200:
            data = response.json()
            return int(data['business_discovery']['followers_count'])
        return -1

    def get_profile_subscribers(self, username: str, token: str) -> int:
        """Получение количества подписчиков профиля"""

        return self._get_subscribers_count(username, token)

    # def _get_accounts(self) -> Dict:
    #     """Шаг 1️⃣: Получаем список страниц и их токены"""
    #     return self._make_request("/me/accounts")
    #
    # def _get_instagram_business_id(self, page_id: str) -> str:
    #     """Шаг 2️⃣: Получаем ID бизнес-аккаунта Instagram"""
    #     data = self._make_request(f"/{page_id}", {"fields": "instagram_business_account"})
    #     self.ig_business_id = data['instagram_business_account']['id']
    #     return self.ig_business_id

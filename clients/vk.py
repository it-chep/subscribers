import requests

from urllib.parse import urlencode

from config.config import app_config


class VkClient:
    api_url = "https://api.vk.com/method/groups.getMembers"
    app_version = 5.199

    def get_subscribers_count(self, username: str) -> int:
        """Получение подписчиков паблика в вк"""

        params = {
            'access_token': app_config.vk.api_key,
            'group_id': username,
            'v': self.app_version
        }

        url = f"{self.api_url}?{urlencode(params)}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                return 0

            return data['response']['count']

        except Exception as e:
            return 0

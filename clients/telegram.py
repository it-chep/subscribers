import pyrogram

from app.exception.domain_error import IsNotTelegramChannel
from config.config import app_config

CLIENT_NAME = "medblogers_base"


class TelegramClient(object):
    client: pyrogram.Client

    def __init__(self):
        self.client = pyrogram.Client(
            name=CLIENT_NAME,
            api_id=app_config.telegram.app_id,
            api_hash=app_config.telegram.app_hash,
        )
        self._is_connected = False

    async def start(self):
        if not self._is_connected:
            await self.client.start()
            self._is_connected = True

    async def get_chat_subscribers(self, chat_id: str) -> int:
        """Получение количества подписчиков канала"""

        if not self._is_connected:
            await self.start()

        try:
            channel = await self.client.get_chat(chat_id)
            if not channel.members_count:
                raise IsNotTelegramChannel(channel_name=chat_id)

            return channel.members_count

        except Exception as e:
            print(f"Error getting subscribers in TelegramClient.get_chat_subscribers: {e}")
            raise e

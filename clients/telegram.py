import pyrogram
from pyrogram.errors.exceptions import FloodWait, UserAlreadyParticipant, UsernameNotOccupied
from app.exception.update_error import FloodWaitError, UsernameNotOccupiedError
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

    # async def _get_subs_from_closed_channel(self, chat_id):
    #     """Получение подписчиков из закрытого канала"""
    #     try:
    #         channel = await self.client.join_chat(chat_id)
    #     except UserAlreadyParticipant:
    #         return await self._get_subs_from_open_channel(chat_id)
    #
    #     return channel.members_count or 0

    async def subscribe_to_channel(self, chat_id) -> bool:
        """Подписаться на канал"""
        if not self._is_connected:
            await self.start()

        try:
            channel = await self.client.join_chat(chat_id)
            return True
        except Exception as ex:
            return False

    async def _get_subs_from_open_channel(self, chat_id):
        """Получение подписчиков из открытого канала"""
        channel = await self.client.get_chat(chat_id)
        if not channel.members_count:
            raise IsNotTelegramChannel(channel_name=chat_id)

        return channel.members_count

    async def get_chat_subscribers(self, chat_id: str, has_subscribed: bool) -> int:
        """Получение количества подписчиков канала"""

        if not self._is_connected:
            await self.start()

        try:
            if not has_subscribed:
                await self.subscribe_to_channel(chat_id)
            return await self._get_subs_from_open_channel(chat_id)
        except FloodWait as e:
            raise FloodWaitError(duration_in_seconds=e.value)
        except UsernameNotOccupied:
            raise UsernameNotOccupiedError(username=chat_id)
        except Exception as e:
            print(f"Error getting subscribers in TelegramClient.get_chat_subscribers: {e}")
            raise e

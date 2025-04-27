import asyncio
import time
import logging

logger = logging.getLogger(__name__)


class UpdateSubscribersService(object):
    def __init__(
            self,
            repository,
            # anonim_instagram_client,
            # instagram_client,
            telegram_client
    ):
        self.repo = repository
        # self.anonim_instagram_client = anonim_instagram_client
        # self.instagram_client = instagram_client
        self.telegram_client = telegram_client

    async def _update_inst_subscribers(self):
        """ Обновляет количество подписчиков в инсте """
        instagram_channels = self.repo.get_instagram_channels()
        for channel in instagram_channels:
            try:
                subs_count = await self.instagram_client.get_profile_subscribers(channel.instagram_channel_name)
                print(f"Количество подписчиков INST {channel.instagram_channel_name} = {subs_count}")
                self.repo.update_instagram_subscribers(channel.doctor_id, subs_count)

                time.sleep(60)
            except Exception as ex:
                logger.error("error updating instagram subscribers", ex)
                continue

    async def _update_tg_subscribers(self):
        """ Обновляет количество подписчиков в тг """
        telegram_channels = self.repo.get_telegram_channels()
        for channel in telegram_channels:
            try:
                subs_count = await self.telegram_client.get_chat_subscribers(channel.telegram_channel_name)
                print(f"Количество подписчиков ТГ {channel.telegram_channel_name} = {subs_count}")
                self.repo.update_telegram_subscribers(channel.doctor_id, subs_count)
            except Exception as ex:
                logger.error("error updating telegram subscribers", ex)
                continue

    async def update_subscribers(self):
        """ Обновляет количество подписчиков """
        # параллельно обновляем подписчиков в инсте и в тг
        await asyncio.gather(
            # self._update_inst_subscribers(),
            self._update_tg_subscribers()
        )

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

    # async def _update_inst_subscribers(self):
    #     """ Обновляет количество подписчиков в инсте """
    #     instagram_channels = self.repo.get_instagram_channels()
    #     for channel in instagram_channels:
    #         try:
    #             subs_count = await self.instagram_client.get_profile_subscribers(channel.instagram_channel_name)
    #             print(f"Количество подписчиков INST {channel.instagram_channel_name} = {subs_count}")
    #             self.repo.update_instagram_subscribers(channel.doctor_id, subs_count)
    #
    #             time.sleep(60)
    #         except Exception as ex:
    #             logger.error("error updating instagram subscribers", ex)
    #             continue

    async def _batched_update_tg_subscribers(self):
        # получаем последнего обновленного доктора
        result = self.repo.get_last_updated_doctor()
        if len(result) == 0:
            return
        # пока у нас обновляется только 1 строчка
        last_updated_doctor = result[0]

        # Получаем каналы с офсетом
        telegram_channels = self.repo.get_telegram_channels_with_offset(last_updated_doctor.id_in_subscribers)
        # если мы всех обошли, то начинаем с id = 1, то есть offset = 0
        if len(telegram_channels) == 0:
            telegram_channels = self.repo.get_telegram_channels_with_offset(offset=0)

        for channel in telegram_channels:
            try:
                # получаем подписчиков у доктора
                subs_count = await self.telegram_client.get_chat_subscribers(chat_id=channel.telegram_channel_name)
                # обновляем подписчиков доктора
                self.repo.update_telegram_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)
                # комитим id последнего доктора
                self.repo.commit_update_subscribers(subscribers_id=channel.internal_id, doctor_id=channel.doctor_id)
            except Exception as ex:
                logger.error("error updating telegram subscribers", ex)
                continue


    async def _update_tg_subscribers(self):
        """ Обновляет количество подписчиков в тг """
        telegram_channels = self.repo.get_telegram_channels()
        for channel in telegram_channels:
            try:
                subs_count = await self.telegram_client.get_chat_subscribers(channel.telegram_channel_name)
                self.repo.update_telegram_subscribers(channel.doctor_id, subs_count)
            except Exception as ex:
                logger.error("error updating telegram subscribers", ex)
                continue

    async def update_subscribers(self):
        """ Обновляет количество подписчиков """
        # параллельно обновляем подписчиков в инсте и в тг
        await asyncio.gather(
            # self._update_inst_subscribers(),
            self._batched_update_tg_subscribers()
        )

import asyncio
import time
import logging

from app.entities.doctor_subs import DoctorSubs
from app.exception.update_error import FloodWaitError, UsernameNotOccupiedError

logger = logging.getLogger(__name__)


class UpdateSubscribersService(object):
    def __init__(
            self,
            repository,
            # anonim_instagram_client,
            # instagram_client,
            telegram_client,
            notification_client
    ):
        self.repo = repository
        self.notification_client = notification_client
        # self.anonim_instagram_client = anonim_instagram_client
        # self.instagram_client = instagram_client
        self.telegram_client = telegram_client

    async def _batched_update_inst_subscribers(self):
        # получаем последнего обновленного доктора
        result = self.repo.get_last_updated_instagram_doctor()
        if len(result) == 0:
            return
        # пока у нас обновляется только 1 строчка
        last_updated_doctor = result[0]

        # Получаем каналы с офсетом
        instagram_channels = self.repo.get_instagram_channels_with_offset(last_updated_doctor.id_in_subscribers)
        # если мы всех обошли, то начинаем с id = 1, то есть offset = 0
        if len(instagram_channels) == 0:
            instagram_channels = self.repo.get_instagram_channels_with_offset(offset=0)

        for channel in instagram_channels:
            try:
                # получаем подписчиков у доктора
                subs_count = self.instagram_client.get_profile_subscribers(channel.instagram_channel_name)
                # комитим id последнего доктора
                self.repo.commit_update_instagram_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети, при этом не коммитим данные
                if subs_count == 0 or not subs_count:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="INSTAGRAM",
                        channel_name=channel.instagram_channel_name
                    )
                    return

                # обновляем подписчиков доктора после коммита в очереди и проверки на 0
                self.repo.update_instagram_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)

            except Exception as ex:
                # комитим id последнего доктора
                self.repo.commit_update_instagram_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                self.notification_client.send_error_message(
                    str(ex) + f"doctorID: {channel.doctor_id}, username: {str(channel.instagram_channel_name)}",
                    "_batched_update_inst_subscribers"
                )
                continue

    async def _subscribe_to_channel(self, channel: DoctorSubs) -> DoctorSubs:
        # если бот не подписан на ТГ канал, то подписываемся
        if not channel.tg_has_subscribed:
            subs_count = await self.telegram_client.subscribe_to_channel(channel.telegram_channel_name)
            if subs_count == 0 or not subs_count:
                self.notification_client.send_error_message(
                    f"Ошибка при подписке на канал пользователя {channel.telegram_channel_name}",
                    "_batched_update_tg_subscribers"
                )
            else:
                self.repo.update_tg_has_subscribed(doctor_id=channel.doctor_id)
                channel.tg_has_subscribed = True

        return channel

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
                # Подписываемся на канал при необходимости
                channel: DoctorSubs = await self._subscribe_to_channel(channel)
                # получаем подписчиков у доктора
                subs_count = await self.telegram_client.get_chat_subscribers(
                    chat_id=channel.telegram_channel_name, has_subscribed=channel.tg_has_subscribed
                )
                # комитим id последнего доктора
                self.repo.commit_update_subscribers(subscribers_id=channel.internal_id, doctor_id=channel.doctor_id)
                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети, при этом не коммитим данные
                if subs_count == 0 or not subs_count:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="Telegram",
                        channel_name=channel.telegram_channel_name,
                    )
                    continue

                # обновляем подписчиков доктора
                self.repo.update_telegram_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)

            except FloodWaitError as ex:
                # комитим id последнего доктора
                self.repo.commit_update_subscribers(subscribers_id=channel.internal_id, doctor_id=channel.doctor_id)
                self.notification_client.send_error_message(
                    str(ex), "_batched_update_tg_subscribers"
                )
                await asyncio.sleep(ex.duration_in_seconds)

            except UsernameNotOccupiedError as ex:
                # комитим id последнего доктора
                self.repo.commit_update_subscribers(subscribers_id=channel.internal_id, doctor_id=channel.doctor_id)
                self.notification_client.send_warning_not_found_doctor(
                    doctor_id=channel.doctor_id,
                    social_media="Telegram",
                    channel_name=channel.telegram_channel_name,
                )
                continue
            except Exception as ex:
                # комитим id последнего доктора
                self.repo.commit_update_subscribers(subscribers_id=channel.internal_id, doctor_id=channel.doctor_id)
                self.notification_client.send_error_message(
                    str(ex) + f"doctorID: {channel.doctor_id}, username: {str(channel.telegram_channel_name)}",
                    "_batched_update_tg_subscribers"
                )
                continue

    async def update_subscribers(self):
        """ Обновляет количество подписчиков """
        # параллельно обновляем подписчиков в инсте и в тг
        await asyncio.gather(
            # self._batched_update_inst_subscribers(),
            self._batched_update_tg_subscribers()
        )

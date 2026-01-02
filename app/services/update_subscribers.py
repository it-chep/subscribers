import asyncio
import os
from datetime import datetime, timedelta
import logging

from dotenv import load_dotenv
from app.exception.update_error import FloodWaitError, UsernameNotOccupiedError

from app.entities.doctor_subs import DoctorSubs
from app.entities.instagram_settings import InstagramSettings

logger = logging.getLogger(__name__)
load_dotenv()


class UpdateSubscribersService(object):
    def __init__(
            self,
            repository,
            instagram_repo,
            instagram_client,
            telegram_client,
            youtube_client,
            vk_client,
            notification_client
    ):
        self.repo = repository
        self.instagram_repo = instagram_repo
        self.notification_client = notification_client
        self.instagram_client = instagram_client
        self.telegram_client = telegram_client
        self.youtube_client = youtube_client
        self.vk_client = vk_client

    def _refresh_instagram_request_limits(self, settings: InstagramSettings):
        """
        Автоматически сбрасывает счетчик запросов, если прошел час с последнего запроса.

        Args:
            settings (InstagramSettings): Текущие настройки лимитов API

        На момент 03.07.2025 Instagram Graph API имеет лимит:
        - 200 запросов в час на 1 access token
        - Окно сброса: ровно через 1 час после первого запроса
        """

        reset_time = settings.last_updated_time + timedelta(hours=1)
        current_time = datetime.now()
        if current_time >= reset_time:
            self.instagram_repo.clear_filled_capacity()

    def _get_instagram_token_info(self) -> InstagramSettings:
        """Получение информации о токене инстаграм"""
        settings: InstagramSettings = self.instagram_repo.get_instagram_settings()

        # Обновляем счетчик запрос. Делать это до запроса в целом не критично,
        # тк мы спокойно можем позволить себе пропустить 1 итерацию обновления
        self._refresh_instagram_request_limits(settings)

        # Если достигли лимит часа, то идем спать 196 <= 200 <= 201
        if settings.filled_capacity <= settings.req_capacity <= settings.filled_capacity + 5:
            self.notification_client.send_error_message(
                "Достигнут лимит запросов к инсте", "_get_instagram_token_info"
            )
            settings.long_access_token = ""
            return settings

        # если у нас есть активный токен, возвращаем его
        if settings.is_active:
            return settings

        # получаем новый токен
        long_lived_token = self.instagram_client.authenticate(settings.short_access_token)
        if long_lived_token == "":
            self.instagram_repo.turn_of_token()
            self.instagram_repo.increment_filled_capacity()
            self.notification_client.send_error_message(
                "Не удалось получить токен INSTAGRAM или он не валиден. Надо срочно что-то сделать",
                "_get_instagram_token_info"
            )
            settings.long_access_token = ""
            return settings

        # сохраняем новый токен
        self.instagram_repo.update_token_info(long_lived_token)
        settings.long_access_token = long_lived_token
        return settings

    def _get_instagram_channels(self) -> list[DoctorSubs]:
        # получаем последнего обновленного доктора
        result = self.repo.get_last_updated_instagram_doctor()
        if len(result) == 0:
            return []
        # пока у нас обновляется только 1 строчка
        last_updated_doctor = result[0]

        # Получаем каналы с офсетом
        instagram_channels = self.repo.get_instagram_channels_with_offset(last_updated_doctor.id_in_subscribers)
        # если мы всех обошли, то начинаем с id = 1, то есть offset = 0
        if len(instagram_channels) == 0:
            instagram_channels = self.repo.get_instagram_channels_with_offset(offset=0)

        # делаем превалидацию данных, чтобы не делать лишний запросов
        prevalidated_channels = []
        for channel in instagram_channels:
            if "http" in channel.instagram_channel_name:
                self.notification_client.send_warning_not_found_doctor(
                    doctor_id=channel.doctor_id,
                    social_media="INSTAGRAM",
                    channel_name=channel.instagram_channel_name
                )
                continue

            prevalidated_channels.append(channel)

        return prevalidated_channels

    async def _batched_update_inst_subscribers(self):
        # получение информации о токене инстаграмма, если его нет, то надо делать датафикс и обновлять руками
        settings = self._get_instagram_token_info()
        if settings.long_access_token == "":
            return

        instagram_channels = self._get_instagram_channels()

        for channel in instagram_channels:
            try:
                # получаем подписчиков у доктора
                subs_count = self.instagram_client.get_profile_subscribers(
                    channel.instagram_channel_name, settings.long_access_token
                )
                # комитим id последнего доктора
                self.repo.commit_update_instagram_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                if subs_count == -1:
                    self.notification_client.send_error_message(
                        "ПРОТУХ ТОКЕН ДЛЯ ИНСТАГРАМ, надо срочно его починить или там другая ошибка",
                        "_batched_update_inst_subscribers"
                    )
                    self.instagram_repo.turn_of_token()

                # Обновляем лимит запросов к инстаграм
                self.instagram_repo.increment_filled_capacity(settings.filled_capacity)

                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети, при этом не коммитим данные
                if subs_count == 0 or not subs_count:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="INSTAGRAM",
                        channel_name=channel.instagram_channel_name
                    )
                    continue

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
            has_subscribed = await self.telegram_client.subscribe_to_channel(channel.telegram_channel_name)
            if not has_subscribed:
                self.notification_client.send_error_message(
                    f"Ошибка при подписке на канал пользователя {channel.telegram_channel_name}",
                    "_batched_update_tg_subscribers"
                )
            else:
                self.repo.update_tg_has_subscribed(doctor_id=channel.doctor_id)
                channel.tg_has_subscribed = True

        return channel

    def _get_telegram_channels(self) -> list[DoctorSubs]:
        # получаем последнего обновленного доктора
        result = self.repo.get_last_updated_doctor()
        if len(result) == 0:
            return []
        # пока у нас обновляется только 1 строчка
        last_updated_doctor = result[0]

        # Получаем каналы с офсетом
        telegram_channels = self.repo.get_telegram_channels_with_offset(last_updated_doctor.id_in_subscribers)
        # если мы всех обошли, то начинаем с id = 1, то есть offset = 0
        if len(telegram_channels) == 0:
            telegram_channels = self.repo.get_telegram_channels_with_offset(offset=0)
        return telegram_channels

    async def _batched_update_tg_subscribers(self):
        telegram_channels = self._get_telegram_channels()

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

    async def _get_youtube_channels(self) -> list[DoctorSubs]:
        # получаем последнего обновленного доктора
        result = self.repo.get_last_updated_youtube_doctor()
        if len(result) == 0:
            return []
        # пока у нас обновляется только 1 строчка
        last_updated_doctor = result[0]

        # Получаем каналы с офсетом
        instagram_channels = self.repo.get_youtube_channels_with_offset(last_updated_doctor.id_in_subscribers)
        # если мы всех обошли, то начинаем с id = 1, то есть offset = 0
        if len(instagram_channels) == 0:
            instagram_channels = self.repo.get_youtube_channels_with_offset(offset=0)

        # делаем превалидацию данных, чтобы не делать лишний запросов
        prevalidated_channels = []
        for channel in instagram_channels:
            if "http" in channel.youtube_channel_name:
                self.notification_client.send_warning_not_found_doctor(
                    doctor_id=channel.doctor_id,
                    social_media="YOUTUBE",
                    channel_name=channel.youtube_channel_name
                )
                continue

            prevalidated_channels.append(channel)

        return prevalidated_channels

    async def _batched_update_youtube_subscribers(self):
        await asyncio.sleep(60 * 5)
        youtube_channels = await self._get_youtube_channels()

        for channel in youtube_channels:
            try:
                # получаем подписчиков у доктора
                subs_count = self.youtube_client.get_subscribers_count(channel.youtube_channel_name)
                # комитим id последнего доктора
                self.repo.commit_update_youtube_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                if subs_count == -1:
                    self.notification_client.send_error_message(
                        "Ошибка получения подписчиков из ЮТУБА",
                        "_batched_update_youtube_subscribers"
                    )

                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети, при этом не коммитим данные
                if subs_count == 0 or not subs_count:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="YOUTUBE",
                        channel_name=channel.youtube_channel_name
                    )
                    continue

                # обновляем подписчиков доктора после коммита в очереди и проверки на 0
                self.repo.update_youtube_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)

            except Exception as ex:
                # комитим id последнего доктора
                self.repo.commit_update_youtube_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                self.notification_client.send_error_message(
                    str(ex) + f"doctorID: {channel.doctor_id}, username: {str(channel.youtube_channel_name)}",
                    "_batched_update_youtube_subscribers"
                )
                continue

    async def _get_vk_channels(self) -> list[DoctorSubs]:
        # получаем последнего обновленного доктора
        result = self.repo.get_last_updated_vk_doctor()
        if len(result) == 0:
            return []
        # пока у нас обновляется только 1 строчка
        last_updated_doctor = result[0]

        # Получаем каналы с офсетом
        vk_channels = self.repo.get_vk_channels_with_offset(last_updated_doctor.id_in_subscribers)
        # если мы всех обошли, то начинаем с id = 1, то есть offset = 0
        if len(vk_channels) == 0:
            vk_channels = self.repo.get_vk_channels_with_offset(offset=0)

        # делаем превалидацию данных, чтобы не делать лишний запросов
        prevalidated_channels = []
        for channel in vk_channels:
            if "http" in channel.vk_channel_name:
                self.notification_client.send_warning_not_found_doctor(
                    doctor_id=channel.doctor_id,
                    social_media="vk",
                    channel_name=channel.vk_channel_name
                )
                continue

            prevalidated_channels.append(channel)

        return prevalidated_channels

    async def _batched_update_vk_subscribers(self):
        await asyncio.sleep(60 * 5)
        vk_channels = await self._get_vk_channels()

        for channel in vk_channels:
            try:
                # получаем подписчиков у доктора
                subs_count = self.vk_client.get_subscribers_count(channel.vk_channel_name)
                # комитим id последнего доктора
                self.repo.commit_update_vk_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                if subs_count == -1:
                    self.notification_client.send_error_message(
                        "Ошибка получения подписчиков из ВК",
                        "_batched_update_vk_subscribers"
                    )

                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети, при этом не коммитим данные
                if subs_count == 0 or not subs_count:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="ВК",
                        channel_name=channel.vk_channel_name
                    )
                    continue

                # обновляем подписчиков доктора после коммита в очереди и проверки на 0
                self.repo.update_vk_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)

            except Exception as ex:
                # комитим id последнего доктора
                self.repo.commit_update_vk_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                self.notification_client.send_error_message(
                    str(ex) + f"doctorID: {channel.doctor_id}, username: {str(channel.vk_channel_name)}",
                    "_batched_update_vk_subscribers"
                )
                continue

    async def update_subscribers(self):
        """ Обновляет количество подписчиков """
        tasks = []

        inst_update = os.getenv('INST_UPDATE', '').lower() == 'true'
        tg_update = os.getenv('TG_UPDATE', '').lower() == 'true'
        youtube_update = os.getenv('YOUTUBE_UPDATE', '').lower() == 'true'
        vk_update = os.getenv('VK_UPDATE', '').lower() == 'true'

        if inst_update:
            tasks.append(self._batched_update_inst_subscribers())

        if tg_update:
            tasks.append(self._batched_update_tg_subscribers())

        if youtube_update:
            tasks.append(self._batched_update_youtube_subscribers())

        if vk_update:
            tasks.append(self._batched_update_vk_subscribers())

        if not tasks:
            return

        # Параллельно выполняем выбранные обновления
        await asyncio.gather(*tasks)

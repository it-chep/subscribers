import asyncio
from datetime import datetime, timedelta
import logging

from app.entities.doctor_subs import DoctorSubs
from app.entities.instagram_settings import InstagramSettings

logger = logging.getLogger(__name__)


class UpdateSubscribersService(object):
    def __init__(
            self,
            repository,
            instagram_repo,
            instagram_client,
            telegram_client,
            notification_client
    ):
        self.repo = repository
        self.instagram_repo = instagram_repo
        self.notification_client = notification_client
        self.instagram_client = instagram_client
        self.telegram_client = telegram_client

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

    def _get_instagram_token_info(self) -> str:
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
            return ""

        # если у нас есть активный токен, возвращаем его
        if settings.is_active:
            return settings.long_access_token

        # получаем новый токен
        long_lived_token = self.instagram_client.authenticate(settings.short_access_token)
        if long_lived_token == "":
            self.instagram_repo.turn_of_token()
            self.instagram_repo.increment_filled_capacity()
            self.notification_client.send_error_message(
                "Не удалось получить токен INSTAGRAM или он не валиден. Надо срочно что-то сделать",
                "_get_instagram_token_info"
            )
            return ""

        # сохраняем новый токен
        self.instagram_repo.update_token_info(long_lived_token)
        return long_lived_token

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
        token = self._get_instagram_token_info()
        if token == "":
            return

        instagram_channels = self._get_instagram_channels()

        for channel in instagram_channels:
            try:
                # получаем подписчиков у доктора
                subs_count = self.instagram_client.get_profile_subscribers(channel.instagram_channel_name, token)
                # обновляем подписчиков доктора
                self.repo.update_instagram_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)
                # комитим id последнего доктора
                self.repo.commit_update_instagram_subscribers(
                    subscribers_id=channel.internal_id,
                    doctor_id=channel.doctor_id
                )
                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети
                if subs_count == 0:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="INSTAGRAM",
                        channel_name=channel.instagram_channel_name
                    )
                if subs_count == -1:
                    self.notification_client.send_error_message(
                        "ПРОТУХ ТОКЕН ДЛЯ ИНСТАГРАМ, надо срочно его починить или там другая ошибка",
                        "_batched_update_inst_subscribers"
                    )
                    self.instagram_repo.turn_of_token()

                # Обновляем лимит запросов к инстаграм
                self.instagram_repo.increment_filled_capacity()

            except Exception as ex:
                self.notification_client.send_error_message(str(ex), "_batched_update_inst_subscribers")
                continue

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
                # получаем подписчиков у доктора
                subs_count = await self.telegram_client.get_chat_subscribers(chat_id=channel.telegram_channel_name)
                # обновляем подписчиков доктора
                self.repo.update_telegram_subscribers(doctor_id=channel.doctor_id, subscribers=subs_count)
                # комитим id последнего доктора
                self.repo.commit_update_subscribers(subscribers_id=channel.internal_id, doctor_id=channel.doctor_id)
                # если подписчиков 0, то считаем, что не смогли найти доктора в соцсети
                if subs_count == 0:
                    self.notification_client.send_warning_not_found_doctor(
                        doctor_id=channel.doctor_id,
                        social_media="Telegram",
                        channel_name=channel.telegram_channel_name,
                    )
            except Exception as ex:
                self.notification_client.send_error_message(str(ex), "_batched_update_tg_subscribers")
                continue

    async def update_subscribers(self):
        """ Обновляет количество подписчиков """
        # параллельно обновляем подписчиков в инсте и в тг
        await asyncio.gather(
            self._batched_update_inst_subscribers(),
            self._batched_update_tg_subscribers()
        )

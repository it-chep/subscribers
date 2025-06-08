class RequiredFieldError(ValueError):
    """Исключение, возникающее когда обязательное поле не заполнено"""

    def __init__(self, field_name: str, message: str = None):
        """
        :param field_name: Название обязательного поля
        :param message: Кастомное сообщение об ошибке (необязательно)
        """
        self.field_name = field_name
        self.message = message or f"Обязательное поле '{field_name}' не заполнено"
        super().__init__(self.message)

    def __str__(self):
        return self.message


class UnavailableTelegramChannel(Exception):
    """Исключение, возникающее при невозможности получить данные о Telegram-канале"""

    def __init__(self, channel_name: str, reason: str = None, original_exception: Exception = None):
        """
        :param channel_name: Название/идентификатор канала
        :param reason: Причина недоступности (необязательно)
        :param original_exception: Оригинальное исключение (если есть)
        """
        self.channel_name = channel_name
        self.reason = reason
        self.original_exception = original_exception

        self.message = f"Telegram канал '{channel_name}' недоступен"
        if reason:
            self.message += f". Причина: {reason}"

        super().__init__(self.message)

    def __str__(self):
        return self.message


class IsNotTelegramChannel(Exception):
    """Исключение, возникающее когда телеграм пытается получить количество подписчиков не у канала, а у ЖИВОГО пользователя"""

    def __init__(self, channel_name: str, original_exception: Exception = None):
        """
        :param channel_name: Название/идентификатор канала
        :param original_exception: Оригинальное исключение (если есть)
        """
        self.channel_name = channel_name
        self.original_exception = original_exception

        self.message = f"Живой юзер '{channel_name}', невозможно сохранить"

        super().__init__(self.message)

    def __str__(self):
        return self.message

class DoctorNotFound(Exception):
    """Исключение, возникающее когда невозможно найти доктора по ID"""

    def __init__(self, doctor_id: int, original_exception: Exception = None):
        """
        :param doctor_id: Название/идентификатор канала
        :param original_exception: Оригинальное исключение (если есть)
        """
        self.doctor_id = doctor_id
        self.original_exception = original_exception

        self.message = f"Доктор не найден ID: '{doctor_id}'"

        super().__init__(self.message)

    def __str__(self):
        return self.message
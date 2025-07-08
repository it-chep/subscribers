class FloodWaitError(Exception):
    """Исключение, возникающее когда происходит слишком много запросов"""

    def __init__(self, duration_in_seconds):
        self.duration_in_seconds = duration_in_seconds

    def __str__(self):
        return f"Нафлудили, спим {self.duration_in_seconds} секунд"


class UsernameNotOccupiedError(Exception):
    """Исключение, возникающее когда мы не можем найти человека"""

    def __init__(self, username):
        self.username = username

    def __str__(self):
        return f"Не найден человек с username: {self.username}"

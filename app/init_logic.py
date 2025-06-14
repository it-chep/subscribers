from app.services.api import ApiService
from app.storage.api import ApiRepository
from clients.telegram import TelegramClient
from clients.instagram import AnonymousClient, WithLoginClient
from app.services.update_subscribers import UpdateSubscribersService
from app.storage.update_subscribers import UpdateSubscribersRepository

# инициализация клиентов
telegram_client = TelegramClient()
# anonym_instagram_client = AnonymousClient()
# instagram_client = WithLoginClient()

# инициализация репозиториев
update_subs_repo = UpdateSubscribersRepository()
api_repo = ApiRepository()

# инициализация сервисов
update_subs_service = UpdateSubscribersService(
    repository=update_subs_repo,
    # anonim_instagram_client=anonym_instagram_client,
    # instagram_client=instagram_client,
    telegram_client=telegram_client,
)

api_service = ApiService(
    repository=api_repo,
    tg_client=telegram_client
)

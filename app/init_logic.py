# инициализация клиентов
from clients.telegram import TelegramClient
from clients.instagram import InstagramGraphApiClient
from clients.notifications.salebot import SaleBotClient

# инициализация репозиториев
from app.storage.api import ApiRepository
from app.storage.update_subscribers import UpdateSubscribersRepository
from app.storage.instagram_settings import InstagramSettingsRepository

# инициализация сервисов
from app.services.api import ApiService
from app.services.update_subscribers import UpdateSubscribersService

# инициализация клиентов
telegram_client = TelegramClient()
instagram_client = InstagramGraphApiClient()
notification_client = SaleBotClient()
# ____________________________________________

# инициализация репозиториев
update_subs_repo = UpdateSubscribersRepository()
api_repo = ApiRepository()
instagram_settings_repo = InstagramSettingsRepository()
# ____________________________________________

# инициализация сервисов
update_subs_service = UpdateSubscribersService(
    repository=update_subs_repo,
    instagram_repo=instagram_settings_repo,
    instagram_client=instagram_client,
    telegram_client=telegram_client,
    notification_client=notification_client
)

api_service = ApiService(
    repository=api_repo,
    tg_client=telegram_client,
    notification_client=notification_client
)
# ____________________________________________

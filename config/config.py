from ruamel.yaml import YAML
from pydantic import BaseModel

yaml = YAML()
yaml.preserve_quotes = True


class DbConfig(BaseModel):
    host: str
    port: int = 5432
    user: str
    password: str
    name: str


class TelegramConfig(BaseModel):
    app_id: int
    app_hash: str


class InstagrapiConfig(BaseModel):
    username: str
    password: str


class InstagramGraphApiConfig(BaseModel):
    app_id: int
    app_secret: str
    fb_business_account_id: int


class SalebotConfig(BaseModel):
    api_key: str
    admin_chat_id: int


class YouTubeConfig(BaseModel):
    api_key: str


class VKConfig(BaseModel):
    api_key: str


class Config(BaseModel):
    db: DbConfig
    telegram: TelegramConfig
    instagrapi: InstagrapiConfig
    salebot: SalebotConfig
    instagramGraphApi: InstagramGraphApiConfig
    youtube: YouTubeConfig
    vk: VKConfig

    @classmethod
    def load(cls, path: str = "config/values.yaml") -> "Config":
        with open(path) as f:
            data = yaml.load(f)
        return cls(**data)


app_config: Config = Config.load()

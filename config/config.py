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


class InstagramConfig(BaseModel):
    username: str
    password: str


class Config(BaseModel):
    db: DbConfig
    telegram: TelegramConfig
    instagram: InstagramConfig

    @classmethod
    def load(cls, path: str = "config/values.yaml") -> "Config":
        with open(path) as f:
            data = yaml.load(f)
        return cls(**data)


app_config: Config = Config.load()

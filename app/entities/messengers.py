from pydantic import BaseModel
from enum import Enum

class SocialNetworkType(str, Enum):
    """Типы социальных сетей для докторов"""
    ALL = "all"
    INSTAGRAM = "inst"
    TELEGRAM = "tg"
    VK = "vk"
    YOUTUBE = "youtube"


class Messenger(BaseModel):
    name: str
    slug: SocialNetworkType
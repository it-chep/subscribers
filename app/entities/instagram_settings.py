from __future__ import annotations

import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel


class InstagramSettings(BaseModel):
    req_capacity: int
    filled_capacity: int
    last_updated_time: datetime.datetime
    long_access_token: str
    short_access_token: str
    is_active: bool

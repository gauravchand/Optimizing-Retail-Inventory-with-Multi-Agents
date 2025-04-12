from datetime import datetime
from pydantic import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    current_user: str = "AkarshanGupta"
    current_datetime: str = "2025-04-10 12:31:21"
    database_url: str = "sqlite+aiosqlite:///retail_inventory.db"

    class Config:
        env_file = ".env"

    @property
    def datetime_obj(self) -> datetime:
        return datetime.strptime(self.current_datetime, "%Y-%m-%d %H:%M:%S")

@lru_cache()
def get_settings():
    return Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
  db_user: Optional[str] = None
  db_password: Optional[str] = None
  db_name: Optional[str] = None
  db_port: Optional[int] = None
  db_host: Optional[str] = None

settings = Settings()
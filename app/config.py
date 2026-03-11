from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = "MasterArt AI Sales Bot"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_base_url: str = "http://localhost:8000"
    app_log_level: str = "INFO"
    app_debug: bool = False

    database_url: str
    redis_url: str
    internal_api_key: str = "replace_me_internal_key"

    telegram_bot_token: str
    telegram_manager_chat_id: str
    telegram_notify_new_lead: bool = True

    openai_api_key: str = ""
    openai_model: str = "gpt-5.2"
    openai_timeout_seconds: int = 20

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

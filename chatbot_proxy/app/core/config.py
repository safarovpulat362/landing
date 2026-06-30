from pydantic_settings import BaseSettings
from pathlib import Path


class AppConfig(BaseSettings):
    proxy_api_key: str
    proxy_base_url: str = "https://api.proxyapi.ru"
    proxy_path: str = "/gigachat/v1/chat/completions"
    model_name: str = "GigaChat"
    database_url: str = "sqlite+aiosqlite:///./data/chatbot.db"

    model_config = {"env_file": str(Path(__file__).resolve().parent.parent.parent / ".env")}


config = AppConfig()

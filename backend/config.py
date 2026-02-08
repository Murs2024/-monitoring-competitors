"""
Конфигурация приложения. Ключи и параметры из .env.
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Корень проекта: при запуске из exe — папка с exe (там лежит .env и history.json)
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings:
    """Настройки приложения."""

    # OpenAI — изображения и fallback для текста, если нет DEEPSEEK_API_KEY
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_vision_model: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

    # DeepSeek — текст и анализ распарсенных страниц (как в прошлом проекте)
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # API
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # История
    history_file: str = os.getenv("HISTORY_FILE", "history.json")
    max_history_items: int = int(os.getenv("MAX_HISTORY_ITEMS", "10"))

    # Парсер
    parser_timeout: int = int(os.getenv("PARSER_TIMEOUT", "10"))
    parser_user_agent: str = os.getenv(
        "PARSER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    use_selenium: bool = os.getenv("USE_SELENIUM", "false").lower() in ("true", "1", "yes")
    parser_selenium_wait: int = int(os.getenv("PARSER_SELENIUM_WAIT", "5"))

    @property
    def history_path(self) -> Path:
        """Путь к файлу истории (в корне проекта)."""
        return PROJECT_ROOT / self.history_file


settings = Settings()

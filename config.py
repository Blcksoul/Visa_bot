"""
visa-bot/config.py
All configuration values are loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # ── Telegram ─────────────────────────────────────────────────────────────
    TELEGRAM_TOKEN: str
    ADMIN_IDS: List[int] = []          # comma-separated list in .env

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./visa_bot.db"

    # ── Scheduler ────────────────────────────────────────────────────────────
    CHECK_INTERVAL: int = 60           # seconds between slot checks

    # ── Browser ──────────────────────────────────────────────────────────────
    HEADLESS_BROWSER: bool = True

    # ── Proxies ──────────────────────────────────────────────────────────────
    # Comma-separated list of proxy URLs, e.g. http://user:pass@host:port
    PROXY_LIST: Optional[str] = None

    @property
    def proxy_list(self) -> List[str]:
        if not self.PROXY_LIST:
            return []
        return [p.strip() for p in self.PROXY_LIST.split(",") if p.strip()]

    # ── Optional email notifications ─────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # ── CAPTCHA solving (2captcha / anticaptcha) ─────────────────────────────
    CAPTCHA_API_KEY: Optional[str] = None

    # ── Visa centre targets ──────────────────────────────────────────────────
    VFS_BASE_URL: str = "https://visa.vfsglobal.com"
    TLS_BASE_URL: str = "https://fr.tlscontact.com"


settings = Settings()

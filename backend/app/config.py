from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://battle:battle@postgres:5432/counterbattle"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://battle:battle@postgres:5432/counterbattle"

    # TikTok
    TIKTOK_USERNAME: str = ""
    TIKTOK_SESSION_ID: str = ""

    # Battle defaults
    BATTLE_DURATION_SECONDS: int = 300  # 5 minutes
    DEFAULT_COUNTRIES: str = "Turkey,Saudi Arabia,Egypt,Pakistan"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://frontend:3000"

    @property
    def countries_list(self) -> list[str]:
        return [c.strip() for c in self.DEFAULT_COUNTRIES.split(",")]

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

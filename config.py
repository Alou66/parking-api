"""
Configuration centralisée avec pydantic-settings.
Lit automatiquement les variables depuis .env
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de l'application"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    database_url: str = "postgresql://alassane:alou123@localhost:5432/parking_db"
    debug: bool | str = False


@lru_cache
def get_settings() -> Settings:
    """Singleton des paramètres"""
    return Settings()
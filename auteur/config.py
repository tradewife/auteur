"""AUTEUR configuration — loads from environment / .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # API keys
    fal_key: str = ""
    kie_api_key: str = ""
    gemini_api_key: str = ""

    # Output
    auteur_output_dir: Path = Path("./output")

    @property
    def has_fal(self) -> bool:
        return bool(self.fal_key)

    @property
    def has_kie(self) -> bool:
        return bool(self.kie_api_key)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

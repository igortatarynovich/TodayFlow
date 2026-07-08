"""Astro service configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    port: int = 8081
    location_dataset_path: str | None = None  # optional path to gazetteer CSV/JSON

    class Config:
        env_file = ".env"


settings = Settings()

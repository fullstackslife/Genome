"""Configuration management for the RNA State Intelligence Platform."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using pydantic BaseSettings."""

    # API Configuration
    api_title: str = "RNA State Intelligence Platform API"
    api_version: str = "0.1.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Data Paths
    data_dir: Path = Path("data")
    examples_dir: Path = Path("data/examples")
    processed_dir: Path = Path("data/processed")

    # Model Paths
    models_dir: Path = Path("models")
    embeddings_dir: Path = Path("embeddings")

    # Processing Configuration
    random_seed: int = 42

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.examples_dir.mkdir(parents=True, exist_ok=True)
settings.processed_dir.mkdir(parents=True, exist_ok=True)
settings.models_dir.mkdir(parents=True, exist_ok=True)
settings.embeddings_dir.mkdir(parents=True, exist_ok=True)

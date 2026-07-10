# backend/app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Paths
    data_dir: Path = Path.home() / ".doc-assistant"
    db_path: Path = data_dir / "app.db"
    qdrant_path: Path = data_dir / "qdrant"
    cache_path: Path = data_dir / "cache.db"

    # LM Studio
    lm_studio_url: str = "http://localhost:1234"
    embedding_model: str = "nomic-embed-text-v1.5"

    # Arize Phoenix
    phoenix_enabled: bool = True
    phoenix_port: int = 6006

    # API
    host: str = "127.0.0.1"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure data directory exists
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.qdrant_path.mkdir(parents=True, exist_ok=True)
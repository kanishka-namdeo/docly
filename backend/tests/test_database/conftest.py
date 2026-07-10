import pytest
import asyncio
from pathlib import Path
from app.config import settings


@pytest.fixture(autouse=True)
def clean_database():
    """Delete the database file before each test to ensure isolation."""
    db_path = Path(settings.db_path)
    if db_path.exists():
        db_path.unlink()
    yield

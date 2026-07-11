from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.config import settings
from app.database.models import Base

engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.db_path}",
    echo=False,
    future=True
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Add reasoning column if it doesn't exist (for existing databases)
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "ALTER TABLE messages ADD COLUMN reasoning TEXT"
            ))
        except Exception:
            pass  # Column already exists or table doesn't exist yet
        
        # Add is_default column to provider_configs if it doesn't exist
        try:
            from sqlalchemy import text
            await conn.execute(text(
                "ALTER TABLE provider_configs ADD COLUMN is_default BOOLEAN NOT NULL DEFAULT 0"
            ))
        except Exception:
            pass  # Column already exists or table doesn't exist yet

@asynccontextmanager
async def get_db_session():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

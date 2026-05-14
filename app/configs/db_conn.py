import os
import urllib.parse

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()


def _get_async_connection_string_from_env() -> str:
    username = os.getenv("POSTGRES_USER", "postgres")
    password = urllib.parse.quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
    server = os.getenv("POSTGRES_SERVER", "localhost")
    database = os.getenv("POSTGRES_DB", "")
    return f"postgresql+asyncpg://{username}:{password}@{server}/{database}"


async_engine = create_async_engine(
    _get_async_connection_string_from_env(),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=5,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

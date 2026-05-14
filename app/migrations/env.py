import asyncio
import sys
from logging.config import fileConfig
from os import environ, getenv
from pathlib import Path
from urllib.parse import quote_plus
from alembic import context
from dotenv import load_dotenv
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

sys.path.insert(0, str(Path(__file__).parent.parent))
from models import BaseModel

load_dotenv()

if "pytest" not in sys.modules:
    environ["ALEMBIC_RUNNING"] = "True"
    
    db_username = getenv("POSTGRES_USER")
    db_password = getenv("POSTGRES_PASSWORD")
    db_host = getenv("POSTGRES_SERVER")
    db_database = getenv("POSTGRES_DB")

    db_password_encoded = quote_plus(db_password).replace("%", "%%")
    
    db_url = (
        f"postgresql+asyncpg://{db_username}:"
        f"{db_password_encoded}"
        f"@{db_host}/{db_database}"
    )
    
    print(f"Using database URL: {db_url}")
    
    config = context.config

    config.set_main_option("sqlalchemy.url", db_url)
    
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)

    target_metadata = BaseModel.metadata

    def run_migrations_offline() -> None:
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def do_run_migrations(connection) -> None:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

    async def run_migrations_online() -> None:
        connectable = create_async_engine(
            db_url.replace("%%", "%"),
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

        await connectable.dispose()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())
else:
    config = None
    target_metadata = None
import sys
from logging.config import fileConfig
from os import environ, getenv
from urllib.parse import quote_plus
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).parent.parent))

from models import BaseModel

load_dotenv()

if "pytest" not in sys.modules:
    environ["ALEMBIC_RUNNING"] = "True"
    db_username = getenv("MYSQL_USER")
    db_password = getenv("MYSQL_PASSWORD")
    db_host = getenv("MYSQL_SERVER")
    db_database = getenv("MYSQL_DATABASE")
    db_password_encoded = quote_plus(db_password)

    db_url = (
        f"mysql+pymysql://{db_username}:"
        f"{db_password_encoded.replace('%', '%%')}"
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

    def run_migrations_online() -> None:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
else:
    config = None
    target_metadata = None

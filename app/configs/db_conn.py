import logging
import os
import urllib.parse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

_ENGINE_CACHE: dict[str, object] = {}


class MySQLConnection:
    def __init__(
        self,
        *,
        pool_size: int = 10,
        max_overflow: int = 5,
        pool_timeout: int = 30,
        pool_recycle: int = 1800,
        pool_pre_ping: bool = True,
        pool_use_lifo: bool = True,
        no_pool: bool = False,
        dispose_on_exit: bool = False,
    ):
        self.dispose_on_exit = dispose_on_exit
        self.connection_string = self._get_connection_string_from_env()

        if self.connection_string not in _ENGINE_CACHE:
            engine_kwargs = {"pool_pre_ping": pool_pre_ping}

            if no_pool:
                engine_kwargs["poolclass"] = NullPool
            else:
                engine_kwargs.update(
                    pool_size=pool_size,
                    max_overflow=max_overflow,
                    pool_timeout=pool_timeout,
                    pool_recycle=pool_recycle,
                    pool_use_lifo=pool_use_lifo,
                )

            _ENGINE_CACHE[self.connection_string] = create_engine(
                self.connection_string, **engine_kwargs
            )

        self.engine = _ENGINE_CACHE[self.connection_string]
        self.SessionFactory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def _get_connection_string_from_env(self) -> str:
        username = os.getenv("MYSQL_USER", "root")
        password = urllib.parse.quote_plus(os.getenv("MYSQL_PASSWORD", ""))
        server   = os.getenv("MYSQL_SERVER", "localhost")
        database = os.getenv("MYSQL_DATABASE", "")
        return f"mysql+pymysql://{username}:{password}@{server}/{database}"

    def get_session(self) -> Session:
        return self.SessionFactory()

    def get_connection(self):
        return self.engine.connect()

    def close(self):
        if hasattr(self, "engine") and self.engine is not None:
            logging.debug("Disposing engine pool.")
            self.engine.dispose()

    def __enter__(self) -> Session:
        self._local_session = self.get_session()
        return self._local_session

    def __exit__(self, exc_type, exc_value, traceback):
        session: Session = getattr(self, "_local_session", None)
        if session:
            try:
                if exc_type:
                    logging.exception("Error detected — rolling back session.")
                    session.rollback()
                else:
                    logging.debug("Committing session.")
                    session.commit()
            finally:
                logging.debug("Closing session.")
                session.close()
                del self._local_session

        if self.dispose_on_exit:
            self.close()

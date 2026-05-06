from sqlalchemy import insert
from models import SystemLog
from configs.db_conn import PostgresConnection

class LogDAO:
    def create(self, **kwargs) -> None:
        stmt = insert(SystemLog).values(**kwargs)
        
        with PostgresConnection() as session:
            session.execute(stmt)
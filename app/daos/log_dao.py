from sqlalchemy import insert
from models import SystemLog
from configs.db_conn import MySQLConnection

class LogDAO:
    def create(self, **kwargs) -> None:
        stmt = insert(SystemLog).values(**kwargs)
        
        with MySQLConnection() as session:
            session.execute(stmt)
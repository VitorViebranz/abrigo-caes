from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models import SystemLog

class LogDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, **kwargs) -> None:
        stmt = insert(SystemLog).values(**kwargs)
        await self._session.execute(stmt)
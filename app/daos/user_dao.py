import datetime

from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import UserModel as User


class UserDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_page(self, page: int, page_size: int) -> tuple[list[User], int]:
        offset = (page - 1) * page_size
        count_stmt = select(func.count()).select_from(User)
        data_stmt = select(User).order_by(User.id).offset(offset).limit(page_size)

        total_result = await self._session.execute(count_stmt)
        data_result = await self._session.execute(data_stmt)
        total = total_result.scalar_one()
        items = data_result.unique().scalars().all()
        return items, total

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, full_name: str, email: str, hashed_password: str, role_id: int | None) -> User:
        stmt = insert(User).values(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            role_id=role_id,
        )
        await self._session.execute(stmt)
        return await self.get_by_email(email)

    async def update(self, user_id: int, **kwargs) -> User | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        result = await self._session.execute(stmt)
        if result.rowcount == 0:
            return None
        return await self.get_by_id(user_id)

    async def update_active(self, user_id: int, is_active: bool) -> User | None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=is_active)
        )
        result = await self._session.execute(stmt)
        if result.rowcount == 0:
            return None
        return await self.get_by_id(user_id)

    async def update_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        if expires_at.tzinfo is not None:
            expires_at = expires_at.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(token=token, token_expires_at=expires_at)
        )
        await self._session.execute(stmt)

    async def get_by_token(self, token: str) -> User | None:
        stmt = select(User).where(User.token == token)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()
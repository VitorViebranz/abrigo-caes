import datetime

from sqlalchemy import insert, select, update
from models import UserModel as User, UserRole
from configs import MySQLConnection


class UserDAO:

    def __init__(self):
        pass

    def get_all(self) -> list[User]:
        with MySQLConnection() as session:
            stmt = select(User)
            return session.execute(stmt).scalars().all()

    def get_by_email(self, email: str) -> User | None:
        with MySQLConnection() as session:
            stmt = select(User).where(User.email == email)
            return session.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        with MySQLConnection() as session:
            stmt = select(User).where(User.id == user_id)
            return session.execute(stmt).scalar_one_or_none()

    def create(self, full_name: str, email: str, hashed_password: str, role: str = "voluntario") -> User:
        with MySQLConnection() as session:
            stmt = insert(User).values(
                full_name=full_name,
                email=email,
                hashed_password=hashed_password,
                role=role,
            )
            session.execute(stmt)
            session.commit()
            return self.get_by_email(email)

    def update(self, user_id: int, **kwargs) -> User | None:
        with MySQLConnection() as session:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(**kwargs)
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                return None
            session.commit()
            return self.get_by_id(user_id)

    def update_active(self, user_id: int, is_active: bool) -> User | None:
        with MySQLConnection() as session:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(is_active=is_active)
            )
            result = session.execute(stmt)
            if result.rowcount == 0:
                return None
            session.commit()
            return self.get_by_id(user_id)

    def update_token(self, user_id: int, token: str, expires_at: datetime) -> None:
        with MySQLConnection() as session:
            stmt = (
                update(User)
                .where(User.id == user_id)
                .values(token=token, token_expires_at=expires_at)
            )
            session.execute(stmt)

    def get_by_token(self, token: str) -> User | None:
        with MySQLConnection() as session:
            stmt = select(User).where(User.token == token)
            return session.execute(stmt).scalar_one_or_none()
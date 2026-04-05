from sqlalchemy import select
from models import User, UserRole
from configs import MySQLConnection


class UserDAO:

    def __init__(self):
        pass

    def get_all(self) -> list[User]:
        with MySQLConnection() as session:
            return session.execute(select(User)).scalars().all()

    def get_by_email(self, email: str) -> User | None:
        with MySQLConnection() as session:
            return session.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        with MySQLConnection() as session:
            return session.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()

    def create(self, full_name: str, email: str, hashed_password: str, role: str = "voluntario") -> User:
        new_user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        with MySQLConnection() as session:
            session.add(new_user)
            session.flush()
            session.refresh(new_user)
            return new_user

    def update_active(self, user_id: int, is_active: bool) -> User | None:
        with MySQLConnection() as session:
            user = session.execute(
                select(User).where(User.id == user_id)
            ).scalar_one_or_none()
            if user:
                user.is_active = is_active
            return user

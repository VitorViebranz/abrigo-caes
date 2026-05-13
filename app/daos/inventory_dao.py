from __future__ import annotations

from sqlalchemy import case, func, select, update
from sqlalchemy.orm import selectinload

from configs import PostgresConnection
from models import InventoryItemModel, InventoryMovementModel, InventoryMovementType


class InventoryItemDAO:

    def get_page(self, include_inactive: bool, page: int, page_size: int) -> tuple[list[InventoryItemModel], int]:
        with PostgresConnection() as session:
            offset = (page - 1) * page_size
            filters = []
            if not include_inactive:
                filters.append(InventoryItemModel.is_active == True)

            count_stmt = select(func.count()).select_from(InventoryItemModel)
            if filters:
                count_stmt = count_stmt.where(*filters)

            data_stmt = (
                select(InventoryItemModel)
                .order_by(InventoryItemModel.name.asc())
                .offset(offset)
                .limit(page_size)
            )
            if filters:
                data_stmt = data_stmt.where(*filters)

            total = session.execute(count_stmt).scalar_one()
            items = session.execute(data_stmt).scalars().all()
            return items, total

    def get_by_id(self, item_id: int) -> InventoryItemModel | None:
        with PostgresConnection() as session:
            stmt = select(InventoryItemModel).where(InventoryItemModel.id == item_id)
            return session.execute(stmt).scalar_one_or_none()

    def create(self, **kwargs) -> InventoryItemModel:
        item = InventoryItemModel(**kwargs)
        with PostgresConnection() as session:
            session.add(item)
            session.flush()
            session.refresh(item)
            return item

    def update(self, item_id: int, **kwargs) -> InventoryItemModel | None:
        with PostgresConnection() as session:
            item = session.execute(
                select(InventoryItemModel).where(InventoryItemModel.id == item_id)
            ).scalar_one_or_none()
            if not item:
                return None
            for field, value in kwargs.items():
                setattr(item, field, value)
            session.flush()
            session.refresh(item)
            return item

    def deactivate(self, item_id: int) -> bool:
        with PostgresConnection() as session:
            result = session.execute(
                update(InventoryItemModel)
                .where(InventoryItemModel.id == item_id, InventoryItemModel.is_active == True)
                .values(is_active=False)
            )
            return result.rowcount > 0


class InventoryMovementDAO:

    def create(self, **kwargs) -> InventoryMovementModel:
        movement = InventoryMovementModel(**kwargs)
        with PostgresConnection() as session:
            session.add(movement)
            session.flush()
            session.refresh(movement)
            return movement

    def list(self, item_id: int | None = None) -> list[InventoryMovementModel]:
        with PostgresConnection() as session:
            stmt = (
                select(InventoryMovementModel)
                .options(selectinload(InventoryMovementModel.item))
                .order_by(InventoryMovementModel.date.desc())
            )
            if item_id:
                stmt = stmt.where(InventoryMovementModel.item_id == item_id)
            return session.execute(stmt).scalars().all()

    def get_balance_by_item(self, item_id: int) -> float:
        with PostgresConnection() as session:
            balance_stmt = select(
                func.coalesce(
                    func.sum(
                        case(
                            (InventoryMovementModel.type == InventoryMovementType.entrada, InventoryMovementModel.quantity),
                            else_=-InventoryMovementModel.quantity,
                        )
                    ),
                    0,
                )
            ).where(InventoryMovementModel.item_id == item_id)
            return float(session.execute(balance_stmt).scalar_one())

    def get_balances(self) -> list[tuple[InventoryItemModel, float]]:
        with PostgresConnection() as session:
            balance_value = func.coalesce(
                func.sum(
                    case(
                        (InventoryMovementModel.type == InventoryMovementType.entrada, InventoryMovementModel.quantity),
                        else_=-InventoryMovementModel.quantity,
                    )
                ),
                0,
            )

            stmt = (
                select(InventoryItemModel, balance_value.label("balance"))
                .outerjoin(InventoryMovementModel, InventoryMovementModel.item_id == InventoryItemModel.id)
                .group_by(InventoryItemModel.id)
                .order_by(InventoryItemModel.name.asc())
            )
            return [(row[0], float(row[1] or 0)) for row in session.execute(stmt).all()]

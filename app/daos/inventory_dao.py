from __future__ import annotations

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models import InventoryItemModel, InventoryMovementModel, InventoryMovementType


class InventoryItemDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_page(self, include_inactive: bool, page: int, page_size: int) -> tuple[list[InventoryItemModel], int]:
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

        total_result = await self._session.execute(count_stmt)
        data_result = await self._session.execute(data_stmt)
        total = total_result.scalar_one()
        items = data_result.scalars().all()
        return items, total

    async def get_by_id(self, item_id: int) -> InventoryItemModel | None:
        stmt = select(InventoryItemModel).where(InventoryItemModel.id == item_id)
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create(self, **kwargs) -> InventoryItemModel:
        item = InventoryItemModel(**kwargs)
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def update(self, item_id: int, **kwargs) -> InventoryItemModel | None:
        result = await self._session.execute(
            select(InventoryItemModel).where(InventoryItemModel.id == item_id)
        )
        item = result.unique().scalar_one_or_none()
        if not item:
            return None
        for field, value in kwargs.items():
            setattr(item, field, value)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def deactivate(self, item_id: int) -> bool:
        result = await self._session.execute(
            update(InventoryItemModel)
            .where(InventoryItemModel.id == item_id, InventoryItemModel.is_active == True)
            .values(is_active=False)
        )
        return result.rowcount > 0


class InventoryMovementDAO:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, **kwargs) -> InventoryMovementModel:
        movement = InventoryMovementModel(**kwargs)
        self._session.add(movement)
        await self._session.flush()
        await self._session.refresh(movement)
        return movement

    async def list(self, item_id: int | None = None) -> list[InventoryMovementModel]:
        stmt = (
            select(InventoryMovementModel)
            .options(selectinload(InventoryMovementModel.item))
            .order_by(InventoryMovementModel.date.desc())
        )
        if item_id:
            stmt = stmt.where(InventoryMovementModel.item_id == item_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_balance_by_item(self, item_id: int) -> float:
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
        result = await self._session.execute(balance_stmt)
        return float(result.scalar_one())

    async def get_balances(self) -> list[tuple[InventoryItemModel, float]]:
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
        result = await self._session.execute(stmt)
        return [(row[0], float(row[1] or 0)) for row in result.all()]

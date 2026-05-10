from fastapi import HTTPException, status

from daos import InventoryItemDAO, InventoryMovementDAO
from schemas import (
    InventoryItemCreateRequest,
    InventoryItemUpdateRequest,
    InventoryItemResponse,
    InventoryItemListResponse,
    InventoryMovementCreateRequest,
    InventoryMovementResponse,
    StockBalanceResponse,
    PaginationInfo,
)


class InventoryService:

    def __init__(self):
        self._item_dao = InventoryItemDAO()
        self._movement_dao = InventoryMovementDAO()

    def get_items(
        self,
        include_inactive: bool,
        offset: int,
        limit: int,
        max_allowed_per_page: int,
    ) -> InventoryItemListResponse:
        items, total = self._item_dao.get_page(include_inactive=include_inactive, offset=offset, limit=limit)
        return InventoryItemListResponse(
            data=[InventoryItemResponse.model_validate(i) for i in items],
            pagination=PaginationInfo(
                actual_page=(offset // limit) + 1,
                per_page=limit,
                max_allowed_per_page=max_allowed_per_page,
                total_items=total,
                total_pages=(total + limit - 1) // limit,
            ),
        )

    def get_item(self, item_id: int) -> InventoryItemResponse:
        item = self._item_dao.get_by_id(item_id)
        if not item or not item.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found.")
        return InventoryItemResponse.model_validate(item)

    def create_item(self, request: InventoryItemCreateRequest) -> InventoryItemResponse:
        item = self._item_dao.create(**request.model_dump())
        return InventoryItemResponse.model_validate(item)

    def update_item(self, item_id: int, request: InventoryItemUpdateRequest) -> InventoryItemResponse:
        updates = request.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )
        item = self._item_dao.update(item_id, **updates)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found.")
        return InventoryItemResponse.model_validate(item)

    def deactivate_item(self, item_id: int) -> dict:
        deactivated = self._item_dao.deactivate(item_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found.")
        return {"message": "Inventory item deactivated."}

    def create_movement(self, request: InventoryMovementCreateRequest) -> InventoryMovementResponse:
        item = self._item_dao.get_by_id(request.item_id)
        if not item or not item.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found.")

        if request.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantity must be positive.")

        if request.type.value == "saida":
            balance = self._movement_dao.get_balance_by_item(request.item_id)
            if request.quantity > balance:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Insufficient stock for this movement.",
                )

        payload = request.model_dump()
        if not payload.get("unit"):
            payload["unit"] = item.unit

        movement = self._movement_dao.create(**payload)
        return InventoryMovementResponse.model_validate(movement)

    def list_movements(self, item_id: int | None = None) -> list[InventoryMovementResponse]:
        movements = self._movement_dao.list(item_id=item_id)
        return [InventoryMovementResponse.model_validate(m) for m in movements]

    def get_balances(self) -> list[StockBalanceResponse]:
        balances = self._movement_dao.get_balances()
        return [
            StockBalanceResponse(
                item_id=item.id,
                item_name=item.name,
                unit=item.unit,
                is_active=item.is_active,
                balance=balance,
            )
            for item, balance in balances
        ]

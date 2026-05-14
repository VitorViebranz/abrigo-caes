from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from configs import get_db
from configs.decorators import route_logger
from dependencies import PermissionChecker
from schemas import (
    InventoryItemCreateRequest,
    InventoryItemUpdateRequest,
    InventoryItemResponse,
    InventoryItemListResponse,
    InventoryMovementCreateRequest,
    InventoryMovementResponse,
    StockBalanceResponse,
    PaginationParams,
)
from services import InventoryService


inventory_router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    dependencies=[Depends(PermissionChecker("manage_finances"))],
)


@inventory_router.get(
    "/items",
    response_model=InventoryItemListResponse,
    summary="[FINANCIAL/ADMIN] List inventory items",
)
@route_logger
async def list_items(
    request: Request,
    include_inactive: bool = False,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.get_items(
        include_inactive=include_inactive,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@inventory_router.get(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
    summary="[FINANCIAL/ADMIN] Get an inventory item",
)
@route_logger
async def get_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.get_item(item_id)


@inventory_router.post(
    "/items",
    response_model=InventoryItemResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Create an inventory item",
)
@route_logger
async def create_item(
    request: Request,
    body: InventoryItemCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.create_item(body)


@inventory_router.patch(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
    summary="[FINANCIAL/ADMIN] Update an inventory item",
)
@route_logger
async def update_item(
    request: Request,
    item_id: int,
    body: InventoryItemUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.update_item(item_id, body)


@inventory_router.patch(
    "/items/{item_id}/deactivate",
    summary="[FINANCIAL/ADMIN] Deactivate an inventory item",
)
@route_logger
async def deactivate_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.deactivate_item(item_id)


@inventory_router.post(
    "/movements",
    response_model=InventoryMovementResponse,
    status_code=201,
    summary="[FINANCIAL/ADMIN] Register a stock movement",
)
@route_logger
async def create_movement(
    request: Request,
    body: InventoryMovementCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.create_movement(body)


@inventory_router.get(
    "/movements",
    response_model=list[InventoryMovementResponse],
    summary="[FINANCIAL/ADMIN] List stock movements",
)
@route_logger
async def list_movements(
    request: Request,
    item_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.list_movements(item_id=item_id)


@inventory_router.get(
    "/stock",
    response_model=list[StockBalanceResponse],
    summary="[FINANCIAL/ADMIN] Get stock balances",
)
@route_logger
async def get_balances(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    service = InventoryService(db)
    return await service.get_balances()

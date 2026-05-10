from fastapi import HTTPException, status
from sqlalchemy import select

from configs import PostgresConnection
from daos import DonationDAO
from models import (
    DonationItemModel,
    DonationModel,
    FinancialCategory,
    FinancialModel,
    FinancialType,
    InventoryItemModel,
    InventoryMovementModel,
    InventoryMovementType,
)
from schemas import DonationCreateRequest, DonationResponse


class DonationService:

    def __init__(self):
        self._dao = DonationDAO()

    def get_all(self) -> list[DonationResponse]:
        donations = self._dao.get_all()
        return [DonationResponse.model_validate(d) for d in donations]

    def get_by_id(self, donation_id: int) -> DonationResponse:
        donation = self._dao.get_by_id(donation_id)
        if not donation or not donation.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found.")
        return DonationResponse.model_validate(donation)

    def create(self, request: DonationCreateRequest) -> DonationResponse:
        if not request.items and request.monetary_value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Donation must include items or monetary value.",
            )

        if request.monetary_value is not None and request.monetary_value <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Monetary value must be positive.",
            )

        for item in request.items:
            if item.quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Item quantity must be positive.",
                )

        with PostgresConnection() as session:
            donation = DonationModel(
                donor=request.donor,
                date=request.date,
                monetary_value=request.monetary_value,
                description=request.description,
            )
            session.add(donation)
            session.flush()

            for item in request.items:
                inventory_item = session.execute(
                    select(InventoryItemModel).where(
                        InventoryItemModel.id == item.item_id,
                        InventoryItemModel.is_active == True,
                    )
                ).scalar_one_or_none()
                if not inventory_item:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Inventory item {item.item_id} not found.",
                    )

                unit = item.unit or inventory_item.unit

                donation_item = DonationItemModel(
                    donation_id=donation.id,
                    item_id=inventory_item.id,
                    quantity=item.quantity,
                    unit=unit,
                )
                session.add(donation_item)

                movement = InventoryMovementModel(
                    item_id=inventory_item.id,
                    type=InventoryMovementType.entrada,
                    quantity=item.quantity,
                    unit=unit,
                    date=request.date,
                    note="Donation",
                    reference=f"donation:{donation.id}",
                )
                session.add(movement)

            if request.monetary_value is not None:
                financial = FinancialModel(
                    type=FinancialType.entrada,
                    value=request.monetary_value,
                    date=request.date,
                    category=FinancialCategory.doacao,
                    description=request.description,
                    donor=request.donor,
                    is_active=True,
                )
                session.add(financial)

            session.flush()

        created = self._dao.get_by_id(donation.id)
        return DonationResponse.model_validate(created)

    def deactivate(self, donation_id: int) -> dict:
        deactivated = self._dao.deactivate(donation_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Donation not found.")
        return {"message": "Donation deactivated."}

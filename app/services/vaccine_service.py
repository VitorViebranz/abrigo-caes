from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from daos import AnimalDAO, VaccineDAO
from schemas import VaccineCreateRequest, VaccineUpdateRequest, VaccineResponse, VaccineAlertResponse


class VaccineService:
    def __init__(self, db: AsyncSession):
        self._dao = VaccineDAO(db)
        self._animal_dao = AnimalDAO(db)

    async def _get_animal_or_404(self, animal_id: int):
        animal = await self._animal_dao.get_by_id(animal_id)
        if not animal or not animal.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found.")
        return animal

    async def get_by_animal(self, animal_id: int) -> list[VaccineResponse]:
        await self._get_animal_or_404(animal_id)
        vaccines = await self._dao.get_by_animal(animal_id)
        return [VaccineResponse.model_validate(v) for v in vaccines]

    async def create(self, request: VaccineCreateRequest) -> VaccineResponse:
        await self._get_animal_or_404(request.animal_id)
        vaccine = await self._dao.create(**request.model_dump())
        return VaccineResponse.model_validate(vaccine)

    async def update(self, vaccine_id: int, request: VaccineUpdateRequest) -> VaccineResponse:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )
        vaccine = await self._dao.update(vaccine_id, **updates)
        if not vaccine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine not found.")
        return VaccineResponse.model_validate(vaccine)

    async def deactivate(self, vaccine_id: int) -> dict:
        deactivated = await self._dao.deactivate(vaccine_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine not found.")
        return {"message": "Vaccine record deactivated successfully."}

    async def get_overdue_alerts(self) -> list[VaccineAlertResponse]:
        vaccines = await self._dao.get_overdue()
        return await self._build_alerts(vaccines, status_label="overdue")

    async def get_due_soon_alerts(self, days: int = 7) -> list[VaccineAlertResponse]:
        vaccines = await self._dao.get_due_soon(days=days)
        return await self._build_alerts(vaccines, status_label="due_soon")

    async def _build_alerts(self, vaccines, status_label: str) -> list[VaccineAlertResponse]:
        alerts = []
        for v in vaccines:
            animal = await self._animal_dao.get_by_id(v.animal_id)
            alerts.append(VaccineAlertResponse(
                id=v.id,
                animal_id=v.animal_id,
                animal_name=animal.name if animal else "Unknown",
                name=v.name,
                next_dose=v.next_dose,
                status=status_label,
            ))
        return alerts

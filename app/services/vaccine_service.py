from fastapi import HTTPException, status

from daos import DogDAO, VaccineDAO
from schemas import VaccineCreateRequest, VaccineUpdateRequest, VaccineResponse, VaccineAlertResponse


class VaccineService:

    def __init__(self):
        self._dao     = VaccineDAO()
        self._dog_dao = DogDAO()

    def _get_dog_or_404(self, dog_id: int):
        dog = self._dog_dao.get_by_id(dog_id)
        if not dog or not dog.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        return dog

    def get_by_dog(self, dog_id: int) -> list[VaccineResponse]:
        self._get_dog_or_404(dog_id)
        vaccines = self._dao.get_by_dog(dog_id)
        return [VaccineResponse.model_validate(v) for v in vaccines]

    def create(self, request: VaccineCreateRequest) -> VaccineResponse:
        self._get_dog_or_404(request.dog_id)
        vaccine = self._dao.create(**request.model_dump())
        return VaccineResponse.model_validate(vaccine)

    def update(self, vaccine_id: int, request: VaccineUpdateRequest) -> VaccineResponse:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )
        vaccine = self._dao.update(vaccine_id, **updates)
        if not vaccine:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine not found.")
        return VaccineResponse.model_validate(vaccine)

    def deactivate(self, vaccine_id: int) -> dict:
        deactivated = self._dao.deactivate(vaccine_id)
        if not deactivated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine not found.")
        return {"message": "Vaccine record deactivated successfully."}

    def get_overdue_alerts(self) -> list[VaccineAlertResponse]:
        vaccines = self._dao.get_overdue()
        return self._build_alerts(vaccines, status_label="overdue")

    def get_due_soon_alerts(self, days: int = 7) -> list[VaccineAlertResponse]:
        vaccines = self._dao.get_due_soon(days=days)
        return self._build_alerts(vaccines, status_label="due_soon")

    def _build_alerts(self, vaccines, status_label: str) -> list[VaccineAlertResponse]:
        alerts = []
        for v in vaccines:
            dog = self._dog_dao.get_by_id(v.dog_id)
            alerts.append(VaccineAlertResponse(
                id=v.id,
                dog_id=v.dog_id,
                dog_name=dog.name if dog else "Unknown",
                name=v.name,
                next_dose=v.next_dose,
                status=status_label,
            ))
        return alerts

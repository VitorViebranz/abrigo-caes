from fastapi import HTTPException, status

from daos import DogDAO
from models import AdoptionStatus
from schemas import DogCreateRequest, DogUpdateRequest, DogStatusUpdateRequest, DogResponse

ALLOWED_TRANSITIONS: dict[AdoptionStatus, list[AdoptionStatus]] = {
    AdoptionStatus.disponivel:  [AdoptionStatus.em_processo],
    AdoptionStatus.em_processo: [AdoptionStatus.adotado, AdoptionStatus.disponivel],
    AdoptionStatus.adotado:     [],
}


class DogService:
    def __init__(self):
        self._dao = DogDAO()

    def get_all(self, include_inactive: bool = False) -> list[DogResponse]:
        dogs = self._dao.get_all(include_inactive=include_inactive)
        return [DogResponse(
            id=d.id,
            name=d.name,
            estimated_age_months=d.estimated_age_months,
            size=d.size,
            adoption_status=d.adoption_status,
            entry_date=d.entry_date,
            is_active=d.is_active,
            notes=d.notes,
            created_at=d.created_at,
            updated_at=d.updated_at,
        ) for d in dogs]

    def get_by_id(self, dog_id: int) -> DogResponse:
        dog = self._dao.get_by_id(dog_id)
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        return DogResponse.model_validate(dog)

    def create(self, request: DogCreateRequest) -> DogResponse:
        dog = self._dao.create(**request.model_dump())
        return DogResponse.model_validate(dog)

    def update(self, dog_id: int, request: DogUpdateRequest) -> DogResponse:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )
        dog = self._dao.update(dog_id, **updates)
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        return DogResponse.model_validate(dog)

    def update_status(self, dog_id: int, request: DogStatusUpdateRequest) -> DogResponse:
        dog = self._dao.get_by_id(dog_id)
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        current_status  = AdoptionStatus(dog.adoption_status)
        new_status      = request.adoption_status
        allowed         = ALLOWED_TRANSITIONS[current_status]

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Cannot transition from '{current_status}' to '{new_status}'. "
                    f"Allowed transitions: {[s.value for s in allowed] or 'none'}."
                ),
            )

        updated = self._dao.update(dog_id, adoption_status=new_status)
        return DogResponse.model_validate(updated)

    def deactivate(self, dog_id: int) -> dict:
        success = self._dao.deactivate(dog_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        return {"message": "Dog removed from the system successfully."}

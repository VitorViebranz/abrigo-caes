from fastapi import HTTPException, status
from daos import DogDAO
from models import AdoptionStatus, DogModel
from schemas import DogCreateRequest, DogUpdateRequest, DogStatusUpdateRequest, DogResponse

ALLOWED_TRANSITIONS: dict[AdoptionStatus, list[AdoptionStatus]] = {
    AdoptionStatus.disponivel:  [AdoptionStatus.em_processo],
    AdoptionStatus.em_processo: [AdoptionStatus.adotado, AdoptionStatus.disponivel],
    AdoptionStatus.adotado:     [],
}


class DogService:
    def __init__(self):
        self._dao = DogDAO()

    def _to_response(self, dog: DogModel) -> DogResponse:
        return DogResponse.model_validate(dog)

    def get_all(self, include_inactive: bool = False) -> list[DogResponse]:
        dogs = self._dao.get_all(include_inactive=include_inactive)
        return [self._to_response(d) for d in dogs]

    def get_by_id(self, dog_id: int) -> DogResponse:
        dog = self._dao.get_by_id(dog_id)
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        return self._to_response(dog)

    def create(self, dog_create: DogCreateRequest) -> DogResponse:
        dog = self._dao.create(dog_create)
        return self._to_response(dog)

    def update(self, dog_id: int, dog_update: DogUpdateRequest) -> dict:
        updates = dog_update.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )
        if not self._dao.get_by_id(dog_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        self._dao.update(dog_id, dog_update)
        return {"message": "Dog updated successfully."}

    def update_status(self, dog_id: int, dog_status_update: DogStatusUpdateRequest) -> dict:
        dog = self._dao.get_by_id(dog_id)
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")

        current_status = AdoptionStatus(dog.adoption_status)
        new_status = dog_status_update.adoption_status
        allowed = ALLOWED_TRANSITIONS[current_status]

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Cannot transition from '{current_status.value}' to '{new_status.value}'. "
                    f"Allowed transitions: {[s.value for s in allowed] or 'none'}."
                ),
            )

        self._dao.update_status(dog_id, adoption_status=new_status)
        return {"message": f"Dog status updated to '{new_status.value}'."}

    def deactivate(self, dog_id: int) -> dict:
        dog = self._dao.deactivate(dog_id)
        if not dog:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dog not found.")
        return {"message": "Dog deactivated. Dogs are never permanently deleted."}

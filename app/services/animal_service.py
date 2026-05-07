from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from daos import AnimalDAO
from models import AdoptionStatus, AnimalModel
from schemas import AnimalCreateRequest, AnimalUpdateRequest, AnimalStatusUpdateRequest, AnimalResponse

ALLOWED_TRANSITIONS: dict[AdoptionStatus, list[AdoptionStatus]] = {
    AdoptionStatus.disponivel:  [AdoptionStatus.em_processo],
    AdoptionStatus.em_processo: [AdoptionStatus.adotado, AdoptionStatus.disponivel],
    AdoptionStatus.adotado:     [],
}


class AnimalService:
    def __init__(self):
        self._dao = AnimalDAO()

        self._image_root = Path("assets") / "img" / "animals"

    def _to_response(self, animal: AnimalModel) -> AnimalResponse:
        return AnimalResponse.model_validate(animal)

    def get_all(self, include_inactive: bool = False) -> list[AnimalResponse]:
        animals = self._dao.get_all(include_inactive=include_inactive)
        return [self._to_response(a) for a in animals]

    def get_by_id(self, animal_id: int) -> AnimalResponse:
        animal = self._dao.get_by_id(animal_id)
        if not animal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found.")
        return self._to_response(animal)

    def create(self, animal_create: AnimalCreateRequest) -> AnimalResponse:
        animal = self._dao.create(animal_create)
        return self._to_response(animal)

    def update(self, animal_id: int, animal_update: AnimalUpdateRequest) -> dict:
        updates = animal_update.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update.",
            )
        if not self._dao.get_by_id(animal_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found.")
        self._dao.update(animal_id, animal_update)
        return {"message": "Animal updated successfully."}

    def update_status(self, animal_id: int, animal_status_update: AnimalStatusUpdateRequest) -> dict:
        animal = self._dao.get_by_id(animal_id)
        if not animal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found.")

        current_status = AdoptionStatus(animal.adoption_status)
        new_status = animal_status_update.adoption_status
        allowed = ALLOWED_TRANSITIONS[current_status]

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Cannot transition from '{current_status.value}' to '{new_status.value}'. "
                    f"Allowed transitions: {[s.value for s in allowed] or 'none'}."
                ),
            )

        self._dao.update_status(animal_id, adoption_status=new_status)
        return {"message": f"Animal status updated to '{new_status.value}'."}

    def deactivate(self, animal_id: int) -> dict:
        animal = self._dao.deactivate(animal_id)
        if not animal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found.")
        return {"message": "Animal deactivated. Animals are never permanently deleted."}

    def set_image(self, animal_id: int, file: UploadFile) -> AnimalResponse:
        animal = self._dao.get_by_id(animal_id)
        if not animal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Animal not found.")

        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Invalid image file.")

        extension = Path(file.filename or "").suffix.lower() or ".png"
        file_name = f"{uuid4().hex}{extension}"

        target_dir = self._image_root / str(animal_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_name

        with target_path.open("wb") as output:
            output.write(file.file.read())

        relative_path = str(Path("assets") / "img" / "animals" / str(animal_id) / file_name)
        self._dao.update_image_path(animal_id, relative_path)

        animal = self._dao.get_by_id(animal_id)
        return self._to_response(animal)

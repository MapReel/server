import uuid

from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository


class ProfileService:
    def __init__(self, repo: ProfileRepository) -> None:
        self._repo = repo

    async def ensure_profile(self, user_id: uuid.UUID, display_name: str | None) -> Profile:
        return await self._repo.upsert(user_id=user_id, display_name=display_name)

    async def get_profile(self, user_id: uuid.UUID) -> Profile | None:
        return await self._repo.get_by_id(user_id=user_id)

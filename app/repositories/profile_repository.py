import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile


class ProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Profile | None:
        return await self._db.get(Profile, user_id)

    async def upsert(self, user_id: uuid.UUID, display_name: str | None) -> Profile:
        profile = await self.get_by_id(user_id)
        if profile is None:
            profile = Profile(id=user_id, display_name=display_name)
            self._db.add(profile)
        else:
            if display_name is not None:
                profile.display_name = display_name
        await self._db.commit()
        await self._db.refresh(profile)
        return profile

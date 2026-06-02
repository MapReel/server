import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.core.errors import NotFoundError
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileUpsert
from app.services.profile_service import ProfileService

router = APIRouter()


def _get_service(db: AsyncSession) -> ProfileService:
    return ProfileService(ProfileRepository(db))


@router.post("/profile", response_model=ProfileResponse)
async def upsert_profile(
    body: ProfileUpsert,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    service = _get_service(db)
    profile = await service.ensure_profile(
        user_id=uuid.UUID(user_id),
        display_name=body.display_name,
    )
    return ProfileResponse.model_validate(profile)


@router.get("/me", response_model=ProfileResponse)
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    service = _get_service(db)
    profile = await service.get_profile(user_id=uuid.UUID(user_id))
    if profile is None:
        raise NotFoundError("Profile")
    return ProfileResponse.model_validate(profile)

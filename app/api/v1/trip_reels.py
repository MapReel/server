import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.repositories.media_repository import MediaRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.trip_reel import TripReelCreate, TripReelResponse
from app.services.media_service import MediaService

router = APIRouter()


def _get_service(db: AsyncSession) -> MediaService:
    return MediaService(MediaRepository(db), TripRepository(db))


@router.post("/trips/{trip_id}/reels", response_model=TripReelResponse, status_code=201)
async def create_reel_metadata(
    trip_id: uuid.UUID,
    body: TripReelCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TripReelResponse:
    service = _get_service(db)
    reel = await service.create_reel(
        trip_id=trip_id, owner_id=uuid.UUID(user_id), data=body
    )
    return TripReelResponse.model_validate(reel)


@router.get("/trips/{trip_id}/reels", response_model=list[TripReelResponse])
async def list_reels(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[TripReelResponse]:
    service = _get_service(db)
    reels = await service.list_reels(trip_id=trip_id, owner_id=uuid.UUID(user_id))
    return [TripReelResponse.model_validate(r) for r in reels]

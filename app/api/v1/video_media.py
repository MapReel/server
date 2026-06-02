import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.repositories.media_repository import MediaRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.video_media import VideoMediaCreate, VideoMediaResponse
from app.services.media_service import MediaService

router = APIRouter()


def _get_service(db: AsyncSession) -> MediaService:
    return MediaService(MediaRepository(db), TripRepository(db))


@router.get("/trips/{trip_id}/videos", response_model=list[VideoMediaResponse])
async def list_videos(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[VideoMediaResponse]:
    service = _get_service(db)
    videos = await service.list_videos(trip_id=trip_id, owner_id=uuid.UUID(user_id))
    return [VideoMediaResponse.model_validate(v) for v in videos]


@router.post("/trips/{trip_id}/videos", response_model=VideoMediaResponse, status_code=201)
async def create_video_metadata(
    trip_id: uuid.UUID,
    body: VideoMediaCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> VideoMediaResponse:
    service = _get_service(db)
    video = await service.create_video(
        trip_id=trip_id, owner_id=uuid.UUID(user_id), data=body
    )
    return VideoMediaResponse.model_validate(video)


@router.delete("/trips/{trip_id}/videos/{video_id}", status_code=204)
async def delete_video_metadata(
    trip_id: uuid.UUID,
    video_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = _get_service(db)
    await service.delete_video(
        video_id=video_id, trip_id=trip_id, owner_id=uuid.UUID(user_id)
    )

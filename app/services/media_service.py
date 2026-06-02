import uuid

from app.core.errors import ForbiddenError, NotFoundError
from app.models.trip_reel import TripReel
from app.models.video_media import VideoMedia
from app.repositories.media_repository import MediaRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.trip_reel import TripReelCreate
from app.schemas.video_media import VideoMediaCreate


class MediaService:
    def __init__(self, repo: MediaRepository, trip_repo: TripRepository) -> None:
        self._repo = repo
        self._trip_repo = trip_repo

    async def _verify_trip_ownership(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID
    ) -> None:
        trip = await self._trip_repo.get_by_id(trip_id)
        if trip is None or trip.deleted_at is not None:
            raise NotFoundError("Trip")
        if trip.owner_id != owner_id:
            raise ForbiddenError()

    async def list_videos(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID
    ) -> list[VideoMedia]:
        return await self._repo.list_videos_by_trip(trip_id, owner_id)

    async def create_video(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID, data: VideoMediaCreate
    ) -> VideoMedia:
        await self._verify_trip_ownership(trip_id, owner_id)

        video = VideoMedia(
            trip_id=trip_id,
            owner_id=owner_id,
            captured_at=data.captured_at,
            duration_ms=data.duration_ms,
            latitude=data.latitude,
            longitude=data.longitude,
            place_id=data.place_id,
            metadata_=data.metadata,
        )
        return await self._repo.create_video(video)

    async def delete_video(
        self, video_id: uuid.UUID, trip_id: uuid.UUID, owner_id: uuid.UUID
    ) -> None:
        video = await self._repo.get_video_by_id(video_id)
        if video is None or video.trip_id != trip_id:
            raise NotFoundError("Video")
        if video.owner_id != owner_id:
            raise ForbiddenError()
        await self._repo.delete_video(video)

    async def create_reel(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID, data: TripReelCreate
    ) -> TripReel:
        reel = TripReel(
            trip_id=trip_id,
            owner_id=owner_id,
            source_video_media_ids=data.source_video_media_ids,
            generated_at=data.generated_at,
            duration_ms=data.duration_ms,
            metadata_=data.metadata,
        )
        return await self._repo.create_reel(reel)

    async def list_reels(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID
    ) -> list[TripReel]:
        return await self._repo.list_reels_by_trip(trip_id, owner_id)

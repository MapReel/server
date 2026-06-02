import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip_reel import TripReel
from app.models.video_media import VideoMedia


class MediaRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # -- Video Media --

    async def list_videos_by_trip(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID
    ) -> list[VideoMedia]:
        stmt = (
            select(VideoMedia)
            .where(
                VideoMedia.trip_id == trip_id,
                VideoMedia.owner_id == owner_id,
                VideoMedia.deleted_at.is_(None),
            )
            .order_by(VideoMedia.captured_at.asc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_video_by_id(self, video_id: uuid.UUID) -> VideoMedia | None:
        return await self._db.get(VideoMedia, video_id)

    async def create_video(self, video: VideoMedia) -> VideoMedia:
        self._db.add(video)
        await self._db.commit()
        await self._db.refresh(video)
        return video

    async def delete_video(self, video: VideoMedia) -> None:
        await self._db.delete(video)
        await self._db.commit()

    # -- Trip Reels --

    async def list_reels_by_trip(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID
    ) -> list[TripReel]:
        stmt = (
            select(TripReel)
            .where(TripReel.trip_id == trip_id, TripReel.owner_id == owner_id)
            .order_by(TripReel.created_at.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def create_reel(self, reel: TripReel) -> TripReel:
        self._db.add(reel)
        await self._db.commit()
        await self._db.refresh(reel)
        return reel

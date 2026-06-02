import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trip import Trip


class TripRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_by_owner(self, owner_id: uuid.UUID) -> list[Trip]:
        stmt = (
            select(Trip)
            .where(Trip.owner_id == owner_id, Trip.deleted_at.is_(None))
            .order_by(Trip.created_at.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, trip_id: uuid.UUID) -> Trip | None:
        return await self._db.get(Trip, trip_id)

    async def create(self, trip: Trip) -> Trip:
        self._db.add(trip)
        await self._db.commit()
        await self._db.refresh(trip)
        return trip

    async def update(self, trip: Trip) -> Trip:
        await self._db.commit()
        await self._db.refresh(trip)
        return trip

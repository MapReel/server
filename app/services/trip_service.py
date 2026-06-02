import uuid
from datetime import datetime, timezone

from app.core.errors import ForbiddenError, NotFoundError
from app.models.trip import Trip
from app.repositories.trip_repository import TripRepository
from app.schemas.trip import TripCreate, TripUpdate


class TripService:
    def __init__(self, repo: TripRepository) -> None:
        self._repo = repo

    async def list_trips(self, owner_id: uuid.UUID) -> list[Trip]:
        return await self._repo.list_by_owner(owner_id)

    async def create_trip(self, owner_id: uuid.UUID, data: TripCreate) -> Trip:
        trip = Trip(
            owner_id=owner_id,
            title=data.title,
            start_date=data.start_date,
            end_date=data.end_date,
            place_id=data.place_id,
            place_snapshot=data.place_snapshot,
        )
        return await self._repo.create(trip)

    async def get_trip(self, trip_id: uuid.UUID, owner_id: uuid.UUID) -> Trip:
        trip = await self._repo.get_by_id(trip_id)
        if trip is None or trip.deleted_at is not None:
            raise NotFoundError("Trip")
        if trip.owner_id != owner_id:
            raise ForbiddenError()
        return trip

    async def update_trip(
        self, trip_id: uuid.UUID, owner_id: uuid.UUID, data: TripUpdate
    ) -> Trip:
        trip = await self.get_trip(trip_id, owner_id)
        update_data = data.model_dump(exclude_unset=True)
        # Map camelCase aliases to snake_case model fields
        field_map = {"startDate": "start_date", "endDate": "end_date", "placeId": "place_id", "placeSnapshot": "place_snapshot"}
        for alias, field in field_map.items():
            if alias in update_data:
                update_data[field] = update_data.pop(alias)
        for key, value in update_data.items():
            setattr(trip, key, value)
        return await self._repo.update(trip)

    async def delete_trip(self, trip_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        trip = await self.get_trip(trip_id, owner_id)
        trip.deleted_at = datetime.now(timezone.utc)
        await self._repo.update(trip)

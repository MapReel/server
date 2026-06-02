import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.repositories.trip_repository import TripRepository
from app.schemas.trip import TripCreate, TripResponse, TripUpdate
from app.services.trip_service import TripService

router = APIRouter()


def _get_service(db: AsyncSession) -> TripService:
    return TripService(TripRepository(db))


@router.get("/", response_model=list[TripResponse])
async def list_trips(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[TripResponse]:
    service = _get_service(db)
    trips = await service.list_trips(owner_id=uuid.UUID(user_id))
    return [TripResponse.model_validate(t) for t in trips]


@router.post("/", response_model=TripResponse, status_code=201)
async def create_trip(
    body: TripCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    service = _get_service(db)
    trip = await service.create_trip(owner_id=uuid.UUID(user_id), data=body)
    return TripResponse.model_validate(trip)


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    service = _get_service(db)
    trip = await service.get_trip(trip_id=trip_id, owner_id=uuid.UUID(user_id))
    return TripResponse.model_validate(trip)


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: uuid.UUID,
    body: TripUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> TripResponse:
    service = _get_service(db)
    trip = await service.update_trip(trip_id=trip_id, owner_id=uuid.UUID(user_id), data=body)
    return TripResponse.model_validate(trip)


@router.delete("/{trip_id}", status_code=204)
async def delete_trip(
    trip_id: uuid.UUID,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> None:
    service = _get_service(db)
    await service.delete_trip(trip_id=trip_id, owner_id=uuid.UUID(user_id))

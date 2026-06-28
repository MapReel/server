from fastapi import APIRouter, Query

from app.schemas.place import PlaceDetail, PlaceSearchResponse
from app.services.places_service import PlacesService

router = APIRouter()


@router.get("/search", response_model=PlaceSearchResponse)
async def search_places(
    query: str = Query(min_length=1),
    lat: float | None = None,
    lng: float | None = None,
) -> PlaceSearchResponse:
    service = PlacesService()
    results = await service.search(query=query, lat=lat, lng=lng)
    return PlaceSearchResponse(results=results)


@router.get("/{place_id}", response_model=PlaceDetail)
async def get_place_detail(
    place_id: str,
) -> PlaceDetail:
    service = PlacesService()
    return await service.get_detail(place_id=place_id)

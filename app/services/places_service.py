import httpx

from app.core.config import settings
from app.core.errors import AppError, NotFoundError
from app.schemas.place import PlaceSearchResult

GOOGLE_PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
GOOGLE_PLACES_DETAIL_URL = "https://places.googleapis.com/v1/places"

FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.location,places.primaryType,places.rating,places.googleMapsUri"
)
DETAIL_FIELD_MASK = (
    "id,displayName,formattedAddress,location,primaryType,rating,googleMapsUri"
)


class PlacesService:
    async def search(
        self, query: str, lat: float | None = None, lng: float | None = None
    ) -> list[PlaceSearchResult]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.google_maps_api_key,
            "X-Goog-FieldMask": FIELD_MASK,
        }
        body: dict = {"textQuery": query}
        if lat is not None and lng is not None:
            body["locationBias"] = {
                "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": 5000.0}
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(GOOGLE_PLACES_TEXT_SEARCH_URL, json=body, headers=headers)

        if resp.status_code != 200:
            raise AppError(
                code="PLACES_SEARCH_FAILED",
                message="Place search failed.",
                status_code=502,
            )

        data = resp.json()
        results: list[PlaceSearchResult] = []
        for p in data.get("places", []):
            results.append(
                PlaceSearchResult(
                    placeId=p.get("id", ""),
                    displayName=p.get("displayName", {}).get("text", ""),
                    formattedAddress=p.get("formattedAddress", ""),
                    latitude=p.get("location", {}).get("latitude", 0),
                    longitude=p.get("location", {}).get("longitude", 0),
                    primaryType=p.get("primaryType"),
                    rating=p.get("rating"),
                    googleMapsUri=p.get("googleMapsUri"),
                )
            )
        return results

    async def get_detail(self, place_id: str) -> PlaceSearchResult:
        headers = {
            "X-Goog-Api-Key": settings.google_maps_api_key,
            "X-Goog-FieldMask": DETAIL_FIELD_MASK,
        }
        url = f"{GOOGLE_PLACES_DETAIL_URL}/{place_id}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)

        if resp.status_code == 404:
            raise NotFoundError("Place")
        if resp.status_code != 200:
            raise AppError(
                code="PLACE_DETAIL_FAILED",
                message="Place detail lookup failed.",
                status_code=502,
            )

        p = resp.json()
        return PlaceSearchResult(
            placeId=p.get("id", place_id),
            displayName=p.get("displayName", {}).get("text", ""),
            formattedAddress=p.get("formattedAddress", ""),
            latitude=p.get("location", {}).get("latitude", 0),
            longitude=p.get("location", {}).get("longitude", 0),
            primaryType=p.get("primaryType"),
            rating=p.get("rating"),
            googleMapsUri=p.get("googleMapsUri"),
        )

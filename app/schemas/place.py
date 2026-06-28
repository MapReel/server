from pydantic import BaseModel, ConfigDict, Field


class PlaceSearchResult(BaseModel):
    place_id: str = Field(alias="placeId")
    display_name: str = Field(alias="displayName")
    formatted_address: str = Field(alias="formattedAddress")
    latitude: float
    longitude: float
    primary_type: str | None = Field(default=None, alias="primaryType")
    rating: float | None = None
    google_maps_uri: str | None = Field(default=None, alias="googleMapsUri")

    model_config = ConfigDict(populate_by_name=True, by_alias=True)


class PlaceSearchResponse(BaseModel):
    results: list[PlaceSearchResult]


class PlaceDetail(PlaceSearchResult):
    """Richer place fields for the Map Card Reel. Superset of PlaceSearchResult.

    `price_range` and `regular_opening_hours` are passed through as raw Google
    Places (New) objects so the client can format them for its own card design.
    """

    user_rating_count: int | None = Field(default=None, alias="userRatingCount")
    primary_type_display_name: str | None = Field(
        default=None, alias="primaryTypeDisplayName"
    )
    price_level: str | None = Field(default=None, alias="priceLevel")
    price_range: dict | None = Field(default=None, alias="priceRange")
    regular_opening_hours: dict | None = Field(
        default=None, alias="regularOpeningHours"
    )

    model_config = ConfigDict(populate_by_name=True, by_alias=True)

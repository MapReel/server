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

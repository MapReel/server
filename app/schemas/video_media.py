import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VideoMediaCreate(BaseModel):
    captured_at: datetime = Field(alias="capturedAt")
    duration_ms: int = Field(alias="durationMs")
    latitude: float | None = None
    longitude: float | None = None
    place_id: str | None = Field(default=None, alias="placeId")
    metadata: dict | None = None

    model_config = ConfigDict(populate_by_name=True)


class VideoMediaResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID = Field(alias="tripId")
    captured_at: datetime = Field(alias="capturedAt")
    duration_ms: int = Field(alias="durationMs")
    latitude: float | None = None
    longitude: float | None = None
    place_id: str | None = Field(alias="placeId")
    metadata: dict | None = Field(default=None, validation_alias="metadata_")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, by_alias=True)

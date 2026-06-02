import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripReelCreate(BaseModel):
    source_video_media_ids: list[uuid.UUID] = Field(alias="sourceVideoMediaIds")
    generated_at: datetime = Field(alias="generatedAt")
    duration_ms: int | None = Field(default=None, alias="durationMs")
    metadata: dict | None = None

    model_config = ConfigDict(populate_by_name=True)


class TripReelResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID = Field(alias="tripId")
    source_video_media_ids: list[uuid.UUID] = Field(alias="sourceVideoMediaIds")
    generated_at: datetime = Field(alias="generatedAt")
    duration_ms: int | None = Field(alias="durationMs")
    metadata: dict | None = Field(default=None, validation_alias="metadata_")
    created_at: datetime = Field(alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, by_alias=True)

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TripCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    place_id: str | None = Field(default=None, alias="placeId")
    place_snapshot: dict | None = Field(default=None, alias="placeSnapshot")

    @model_validator(mode="after")
    def validate_dates(self) -> "TripCreate":
        if self.end_date < self.start_date:
            raise ValueError("endDate must be >= startDate")
        return self

    model_config = ConfigDict(populate_by_name=True)


class TripUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    place_id: str | None = Field(default=None, alias="placeId")
    place_snapshot: dict | None = Field(default=None, alias="placeSnapshot")

    model_config = ConfigDict(populate_by_name=True)


class TripResponse(BaseModel):
    id: uuid.UUID
    title: str
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    place_id: str | None = Field(alias="placeId")
    place_snapshot: dict | None = Field(alias="placeSnapshot")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, by_alias=True)

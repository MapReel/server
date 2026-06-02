from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileUpsert(BaseModel):
    display_name: str | None = Field(None, alias="displayName")

    model_config = ConfigDict(populate_by_name=True)


class ProfileResponse(BaseModel):
    id: UUID
    display_name: str | None = Field(alias="displayName")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, by_alias=True)

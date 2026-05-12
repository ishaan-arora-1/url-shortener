from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ShortenRequest(BaseModel):
    url: HttpUrl = Field(..., description="The long URL to shorten")


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    last_accessed_at: datetime | None

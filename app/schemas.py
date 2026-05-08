from pydantic import BaseModel, Field, HttpUrl


class ShortenRequest(BaseModel):
    url: HttpUrl = Field(..., description="The long URL to shorten")


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str

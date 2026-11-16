from pydantic import BaseModel, Field, HttpUrl


class LinkCreate(BaseModel):
    url: HttpUrl
    owner_key: str = Field(min_length=8, max_length=64)


class LinkCreated(BaseModel):
    code: str
    short_url: str
    url: str

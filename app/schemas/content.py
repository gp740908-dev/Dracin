from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from app.models.content import AccessLevel, SeriesStatus


class EpisodeBase(BaseModel):
    id: int
    title: str
    slug: str
    cover_image_url: str | None = None
    description: str | None = None
    genres: list[str] = Field(default_factory=list, alias="genre")
    episode_number: int
    total_episodes: int | None = None
    series_id: int
    duration: int | None = None
    release_date: date | None = None
    view_count: int
    status: SeriesStatus
    is_exclusive: bool
    access_level: AccessLevel
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EpisodeDetail(EpisodeBase):
    video_url: str | None = None


class SeriesBase(BaseModel):
    id: int
    title: str
    slug: str
    cover_image_url: str | None = None
    description: str | None = None
    genres: list[str] = Field(default_factory=list, alias="genre")
    total_episodes: int
    release_date: date | None = None
    view_count: int
    status: SeriesStatus
    is_exclusive: bool
    access_level: AccessLevel
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SeriesDetail(SeriesBase):
    episodes: list[EpisodeDetail] = Field(default_factory=list)


class PaginatedSeries(BaseModel):
    page: int
    page_size: int
    total: int
    items: list[SeriesBase]

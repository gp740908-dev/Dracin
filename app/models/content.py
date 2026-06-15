import enum
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AccessLevel(str, enum.Enum):
    free = "free"
    premium = "premium"
    exclusive = "exclusive"


class SeriesStatus(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"


class Series(Base):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1024))
    description: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    total_episodes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    release_date: Mapped[Date | None] = mapped_column(Date)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[SeriesStatus] = mapped_column(Enum(SeriesStatus), default=SeriesStatus.ongoing)
    is_exclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(Enum(AccessLevel), default=AccessLevel.free)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    episodes: Mapped[list["Episode"]] = relationship(back_populates="series", cascade="all, delete-orphan")


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    cover_image_url: Mapped[str | None] = mapped_column(String(1024))
    video_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, comment="Duration in seconds")
    release_date: Mapped[Date | None] = mapped_column(Date)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[SeriesStatus] = mapped_column(Enum(SeriesStatus), default=SeriesStatus.ongoing)
    is_exclusive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    access_level: Mapped[AccessLevel] = mapped_column(Enum(AccessLevel), default=AccessLevel.free)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id", ondelete="CASCADE"), index=True)
    series: Mapped[Series] = relationship(back_populates="episodes")


class PartnerApiKey(Base):
    __tablename__ = "partner_api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    partner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    allowed_access_level: Mapped[AccessLevel] = mapped_column(Enum(AccessLevel), default=AccessLevel.free)
    allowed_origins: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=120, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_key_id: Mapped[int | None] = mapped_column(ForeignKey("partner_api_keys.id"))
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    is_exclusive_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

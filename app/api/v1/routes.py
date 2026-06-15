from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.rate_limit import enforce_rate_limit
from app.core.security import can_access, get_partner, sign_video_url
from app.db.session import get_db
from app.models.content import AccessLevel, Episode, PartnerApiKey, Series
from app.schemas.content import EpisodeDetail, PaginatedSeries, SeriesBase, SeriesDetail

router = APIRouter(dependencies=[Depends(get_partner), Depends(enforce_rate_limit)])


def episode_out(ep: Episode, partner: PartnerApiKey, include_video: bool = False) -> EpisodeDetail:
    allowed = can_access(partner.allowed_access_level, ep.access_level)
    video_url = sign_video_url(ep.video_path, partner.id) if include_video and allowed else None
    return EpisodeDetail.model_validate({**ep.__dict__, "total_episodes": ep.series.total_episodes, "video_url": video_url})


@router.get("/series", response_model=PaginatedSeries)
async def list_series(
    access_level: AccessLevel | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Series)
    count_stmt = select(func.count(Series.id))
    if access_level:
        stmt = stmt.where(Series.access_level == access_level)
        count_stmt = count_stmt.where(Series.access_level == access_level)
    total = await db.scalar(count_stmt) or 0
    rows = (await db.execute(stmt.order_by(Series.release_date.desc()).offset((page - 1) * page_size).limit(page_size))).scalars().all()
    return {"page": page, "page_size": page_size, "total": total, "items": rows}


@router.get("/series/{series_id}", response_model=SeriesDetail)
async def get_series(series_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    series = (await db.execute(select(Series).options(selectinload(Series.episodes)).where(Series.id == series_id))).scalar_one_or_none()
    if not series:
        raise HTTPException(404, "Series not found")
    partner = request.state.partner
    episodes = [episode_out(ep, partner, include_video=True) for ep in sorted(series.episodes, key=lambda e: e.episode_number)]
    return SeriesDetail.model_validate({**series.__dict__, "episodes": episodes})


@router.get("/episodes/{episode_id}", response_model=EpisodeDetail)
async def get_episode(episode_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    episode = (await db.execute(select(Episode).options(selectinload(Episode.series)).where(Episode.id == episode_id))).scalar_one_or_none()
    if not episode:
        raise HTTPException(404, "Episode not found")
    if episode.is_exclusive:
        request.state.is_exclusive_access = True
    return episode_out(episode, request.state.partner, include_video=True)


@router.get("/search", response_model=list[SeriesBase])
async def search(q: str = Query(..., min_length=2), db: AsyncSession = Depends(get_db)):
    pattern = f"%{q}%"
    rows = (await db.execute(select(Series).where(or_(Series.title.ilike(pattern), Series.genres.any(q))).limit(50))).scalars().all()
    return rows


@router.get("/genres", response_model=list[str])
async def genres(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(func.unnest(Series.genres)).distinct().order_by(func.unnest(Series.genres)))
    return [row[0] for row in rows]


@router.get("/exclusive", response_model=list[SeriesBase])
async def exclusive(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Series).where(Series.access_level.in_([AccessLevel.premium, AccessLevel.exclusive])).order_by(Series.release_date.desc()).limit(100))).scalars().all()
    return rows

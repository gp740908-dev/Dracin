import hashlib
import hmac
import time
from urllib.parse import urlencode
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.db.session import get_db
from app.models.content import AccessLevel, PartnerApiKey

ACCESS_RANK = {AccessLevel.free: 0, AccessLevel.premium: 1, AccessLevel.exclusive: 2}


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def can_access(granted: AccessLevel, required: AccessLevel) -> bool:
    return ACCESS_RANK[granted] >= ACCESS_RANK[required]


async def get_partner(
    request: Request,
    x_api_key: str = Header(..., alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> PartnerApiKey:
    result = await db.execute(
        select(PartnerApiKey).where(
            PartnerApiKey.api_key_hash == hash_api_key(x_api_key), PartnerApiKey.is_active.is_(True)
        )
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
    origin = request.headers.get("origin")
    if origin and partner.allowed_origins and origin not in partner.allowed_origins:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Origin is not allowed for this API key")
    request.state.partner = partner
    return partner


def sign_video_url(video_path: str, partner_id: int) -> str:
    settings = get_settings()
    expires = int(time.time()) + settings.signed_url_ttl_seconds
    payload = f"{video_path}:{partner_id}:{expires}"
    signature = hmac.new(settings.signing_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    query = urlencode({"partner": partner_id, "expires": expires, "sig": signature})
    return f"{str(settings.video_cdn_base_url).rstrip('/')}/{video_path.lstrip('/')}?{query}"

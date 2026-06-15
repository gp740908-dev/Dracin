import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router
from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models.content import RequestLog

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("melolo-api")

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="REST API aggregator untuk distribusi konten video Melolo ke partner site dengan API key, tier access, rate limit, signed URL, cache, dan logging.",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["X-API-Key", "Content-Type"],
)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    response = await call_next(request)
    partner = getattr(request.state, "partner", None)
    is_exclusive = getattr(request.state, "is_exclusive_access", False)
    logger.info(
        "partner=%s method=%s path=%s status=%s exclusive=%s",
        getattr(partner, "partner_name", "anonymous"),
        request.method,
        request.url.path,
        response.status_code,
        is_exclusive,
    )
    if partner:
        async with AsyncSessionLocal() as session:
            session.add(
                RequestLog(
                    api_key_id=partner.id,
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    is_exclusive_access=is_exclusive,
                )
            )
            await session.commit()
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router, prefix="/api/v1", tags=["content"])

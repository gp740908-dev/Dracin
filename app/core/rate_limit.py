import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request, status

_hits: dict[int, deque[float]] = defaultdict(deque)


async def enforce_rate_limit(request: Request) -> None:
    partner = getattr(request.state, "partner", None)
    if not partner:
        return
    now = time.time()
    bucket = _hits[partner.id]
    while bucket and bucket[0] <= now - 60:
        bucket.popleft()
    if len(bucket) >= partner.rate_limit_per_minute:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded")
    bucket.append(now)

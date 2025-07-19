import redis
import time
from fastapi import HTTPException

r = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

def rate_limit(key: str, limit: int, window_sec: int):
    now = int(time.time())
    window_key = f"rl:{key}:{now // window_sec}"

    current = r.incr(window_key)
    if current == 1:
        r.expire(window_key, window_sec)

    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

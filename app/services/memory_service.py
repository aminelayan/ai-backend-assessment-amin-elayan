import redis
import json
import os
from datetime import datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

SHORT_TERM_TURNS = 10
LONG_TERM_SUMMARIZE_EVERY = 20  # just an example

def store_message(conversation_id: str, role: str, message: str):
    key = f"chat:{conversation_id}:messages"

    # Append to Redis list
    redis_client.rpush(key, json.dumps({
        "role": role,
        "message": message,
        "timestamp": str(datetime.utcnow())
    }))

    # Keep only the last N for short-term
    redis_client.ltrim(key, -SHORT_TERM_TURNS, -1)

def get_context(conversation_id: str):
    key = f"chat:{conversation_id}:messages"
    messages = redis_client.lrange(key, 0, -1)

    return [json.loads(msg) for msg in messages]

import time
from fastapi import Request

startup_time = time.time()
request_count = 0
total_latency = 0.0

def track_metrics(request: Request, response_time_ms: float):
    global request_count, total_latency
    request_count += 1
    total_latency += response_time_ms

def get_metrics():
    uptime = int(time.time() - startup_time)
    avg_latency = round(total_latency / request_count, 2) if request_count else 0

    return {
        "uptime_seconds": uptime,
        "requests_total": request_count,
        "avg_latency_ms": avg_latency,
        "cache_hit_ratio": 0.0,  # Placeholder
        "embedding_queue_backlog": 0  # Placeholder
    }

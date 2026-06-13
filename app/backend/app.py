import os
from datetime import datetime, timezone

import redis
import requests
from flask import Flask, jsonify


app = Flask(__name__)


def redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD") or None,
        decode_responses=True,
    )


@app.get("/api/ping")
def ping():
    visits = None
    redis_status = "ok"

    try:
        client = redis_client()
        visits = client.incr("ping_count")
    except redis.RedisError as exc:
        redis_status = f"error: {exc.__class__.__name__}"

    print(f"[{datetime.now(timezone.utc).isoformat()}] received /api/ping request", flush=True)
    return jsonify(
        {
            "status": "ok",
            "service": "flask-backend",
            "redis": redis_status,
            "visits": visits,
        }
    )


@app.get("/api/info")
def info():
    # requests is the extra package added for the course requirement.
    return jsonify(
        {
            "status": "ok",
            "extra_package": "requests",
            "requests_version": requests.__version__,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

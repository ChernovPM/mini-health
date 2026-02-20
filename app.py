import os
import time
import logging
from datetime import datetime

from flask import Flask, Response, g, jsonify, request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

app = Flask(__name__)

START_TIME = time.time()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)
PROCESS_UPTIME = Gauge("process_uptime_seconds", "Process uptime in seconds")


@app.before_request
def before_request() -> None:
    g.start_time = time.perf_counter()


@app.after_request
def after_request(response):
    duration = time.perf_counter() - getattr(g, "start_time", time.perf_counter())
    REQUEST_COUNT.labels(
        method=request.method,
        path=request.path,
        status=str(response.status_code),
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, path=request.path).observe(duration)
    logger.info("request path=%s status=%s", request.path, response.status_code)
    return response


@app.route("/")
def index():
    return jsonify({"message": "Mini Health API is running"})


@app.route("/health")
def health():
    uptime = time.time() - START_TIME
    return jsonify(
        {
            "status": "ok",
            "uptime_seconds": uptime,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.route("/metrics")
def metrics():
    PROCESS_UPTIME.set(time.time() - START_TIME)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

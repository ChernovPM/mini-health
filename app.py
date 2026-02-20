import os
import time
import logging
from datetime import datetime

import psutil
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

# ---- Logging to stdout (Docker-friendly) ----
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("mini-health")

# ---- Prometheus metrics ----
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
CPU_PERCENT = Gauge("system_cpu_percent", "System CPU usage percent")
MEMORY_PERCENT = Gauge("system_memory_percent", "System memory usage percent")


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
    logger.info("request path=%s status=%s duration=%.4fs", request.path, response.status_code, duration)
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
    CPU_PERCENT.set(psutil.cpu_percent(interval=None))
    MEMORY_PERCENT.set(psutil.virtual_memory().percent)

    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)

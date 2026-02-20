import os
import time
import logging
from datetime import datetime
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

START_TIME = time.time()
LOG_FILE = "health.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.route("/")
def index():
    return jsonify({"message": "Mini Health API is running"})

@app.route("/health")
def health():
    uptime = time.time() - START_TIME
    logging.info("Health endpoint called")

    return jsonify({
        "status": "ok",
        "uptime_seconds": uptime,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    return jsonify({
        "cpu_percent": cpu,
        "memory_percent": memory
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

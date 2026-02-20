# mini-health

A minimal Flask service with health checks and Prometheus metrics.

## Run locally (venv)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:8000 app:app
```

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

The app is available at `http://localhost:8000`.

## Check endpoints

Health:

```bash
curl http://localhost:8000/healthz
```

Prometheus metrics:

```bash
curl http://localhost:8000/metrics
```

## Prometheus scraping notes

Use `/metrics` as the scrape target path and scrape on port `8000`.
Example job:

```yaml
scrape_configs:
  - job_name: mini-health
    metrics_path: /metrics
    static_configs:
      - targets: ["mini-health:8000"]
```

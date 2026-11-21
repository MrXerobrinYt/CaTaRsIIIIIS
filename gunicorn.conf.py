# Gunicorn configuration for Figura Unchained Backend (optional production worker)
# Usage: gunicorn -c gunicorn.conf.py server:app

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"
workers = 1                       # aiohttp is single-process async; keep 1 worker
worker_class = "aiohttp.GunicornWorker"
worker_connections = 1000
keepalive = 25                    # matches WebSocket heartbeat
timeout = 30
graceful_timeout = 10
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging to stdout (Render captures it)
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True

# Proxy headers (Render load balancer)
proxy_allow_ips = "*"
forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

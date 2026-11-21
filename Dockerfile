FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=55000

WORKDIR /app

# System dependencies (minimal; we only need Python + libs already in requirements)
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Non-root user for security
RUN useradd -m -s /bin/bash figurauser \
    && mkdir -p /app/data/avatars \
    && chown -R figurauser:figurauser /app/data /app

COPY --chown=figurauser:figurauser . .
USER figurauser

# Render injects PORT automatically; fall back to 55000 locally.
EXPOSE ${PORT}
CMD ["python", "server.py"]

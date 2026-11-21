# Figura Unchained Backend — Render deployment & Russia access guide
#
# This backend serves the Figura Unchained Minecraft addon (HTTP API + WebSocket).
# It is written in Python (aiohttp) and is ready to deploy on Render.

# =====================================================================
# 1. DEPLOY ON RENDER (free tier)
# =====================================================================
#
# Option A — Render Blueprint (recommended)
#   1. Push this repo to GitHub (or your own fork).
#   2. Go to https://dashboard.render.com/ → "Blueprint" → connect the repo.
#   3. Render reads render.yaml and creates the Web Service automatically.
#   4. Add the secrets that must NOT be in git (Render dashboard → Environment):
#        IDENTITY_KEY   (optional, base64 Ed25519 seed)
#        GITHUB_TOKEN   (optional, raises assets download rate limit)
#
# Option B — Manual Web Service
#   1. "New +" → "Web Service" → connect your GitHub repo.
#   4. Region: Frankfurt (closest to Russia → best latency).
#   5. Build command:   pip install -r requirements.txt
#   6. Start command:   python server.py
#   7. Add env vars from .env.example (Render dashboard → Environment).
#   8. PORT is set by Render automatically (do not hardcode).
#
# Free-tier limits to know:
#   • 512 MB RAM, shared CPU — enough for a small player base.
#   • Service spins down after ~15 min of inactivity (free tier). The first
#     request after sleep takes ~10–30 s to wake up.
#   • /data is EPHEMERAL on free tier — SQLite DB + avatars are reset on every
#     deploy/restart. For persistent data, add a paid Render Disk or use an
#     external store.

# =====================================================================
# 2. MAKE IT WORK FROM RUSSIA
# =====================================================================
#
# Problem: *.onrender.com addresses are sometimes throttled/blocked from Russia,
# and github.com / api.github.com / codeload.github.com (used for asset sync)
# can be unreachable or slow.
#
# Recommended fix: Cloudflare in front of Render
#   1. Register a domain (any registrar).
#   2. Add it to Cloudflare (free plan) and point DNS at your Render service
#      (CNAME to your-service.onrender.com, proxy = ON / orange cloud).
#   3. Enable "Always Online" / caching for static asset paths if desired.
#   4. In Figura mod settings, put your domain (e.g. figura.example.com) as the
#      "Server IP" / "Cloud IP".
#
# Why this helps from Russia:
#   • Cloudflare edge IPs are generally reachable from Russia.
#   • SSL terminates at Cloudflare (full SSL or flexible).
#   • You can enable Cloudflare cache for /assets/* to offload Render.
#
# Alternatives if Cloudflare is not an option:
#   • Put a small reverse proxy VPS outside Russia (e.g. Finland / Germany /
#     Kazakhstan) → Nginx/Caddy proxy_pass to Render.
#   • Use a VPN/WireGuard tunnel from the Russian client to the server.
#
# Backend-side settings that matter for Russia:
#   • TRUSTED_PROXIES — include the proxy/CF IPs so real client IPs are read
#     from X-Forwarded-For / CF-Connecting-IP (rate limiting per real IP).
#   • CUSTOM_REAL_IP_HEADER — if using Cloudflare, set to "CF-Connecting-IP".
#   • ASSETS_UPDATE_INTERVAL_HOURS — if api.github.com/codeload.github.com is
#     unreachable from the Render egress, set to 0 to disable asset auto-sync
#     and pre-bake assets into the image instead.

# =====================================================================
# 3. ENV VARIABLES QUICK REFERENCE
# =====================================================================
# PORT            Render sets this automatically.
# DEBUG           false in production.
# REQUIRE_AUTH    true = players must /register and /login.
# AVATAR_DIR      where .nbt skins are stored (data/avatars).
# TRUSTED_PROXIES   proxy CIDRs so rate limiting uses real client IP.
# CUSTOM_REAL_IP_HEADER  e.g. CF-Connecting-IP (Cloudflare) or X-Forwarded-For.
# ASSETS_UPDATE_INTERVAL_HOURS  set 0 to disable GitHub asset sync.
# IDENTITY_KEY / GITHUB_TOKEN   optional secrets (Render dashboard).

# =====================================================================
# 4. LOCAL TESTING
# =====================================================================
#   cp .env.example .env
#   pip install -r requirements.txt
#   python server.py
#   http://localhost:55000/       → landing page
#   http://localhost:55000/api/version → backend version
#   ws://localhost:55000/ws       → WebSocket endpoint

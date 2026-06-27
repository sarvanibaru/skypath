import os

# ── business rules ─────────────────────────────────────────
MIN_LAYOVER_DOMESTIC      = 45   # minutes
MIN_LAYOVER_INTERNATIONAL = 90   # minutes
MAX_LAYOVER               = 360  # minutes (6 hours)

# ── cache settings ─────────────────────────────────────────
# update if flights.json airport count changes
TIMEZONE_CACHE_SIZE = 25

# ── data path ──────────────────────────────────────────────
# overridable via environment variable for Docker deployments
DATA_PATH = os.getenv(
    "FLIGHTS_DATA_PATH",
    os.path.join(os.path.dirname(__file__), "..", "flights.json")
)
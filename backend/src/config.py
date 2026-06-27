import os

# ── business rules ─────────────────────────────────────────
MIN_LAYOVER_DOMESTIC      = 45
MIN_LAYOVER_INTERNATIONAL = 90
MAX_LAYOVER               = 360

# ── cache settings ─────────────────────────────────────────
TIMEZONE_CACHE_SIZE = 25

# ── data path ──────────────────────────────────────────────
# Local: flights.json is at skypath/flights.json (two levels up from src/)
# Docker: overridden via FLIGHTS_DATA_PATH environment variable
DATA_PATH = os.getenv(
    "FLIGHTS_DATA_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "flights.json")
)
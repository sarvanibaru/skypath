import re
from datetime import datetime
from dataclasses import asdict
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from search import load_data, search_itineraries

# ── app setup ──────────────────────────────────────────────
app = FastAPI(title="SkyPath Flight Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── load data once on startup ──────────────────────────────
airports, flights_by_origin_date = load_data()

# ── helpers ────────────────────────────────────────────────
def validate_airport_code(code: str, field: str) -> str:
    code = code.strip().upper()
    if not re.match(r'^[A-Z]{3}$', code):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field} airport code: '{code}'. Must be exactly 3 letters"
        )
    if code not in airports:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown {field} airport code: '{code}'"
        )
    return code

def validate_date(date: str) -> str:
    date = date.strip()
    try:
        parsed = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date format: '{date}'. Expected YYYY-MM-DD"
        )
    if parsed.year < 2000 or parsed.year > 2100:
        raise HTTPException(
            status_code=400,
            detail=f"Date out of reasonable range: '{date}'"
        )
    return date

# ── routes ─────────────────────────────────────────────────
@app.get("/api/search")
def search(
    origin     : str = Query(..., description="3-letter IATA origin code"),
    destination: str = Query(..., description="3-letter IATA destination code"),
    date       : str = Query(..., description="Travel date YYYY-MM-DD"),
):
    # validate inputs
    origin      = validate_airport_code(origin, "origin")
    destination = validate_airport_code(destination, "destination")
    date        = validate_date(date)

    # business rule validation delegated to search
    try:
        results = search_itineraries(
            origin      = origin,
            destination = destination,
            date        = date,
            airports    = airports,
            flights_by_origin_date = flights_by_origin_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "origin"     : origin,
        "destination": destination,
        "date"       : date,
        "count"      : len(results),
        "itineraries": [asdict(r) for r in results]
    }

@app.get("/api/airports")
def list_airports():
    """Returns all known airport codes — useful for frontend autocomplete."""
    return {
        "airports": [
            {"code": a.code, "name": a.name, "city": a.city, "country": a.country}
            for a in airports.values()
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok", "airports_loaded": len(airports)}
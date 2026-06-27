# SkyPath ✈ Flight Connection Search Engine

A prototype flight search engine that finds valid direct and multi-stop itineraries between airports, with full timezone-aware layover validation.

---

## Prerequisites

- Python 3.9+
- Docker Desktop — [download for Mac](https://docs.docker.com/desktop/mac/)
  - Check your Mac chip first: run `uname -m` in terminal
  - `arm64` = Apple Silicon (M1/M2/M3), `x86_64` = Intel
- Git
- Tested on Chrome browser
---

## Quick Start

```bash
git clone <your-repo-url>
cd skypath
docker compose up --build
```

Then open:
- Frontend: http://localhost:3000
- Backend API: http://localhost:4000
- Health check: http://localhost:4000/health

---

## Running Locally (without Docker)

```bash
# Install dependencies
cd backend
pip install fastapi uvicorn pytest

# Start backend
python3 -m uvicorn src.main:app --reload --port 4000

# Open frontend directly in browser
open frontend/index.html
```

---

## Running Tests

```bash
cd backend
python3 -m pytest tests/ -v
```

---

## Project Structure
skypath/

├── backend/

│   ├── src/

│   │   ├── config.py      # business rules and configuration

│   │   ├── models.py      # data classes (Airport, Flight, Itinerary...)

│   │   ├── utils.py       # timezone helpers

│   │   ├── search.py      # flight search algorithm

│   │   └── main.py        # FastAPI routes and validation

│   ├── tests/

│   │   └── test_search.py # unit tests for connection validation

│   ├── requirements.txt

│   └── Dockerfile

├── frontend/

│   ├── index.html

│   ├── style.css

│   ├── app.js

│   ├── nginx.conf

│   └── Dockerfile

├── flights.json

└── docker-compose.yml

---

## Architecture Decisions

### Backend — Python + FastAPI
Chose Python + FastAPI over Java/Spring Boot for minimal setup overhead and fast iteration. FastAPI's typed route handlers provide similar structure to Spring controllers without the boilerplate. `zoneinfo` (built into Python 3.9+) handles IANA timezone conversion accurately with no extra dependencies.

### Data loading — in-memory on startup
The dataset (260 flights, 25 airports) is small enough to load entirely into memory on startup. Built two indexes:
- `airports` — keyed by IATA code for O(1) lookup
- `flights_by_origin_date` — keyed by `(origin, date)` tuple so search never scans the full list

### Search algorithm — bounded BFS
Three separate loops handle direct, 1-stop, and 2-stop itineraries. Each loop uses the `flights_by_origin_date` index to fetch only relevant flights (~10 per airport) making the effective complexity closer to O(1) than O(n³) for this dataset size.

### Connection validation
Each consecutive flight pair is validated for:
- Same connecting airport
- Layover within 45–360 minutes (domestic) or 90–360 minutes (international)
- Domestic determination checks all three countries: origin, layover airport, and destination — catching edge cases like US→Canada→US which should be international

### Timezone handling
All flight times are stored in local time. Converted to UTC using `zoneinfo` before any duration calculation. This correctly handles dateline crossings (SYD→LAX appears to arrive before departing in local time but calculates correctly in UTC).

### Frontend — plain HTML/CSS/JS + nginx
No build tools, no framework. Served by nginx in Docker which also proxies `/api/*` requests to the backend — frontend always calls its own origin, no hardcoded backend URLs in production.

### Configuration — `config.py`
All business rules (layover minimums, cache size) and paths live in one file. The `FLIGHTS_DATA_PATH` environment variable allows Docker to override the data path without code changes — local development falls back to a relative path automatically.

---

## Tradeoffs

| Decision | Chosen | Alternative at scale |
|---|---|---|
| In-memory data | Simple, fast for 260 flights | PostgreSQL for millions of flights |
| No caching | Fine for prototype | Redis for popular routes |
| Sequential search | Fast enough for small dataset | Pre-computed connection graph |
| No auth | Fine for take-home | API keys + rate limiting |
| Plain HTML frontend | Zero build tools | React for complex state management |
| Single date support | Matches dataset | Date ranges, recurring schedules |

---

## Assumptions

- All flights in the dataset operate on `2024-03-15` (some overnight flights land on `2024-03-16` or `2024-03-17`)
- A connection is "domestic" only if origin, layover airport, and destination are all in the same country — transiting through a foreign country (e.g. US→Canada→US) counts as international and requires 90-minute minimum layover
- Maximum 2 stops per itinerary as specified
- The nested loops are technically O(n³) for 2-stop connections, but with ~10 flights per airport in this dataset it is effectively constant time. For production scale, connection pairs could be precomputed on startup reducing search to O(1) lookups — similar to how real GDS (Global Distribution Systems) work
- Price fields in `flights.json` are inconsistent (some strings, some floats) — normalized to float on load
- Passengers cannot change airports during layover (JFK→LGA is invalid)

---

## What I Would Improve With More Time

- **Database** — move from in-memory to PostgreSQL for persistence and scalability
- **More test coverage** — integration tests for full search scenarios, edge cases for dateline crossings
- **Pagination** — 27 results for JFK→LAX is fine, but popular routes at scale could return hundreds
- **Autocomplete** — the `/api/airports` endpoint exists; wire it to the frontend search inputs
- **Better error messages** — distinguish "no flights on this date" from "no valid connections exist"
- **Deploy** — containerized app is ready for Railway, Render, or AWS ECS with minimal changes
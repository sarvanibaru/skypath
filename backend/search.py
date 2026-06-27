import json
from datetime import datetime
from decimal import Decimal
from models import Airport, Flight, Segment, Layover, Itinerary
from utils import layover_minutes, total_duration_minutes
from config import (
    MIN_LAYOVER_DOMESTIC,
    MIN_LAYOVER_INTERNATIONAL,
    MAX_LAYOVER,
    DATA_PATH
)

def load_data(filepath: str = DATA_PATH) -> tuple[dict[str, Airport], dict[tuple, list[Flight]]]:
    with open(filepath) as f:
        raw = json.load(f)

    airports: dict[str, Airport] = {
        a["code"]: Airport(**a) for a in raw["airports"]
    }

    flights_by_origin_date: dict[tuple, list[Flight]] = {}
    for f in raw["flights"]:
        flight = Flight(**f)
        date   = datetime.fromisoformat(flight.departureTime).date().isoformat()
        key    = (flight.origin, date)
        flights_by_origin_date.setdefault(key, []).append(flight)

    return airports, flights_by_origin_date


def is_valid_connection(
    arriving : Flight,
    departing: Flight,
    airports : dict[str, Airport]
) -> bool:
    if arriving.destination != departing.origin:
        return False

    minutes = layover_minutes(arriving, departing, airports)

    origin_country  = airports[arriving.origin].country
    layover_country = airports[arriving.destination].country
    dest_country    = airports[departing.destination].country

    same_country = (origin_country == layover_country == dest_country)
    min_layover  = MIN_LAYOVER_DOMESTIC if same_country else MIN_LAYOVER_INTERNATIONAL

    return min_layover <= minutes <= MAX_LAYOVER


def build_itinerary(flights: list[Flight], airports: dict[str, Airport]) -> Itinerary:
    segments = [
        Segment(
            flightNumber  = f.flightNumber,
            airline       = f.airline,
            origin        = f.origin,
            destination   = f.destination,
            departureTime = f.departureTime,
            arrivalTime   = f.arrivalTime,
            price         = f.price
        ) for f in flights
    ]

    layovers = [
        Layover(
            airport         = arriving.destination,
            durationMinutes = layover_minutes(arriving, departing, airports)
        )
        for arriving, departing in zip(flights, flights[1:])
    ]

    total_price = sum(Decimal(str(f.price)) for f in flights)

    return Itinerary(
        segments             = segments,
        layovers             = layovers,
        totalDurationMinutes = total_duration_minutes(flights, airports),
        totalPrice           = float(round(total_price, 2))
    )


def search_itineraries(
    origin     : str,
    destination: str,
    date       : str,
    airports   : dict[str, Airport],
    flights_by_origin_date: dict[tuple, list[Flight]]
) -> list[Itinerary]:

    origin      = origin.strip().upper()
    destination = destination.strip().upper()
    date        = date.strip()

    if origin == destination:
        raise ValueError("Origin and destination cannot be the same")

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")

    results       = []
    origin_flights = get_flights(origin)  # fetch once

    def get_flights(airport: str) -> list[Flight]:
        return flights_by_origin_date.get((airport, date), [])

    # direct
    for f1 in origin_flights:
        if f1.destination == destination:
            results.append(build_itinerary([f1], airports))

    # 1-stop 
    for f1 in origin_flights:
        if f1.destination == destination:
            continue
        for f2 in flights_by_origin_date.get((f1.destination, date), []):
            if f2.destination != destination:
                continue
            if is_valid_connection(f1, f2, airports):
                results.append(build_itinerary([f1, f2], airports))

    # 2-stop — visited needed to prevent JFK→ORD→JFK→LAX
    for f1 in origin_flights:
        if f1.destination == destination:
            continue
        visited = {f1.origin, f1.destination}
        for f2 in flights_by_origin_date.get((f1.destination, date), []):
            if f2.destination == destination:
                continue
            if f2.destination in visited:
                continue
            if not is_valid_connection(f1, f2, airports):
                continue
            visited2 = visited | {f2.destination}
            for f3 in flights_by_origin_date.get((f2.destination, date), []):
                if f3.destination != destination:
                    continue
                if f3.destination in visited2:
                    continue
                if is_valid_connection(f2, f3, airports):
                    results.append(build_itinerary([f1, f2, f3], airports))

    results.sort(key=lambda x: x.totalDurationMinutes)
    return results
import os
import pytest
from src.search import is_valid_connection, load_data, search_itineraries
from src.models import Flight

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "flights.json")

# ── fixtures ───────────────────────────────────────────────
@pytest.fixture(scope="session")
def data():
    airports, flights_by_origin_date = load_data(DATA_PATH)
    return airports, flights_by_origin_date

@pytest.fixture(scope="session")
def airports(data):
    return data[0]

@pytest.fixture(scope="session")
def flights_by_origin_date(data):
    return data[1]

# ── helpers ────────────────────────────────────────────────
def make_flight(origin, destination, dep, arr, price=200):
    return Flight(
        flightNumber="TEST",
        airline="Test Air",
        origin=origin,
        destination=destination,
        departureTime=dep,
        arrivalTime=arr,
        price=price,
        aircraft="A320"
    )

# ── tests ──────────────────────────────────────────────────
def test_valid_domestic_connection(airports):
    f1 = make_flight("JFK", "ORD", "2024-03-15T07:00:00", "2024-03-15T08:30:00")
    f2 = make_flight("ORD", "LAX", "2024-03-15T09:15:00", "2024-03-15T11:30:00")
    assert is_valid_connection(f1, f2, airports) == True

def test_domestic_layover_too_short(airports):
    f1 = make_flight("JFK", "ORD", "2024-03-15T07:00:00", "2024-03-15T08:30:00")
    f2 = make_flight("ORD", "LAX", "2024-03-15T09:00:00", "2024-03-15T11:00:00")
    assert is_valid_connection(f1, f2, airports) == False

def test_international_layover_minimum(airports):
    f1 = make_flight("SFO", "LAX", "2024-03-15T08:00:00", "2024-03-15T09:30:00")
    f2 = make_flight("LAX", "NRT", "2024-03-15T11:00:00", "2024-03-16T15:00:00")
    assert is_valid_connection(f1, f2, airports) == True

def test_international_layover_too_short(airports):
    f1 = make_flight("SFO", "LAX", "2024-03-15T08:00:00", "2024-03-15T09:30:00")
    f2 = make_flight("LAX", "NRT", "2024-03-15T10:45:00", "2024-03-16T15:00:00")
    assert is_valid_connection(f1, f2, airports) == False

def test_layover_too_long(airports):
    f1 = make_flight("JFK", "ORD", "2024-03-15T07:00:00", "2024-03-15T08:30:00")
    f2 = make_flight("ORD", "LAX", "2024-03-15T16:00:00", "2024-03-15T18:00:00")
    assert is_valid_connection(f1, f2, airports) == False

def test_wrong_airport_connection(airports):
    f1 = make_flight("JFK", "ORD", "2024-03-15T07:00:00", "2024-03-15T08:30:00")
    f2 = make_flight("LAX", "SFO", "2024-03-15T10:00:00", "2024-03-15T11:30:00")
    assert is_valid_connection(f1, f2, airports) == False

def test_same_origin_destination(airports, flights_by_origin_date):
    with pytest.raises(ValueError):
        search_itineraries("JFK", "JFK", "2024-03-15", airports, flights_by_origin_date)
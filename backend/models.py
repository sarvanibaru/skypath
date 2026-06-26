from dataclasses import dataclass, field
from typing import List

@dataclass
class FlightBase:
    flightNumber: str
    airline: str
    origin: str
    destination: str
    departureTime: str  # local time string e.g. "2024-03-15T08:30:00"
    arrivalTime: str    # local time string
    price: float

@dataclass
class Flight(FlightBase):
    aircraft: str       # internal field, not exposed to frontend

@dataclass
class Segment(FlightBase):
    pass                # inherits all FlightBase fields, acts as DTO

@dataclass
class Airport:
    code: str
    name: str
    city: str
    country: str
    timezone: str

@dataclass
class Layover:
    airport: str
    durationMinutes: int

@dataclass
class Itinerary:
    segments: List[Segment]
    layovers: List[Layover]
    totalDurationMinutes: int
    totalPrice: float
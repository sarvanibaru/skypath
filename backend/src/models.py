from dataclasses import dataclass

@dataclass
class FlightBase:
    flightNumber : str
    airline      : str
    origin       : str
    destination  : str
    departureTime: str
    arrivalTime  : str
    price        : float

@dataclass
class Flight(FlightBase):
    aircraft: str

@dataclass
class Segment(FlightBase):
    pass

@dataclass
class Airport:
    code    : str
    name    : str
    city    : str
    country : str
    timezone: str

@dataclass
class Layover:
    airport        : str
    durationMinutes: int

@dataclass
class Itinerary:
    segments            : list[Segment]
    layovers            : list[Layover]
    totalDurationMinutes: int
    totalPrice          : float
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from functools import lru_cache
from src.models import Flight, Airport
from src.config import TIMEZONE_CACHE_SIZE 

@lru_cache(maxsize=TIMEZONE_CACHE_SIZE)
def _get_timezone(tz_name: str) -> ZoneInfo:
    """Cache timezone objects — bounded by TIMEZONE_CACHE_SIZE in config."""
    return ZoneInfo(tz_name)

def _to_utc(local_time_str: str, tz_name: str):
    """Convert local time string to UTC datetime. Private helper."""
    local_dt = datetime.fromisoformat(local_time_str)
    local_dt = local_dt.replace(tzinfo=_get_timezone(tz_name))
    return local_dt.astimezone(timezone.utc)

def layover_minutes(arriving: Flight, departing: Flight, airports: dict[str, Airport]) -> int:
    """Calculate layover duration in minutes between two flights."""
    arr_tz  = airports[arriving.destination].timezone
    dep_tz  = airports[departing.origin].timezone
    arr_utc = _to_utc(arriving.arrivalTime, arr_tz)
    dep_utc = _to_utc(departing.departureTime, dep_tz)
    return int((dep_utc - arr_utc).total_seconds() / 60)

def total_duration_minutes(flights: list[Flight], airports: dict[str, Airport]) -> int:
    """Total trip duration from first departure to last arrival in UTC."""
    first   = flights[0]
    last    = flights[-1]
    dep_utc = _to_utc(first.departureTime, airports[first.origin].timezone)
    arr_utc = _to_utc(last.arrivalTime,    airports[last.destination].timezone)
    return int((arr_utc - dep_utc).total_seconds() / 60)
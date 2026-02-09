# backend/app/utils.py
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Literal, List, Optional
import pandas as pd

STATION_MAPPING = {
    "Meteo Station Gabriel de Castilla": "89070",
    "Meteo Station Juan Carlos I": "89064",
}

REVERSE_STATION_MAPPING = {v: k for k, v in STATION_MAPPING.items()}


def get_station_id_by_name(station_name: str) -> Optional[str]:
    return STATION_MAPPING.get(station_name)


def get_station_name_by_id(station_id: str) -> str:
    return REVERSE_STATION_MAPPING.get(station_id, f"Unknown ({station_id})")


def parse_datetime_str(dt_str: str) -> datetime:
    """Parsea '2025-02-09T12:00:00' a datetime naive"""
    try:
        return datetime.fromisoformat(dt_str)
    except ValueError:
        raise ValueError(f"Formato inválido: {dt_str}. Use AAAA-MM-DDTHH:MM:SS")


def to_madrid_datetime(dt_utc: datetime) -> datetime:
    """Convierte un datetime en UTC a Europe/Madrid (maneja DST automáticamente)"""
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))
    return dt_utc.astimezone(ZoneInfo("Europe/Madrid"))


def format_with_offset(dt: datetime) -> str:
    """Devuelve: 2025-02-09T12:00:00+01:00 o +02:00 en verano"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def get_resample_rule(aggregation: Literal["None", "Hourly", "Daily", "Monthly"]) -> Optional[str]:
    rules = {
        "Hourly": "h",
        "Daily": "D",
        "Monthly": "ME",        # Month End
    }
    return rules.get(aggregation)
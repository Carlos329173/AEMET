import httpx
import pandas as pd
from datetime import datetime
import pytz
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from .models import Measurement
from .utils import map_station_name_to_id, process_and_aggregate

AEMET_BASE = "https://opendata.aemet.es/opendata"

async def fetch_aemet_data(station_id: str, fecha_ini: str, fecha_fin: str, api_key: str):
    url = f"{AEMET_BASE}/api/antartida/datos/fechaini/{fecha_ini}/fechafin/{fecha_fin}/estacion/{station_id}"
    headers = {"api_key": api_key}

import httpx
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import Measurement
from .schemas import DataRequest, MeasurementOut

AEMET_BASE_URL = "https://opendata.aemet.es/opendata"

STATION_MAPPING = {
    "Meteo Station Gabriel de Castilla": "89070",
    "Meteo Station Juan Carlos I": "89064",
}

REVERSE_STATION_MAPPING = {v: k for k, v in STATION_MAPPING.items()}


def map_station_name_to_id(station_name: str) -> Optional[str]:
    return STATION_MAPPING.get(station_name)


async def fetch_aemet_data(station_id: str, fecha_ini: str, fecha_fin: str, api_key: str) -> List[dict]:
    """Llama al endpoint de AEMET y devuelve los datos crudos."""
    url = f"{AEMET_BASE_URL}/api/antartida/datos/fechaini/{fecha_ini}/fechafin/{fecha_fin}/estacion/{station_id}"
    headers = {"api_key": api_key}

    async with httpx.AsyncClient(timeout=40.0) as client:
        # Primera llamada → obtiene la URL de datos
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        data_url = resp.json().get("datos")

        if not data_url:
            raise ValueError("AEMET no devolvió URL de datos")

        # Segunda llamada → datos reales
        data_resp = await client.get(data_url)
        data_resp.raise_for_status()
        return data_resp.json()


async def get_or_fetch_data(db: Session, request: DataRequest, api_key: str) -> List[MeasurementOut]:
    """
    1. Busca en caché (SQLite)
    2. Si faltan datos → fetch + guarda
    3. Procesa (timezone + agregación)
    4. Devuelve lista de MeasurementOut
    """
    station_id = map_station_name_to_id(request.estacion)
    if not station_id:
        raise ValueError(f"Estación desconocida: {request.estacion}")

    # Convertir fechas de entrada a UTC para almacenar y consultar
    tz_input = ZoneInfo(request.location or "Europe/Berlin")
    start_utc = request.fecha_ini.astimezone(ZoneInfo("UTC"))
    end_utc = request.fecha_fin.astimezone(ZoneInfo("UTC"))

    # === 1. Buscar en caché ===
    existing = db.query(Measurement).filter(
        and_(
            Measurement.station == station_id,
            Measurement.datetime >= start_utc,
            Measurement.datetime <= end_utc,
        )
    ).all()

    # === 2. Si faltan datos → fetch y guardar ===
    if not existing or len(existing) < 100:          # Umbral más razonable (ajusta según necesites)
        try:
            fecha_ini_str = request.fecha_ini.strftime("%Y-%m-%dT%H:%M:%S")
            fecha_fin_str = request.fecha_fin.strftime("%Y-%m-%dT%H:%M:%S")

            raw_data = await fetch_aemet_data(station_id, fecha_ini_str, fecha_fin_str, api_key)

            if raw_data:
                df = pd.DataFrame(raw_data)

                # Renombrar columnas según el challenge
                df = df.rename(columns={
                    "nombre": "station_name",
                    "fhora": "fhora_str",
                    "temp": "temperature",
                    "pres": "pressure",
                    "vel": "speed"
                })

                # Parsear datetime (AEMET suele devolverlo en hora local de la estación o UTC)
                df["datetime"] = pd.to_datetime(df["fhora_str"], errors="coerce")

                # Guardamos todo en UTC (mejor práctica)
                df["datetime"] = df["datetime"].dt.tz_localize("UTC", ambiguous="NaT", nonexistent="shift_forward")

                records_to_insert = []
                for _, row in df.iterrows():
                    if pd.isna(row["datetime"]):
                        continue

                    records_to_insert.append({
                        "station": station_id,
                        "datetime": row["datetime"].to_pydatetime(),
                        "temperature": float(row["temperature"]) if pd.notna(row.get("temperature")) else None,
                        "pressure": float(row["pressure"]) if pd.notna(row.get("pressure")) else None,
                        "speed": float(row["speed"]) if pd.notna(row.get("speed")) else None,
                        "raw_data": str(row.to_dict())   # backup
                    })

                # Inserción segura (evitamos duplicados por timestamp)
                if records_to_insert:
                    for rec in records_to_insert:
                        exists = db.query(Measurement).filter(
                            Measurement.station == rec["station"],
                            Measurement.datetime == rec["datetime"]
                        ).first()
                        if not exists:
                            db.add(Measurement(**rec))
                    db.commit()

        except Exception as e:
            # Loguear pero continuar con datos en caché si existen
            print(f"[WARNING] Error al obtener datos de AEMET: {e}")
            # En producción → usar structlog o logging configurado

    # === 3. Re-leer datos (ahora actualizados) y procesar ===
    data = db.query(Measurement).filter(
        and_(
            Measurement.station == station_id,
            Measurement.datetime >= start_utc,
            Measurement.datetime <= end_utc,
        )
    ).all()

    if not data:
        return []

    # Convertir a DataFrame para fácil manipulación
    df = pd.DataFrame([{
        "datetime_utc": d.datetime,
        "temperature": d.temperature,
        "pressure": d.pressure,
        "speed": d.speed,
    } for d in data])

    # Convertir a hora de Madrid (CET/CEST) con offset
    madrid_tz = ZoneInfo("Europe/Madrid")
    df["datetime"] = pd.to_datetime(df["datetime_utc"]).dt.tz_convert(madrid_tz)

    # Formato final con offset (ej: 2025-01-15T10:30:00+01:00)
    df["datetime_str"] = df["datetime"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Seleccionar variables solicitadas
    variables = request.variables or ["temperature", "pressure", "speed"]
    col_map = {"temperature": "temperature", "pressure": "pressure", "speed": "speed"}
    selected_cols = ["datetime_str"] + [col_map[v] for v in variables if v in col_map]

    df_out = df[selected_cols].copy()

    # === 4. Agregación ===
    if request.aggregation != "None":
        df_out = df_out.set_index("datetime")
        
        agg_dict = {
            "temperature": "mean",
            "pressure": "mean",
            "speed": "mean"
        }

        if request.aggregation == "Hourly":
            df_out = df_out.resample("h").agg(agg_dict).reset_index()
        elif request.aggregation == "Daily":
            df_out = df_out.resample("D").agg(agg_dict).reset_index()
        elif request.aggregation == "Monthly":
            df_out = df_out.resample("ME").agg(agg_dict).reset_index()

        # Volver a formatear datetime con offset
        df_out["datetime"] = pd.to_datetime(df_out["datetime"]).dt.tz_convert(madrid_tz)
        df_out["datetime_str"] = df_out["datetime"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")

    # Renombrar para el esquema de salida
    df_out = df_out.rename(columns={"datetime_str": "datetime"})

    # Convertir a lista de Pydantic models
    result = []
    for _, row in df_out.iterrows():
        result.append(MeasurementOut(
            station=REVERSE_STATION_MAPPING.get(station_id, station_id),
            datetime=row["datetime"],
            temperature=float(row["temperature"]) if pd.notna(row.get("temperature")) else None,
            pressure=float(row["pressure"]) if pd.notna(row.get("pressure")) else None,
            speed=float(row["speed"]) if pd.notna(row.get("speed")) else None,
        ))

    return result
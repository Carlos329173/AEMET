# backend/app/routers/antartida.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.schemas import MeasurementOut, DataRequest
from app.services import get_or_fetch_data
from app.utils import (
    parse_datetime_str,
    get_station_id_by_name,
    get_station_name_by_id
)
from app.dependencies import get_db
from app.config import Settings, get_settings

router = APIRouter(prefix="/api", tags=["Antártida"])


@router.get(
    "/antartida/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{identificacion}",
    response_model=List[MeasurementOut],
    summary="Obtener datos meteorológicos Antártida (AEMET)"
)
async def get_antartida_datos(
    fechaIniStr: str,
    fechaFinStr: str,
    identificacion: str,                          # 89064 o 89070
    location: str = Query("Europe/Berlin", description="Timezone del input"),
    aggregation: str = Query("None", enum=["None", "Hourly", "Daily", "Monthly"]),
    variables: List[str] = Query(
        default=[],
        description="temperature, pressure, speed (vacío = todas)"
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings)
):
    try:
        fecha_ini = parse_datetime_str(fechaIniStr)
        fecha_fin = parse_datetime_str(fechaFinStr)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if fecha_ini >= fecha_fin:
        raise HTTPException(status_code=400, detail="fechaIniStr debe ser anterior a fechaFinStr")

    # Validar estación
    station_name = get_station_name_by_id(identificacion)
    if "Unknown" in station_name:
        raise HTTPException(status_code=400, detail="Estación no válida. Use: 89064 (Juan Carlos I) o 89070 (Gabriel de Castilla)")

    # Construimos el modelo interno
    request_body = DataRequest(
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin,
        location=location,
        estacion=station_name,
        aggregation=aggregation,          # type: ignore
        variables=variables or []
    )

    # Llamamos al servicio principal
    result = await get_or_fetch_data(
        db=db,
        request=request_body,
        api_key=settings.AEMET_API_KEY
    )

    return result
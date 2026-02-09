from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional

from .models import Measurement


def get_measurements_by_range(
    db: Session,
    station_id: str,
    start: datetime,
    end: datetime
) -> List[Measurement]:
    """Obtiene mediciones en un rango de fechas (UTC)"""
    return db.query(Measurement).filter(
        and_(
            Measurement.station == station_id,
            Measurement.datetime >= start,
            Measurement.datetime <= end,
        )
    ).order_by(Measurement.datetime).all()


def create_measurements_bulk(
    db: Session,
    records: List[dict]
) -> int:
    """Inserta múltiples registros evitando duplicados por (station + datetime)"""
    inserted = 0
    for rec in records:
        # Verificar si ya existe
        exists = db.query(Measurement).filter(
            Measurement.station == rec["station"],
            Measurement.datetime == rec["datetime"]
        ).first()

        if not exists:
            db.add(Measurement(**rec))
            inserted += 1

    if inserted > 0:
        db.commit()
    return inserted


def get_all_stations(db: Session) -> List[str]:
    """Devuelve las estaciones que tenemos en la BBDD"""
    return [row[0] for row in db.query(Measurement.station).distinct().all()]
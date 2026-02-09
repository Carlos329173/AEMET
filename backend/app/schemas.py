from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, List, Optional

class DataRequest(BaseModel):
    fecha_ini: datetime = Field(..., description="AAAA-MM-DDTHH:MM:SS")
    fecha_fin: datetime = Field(..., description="AAAA-MM-DDTHH:MM:SS")
    location: Optional[str] = "Europe/Berlin"   # Timezone del input
    estacion: Literal["Meteo Station Gabriel de Castilla", "Meteo Station Juan Carlos I"]
    aggregation: Literal["None", "Hourly", "Daily", "Monthly"] = "None"
    variables: List[Literal["temperature", "pressure", "speed"]] = Field(
        default_factory=list, description="Vacío = todas"
    )

class MeasurementOut(BaseModel):
    station: str
    datetime: str   # Con offset, ej: 2025-01-01T10:00:00+01:00
    temperature: Optional[float]
    pressure: Optional[float]
    speed: Optional[float]

    class Config:
        from_attributes = True
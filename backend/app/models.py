from sqlalchemy import Column, Integer, String, Float, DateTime
from .database import Base
from datetime import datetime

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    station = Column(String, index=True)           # "89064" o "89070"
    datetime = Column(DateTime, index=True)        # Guardamos en UTC
    temperature = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    raw_data = Column(String)                      # JSON original por si acaso
from sqlalchemy.orm import Session
from fastapi import Depends

from .database import SessionLocal
from .config import Settings, get_settings


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Para usar settings en los routers
def get_settings_dependency() -> Settings:
    return get_settings()
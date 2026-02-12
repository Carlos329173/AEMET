# Etapa base - builder
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero → mejor cacheo de capas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app/ ./app

# Crear directorios para datos persistentes y logs
RUN mkdir -p /app/data /app/logs \
    && chmod -R 777 /app/data /app/logs

# Etapa final - imagen más ligera
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copiar solo lo necesario desde la etapa builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Puerto de FastAPI
EXPOSE 8000

# Ejecutar con uvicorn (workers ajustables según CPU)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
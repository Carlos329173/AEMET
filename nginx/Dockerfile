# Etapa 1: Builder (opcional, pero £til si quieres validar sintaxis nginx)
FROM nginx:alpine AS builder

# Copiamos la configuraci¢n para validarla (opcional)
WORKDIR /etc/nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Validar sintaxis (falla el build si hay error)
RUN nginx -t


# Etapa 2: Imagen final - muy ligera
FROM nginx:alpine

# Etiquetas recomendadas (OCI)
LABEL maintainer="tu-nombre@empresa.com" \
      org.opencontainers.image.title="Nginx Reverse Proxy" \
      org.opencontainers.image.description="Reverse proxy para FastAPI + React frontend" \
      org.opencontainers.image.source="https://github.com/tu-repo/aemet-antartida-api"

# Crear directorios necesarios y ajustar permisos
RUN mkdir -p /var/cache/nginx/client_temp \
    && chown -R nginx:nginx /var/cache/nginx \
    && chmod -R 755 /var/cache/nginx

# Copiar configuraci¢n (sobrescribe la default)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Eliminar configuraci¢n por defecto que no usamos
RUN rm -f /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

# Usuario no root (ya viene en alpine, pero lo reforzamos)
USER nginx

# Healthcheck (£til para docker compose / kubernetes)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Puerto expuesto
EXPOSE 80 443

# Comando por defecto
CMD ["nginx", "-g", "daemon off;"]

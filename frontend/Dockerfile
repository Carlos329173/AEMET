# Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm config set strict-ssl false   # temporary - insecure

# Serve con nginx (ligero)
FROM nginx:alpine

# Copiamos solo lo que generó Vite
COPY --from=builder /app/dist /usr/share/nginx/html

# NO necesitamos copiar ningún nginx.conf → usamos el default de nginx:alpine
# (ya sirve contenido estático correctamente desde /usr/share/nginx/html)

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

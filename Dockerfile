# Stage 1: Build Vue Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.12-slim
WORKDIR /app

# Instalar git y dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Copiar dependencias del backend e instalarlas
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del backend
COPY backend/ ./backend

# Copiar artefactos compilados del frontend desde la Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Exponer el puerto interno
EXPOSE 4000

# Variables de entorno por defecto
ENV PORT=4000
ENV PYTHONPATH=/app/backend

WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000"]

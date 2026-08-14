#!/usr/bin/env bash
set -e

echo "=== Instalación de PteroDev Companion ==="

# 1. Generar SECRET_ENCRYPT_KEY si no existe en .env
if [ ! -f .env ]; then
    echo "Generando archivo .env..."
    PYTHON_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || echo "gAAAAABl_example_key_change_me_in_production=")
    cat <<EOF > .env
SECRET_ENCRYPT_KEY=${PYTHON_KEY}
JWT_SECRET=$(openssl rand -hex 16 2>/dev/null || echo "super-secret-jwt-key")
PTERODACTYL_URL=https://panel.fenixcloud.xyz/api/client
GEMINI_API_KEY=
DB_PATH=companion.db
EOF
    echo "Archivo .env creado con éxito."
else
    echo "El archivo .env ya existe."
fi

# 2. Levantar el contenedor Docker
if command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1; then
    echo "Desplegando contenedor Docker..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d --build
    else
        docker compose up -d --build
    fi
else
    echo "Aviso: Docker Compose no está disponible en este entorno. Puedes ejecutar el backend manualmente con uvicorn."
fi

# 3. Generar configuración para Nginx Proxy Inverso
NGINX_CONF_PATH="/etc/nginx/sites-available/pterodev-companion.conf"
echo "Generando plantilla de Nginx Proxy Inverso en ./nginx-pterodev.conf..."

cat <<'EOF' > nginx-pterodev.conf
server {
    listen 80;
    server_name companion.local;

    location / {
        proxy_pass http://127.0.0.1:4000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

if [ -d "/etc/nginx/sites-available" ] && [ "$(id -u)" -eq 0 ]; then
    cp nginx-pterodev.conf "$NGINX_CONF_PATH"
    ln -sf "$NGINX_CONF_PATH" /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx || true
    echo "Configuración de Nginx instalada en $NGINX_CONF_PATH."
fi

echo "=== Instalación de PteroDev Companion finalizada exitosamente ==="

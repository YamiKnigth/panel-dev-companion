# PteroDev Companion 🚀

**PteroDev Companion** es un entorno de desarrollo privado y aislado (FastAPI + Vue 3 + SQLite) diseñado como un copiloto de desarrollo e integración para servidores de Pterodactyl (especialmente optimizado para servidores de Minecraft).

---

## 📋 Contenido del Repositorio

El repositorio está organizado en las siguientes carpetas y componentes:

```text
panel-dev-companion/
├── backend/                  # Código fuente del Backend (FastAPI)
│   ├── main.py               # Servidor principal, endpoints de API y proxies
│   ├── vault.py              # Bóveda segura (SQLite + Fernet encryption)
│   ├── auth.py               # Gestión de JWT de sesión local
│   ├── ai_engine.py          # Copiloto de Inteligencia Artificial (Google Gemini API)
│   ├── db_chat.py            # Almacenamiento de historial de chat de la IA en SQLite
│   ├── git_sync.py           # Motor de sincronización de repositorios Git
│   ├── requirements.txt      # Dependencias de Python
│   └── test_milestone*.py    # Scripts de pruebas automatizadas por Hitos
├── frontend/                 # Código fuente del Frontend (Vue 3 + Vite + Tailwind CSS)
│   ├── src/
│   │   ├── components/       # Componentes Vue (Login, Dashboard, Terminal, Editor, GitSync, CopilotDrawer)
│   │   ├── App.vue           # Vista principal
│   │   └── style.css         # Estilos globales y configuración Tailwind CSS
│   ├── dist/                 # Artefactos compilados estáticos del Frontend
│   └── package.json          # Dependencias y scripts de Node.js
├── Dockerfile                # Compilación Multi-Stage (Node build -> Python runtime)
├── docker-compose.yml        # Orquestación de contenedores y volúmenes de datos
├── install.sh                # Script de instalación y despliegue automatizado Cero-Fricciones
├── nginx-pterodev.conf       # Plantilla de Proxy Inverso para Nginx
└── README.md                 # Documentación del proyecto
```

---

## 🌟 Características Principales

1. **Bóveda Segura (Zero-Trust):**
   - Cifrado simétrico Fernet para tokens individuales de servidores guardados en SQLite (`companion.db`).
   - Filtrado estricto: Solo muestra servidores donde seas el propietario (`server_owner == true`).
   - Los servidores bloqueados no permiten ninguna operación hasta ingresar su clave individual (HTTP 403 enforcement).

2. **Copiloto de Inteligencia Artificial (Google Gemini):**
   - **Agente Experto en Minecraft:** Configurado con instrucciones de sistema para diagnosticar software (Paper, Spigot, Forge, Fabric, etc.) y versiones.
   - **Análisis de Consola:** Botón "🔍 Analizar Error" para diagnosticar crasheos en los logs.
   - **Edición Automática e Inyección:** Botón "✨ Modificar con IA" para modificar archivos de configuración directamente mediante instrucciones en lenguaje natural.
   - **Chat Contextual:** Panel lateral colapsable Caddy / Copilot con memoria contextual guardada en SQLite.

3. **Gestión e Interfaz de Servidor:**
   - **Terminal:** Envío inmediato de comandos a la consola de Pterodactyl.
   - **Editor de Código:** Explorador de archivos e inyección con cabecera estricta `Content-Type: text/plain`.
   - **Git Sync:** Sincronización e inyección directa de archivos desde repositorios Git remotos ignorando la carpeta `.git`.

---

## ⚙️ Variables de Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto con la siguiente configuración:

```env
# Clave simétrica Fernet para cifrar tokens en SQLite (se autogenera con install.sh)
SECRET_ENCRYPT_KEY=tu_clave_fernet_aqui

# Secreto para la firma de tokens JWT locales
JWT_SECRET=super-secret-pterodev-companion-key

# URL Base de la API Client de tu panel Pterodactyl
PTERODACTYL_URL=https://panel.fenixcloud.xyz/api/client

# API Key de Google Gemini (opcional para funciones de IA)
GEMINI_API_KEY=tu_gemini_api_key_aqui

# Ruta de la base de datos SQLite
DB_PATH=companion.db
```

---

## 🚀 Paso a Paso: Instalación y Despliegue en Producción

### Opción 1: Instalación Cero-Fricciones con Script (Recomendado)

Ejecuta el script `install.sh` que creará las variables de entorno, compilará la imagen de Docker, levantará el servicio y generará la configuración para Nginx:

```bash
chmod +x install.sh
./install.sh
```

### Opción 2: Despliegue con Docker Compose

```bash
# 1. Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd panel-dev-companion

# 2. Iniciar con Docker Compose (Construye el frontend Vue y levanta FastAPI)
docker-compose up -d --build
```

El servicio estará disponible en el puerto local `4000` (`http://localhost:4000`).

---

## 🧪 Guía para Ejecución y Pruebas Locales (Entorno de Desarrollo)

Si deseas probar o desarrollar de forma local sin Docker, sigue estos pasos:

### 1. Requisitos Previos
- Python 3.10+
- Node.js 18+ y npm

### 2. Configuración del Backend

```bash
# Instalar dependencias de Python
pip install -r backend/requirements.txt

# Generar archivo .env inicial
python3 backend/create_env.py
```

### 3. Ejecutar las Pruebas Automatizadas de los Hitos

Puedes verificar el correcto funcionamiento de cada hito mediante los scripts de prueba incluidos:

```bash
# Probar Bóveda y Cifrado Fernet (Milestone 1)
python3 backend/test_milestone1.py

# Probar Autenticación y Descubrimiento Zero-Trust (Milestone 2)
python3 backend/test_milestone2.py

# Probar Proxy de API, Comandos y Lectura/Escritura de Archivos (Milestone 3)
python3 backend/test_milestone3.py

# Probar Motor de Inteligencia Artificial Gemini (Milestone 4)
python3 backend/test_milestone4.py

# Probar Motor de Sincronización Git (Milestone 5)
python3 backend/test_milestone5.py
```

### 4. Compilar e Iniciar el Servidor de Pruebas

#### Modo A: Servidor Unificado (Servir Frontend Compilado + Backend)
```bash
# Compilar el Frontend Vue
cd frontend
npm install
npm run build
cd ..

# Iniciar el servidor FastAPI (escuchando en puerto 8000)
PYTHONPATH=backend uvicorn main:app --reload --port 8000
```
Abre tu navegador en `http://localhost:8000`.

#### Modo B: Servidor de Desarrollo Frontend con HMR (Hot Module Replacement)
```bash
# En una terminal: Iniciar el Backend
PYTHONPATH=backend uvicorn main:app --reload --port 8000

# En otra terminal: Iniciar el servidor dev de Vite
cd frontend
npm run dev
```
Abre tu navegador en `http://localhost:3000` (los endpoints `/api` se redirigirán automáticamente al puerto 8000).

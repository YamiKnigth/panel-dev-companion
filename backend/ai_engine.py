import os
import google.generativeai as genai
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DEFAULT_MODEL = "gemini-1.5-flash"

MINECRAFT_SYSTEM_INSTRUCTION = """
Eres un Agente Experto en Servidores de Minecraft (Paper, Spigot, Forge, Fabric, Purpur, Velocity, BungeeCord, Vanilla, etc.).
Tu objetivo es ayudar a administrar, reparar, depurar y optimizar servidores de Minecraft.
Debes analizar atentamente los logs, archivos de configuración (server.properties, paper.yml, spigot.yml, plugins/..., config.yml) y responder con soluciones precisas, directas y efectivas.
Si se te proporciona información de archivos o logs del servidor, utilízala para determinar con exactitud el software y versión de Minecraft instalados.
"""

def get_model(system_instruction: Optional[str] = MINECRAFT_SYSTEM_INSTRUCTION):
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction
    )

async def analyze_logs_ai(logs_text: str) -> str:
    if not GEMINI_API_KEY:
        return f"[Simulación IA - GEMINI_API_KEY no configurada] Análisis de logs:\n" \
               f"Se detectaron {len(logs_text.splitlines())} líneas de log. " \
               f"Revisa posibles conflictos de plugins, versiones incompatibles de Java o archivos corruptos."

    prompt = f"""
Analiza los siguientes logs de la consola del servidor de Minecraft (últimas líneas):

```
{logs_text}
```

Identifica el tipo de servidor de Minecraft y versión si están visibles, la causa raíz del error o crasheo, y proporciona la solución exacta o comando para corregirlo.
    """
    model = get_model()
    response = model.generate_content(prompt)
    return response.text

async def edit_file_ai(file_path: str, current_content: str, user_prompt: str) -> str:
    if not GEMINI_API_KEY:
        # En modo simulación (sin API key), devolvemos el contenido con un comentario descriptivo
        return f"# Modificado por IA (Simulación para {file_path}): {user_prompt}\n" + current_content

    prompt = f"""
Eres un motor de edición automática de código para servidores de Minecraft.
El usuario desea modificar el archivo `{file_path}`.

Instrucción del usuario:
"{user_prompt}"

Contenido actual del archivo:
```
{current_content}
```

REGLA ESTRICTA DE SALIDA:
Devuelve EXCLUSIVAMENTE el nuevo contenido completo del archivo modificado.
NO incluyas bloques de código Markdown (no uses ``` ni ```yaml ni ```json ni ```text), NO agregues explicaciones, introducciones o comentarios adicionales fuera del propio archivo.
Solo el código/texto plano final que debe ser guardado en el archivo.
    """
    model = get_model()
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Limpiar cualquier cerco Markdown si la IA por error lo incluyó
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()
        if len(lines) >= 2 and lines[-1].startswith("```"):
            raw_text = "\n".join(lines[1:-1]).strip()
    return raw_text

async def chat_ai(server_info: str, history: List[Dict[str, str]], user_message: str) -> str:
    if not GEMINI_API_KEY:
        return f"[Simulación IA - Experto Minecraft]: He recibido tu mensaje: '{user_message}'. Servidor detectado: {server_info}."

    model = get_model()

    # Construir contexto de conversación
    formatted_history = []
    for msg in history:
        role = "user" if msg["role"] in ("user", "human") else "model"
        formatted_history.append({"role": role, "parts": [msg["content"]]})

    chat = model.start_chat(history=formatted_history)
    prompt = f"[Contexto del servidor: {server_info}]\n\nMensaje del usuario: {user_message}"
    response = chat.send_message(prompt)
    return response.text

import os
import httpx
from fastapi import FastAPI, HTTPException, Depends, Header, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

from vault import init_db, is_server_unlocked, get_server_token, save_server_token
from auth import create_access_token, verify_token
from db_chat import add_chat_message, get_chat_history, clear_chat_history
from ai_engine import analyze_logs_ai, edit_file_ai, chat_ai
from git_sync import sync_git_repository

load_dotenv()

PTERODACTYL_URL = os.getenv("PTERODACTYL_URL", "https://panel.fenixcloud.xyz/api/client").rstrip("/")

app = FastAPI(title="PteroDev Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# --- Models ---
class LoginRequest(BaseModel):
    api_key: str

class UnlockRequest(BaseModel):
    identifier: str
    token: str

class CommandRequest(BaseModel):
    command: str

class AnalyzeLogsRequest(BaseModel):
    logs: str

class EditFileAIRequest(BaseModel):
    file_path: str
    user_prompt: str

class ChatAIRequest(BaseModel):
    message: str

class GitSyncRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = "main"

# --- Helper: Get Unlocked Server Token ---
def require_server_token(identifier: str) -> str:
    token = get_server_token(identifier)
    if not token:
        raise HTTPException(
            status_code=403,
            detail=f"Servidor {identifier} está bloqueado. Debe proveer un token individual."
        )
    return token

# --- Authentication & Discovery ---
@app.post("/api/auth/login")
async def login(req: LoginRequest):
    api_key = req.api_key.strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key es requerida")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.get(PTERODACTYL_URL, headers=headers)
            if res.status_code in (401, 403):
                raise HTTPException(status_code=401, detail="Master API Key inválida o no autorizada en Pterodactyl")
            elif res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Error de Pterodactyl: {res.text}")

            ptero_data = res.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"No se pudo conectar a Pterodactyl: {str(exc)}")

    raw_servers = ptero_data.get("data", [])
    filtered_servers = []

    for item in raw_servers:
        attrs = item.get("attributes", {})
        if attrs.get("server_owner") is True:
            identifier = attrs.get("identifier")
            attrs["is_unlocked"] = is_server_unlocked(identifier)
            filtered_servers.append({
                "object": item.get("object", "server"),
                "attributes": attrs
            })

    session_token = create_access_token({"sub": "admin", "master_key": api_key})

    return {
        "token": session_token,
        "servers": filtered_servers
    }

# --- Server Unlock ---
@app.post("/api/servers/unlock")
async def unlock_server(req: UnlockRequest, auth_payload: dict = Depends(verify_token)):
    identifier = req.identifier.strip()
    token = req.token.strip()

    if not identifier or not token:
        raise HTTPException(status_code=400, detail="identifier y token son requeridos")

    url = f"{PTERODACTYL_URL}/servers/{identifier}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.get(url, headers=headers)
            if res.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="El token ingresado no es válido para este servidor en Pterodactyl"
                )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error al verificar token con Pterodactyl: {str(exc)}")

    save_server_token(identifier, token)
    return {"message": f"Servidor {identifier} desbloqueado exitosamente", "is_unlocked": True}

# --- Proxy: Console Command ---
@app.post("/api/servers/{identifier}/command")
async def send_command(identifier: str, req: CommandRequest, auth_payload: dict = Depends(verify_token)):
    token = require_server_token(identifier)
    url = f"{PTERODACTYL_URL}/servers/{identifier}/command"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.post(url, headers=headers, json={"command": req.command})
            if res.status_code not in (200, 204):
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return Response(status_code=204)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error de red con Pterodactyl: {str(exc)}")

# --- Proxy: List Files ---
@app.get("/api/servers/{identifier}/files/list")
async def list_files(identifier: str, directory: str = Query("/", alias="directory"), auth_payload: dict = Depends(verify_token)):
    token = require_server_token(identifier)
    url = f"{PTERODACTYL_URL}/servers/{identifier}/files/list"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.get(url, headers=headers, params={"directory": directory})
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return res.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error de red con Pterodactyl: {str(exc)}")

# --- Proxy: Read File ---
@app.get("/api/servers/{identifier}/files/contents")
async def read_file_content(identifier: str, file: str = Query(...), auth_payload: dict = Depends(verify_token)):
    token = require_server_token(identifier)
    url = f"{PTERODACTYL_URL}/servers/{identifier}/files/contents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.get(url, headers=headers, params={"file": file})
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return Response(content=res.text, media_type="text/plain")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error de red con Pterodactyl: {str(exc)}")

# --- Proxy: Write File ---
@app.post("/api/servers/{identifier}/files/write")
async def write_file_content(identifier: str, request: Request, file: str = Query(...), auth_payload: dict = Depends(verify_token)):
    token = require_server_token(identifier)
    body = await request.body()
    url = f"{PTERODACTYL_URL}/servers/{identifier}/files/write"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.post(url, headers=headers, params={"file": file}, content=body)
            if res.status_code not in (200, 204):
                raise HTTPException(status_code=res.status_code, detail=res.text)
            return Response(status_code=204)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error de red con Pterodactyl: {str(exc)}")

# --- AI Engine Endpoints ---

@app.post("/api/servers/{identifier}/ai/analyze-logs")
async def ai_analyze_logs(identifier: str, req: AnalyzeLogsRequest, auth_payload: dict = Depends(verify_token)):
    require_server_token(identifier)
    if not req.logs.strip():
        raise HTTPException(status_code=400, detail="No hay logs para analizar")

    analysis = await analyze_logs_ai(req.logs)
    return {"analysis": analysis}

@app.post("/api/servers/{identifier}/ai/edit-file")
async def ai_edit_file(identifier: str, req: EditFileAIRequest, auth_payload: dict = Depends(verify_token)):
    token = require_server_token(identifier)
    file_path = req.file_path

    url_read = f"{PTERODACTYL_URL}/servers/{identifier}/files/contents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.get(url_read, headers=headers, params={"file": file_path})
            if res.status_code != 200:
                raise HTTPException(status_code=res.status_code, detail=f"Error leyendo archivo {file_path}: {res.text}")
            current_content = res.text
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error de red leyendo {file_path}: {str(exc)}")

    new_content = await edit_file_ai(file_path, current_content, req.user_prompt)

    url_write = f"{PTERODACTYL_URL}/servers/{identifier}/files/write"
    headers_write = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            res = await client.post(url_write, headers=headers_write, params={"file": file_path}, content=new_content.encode("utf-8"))
            if res.status_code not in (200, 204):
                raise HTTPException(status_code=res.status_code, detail=f"Error guardando archivo modificado: {res.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Error de red escribiendo {file_path}: {str(exc)}")

    return {"message": f"Archivo {file_path} modificado con éxito por IA", "new_content": new_content}

@app.get("/api/servers/{identifier}/ai/chat")
async def get_ai_chat_history(identifier: str, auth_payload: dict = Depends(verify_token)):
    require_server_token(identifier)
    history = get_chat_history(identifier)
    return {"history": history}

@app.post("/api/servers/{identifier}/ai/chat")
async def ai_chat(identifier: str, req: ChatAIRequest, auth_payload: dict = Depends(verify_token)):
    token = require_server_token(identifier)
    user_msg = req.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

    add_chat_message(identifier, "user", user_msg)
    history = get_chat_history(identifier, limit=10)

    server_info = f"Servidor ID: {identifier}"
    url_details = f"{PTERODACTYL_URL}/servers/{identifier}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(url_details, headers=headers)
            if res.status_code == 200:
                s_data = res.json().get("attributes", {})
                s_name = s_data.get("name", "")
                s_node = s_data.get("node", "")
                server_info += f", Nombre: {s_name}, Nodo: {s_node}"
        except Exception:
            pass

    ai_reply = await chat_ai(server_info, history[:-1], user_msg)
    add_chat_message(identifier, "model", ai_reply)

    return {"reply": ai_reply}

# --- Git Sync Endpoint ---

@app.post("/api/servers/{identifier}/git/sync")
async def sync_git(identifier: str, req: GitSyncRequest, auth_payload: dict = Depends(verify_token)):
    require_server_token(identifier)
    if not req.repo_url.strip():
        raise HTTPException(status_code=400, detail="repo_url es requerida")

    res = await sync_git_repository(identifier, req.repo_url, req.branch or "main")
    return res

# --- Serve Static Frontend Files ---
frontend_dist_path = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist_path):
    assets_path = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="API route not found")
        target_file = os.path.join(frontend_dist_path, full_path)
        if full_path and os.path.exists(target_file) and os.path.isfile(target_file):
            return FileResponse(target_file)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

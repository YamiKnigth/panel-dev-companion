import os
import shutil
import tempfile
import git
import httpx
from fastapi import HTTPException

from vault import get_server_token

PTERODACTYL_URL = os.getenv("PTERODACTYL_URL", "https://panel.fenixcloud.xyz/api/client").rstrip("/")

async def sync_git_repository(identifier: str, repo_url: str, branch: str = "main") -> dict:
    token = get_server_token(identifier)
    if not token:
        raise HTTPException(status_code=403, detail=f"Servidor {identifier} bloqueado. Se requiere token.")

    temp_dir = os.path.join(tempfile.gettempdir(), "git_sync", identifier)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        print(f"Clonando {repo_url} (rama: {branch}) en {temp_dir}...")
        git.Repo.clone_from(repo_url, temp_dir, branch=branch, depth=1)
    except Exception as e:
        try:
            git.Repo.clone_from(repo_url, temp_dir, depth=1)
        except Exception as e2:
            raise HTTPException(status_code=400, detail=f"Error clonando repositorio Git: {str(e2)}")

    synced_files = []
    failed_files = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for root, dirs, files in os.walk(temp_dir):
            if ".git" in root.split(os.sep):
                continue

            for file_name in files:
                full_local_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(full_local_path, temp_dir)
                ptero_file_path = "/" + rel_path.replace("\\", "/")

                try:
                    with open(full_local_path, "rb") as f:
                        file_content = f.read()

                    url_write = f"{PTERODACTYL_URL}/servers/{identifier}/files/write"
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "text/plain",
                        "Accept": "application/json"
                    }

                    res = await client.post(
                        url_write,
                        headers=headers,
                        params={"file": ptero_file_path},
                        content=file_content
                    )

                    if res.status_code in (200, 204):
                        synced_files.append(ptero_file_path)
                    else:
                        failed_files.append({"file": ptero_file_path, "error": res.text})
                except Exception as exc:
                    failed_files.append({"file": ptero_file_path, "error": str(exc)})

    shutil.rmtree(temp_dir, ignore_errors=True)

    return {
        "message": f"Sincronización Git completada para {identifier}",
        "total_synced": len(synced_files),
        "synced_files": synced_files,
        "failed_files": failed_files
    }

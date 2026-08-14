import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(__file__))

from main import app
from vault import init_db, save_server_token
from auth import create_access_token

client = TestClient(app)
jwt_token = create_access_token({"sub": "admin"})
auth_headers = {"Authorization": f"Bearer {jwt_token}"}

def setup_module():
    init_db()

def test_git_sync_endpoint():
    srv_id = "git_srv_1"
    save_server_token(srv_id, "token_git_1")

    with patch("git_sync.git.Repo.clone_from") as mock_clone, patch("httpx.AsyncClient.post") as mock_post:
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 204
        mock_post.return_value = mock_post_resp

        # Simular clonado creando un archivo en el directorio temporal si se pasa
        def side_effect_clone(url, to_path, **kwargs):
            os.makedirs(to_path, exist_ok=True)
            with open(os.path.join(to_path, "README.md"), "w") as f:
                f.write("# Test Repo")
            git_dir = os.path.join(to_path, ".git")
            os.makedirs(git_dir, exist_ok=True)
            with open(os.path.join(git_dir, "config"), "w") as f:
                f.write("git config")

        mock_clone.side_effect = side_effect_clone

        response = client.post(
            f"/api/servers/{srv_id}/git/sync",
            json={"repo_url": "https://github.com/example/repo.git", "branch": "main"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_synced"] == 1
        assert "/README.md" in data["synced_files"]
        print("✓ Motor de sincronización Git e ignorado de carpeta .git verificado.")

if __name__ == "__main__":
    setup_module()
    test_git_sync_endpoint()
    print("\n¡TODAS LAS PRUEBAS DEL MILESTONE 5 PASARON CON ÉXITO!")

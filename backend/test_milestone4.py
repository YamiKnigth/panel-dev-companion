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

def test_ai_analyze_logs():
    srv_id = "ai_srv_1"
    save_server_token(srv_id, "token_ai_1")

    logs = "[12:00:00 ERROR]: Could not load 'plugins/Essentials.jar' in folder 'plugins'\njava.lang.ClassNotFoundException: org.bukkit.plugin.java.JavaPlugin"

    response = client.post(
        f"/api/servers/{srv_id}/ai/analyze-logs",
        json={"logs": logs},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert len(data["analysis"]) > 0
    print("✓ Endpoint /ai/analyze-logs verificado.")

def test_ai_edit_file():
    srv_id = "ai_srv_1"
    save_server_token(srv_id, "token_ai_1")

    with patch("httpx.AsyncClient.get") as mock_get, patch("httpx.AsyncClient.post") as mock_post:
        # Mock para GET file/contents
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.text = "server-port=25565\ndebug=false\n"
        mock_get.return_value = mock_get_resp

        # Mock para POST file/write
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 204
        mock_post.return_value = mock_post_resp

        response = client.post(
            f"/api/servers/{srv_id}/ai/edit-file",
            json={"file_path": "/server.properties", "user_prompt": "Cambia debug a true"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "new_content" in data

        # Verificar que efectivamente llamó a file/write con Content-Type: text/plain
        assert mock_post.called
        called_headers = mock_post.call_args.kwargs["headers"]
        assert called_headers["Content-Type"] == "text/plain"
        print("✓ Endpoint /ai/edit-file con reescritura directa verificado.")

def test_ai_chat():
    srv_id = "ai_srv_1"
    save_server_token(srv_id, "token_ai_1")

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"attributes": {"name": "PaperMC 1.20.4", "node": "Node-1"}}
        mock_get.return_value = mock_get_resp

        # 1. Enviar mensaje en chat
        res = client.post(
            f"/api/servers/{srv_id}/ai/chat",
            json={"message": "¿Cómo optimizo PaperMC para reducir el lag?"},
            headers=auth_headers
        )
        assert res.status_code == 200
        assert "reply" in res.json()

        # 2. Consultar historial del chat
        res_hist = client.get(
            f"/api/servers/{srv_id}/ai/chat",
            headers=auth_headers
        )
        assert res_hist.status_code == 200
        history = res_hist.json()["history"]
        assert len(history) >= 2 # user msg + model msg
        print("✓ Endpoint /ai/chat e historial contextual en SQLite verificado.")

if __name__ == "__main__":
    setup_module()
    test_ai_analyze_logs()
    test_ai_edit_file()
    test_ai_chat()
    print("\n¡TODAS LAS PRUEBAS DEL MILESTONE 4 PASARON CON ÉXITO!")

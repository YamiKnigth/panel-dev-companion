import asyncio
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(__file__))

from main import app
from vault import init_db, save_server_token

client = TestClient(app)

def setup_module():
    init_db()

def test_login_success():
    mock_ptero_response = {
        "object": "list",
        "data": [
            {
                "object": "server",
                "attributes": {
                    "server_owner": True,
                    "identifier": "owner_srv_1",
                    "internal_id": 1,
                    "name": "Servidor Propio",
                    "node": "Node-1"
                }
            },
            {
                "object": "server",
                "attributes": {
                    "server_owner": False,
                    "identifier": "other_srv_2",
                    "internal_id": 2,
                    "name": "Servidor Ajeno",
                    "node": "Node-1"
                }
            }
        ]
    }

    # Desbloqueamos owner_srv_1 en la base de datos local
    save_server_token("owner_srv_1", "test_srv_token_abc")

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_ptero_response
        mock_get.return_value = mock_resp

        response = client.post("/api/auth/login", json={"api_key": "ptlc_master_key_123"})

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "token" in data
        assert "servers" in data
        servers = data["servers"]

        # Debe haber filtrado el servidor no propio (server_owner == False)
        assert len(servers) == 1
        assert servers[0]["attributes"]["identifier"] == "owner_srv_1"
        assert servers[0]["attributes"]["is_unlocked"] is True
        print("✓ Pruebas de login exitoso y filtrado Zero-Trust verificadas.")

def test_login_invalid_key():
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_get.return_value = mock_resp

        response = client.post("/api/auth/login", json={"api_key": "ptlc_invalid"})
        assert response.status_code == 401
        assert "Master API Key inválida" in response.json()["detail"]
        print("✓ Pruebas de manejo de Master Key inválida verificadas.")

if __name__ == "__main__":
    setup_module()
    test_login_success()
    test_login_invalid_key()
    print("\n¡TODAS LAS PRUEBAS DEL MILESTONE 2 PASARON CON ÉXITO!")

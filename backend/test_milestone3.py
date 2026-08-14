import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(__file__))

from main import app
from vault import init_db, save_server_token, get_server_token
from auth import create_access_token

client = TestClient(app)
jwt_token = create_access_token({"sub": "admin"})
auth_headers = {"Authorization": f"Bearer {jwt_token}"}

def setup_module():
    init_db()

def test_unlock_server():
    server_id = "test_unlock_srv"
    srv_token = "ptlc_srv_token_999"

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        # Llamar a /api/servers/unlock
        response = client.post(
            "/api/servers/unlock",
            json={"identifier": server_id, "token": srv_token},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["is_unlocked"] is True

        # Verificar que el token se guardó desencriptado en DB
        saved = get_server_token(server_id)
        assert saved == srv_token
        print("✓ Desbloqueo de servidor y almacenamiento cifrado verificado.")

def test_zero_trust_locked_server():
    locked_id = "locked_server_000"

    # Intentar enviar comando a servidor bloqueado sin token en DB
    res = client.post(
        f"/api/servers/{locked_id}/command",
        json={"command": "say test"},
        headers=auth_headers
    )
    assert res.status_code == 403
    assert "bloqueado" in res.json()["detail"]
    print("✓ Regla de oro Zero-Trust (HTTP 403 en servidor bloqueado) verificada.")

def test_proxy_send_command():
    srv_id = "unlocked_srv_1"
    srv_token = "ptlc_unlocked_token"
    save_server_token(srv_id, srv_token)

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_post.return_value = mock_resp

        res = client.post(
            f"/api/servers/{srv_id}/command",
            json={"command": "say hola"},
            headers=auth_headers
        )
        assert res.status_code == 204

        # Verificar que Pterodactyl recibió el token del servidor en Authorization header
        called_headers = mock_post.call_args.kwargs["headers"]
        assert called_headers["Authorization"] == f"Bearer {srv_token}"
        print("✓ Proxy de envío de comando con inyección de token verificado.")

def test_proxy_read_write_file():
    srv_id = "unlocked_srv_1"
    srv_token = "ptlc_unlocked_token"

    # Leer archivo
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "contenido del archivo json"
        mock_get.return_value = mock_resp

        res = client.get(
            f"/api/servers/{srv_id}/files/contents?file=/config.json",
            headers=auth_headers
        )
        assert res.status_code == 200
        assert res.text == "contenido del archivo json"
        print("✓ Proxy de lectura de archivo verificado.")

    # Escribir archivo con Content-Type: text/plain
    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_post.return_value = mock_resp

        raw_content = "server-ip=0.0.0.0\nserver-port=25565"
        res = client.post(
            f"/api/servers/{srv_id}/files/write?file=/server.properties",
            content=raw_content,
            headers={"Authorization": f"Bearer {jwt_token}", "Content-Type": "text/plain"}
        )
        assert res.status_code == 204

        # Verificar Content-Type: text/plain enviado a Pterodactyl
        called_headers = mock_post.call_args.kwargs["headers"]
        assert called_headers["Content-Type"] == "text/plain"
        assert called_headers["Authorization"] == f"Bearer {srv_token}"
        print("✓ Proxy de escritura de archivo con Content-Type: text/plain verificado.")

if __name__ == "__main__":
    setup_module()
    test_unlock_server()
    test_zero_trust_locked_server()
    test_proxy_send_command()
    test_proxy_read_write_file()
    print("\n¡TODAS LAS PRUEBAS DEL MILESTONE 3 PASARON CON ÉXITO!")

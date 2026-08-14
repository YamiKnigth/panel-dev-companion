import os
import sys
from dotenv import load_dotenv

load_dotenv(".env")

from vault import init_db, save_server_token, get_server_token, is_server_unlocked, encrypt_token, decrypt_token

def test_vault():
    print("Iniciando pruebas del Milestone 1: Setup y Bóveda Segura...")
    init_db()

    test_identifier = "a1b2c3d4"
    test_token = "ptlc_test_token_1234567890_secret"

    # 1. Cifrar y descifrar en memoria
    enc = encrypt_token(test_token)
    dec = decrypt_token(enc)
    assert test_token == dec, f"Fallo cifrado en memoria: {test_token} != {dec}"
    assert test_token != enc, "El token cifrado no cambió"
    print("✓ Cifrado y descifrado en memoria verificado.")

    # 2. Guardar en DB
    save_server_token(test_identifier, test_token)
    assert is_server_unlocked(test_identifier) == True, "El servidor debería figurar como desbloqueado"
    print("✓ Guardado en DB verificado.")

    # 3. Leer de DB y descifrar
    retrieved_token = get_server_token(test_identifier)
    assert retrieved_token == test_token, f"Token recuperado no coincide: {retrieved_token} != {test_token}"
    print("✓ Recuperación y descifrado desde DB verificado.")

    # 4. Probar un ID inexistente
    assert is_server_unlocked("non_existent") == False, "Servidor no existente debería ser False"
    assert get_server_token("non_existent") is None, "Token inexistente debería ser None"
    print("✓ Manejo de IDs inexistentes verificado.")

    print("\n¡TODAS LAS PRUEBAS DEL MILESTONE 1 PASARON CON ÉXITO!")

if __name__ == "__main__":
    test_vault()

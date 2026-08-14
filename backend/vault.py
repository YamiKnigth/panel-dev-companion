import os
import sqlite3
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "companion.db")
SECRET_ENCRYPT_KEY = os.getenv("SECRET_ENCRYPT_KEY")

def get_fernet() -> Fernet:
    key = os.getenv("SECRET_ENCRYPT_KEY")
    if not key:
        # Generar una clave por defecto en desarrollo si no existe
        key = Fernet.generate_key().decode()
        os.environ["SECRET_ENCRYPT_KEY"] = key
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_vault (
            identifier TEXT PRIMARY KEY,
            encrypted_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def encrypt_token(token: str) -> str:
    f = get_fernet()
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    f = get_fernet()
    return f.decrypt(encrypted_token.encode()).decode()

def save_server_token(identifier: str, token: str):
    enc = encrypt_token(token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO server_vault (identifier, encrypted_token)
        VALUES (?, ?)
        ON CONFLICT(identifier) DO UPDATE SET encrypted_token=excluded.encrypted_token
    """, (identifier, enc))
    conn.commit()
    conn.close()

def get_server_token(identifier: str) -> str | None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_token FROM server_vault WHERE identifier = ?", (identifier,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return decrypt_token(row["encrypted_token"])
    return None

def is_server_unlocked(identifier: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM server_vault WHERE identifier = ?", (identifier,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

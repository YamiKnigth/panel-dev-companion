import sqlite3
from typing import List, Dict
from vault import get_db_connection

def add_chat_message(server_id: str, role: str, content: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO chat_history (server_id, role, content)
        VALUES (?, ?, ?)
    """, (server_id, role, content))
    conn.commit()
    conn.close()

def get_chat_history(server_id: str, limit: int = 20) -> List[Dict[str, str]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, timestamp FROM chat_history
        WHERE server_id = ?
        ORDER BY id ASC
        LIMIT ?
    """, (server_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"], "timestamp": row["timestamp"]} for row in rows]

def clear_chat_history(server_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_history WHERE server_id = ?", (server_id,))
    conn.commit()
    conn.close()

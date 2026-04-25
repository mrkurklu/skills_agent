import sqlite3
import json
import os

DB_PATH = "skillflow.db"

def init_db():
    """Veritabanını ve dünya standardı (Tool Calling) Tablosunu oluşturur."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            parameters_schema TEXT NOT NULL, -- JSON Schema formatı
            python_code TEXT NOT NULL -- Asıl işi yapacak Python kodu
        )
    ''')
    conn.commit()
    conn.close()

def get_all_skills():
    """Tüm yetenekleri DB'den çeker."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM skills')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_skill(name: str, description: str, parameters_schema: dict, python_code: str):
    """Yeni bir yeteneği veritabanına ekler."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO skills (name, description, parameters_schema, python_code)
            VALUES (?, ?, ?, ?)
        ''', (name, description, json.dumps(parameters_schema), python_code))
        conn.commit()
    except sqlite3.IntegrityError:
        # Eğer zaten varsa güncellesin
        cursor.execute('''
            UPDATE skills 
            SET description=?, parameters_schema=?, python_code=? 
            WHERE name=?
        ''', (description, json.dumps(parameters_schema), python_code, name))
        conn.commit()
    finally:
        conn.close()
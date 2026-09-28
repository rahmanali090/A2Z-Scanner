import sqlite3
from pathlib import Path

DB_PATH = Path("a2z_scanner.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS signals (signal_id TEXT PRIMARY KEY, symbol TEXT NOT NULL, state TEXT NOT NULL, confidence REAL, reason TEXT, created_at REAL NOT NULL, metadata TEXT)")
    conn.commit()
    conn.close()

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


def init_extended_tables():
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS signal_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, signal_id TEXT NOT NULL, event_type TEXT NOT NULL, state TEXT, event_timestamp REAL NOT NULL, data TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS market_snapshots (snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT, signal_id TEXT, symbol TEXT NOT NULL, source TEXT NOT NULL, source_timestamp REAL, receipt_timestamp REAL, processing_timestamp REAL, decision_timestamp REAL, price REAL, volume REAL, open_interest REAL, funding_rate REAL, data_quality TEXT, provenance TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS health_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, component TEXT NOT NULL, status TEXT NOT NULL, event_timestamp REAL NOT NULL, reason TEXT, data TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS config_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, config_version TEXT NOT NULL, old_config TEXT, new_config TEXT, reason TEXT, author TEXT, event_timestamp REAL NOT NULL)")
    conn.commit()
    conn.close()

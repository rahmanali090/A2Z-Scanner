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
    conn.execute("CREATE TABLE IF NOT EXISTS news_events (news_id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, source_id TEXT, title TEXT NOT NULL, symbol TEXT, published_at REAL, received_at REAL NOT NULL, url TEXT, category TEXT, data TEXT)")
    conn.commit()


def init_extended_tables():
    conn = get_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS signal_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, signal_id TEXT NOT NULL, event_type TEXT NOT NULL, state TEXT, event_timestamp REAL NOT NULL, data TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS market_snapshots (snapshot_id INTEGER PRIMARY KEY AUTOINCREMENT, signal_id TEXT, symbol TEXT NOT NULL, source TEXT NOT NULL, source_timestamp REAL, receipt_timestamp REAL, processing_timestamp REAL, decision_timestamp REAL, price REAL, volume REAL, open_interest REAL, funding_rate REAL, data_quality TEXT, provenance TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS health_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, component TEXT NOT NULL, status TEXT NOT NULL, event_timestamp REAL NOT NULL, reason TEXT, data TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS config_events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, config_version TEXT NOT NULL, old_config TEXT, new_config TEXT, reason TEXT, author TEXT, event_timestamp REAL NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS news_alpha_tokens (linkage_id INTEGER PRIMARY KEY AUTOINCREMENT, news_id INTEGER NOT NULL, symbol TEXT NOT NULL, token_id TEXT, chain_id TEXT, contract_address TEXT, UNIQUE(news_id, symbol))")
    conn.commit()
    conn.close()


def save_news_event(source, source_id, title, symbol, published_at, received_at, url, category, data):
    conn = get_connection()
    conn.execute(
        "INSERT INTO news_events "
        "(source, source_id, title, symbol, published_at, received_at, url, category, data) "
        "SELECT ?, ?, ?, ?, ?, ?, ?, ?, ? "
        "WHERE NOT EXISTS "
        "(SELECT 1 FROM news_events WHERE source = ? AND source_id = ?)",
        (
            source, source_id, title, symbol, published_at,
            received_at, url, category, data, source, source_id
        ),
    )
    conn.commit()

    row = conn.execute(
        "SELECT news_id FROM news_events WHERE source = ? AND source_id = ?",
        (source, source_id),
    ).fetchone()

    conn.close()
    return row[0] if row else None

def save_inverted_hammer_candidate(symbol, timeframe, candle, pattern_data):
    import json
    import time

    signal_id = f"IH-{symbol}-{timeframe}-{candle['open_time']}"

    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO signals
        (signal_id, symbol, state, confidence, reason, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            signal_id,
            symbol,
            "CANDIDATE",
            None,
            "INVERTED_HAMMER_LONG_CANDIDATE",
            time.time(),
            json.dumps({
                "pattern": "INVERTED_HAMMER",
                "direction": "LONG_CANDIDATE",
                "timeframe": timeframe,
                "candle": candle,
                "pattern_data": pattern_data,
                "manual_verification_required": True,
            }),
        ),
    )

    event_exists = conn.execute(
        """
        SELECT 1 FROM signal_events
        WHERE signal_id = ? AND event_type = ? AND state = ?
        LIMIT 1
        """,
        (
            signal_id,
            "INVERTED_HAMMER_DETECTED",
            "CANDIDATE",
        ),
    ).fetchone()

    if not event_exists:
        conn.execute(
            """
            INSERT INTO signal_events
            (signal_id, event_type, state, event_timestamp, data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                signal_id,
                "INVERTED_HAMMER_DETECTED",
                "CANDIDATE",
                time.time(),
                json.dumps(pattern_data),
            ),
        )

    conn.commit()
    conn.close()

    return signal_id

def inverted_hammer_alert_sent(signal_id):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT 1 FROM signal_events
        WHERE signal_id = ? AND event_type = ?
        LIMIT 1
        """,
        (signal_id, "INVERTED_HAMMER_ALERT_SENT"),
    ).fetchone()
    conn.close()
    return row is not None

def mark_inverted_hammer_alert_sent(signal_id):
    import json
    import time
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO signal_events
        (signal_id, event_type, state, event_timestamp, data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            signal_id,
            "INVERTED_HAMMER_ALERT_SENT",
            "CANDIDATE",
            time.time(),
            json.dumps({"alert_sent": True}),
        ),
    )
    conn.commit()
    conn.close()

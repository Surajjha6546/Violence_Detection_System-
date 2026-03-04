from datetime import datetime
from .database import get_connection

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source TEXT,
            is_violent INTEGER,
            severity TEXT,
            confidence REAL
        )
    """)

    conn.commit()
    conn.close()


def log_incident(source, is_violent, severity, confidence):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO incidents (timestamp, source, is_violent, severity, confidence)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        source,
        int(is_violent),
        severity,
        confidence
    ))

    conn.commit()
    conn.close()


def fetch_incidents(limit=100):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, source, is_violent, severity, confidence
        FROM incidents
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows

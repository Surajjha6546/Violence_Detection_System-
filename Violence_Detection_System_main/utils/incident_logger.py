# utils/incident_logger.py

import sqlite3
from datetime import datetime
import os

DB_PATH = "storage/incidents.db"


def init_db():
    os.makedirs("storage", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
    conn = sqlite3.connect(DB_PATH)
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


def fetch_incidents(limit=50):
    conn = sqlite3.connect(DB_PATH)
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

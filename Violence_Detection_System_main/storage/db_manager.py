import sqlite3
from datetime import datetime
import os

DB = "storage/logs.db"

def init_db():
    os.makedirs("storage", exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        frame_path TEXT,
        evidence_path TEXT,
        confidence REAL,
        severity TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_incident(frame_path, evidence_path, confidence, severity):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO incidents VALUES (NULL,?,?,?,?,?)",
        (datetime.now(), frame_path, evidence_path, confidence, severity)
    )
    conn.commit()
    conn.close()

def get_all_incidents():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    rows = c.execute(
        "SELECT timestamp, frame_path, evidence_path, confidence, severity FROM incidents"
    ).fetchall()
    conn.close()
    return rows

import sqlite3
import os

DB_PATH = "storage/incidents.db"

def get_connection():
    os.makedirs("storage", exist_ok=True)
    return sqlite3.connect(DB_PATH)

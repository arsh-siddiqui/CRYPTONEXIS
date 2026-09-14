import sqlite3
import os
import logging

logger = logging.getLogger("cryptonexis.db")

DB_DIR = "app_data"
DB_FILE = os.path.join(DB_DIR, "cryptonexis.sqlite")

def get_connection():
    """Returns a connection to the SQLite database."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

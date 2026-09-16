import sqlite3
import logging
from database.connection import get_connection

logger = logging.getLogger(__name__)

def initialize_database():
    """Initializes the database schema if tables do not exist."""
    conn = get_connection()
    if not conn:
        logger.error("Failed to connect to DB for schema initialization.")
        return
        
    try:
        cursor = conn.cursor()
        
        # 1. Monitored Wallets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitored_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT NOT NULL,
                blockchain TEXT NOT NULL,
                label TEXT,
                enabled BOOLEAN DEFAULT 1,
                last_checked_at TEXT,
                last_seen_transaction TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(wallet_address, blockchain)
            )
        """)
        
        # 2. Monitoring Transactions (Baseline / Hashes)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                tx_hash TEXT NOT NULL,
                first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
                transaction_timestamp TEXT,
                direction TEXT,
                amount REAL,
                asset TEXT,
                status TEXT,
                UNIQUE(wallet_id, tx_hash),
                FOREIGN KEY(wallet_id) REFERENCES monitored_wallets(id) ON DELETE CASCADE
            )
        """)
        
        # 3. Alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                blockchain TEXT NOT NULL,
                wallet_address TEXT NOT NULL,
                tx_hash TEXT NOT NULL,
                direction TEXT,
                amount REAL,
                asset TEXT,
                transaction_timestamp TEXT,
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                severity TEXT NOT NULL,
                status TEXT DEFAULT 'UNREAD',
                message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(wallet_id) REFERENCES monitored_wallets(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        logger.info("Database schema initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database schema initialization failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_schema()

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
        # 4. Cases
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_number TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'OPEN',
                priority TEXT DEFAULT 'MEDIUM',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'Analyst',
                primary_wallet TEXT,
                primary_blockchain TEXT,
                notes TEXT
            )
        """)

        # 5. Case Wallets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_wallets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                wallet_address TEXT NOT NULL,
                blockchain TEXT NOT NULL,
                label TEXT,
                role TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(case_id, wallet_address, blockchain),
                FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            )
        """)

        # 6. Case Transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                tx_hash TEXT NOT NULL,
                blockchain TEXT NOT NULL,
                relationship TEXT,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(case_id, tx_hash, blockchain),
                FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            )
        """)

        # 7. Case Alerts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                alert_id INTEGER NOT NULL,
                added_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(case_id, alert_id),
                FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,
                FOREIGN KEY(alert_id) REFERENCES alerts(id) ON DELETE CASCADE
            )
        """)

        # 8. Case Evidence
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                evidence_type TEXT NOT NULL,
                reference_id TEXT,
                title TEXT,
                description TEXT,
                source TEXT,
                source_type TEXT,
                data_mode TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes for fast lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_wallets_case_id ON case_wallets(case_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_transactions_case_id ON case_transactions(case_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_alerts_case_id ON case_alerts(case_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_evidence_case_id ON case_evidence(case_id)")

        conn.commit()
        logger.info("Database schema initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database schema initialization failed: {e}")
    finally:
        conn.close()

initialize_schema = initialize_database

if __name__ == "__main__":
    initialize_database()

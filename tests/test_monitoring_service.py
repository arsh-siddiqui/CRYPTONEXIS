import pytest
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock
from services.monitoring_service import MonitoringService
from analysis.alert_models import MonitoredWallet
import datetime

@pytest.fixture
def mock_db():
    temp_db = tempfile.NamedTemporaryFile(delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    
    conn = sqlite3.connect(temp_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE monitored_wallets (
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
    cursor.execute("""
        CREATE TABLE monitoring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id INTEGER NOT NULL,
            tx_hash TEXT NOT NULL,
            first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
            transaction_timestamp TEXT,
            direction TEXT,
            amount REAL,
            asset TEXT,
            status TEXT,
            UNIQUE(wallet_id, tx_hash)
        )
    """)
    cursor.execute("""
        CREATE TABLE alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id INTEGER NOT NULL,
            blockchain TEXT NOT NULL,
            wallet_address TEXT NOT NULL,
            tx_hash TEXT NOT NULL,
            direction TEXT,
            amount REAL,
            asset TEXT,
            transaction_timestamp TEXT,
            detected_at TEXT,
            severity TEXT NOT NULL,
            status TEXT DEFAULT 'UNREAD',
            message TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()
    
    # Now provide a factory function for get_connection
    def get_conn():
        c = sqlite3.connect(temp_db_path)
        c.row_factory = sqlite3.Row
        return c
        
    return get_conn

@patch('services.monitoring_service.get_connection')
def test_add_wallet_baseline(mock_get_conn, mock_db):
    mock_get_conn.side_effect = mock_db
    
    with patch.object(MonitoringService, '_fetch_transactions') as mock_fetch:
        mock_tx = MagicMock()
        mock_tx.tx_hash = "0xBASE"
        mock_fetch.return_value = [mock_tx]
        
        service = MonitoringService({})
        wallet = service.add_wallet("addr1", "Bitcoin", "Label1")
        
        assert wallet is not None
        assert wallet.wallet_address == "addr1"
        assert wallet.blockchain == "Bitcoin"
        assert wallet.enabled == True
        
        # Verify baseline transaction was recorded
        conn = mock_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM monitoring_transactions WHERE tx_hash='0xBASE'")
        row = cursor.fetchone()
        assert row is not None
        assert row["status"] == "BASELINE"
        conn.close()

@patch('services.monitoring_service.get_connection')
def test_duplicate_wallet(mock_get_conn, mock_db):
    mock_get_conn.side_effect = mock_db
    
    with patch.object(MonitoringService, '_fetch_transactions') as mock_fetch:
        mock_fetch.return_value = []
        service = MonitoringService({})
        w1 = service.add_wallet("addr1", "Bitcoin", "L1")
        w2 = service.add_wallet("addr1", "Bitcoin", "L2")
        
        assert w1 is not None
        assert w2 is None # Duplicate rejected

@patch('services.monitoring_service.get_connection')
def test_check_wallet_new_tx(mock_get_conn, mock_db):
    mock_get_conn.side_effect = mock_db
    
    with patch.object(MonitoringService, '_fetch_transactions') as mock_fetch:
        # 1. Baseline
        mock_tx_base = MagicMock()
        mock_tx_base.tx_hash = "0xBASE"
        mock_fetch.return_value = [mock_tx_base]
        
        service = MonitoringService({})
        wallet = service.add_wallet("addr1", "Bitcoin")
        
        # 2. Check wallet with new tx
        mock_tx_new = MagicMock()
        mock_tx_new.tx_hash = "0xNEW"
        mock_tx_new.direction = "INCOMING"
        mock_tx_new.amount = 1.0
        mock_tx_new.asset = "BTC"
        mock_tx_new.timestamp = "2026-01-01"
        
        # Mock fetch now returns both baseline + new
        mock_fetch.return_value = [mock_tx_base, mock_tx_new]
        
        # Mock alert engine to return a dummy alert
        mock_alert = MagicMock()
        mock_alert.wallet_id = wallet.id
        mock_alert.blockchain = wallet.blockchain
        mock_alert.wallet_address = wallet.wallet_address
        mock_alert.tx_hash = "0xNEW"
        mock_alert.direction = "INCOMING"
        mock_alert.amount = 1.0
        mock_alert.asset = "BTC"
        mock_alert.transaction_timestamp = "2026-01-01"
        mock_alert.severity = "INFO"
        mock_alert.status = "UNREAD"
        mock_alert.message = "New"
        service.alert_engine.evaluate_transaction = MagicMock(return_value=mock_alert)
        
        service.check_wallet(wallet)
        
        # Verify alert was created for the new tx, but NOT the baseline tx
        alerts = service.get_alerts()
        assert len(alerts) == 1
        assert alerts[0].tx_hash == "0xNEW"

@patch('services.monitoring_service.get_connection')
def test_simulate_demo_transaction(mock_get_conn, mock_db):
    mock_get_conn.side_effect = mock_db
    
    with patch.object(MonitoringService, '_fetch_transactions') as mock_fetch:
        mock_fetch.return_value = []
        service = MonitoringService({})
        wallet = service.add_wallet("demo_addr", "Ethereum", "Demo")
        
        service.simulate_demo_transaction(wallet.id)
        
        alerts = service.get_alerts()
        assert len(alerts) == 1
        assert "0xDEMO" in alerts[0].tx_hash
        assert alerts[0].wallet_address == "demo_addr"

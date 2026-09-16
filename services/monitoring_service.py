import threading
import time
import logging
import datetime
from typing import List, Dict, Optional
from database.connection import get_connection
from analysis.alert_models import MonitoredWallet, AlertRecord
from analysis.alert_engine import AlertEngine

# Existing provider services
from services.bitcoin_service import BitcoinService
from services.ethereum_service import EthereumService
from services.bsc_service import BscService
from analysis.transaction_normalizer import normalize_transactions

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(self, config: dict):
        self.config = config
        self.alert_engine = AlertEngine()
        
        # Provider instances
        self.btc_service = BitcoinService()
        self.eth_service = EthereumService(config.get("ETHERSCAN_API_KEY", ""))
        self.bsc_service = BscService(config.get("ANKR_API_KEY", ""))
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.interval = 60 # Default interval in seconds

    # -----------------------------------------------------
    # Database Operations
    # -----------------------------------------------------
    def add_wallet(self, address: str, blockchain: str, label: str = "") -> Optional[MonitoredWallet]:
        """Adds a wallet to the watchlist and initializes its baseline."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Simple validation logic to avoid duplicates
            cursor.execute("SELECT id FROM monitored_wallets WHERE wallet_address=? AND blockchain=?", (address, blockchain))
            if cursor.fetchone():
                logger.warning(f"Wallet {address} on {blockchain} already monitored.")
                return None
                
            cursor.execute(
                "INSERT INTO monitored_wallets (wallet_address, blockchain, label, enabled) VALUES (?, ?, ?, 1)",
                (address, blockchain, label)
            )
            wallet_id = cursor.lastrowid
            conn.commit()
            
            wallet = self.get_wallet(wallet_id)
            if wallet:
                # Initialize Baseline (fetch existing txs and store hashes)
                self._initialize_baseline(wallet)
                return wallet
        except Exception as e:
            logger.error(f"Failed to add wallet: {e}")
        finally:
            conn.close()
        return None
        
    def remove_wallet(self, wallet_id: int):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM monitored_wallets WHERE id=?", (wallet_id,))
            conn.commit()
        finally:
            conn.close()

    def get_wallet(self, wallet_id: int) -> Optional[MonitoredWallet]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monitored_wallets WHERE id=?", (wallet_id,))
            row = cursor.fetchone()
            if row:
                return MonitoredWallet(**dict(row))
        finally:
            conn.close()
        return None

    def list_wallets(self) -> List[MonitoredWallet]:
        conn = get_connection()
        wallets = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM monitored_wallets ORDER BY id DESC")
            for row in cursor.fetchall():
                wallets.append(MonitoredWallet(**dict(row)))
        finally:
            conn.close()
        return wallets
        
    def toggle_wallet(self, wallet_id: int, enabled: bool):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE monitored_wallets SET enabled=? WHERE id=?", (int(enabled), wallet_id))
            conn.commit()
        finally:
            conn.close()
            
    def get_alerts(self) -> List[AlertRecord]:
        conn = get_connection()
        alerts = []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 100")
            for row in cursor.fetchall():
                alerts.append(AlertRecord(**dict(row)))
        finally:
            conn.close()
        return alerts

    # -----------------------------------------------------
    # Baseline & Transactions
    # -----------------------------------------------------
    def _fetch_transactions(self, address: str, blockchain: str) -> List[dict]:
        """Fetches transactions using existing provider services and normalizes them."""
        raw_txs = []
        provider_name = ""
        
        try:
            if blockchain.lower() == "bitcoin":
                raw_txs = self.btc_service.get_transactions(address)
                provider_name = "blockchain.com"
            elif blockchain.lower() == "ethereum":
                raw_txs = self.eth_service.get_transactions(address)
                provider_name = "etherscan"
            elif blockchain.lower() == "bnb smart chain":
                raw_txs = self.bsc_service.get_transactions(address)
                provider_name = "ankr"
                
            # Normalize them
            normalized = normalize_transactions(provider_name, raw_txs, address, blockchain)
            return normalized
        except Exception as e:
            logger.error(f"Failed to fetch transactions for {address} on {blockchain}: {e}")
            return []

    def _initialize_baseline(self, wallet: MonitoredWallet):
        """Fetches initial transactions and stores them quietly as a baseline."""
        logger.info(f"Initializing baseline for {wallet.wallet_address}")
        txs = self._fetch_transactions(wallet.wallet_address, wallet.blockchain)
        if not txs:
            return
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            for tx in txs:
                # Store hashes in monitoring_transactions to prevent future alerts
                try:
                    cursor.execute(
                        "INSERT INTO monitoring_transactions (wallet_id, tx_hash, status) VALUES (?, ?, ?)",
                        (wallet.id, tx.tx_hash, "BASELINE")
                    )
                except Exception:
                    pass # Ignore unique constraint duplicates
            conn.commit()
        finally:
            conn.close()

    # -----------------------------------------------------
    # Core Monitoring Logic
    # -----------------------------------------------------
    def start_monitoring(self):
        if self.monitoring_active:
            return
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logger.info("Monitoring started.")

    def stop_monitoring(self):
        self.monitoring_active = False
        logger.info("Monitoring stopped.")

    def _monitoring_loop(self):
        """Background thread executing staggered polling."""
        while self.monitoring_active:
            wallets = [w for w in self.list_wallets() if w.enabled]
            
            if not wallets:
                time.sleep(5)
                continue
                
            # Staggered polling: check 1 wallet every X seconds across the interval
            stagger_delay = max(1, self.interval / len(wallets))
            
            for wallet in wallets:
                if not self.monitoring_active:
                    break
                
                try:
                    self.check_wallet(wallet)
                except Exception as e:
                    logger.error(f"Error checking wallet {wallet.wallet_address}: {e}")
                    
                # Wait before checking next wallet to protect rate limits
                time.sleep(stagger_delay)

    def check_wallet(self, wallet: MonitoredWallet):
        """Checks a specific wallet for new transactions and triggers alerts."""
        txs = self._fetch_transactions(wallet.wallet_address, wallet.blockchain)
        conn = get_connection()
        cursor = conn.cursor()
        
        new_tx_count = 0
        last_hash = wallet.last_seen_transaction
        
        try:
            for tx in txs:
                # Check if hash already seen
                cursor.execute("SELECT id FROM monitoring_transactions WHERE wallet_id=? AND tx_hash=?", (wallet.id, tx.tx_hash))
                if cursor.fetchone():
                    continue # Already processed
                    
                # IT'S A NEW TRANSACTION
                new_tx_count += 1
                last_hash = tx.tx_hash
                
                # 1. Insert into tracking to prevent duplicate alerts
                cursor.execute(
                    "INSERT INTO monitoring_transactions (wallet_id, tx_hash, status) VALUES (?, ?, ?)",
                    (wallet.id, tx.tx_hash, "DETECTED")
                )
                
                # 2. Evaluate Severity
                # Convert normalized TX to dict for engine
                tx_dict = {
                    "tx_hash": tx.tx_hash,
                    "direction": tx.direction.value if hasattr(tx.direction, "value") else str(tx.direction),
                    "amount": tx.amount,
                    "asset": tx.asset,
                    "timestamp": tx.timestamp,
                    "data_mode": "LIVE"
                }
                alert = self.alert_engine.evaluate_transaction(wallet.id, wallet.wallet_address, wallet.blockchain, tx_dict)
                
                # 3. Create Alert
                cursor.execute("""
                    INSERT INTO alerts (wallet_id, blockchain, wallet_address, tx_hash, direction, amount, asset, transaction_timestamp, severity, status, message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.wallet_id, alert.blockchain, alert.wallet_address, alert.tx_hash,
                    alert.direction, alert.amount, alert.asset, alert.transaction_timestamp,
                    alert.severity, alert.status, alert.message
                ))
                
            # Update wallet check timestamps
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.execute("UPDATE monitored_wallets SET last_checked_at=?, last_seen_transaction=? WHERE id=?", (now, last_hash, wallet.id))
            conn.commit()
            
            if new_tx_count > 0:
                logger.info(f"Detected {new_tx_count} new transactions for {wallet.wallet_address}")
                
        finally:
            conn.close()

    # -----------------------------------------------------
    # Demo Mode Actions
    # -----------------------------------------------------
    def simulate_demo_transaction(self, wallet_id: int):
        """Simulates a new incoming transaction for a specific demo wallet exactly as requested."""
        wallet = self.get_wallet(wallet_id)
        if not wallet:
            return
            
        import uuid
        mock_hash = f"0xDEMO{uuid.uuid4().hex[:12].upper()}"
        
        logger.info(f"Simulating DEMO transaction {mock_hash} for {wallet.wallet_address}")
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Record transaction
            cursor.execute(
                "INSERT INTO monitoring_transactions (wallet_id, tx_hash, status) VALUES (?, ?, ?)",
                (wallet.id, mock_hash, "DETECTED_DEMO")
            )
            
            # 2. Evaluate
            tx_dict = {
                "tx_hash": mock_hash,
                "direction": "INCOMING",
                "amount": 0.5,
                "asset": "DEMO_ASSET",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "data_mode": "DEMO"
            }
            alert = self.alert_engine.evaluate_transaction(wallet.id, wallet.wallet_address, wallet.blockchain, tx_dict)
            
            # 3. Raise Alert
            cursor.execute("""
                INSERT INTO alerts (wallet_id, blockchain, wallet_address, tx_hash, direction, amount, asset, transaction_timestamp, severity, status, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.wallet_id, alert.blockchain, alert.wallet_address, alert.tx_hash,
                alert.direction, alert.amount, alert.asset, alert.transaction_timestamp,
                alert.severity, alert.status, alert.message
            ))
            
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            cursor.execute("UPDATE monitored_wallets SET last_checked_at=?, last_seen_transaction=? WHERE id=?", (now, mock_hash, wallet.id))
            
            conn.commit()
        finally:
            conn.close()

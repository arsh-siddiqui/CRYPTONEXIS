import logging
import datetime
from analysis.alert_models import AlertSeverity, AlertRecord
from analysis.reputation_engine import check_address
from analysis.correlation_engine import CorrelationEngine
from analysis.risk_engine import RiskEngine

logger = logging.getLogger(__name__)

class AlertEngine:
    def __init__(self):
        self.correlation_engine = CorrelationEngine()
        self.risk_engine = RiskEngine()

    def evaluate_transaction(self, wallet_id: int, wallet_address: str, blockchain: str, tx: dict) -> AlertRecord:
        """
        Evaluates a new transaction against risk factors to determine alert severity.
        `tx` is expected to be a dictionary representing a NormalizedTransaction or similar.
        """
        severity = AlertSeverity.INFO
        
        # Determine direction safely
        # Note: In a real system we'd parse the NormalizedTransaction fully.
        direction = tx.get("direction", "UNKNOWN")
        amount = tx.get("amount", 0.0)
        asset = tx.get("asset", "Unknown")
        tx_hash = tx.get("tx_hash", "Unknown")
        tx_ts = tx.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())
        if isinstance(tx_ts, datetime.datetime):
            tx_ts = tx_ts.isoformat()
            
        message = f"New {direction.lower()} transaction detected."

        try:
            # Check reputation of the wallet itself or counterparties if we had them.
            # For Phase 9, we check the monitored wallet's risk to elevate the severity of ANY transaction it makes.
            rep_summary = check_address(wallet_address, blockchain)
            
            # Note: Demo tx from monitoring service will carry `data_mode="DEMO"` in metadata or tx object.
            is_demo = tx.get("data_mode") == "DEMO"
            
            # Correlate & Risk
            findings = self.correlation_engine.correlate(wallet_address, blockchain, reputation_summary=rep_summary)
            risk_assessment = self.risk_engine.evaluate(findings)
            
            level = risk_assessment.level
            if level == "CRITICAL":
                severity = AlertSeverity.CRITICAL
                message += " High risk indicators present."
            elif level == "HIGH":
                severity = AlertSeverity.HIGH
                message += " Elevated risk indicators present."
            elif level == "MEDIUM":
                severity = AlertSeverity.MEDIUM
            else:
                # If amount > 0, maybe LOW, otherwise INFO
                if float(amount) > 0:
                    severity = AlertSeverity.LOW
                    
            if is_demo:
                message = "[DEMO] " + message
                
        except Exception as e:
            logger.error(f"Failed to evaluate transaction risk: {e}")
            
        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
        return AlertRecord(
            id=None,
            wallet_id=wallet_id,
            blockchain=blockchain,
            wallet_address=wallet_address,
            tx_hash=tx_hash,
            direction=direction,
            amount=amount,
            asset=asset,
            transaction_timestamp=tx_ts,
            detected_at=now_utc,
            severity=severity.value,
            status="UNREAD",
            message=message,
            created_at=now_utc
        )

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class AlertSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

@dataclass
class MonitoredWallet:
    id: int
    wallet_address: str
    blockchain: str
    label: Optional[str]
    enabled: bool
    last_checked_at: Optional[str]
    last_seen_transaction: Optional[str]
    created_at: str
    updated_at: str

@dataclass
class AlertRecord:
    id: Optional[int]
    wallet_id: int
    blockchain: str
    wallet_address: str
    tx_hash: str
    direction: str
    amount: float
    asset: str
    transaction_timestamp: str
    detected_at: str
    severity: str
    status: str
    message: str
    created_at: str

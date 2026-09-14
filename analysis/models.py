from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any

class TransactionDirection(str, Enum):
    INCOMING = "INCOMING"
    OUTGOING = "OUTGOING"
    INTERNAL = "INTERNAL"
    RELATED = "RELATED"
    UNKNOWN = "UNKNOWN"

class TransactionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"

@dataclass
class NormalizedTransaction:
    blockchain: str
    tx_hash: str
    amount: Decimal
    asset: str
    direction: TransactionDirection
    status: TransactionStatus
    
    # Required optional fields (may be None if provider doesn't supply or ambiguous)
    from_address: Optional[str] = None
    to_address: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    # Optional fields
    block_number: Optional[int] = None
    confirmations: Optional[int] = None
    transaction_index: Optional[int] = None
    fee: Optional[Decimal] = None
    fee_asset: Optional[str] = None
    native_value: Optional[Decimal] = None
    token_address: Optional[str] = None
    token_symbol: Optional[str] = None
    token_decimals: Optional[int] = None
    transaction_type: Optional[str] = None
    
    # Metadata
    provider: str = ""
    investigated_address: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

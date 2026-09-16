from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

class CaseStatus(Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    CLOSED = "CLOSED"

class CasePriority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class EvidenceType(Enum):
    TRANSACTION = "TRANSACTION"
    WALLET = "WALLET"
    GRAPH = "GRAPH"
    TRACE = "TRACE"
    REPUTATION = "REPUTATION"
    RANSOMWARE = "RANSOMWARE"
    OSINT = "OSINT"
    RISK_ANALYSIS = "RISK_ANALYSIS"
    ALERT = "ALERT"
    NOTE = "NOTE"

@dataclass
class CaseWallet:
    case_id: int
    wallet_address: str
    blockchain: str
    label: Optional[str] = None
    role: str = "TARGET"
    added_at: Optional[str] = None
    id: Optional[int] = None

@dataclass
class CaseTransaction:
    case_id: int
    tx_hash: str
    blockchain: str
    relationship: str = "UNKNOWN"
    added_at: Optional[str] = None
    id: Optional[int] = None

@dataclass
class CaseAlert:
    case_id: int
    alert_id: int
    added_at: Optional[str] = None
    id: Optional[int] = None

@dataclass
class CaseEvidence:
    case_id: int
    evidence_type: str
    title: str
    description: str
    source: str
    source_type: str
    data_mode: str
    reference_id: Optional[str] = None
    metadata: Optional[str] = None  # JSON string
    created_at: Optional[str] = None
    id: Optional[int] = None

@dataclass
class Case:
    case_number: str
    title: str
    description: str = ""
    status: str = CaseStatus.OPEN.value
    priority: str = CasePriority.MEDIUM.value
    created_by: str = "Analyst"
    primary_wallet: Optional[str] = None
    primary_blockchain: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    id: Optional[int] = None
    
    # Relationships for convenience when passing around
    wallets: List[CaseWallet] = field(default_factory=list)
    transactions: List[CaseTransaction] = field(default_factory=list)
    alerts: List[CaseAlert] = field(default_factory=list)
    evidence: List[CaseEvidence] = field(default_factory=list)

@dataclass
class CaseSummary:
    case_id: int
    num_wallets: int
    num_transactions: int
    num_alerts: int
    num_evidence: int
    observed_blockchains: List[str]
    latest_activity: Optional[str]
    current_risk_score: Optional[int]
    latest_monitoring_status: Optional[str]

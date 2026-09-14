from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List

class ReputationStatus(str, Enum):
    NO_MATCH = "NO_MATCH"
    REPORTED = "REPORTED"
    MATCH = "MATCH"
    UNKNOWN = "UNKNOWN"
    ERROR = "ERROR"

@dataclass
class ReputationFinding:
    address: str
    blockchain: str
    finding_type: str
    finding: str
    source: str
    source_type: str
    reported_date: Optional[str] = None
    confidence: str = "UNKNOWN"
    reference: Optional[str] = None
    data_mode: str = "demo"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReputationSummary:
    address: str
    blockchain: str
    status: ReputationStatus
    ransomware_reports: int = 0
    other_reports: int = 0
    sources_checked: int = 0
    findings: List[ReputationFinding] = field(default_factory=list)
    message: str = ""
    data_mode: str = "demo"

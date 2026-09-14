from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List

class CorrelationCategory(str, Enum):
    TRANSACTION_ACTIVITY = "TRANSACTION_ACTIVITY"
    GRAPH_RELATIONSHIP = "GRAPH_RELATIONSHIP"
    REPUTATION = "REPUTATION"
    RANSOMWARE = "RANSOMWARE"
    OSINT = "OSINT"

@dataclass
class CorrelationFinding:
    category: CorrelationCategory
    description: str
    source: str
    source_type: str
    evidence: str
    confidence: str = "UNKNOWN"
    severity: str = "NEUTRAL"
    data_mode: str = "demo"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class RiskFactor:
    factor_id: str
    description: str
    score: int
    evidence: str
    source: str = "Cryptonexis"
    source_type: str = "internal"
    confidence: str = "UNKNOWN"
    data_mode: str = "demo"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskAssessment:
    score: int
    level: str
    factors: List[RiskFactor] = field(default_factory=list)
    evidence: List[CorrelationFinding] = field(default_factory=list)
    data_mode: str = "demo"
    generated_at: str = ""
    methodology_version: str = "1.0"

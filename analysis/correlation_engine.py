import json
import os
import logging
from typing import List, Dict, Any, Optional
from analysis.correlation_models import CorrelationFinding, CorrelationCategory
from analysis.reputation_models import ReputationSummary, ReputationFinding
from analysis.reputation_engine import _address_matches

logger = logging.getLogger(__name__)

class CorrelationEngine:
    def __init__(self, data_dir: str = "data"):
        self.osint_path = os.path.join(data_dir, "threat_intelligence", "osint_records.json")
        
    def _load_osint(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.osint_path):
            return []
        try:
            with open(self.osint_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load OSINT dataset: {e}")
            return []

    def correlate(self, 
                 address: str, 
                 blockchain: str,
                 reputation_summary: Optional[ReputationSummary] = None,
                 graph_paths: Optional[List[List[Any]]] = None,
                 transactions: Optional[List[Any]] = None) -> List[CorrelationFinding]:
        """
        Aggregates evidence into normalized CorrelationFindings.
        Implements strict deduplication.
        """
        findings: List[CorrelationFinding] = []
        seen_signatures = set()
        
        def add_finding(f: CorrelationFinding):
            sig = f"{f.category.value}:{f.source}:{f.evidence}"
            if sig not in seen_signatures:
                seen_signatures.add(sig)
                findings.append(f)
                
        # 1. Reputation & Ransomware
        if reputation_summary:
            for rep_finding in reputation_summary.findings:
                cat = CorrelationCategory.REPUTATION
                if rep_finding.finding_type == "ransomware":
                    cat = CorrelationCategory.RANSOMWARE
                    
                cf = CorrelationFinding(
                    category=cat,
                    description=rep_finding.finding,
                    source=rep_finding.source,
                    source_type=rep_finding.source_type,
                    evidence=f"Address matched in {rep_finding.source_type}",
                    confidence=rep_finding.confidence,
                    data_mode=rep_finding.data_mode,
                    metadata={"reported_date": rep_finding.reported_date, "reference": rep_finding.reference}
                )
                add_finding(cf)
                
        # 2. OSINT
        osint_data = self._load_osint()
        for rec in osint_data:
            if _address_matches(address, blockchain, rec.get("address", ""), rec.get("blockchain", "")):
                cf = CorrelationFinding(
                    category=CorrelationCategory.OSINT,
                    description=rec.get("finding", "OSINT Indicator"),
                    source=rec.get("source", "Unknown OSINT"),
                    source_type=rec.get("source_type", "osint"),
                    evidence="Source-reported OSINT indicator",
                    confidence=rec.get("confidence", "UNKNOWN"),
                    data_mode=rec.get("data_mode", "demo"),
                    metadata={"reference": rec.get("reference")}
                )
                add_finding(cf)
                
        # 3. Graph Observations
        if graph_paths:
            max_hops = max([len(p) for p in graph_paths]) if graph_paths else 0
            if max_hops >= 3:
                cf = CorrelationFinding(
                    category=CorrelationCategory.GRAPH_RELATIONSHIP,
                    description=f"Transaction path of {max_hops} or more hops observed.",
                    source="Cryptonexis Graph Engine",
                    source_type="internal",
                    evidence=f"Path length: {max_hops}",
                    data_mode="live" # Derived from loaded dataset
                )
                add_finding(cf)
                
        # 4. Transaction Activity (Fund Splitting Pattern)
        if transactions:
            # We look for a pattern where one tx has many outputs (>=5) from the address
            # Or other documented patterns. 
            # In Phase 5/6 we didn't perfectly map UTXO splitting to single properties, 
            # but we can simulate looking at output counts if we have raw metadata, 
            # or just look at counterparty count.
            outbound_txs = [t for t in transactions if t.from_address and t.from_address.lower() == address.lower()]
            if len(outbound_txs) > 10: 
                # Basic heuristic for demonstration if detailed UTXO metadata isn't parsed
                cf = CorrelationFinding(
                    category=CorrelationCategory.TRANSACTION_ACTIVITY,
                    description="High volume of outbound transactions.",
                    source="Cryptonexis Transaction Engine",
                    source_type="internal",
                    evidence=f"{len(outbound_txs)} outbound transactions observed.",
                    data_mode="live"
                )
                add_finding(cf)
                
        return findings

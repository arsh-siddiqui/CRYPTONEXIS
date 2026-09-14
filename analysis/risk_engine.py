import datetime
from typing import List, Dict
from analysis.correlation_models import CorrelationFinding, CorrelationCategory, RiskFactor, RiskAssessment

RISK_WEIGHTS = {
    "RANSOMWARE_REPORTED": 30,
    "REPUTATION_REPORTED": 25,
    "OSINT_REPORTED": 20,
    "MULTI_HOP_MOVEMENT": 10,
    "FUND_SPLITTING": 15,
}

class RiskEngine:
    def __init__(self):
        self.methodology_version = "1.0"
        
    def _get_level(self, score: int) -> str:
        if score <= 24:
            return "LOW"
        elif score <= 49:
            return "MEDIUM"
        elif score <= 74:
            return "HIGH"
        return "CRITICAL"
        
    def evaluate(self, findings: List[CorrelationFinding]) -> RiskAssessment:
        factors: List[RiskFactor] = []
        total_score = 0
        
        # Track applied factors to prevent double counting the same factor type multiple times
        # Requirements state: "Distinct independent findings may contribute separately." 
        # But usually we cap the factor application or apply per distinct finding. 
        # For this prototype, we'll apply the score for each distinct finding that maps to a factor,
        # but deduplication was already handled in CorrelationEngine.
        
        for finding in findings:
            factor_id = None
            score = 0
            
            if finding.category == CorrelationCategory.RANSOMWARE:
                factor_id = "RANSOMWARE_REPORTED"
                score = RISK_WEIGHTS[factor_id]
            elif finding.category == CorrelationCategory.REPUTATION:
                factor_id = "REPUTATION_REPORTED"
                score = RISK_WEIGHTS[factor_id]
            elif finding.category == CorrelationCategory.OSINT:
                factor_id = "OSINT_REPORTED"
                score = RISK_WEIGHTS[factor_id]
            elif finding.category == CorrelationCategory.GRAPH_RELATIONSHIP:
                factor_id = "MULTI_HOP_MOVEMENT"
                score = RISK_WEIGHTS[factor_id]
            elif finding.category == CorrelationCategory.TRANSACTION_ACTIVITY:
                factor_id = "FUND_SPLITTING"
                score = RISK_WEIGHTS[factor_id]
                
            if factor_id:
                # Append the factor
                rf = RiskFactor(
                    factor_id=factor_id,
                    description=finding.description,
                    score=score,
                    evidence=finding.evidence,
                    source=finding.source,
                    source_type=finding.source_type,
                    confidence=finding.confidence,
                    data_mode=finding.data_mode
                )
                factors.append(rf)
                total_score += score
                
        # Clamp score
        final_score = min(total_score, 100)
        final_score = max(final_score, 0)
        
        # Data mode
        global_mode = "demo"
        if any(f.data_mode == "live" for f in findings):
            global_mode = "live"
            if any(f.data_mode == "demo" for f in findings):
                global_mode = "LIVE + DEMO"
                
        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        return RiskAssessment(
            score=final_score,
            level=self._get_level(final_score),
            factors=factors,
            evidence=findings,
            data_mode=global_mode,
            generated_at=now_utc,
            methodology_version=self.methodology_version
        )

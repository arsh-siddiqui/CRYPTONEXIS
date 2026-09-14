import pytest
from analysis.correlation_models import CorrelationFinding, CorrelationCategory
from analysis.risk_engine import RiskEngine

def test_risk_engine_empty():
    engine = RiskEngine()
    assessment = engine.evaluate([])
    assert assessment.score == 0
    assert assessment.level == "LOW"
    assert len(assessment.factors) == 0

def test_risk_engine_single_factor():
    engine = RiskEngine()
    findings = [
        CorrelationFinding(
            category=CorrelationCategory.RANSOMWARE,
            description="Assoc",
            source="Test",
            source_type="Test",
            evidence="Evid"
        )
    ]
    assessment = engine.evaluate(findings)
    assert assessment.score == 30
    assert assessment.level == "MEDIUM"
    assert len(assessment.factors) == 1
    assert assessment.factors[0].factor_id == "RANSOMWARE_REPORTED"

def test_risk_engine_multiple_and_clamped():
    engine = RiskEngine()
    findings = [
        CorrelationFinding(category=CorrelationCategory.RANSOMWARE, description="", source="A", source_type="B", evidence="C"), # 30
        CorrelationFinding(category=CorrelationCategory.REPUTATION, description="", source="A", source_type="B", evidence="C"), # 25
        CorrelationFinding(category=CorrelationCategory.OSINT, description="", source="A", source_type="B", evidence="C"), # 20
        CorrelationFinding(category=CorrelationCategory.GRAPH_RELATIONSHIP, description="", source="A", source_type="B", evidence="C"), # 10
        CorrelationFinding(category=CorrelationCategory.TRANSACTION_ACTIVITY, description="", source="A", source_type="B", evidence="C"), # 15
        CorrelationFinding(category=CorrelationCategory.RANSOMWARE, description="Second Ransomware from different source", source="D", source_type="E", evidence="F") # 30
    ]
    
    assessment = engine.evaluate(findings)
    # Total theoretical score = 30 + 25 + 20 + 10 + 15 + 30 = 130
    # Clamped to 100
    assert assessment.score == 100
    assert assessment.level == "CRITICAL"
    assert len(assessment.factors) == 6

def test_risk_engine_levels():
    engine = RiskEngine()
    
    assert engine._get_level(0) == "LOW"
    assert engine._get_level(24) == "LOW"
    assert engine._get_level(25) == "MEDIUM"
    assert engine._get_level(49) == "MEDIUM"
    assert engine._get_level(50) == "HIGH"
    assert engine._get_level(74) == "HIGH"
    assert engine._get_level(75) == "CRITICAL"
    assert engine._get_level(100) == "CRITICAL"

def test_risk_engine_methodology():
    engine = RiskEngine()
    assessment = engine.evaluate([])
    assert assessment.methodology_version == "1.0"

def test_data_mode():
    engine = RiskEngine()
    findings = [
        CorrelationFinding(category=CorrelationCategory.RANSOMWARE, description="", source="", source_type="", evidence="", data_mode="live"),
        CorrelationFinding(category=CorrelationCategory.REPUTATION, description="", source="", source_type="", evidence="", data_mode="demo")
    ]
    assessment = engine.evaluate(findings)
    assert assessment.data_mode == "LIVE + DEMO"

import pytest
from analysis.correlation_models import CorrelationFinding, CorrelationCategory
from analysis.reputation_models import ReputationSummary, ReputationStatus, ReputationFinding
from analysis.correlation_engine import CorrelationEngine
import json
import os

@pytest.fixture
def osint_data_dir(tmp_path):
    data_dir = tmp_path / "data"
    osint_dir = data_dir / "threat_intelligence"
    osint_dir.mkdir(parents=True)
    
    osint_data = [
        {
            "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "blockchain": "Bitcoin",
            "category": "osint",
            "finding": "Demo investigative indicator",
            "source": "OSINT Data",
            "source_type": "demo_osint",
            "data_mode": "demo"
        }
    ]
    with open(osint_dir / "osint_records.json", "w", encoding="utf-8") as f:
        json.dump(osint_data, f)
        
    return str(data_dir)

def test_correlation_engine_osint(osint_data_dir):
    engine = CorrelationEngine(osint_data_dir)
    findings = engine.correlate("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin")
    
    assert len(findings) == 1
    assert findings[0].category == CorrelationCategory.OSINT
    assert findings[0].source == "OSINT Data"
    assert findings[0].data_mode == "demo"

def test_correlation_engine_reputation(osint_data_dir):
    engine = CorrelationEngine(osint_data_dir)
    
    rep_summary = ReputationSummary(
        address="addr", blockchain="Ethereum", status=ReputationStatus.MATCH,
        findings=[
            ReputationFinding(address="addr", blockchain="Ethereum", finding_type="ransomware", 
                              finding="Ransomware assoc", source="Src", source_type="test")
        ]
    )
    
    findings = engine.correlate("addr", "Ethereum", reputation_summary=rep_summary)
    # 1 for reputation ransomware
    assert len(findings) == 1
    assert findings[0].category == CorrelationCategory.RANSOMWARE

def test_correlation_engine_graph(osint_data_dir):
    engine = CorrelationEngine(osint_data_dir)
    # mock graph path
    paths = [[1, 2, 3, 4]] # length 4 hops
    
    findings = engine.correlate("addr", "Bitcoin", graph_paths=paths)
    assert len(findings) == 1
    assert findings[0].category == CorrelationCategory.GRAPH_RELATIONSHIP
    assert "4 or more hops" in findings[0].description

def test_correlation_engine_transaction_splitting(osint_data_dir):
    engine = CorrelationEngine(osint_data_dir)
    
    class DummyTx:
        def __init__(self, f):
            self.from_address = f
            
    txs = [DummyTx("addr") for _ in range(15)]
    
    findings = engine.correlate("addr", "Bitcoin", transactions=txs)
    assert len(findings) == 1
    assert findings[0].category == CorrelationCategory.TRANSACTION_ACTIVITY
    assert "15 outbound" in findings[0].evidence

def test_correlation_engine_deduplication(osint_data_dir):
    engine = CorrelationEngine(osint_data_dir)
    
    rep_summary = ReputationSummary(
        address="addr", blockchain="Ethereum", status=ReputationStatus.MATCH,
        findings=[
            # Exact duplicates from the same source should ideally be stripped out
            ReputationFinding(address="addr", blockchain="Ethereum", finding_type="scam", 
                              finding="Scam", source="Src", source_type="test"),
            ReputationFinding(address="addr", blockchain="Ethereum", finding_type="scam", 
                              finding="Scam", source="Src", source_type="test")
        ]
    )
    
    # Engine uses sig: {category}:{source}:{evidence}
    findings = engine.correlate("addr", "Ethereum", reputation_summary=rep_summary)
    
    # Should be deduplicated to 1
    assert len(findings) == 1

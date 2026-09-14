import pytest
import os
import json
from analysis.reputation_models import ReputationStatus
from analysis.reputation_engine import check_address

@pytest.fixture
def temp_data_dir(tmp_path):
    # Setup temporary directories
    data_dir = tmp_path / "data"
    ransomware_dir = data_dir / "ransomware"
    threat_dir = data_dir / "threat_intelligence"
    ransomware_dir.mkdir(parents=True)
    threat_dir.mkdir(parents=True)
    
    # Ransomware dummy data
    rw_data = [
        {
            "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "blockchain": "Bitcoin",
            "family": "DemoRansom",
            "source": "Local Threat Dataset",
            "source_type": "ransomware_intelligence",
            "reported_date": "2025-01-01",
            "confidence": "HIGH",
            "reference": "https://example.com/report/1",
            "data_mode": "demo"
        },
        {
            "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "blockchain": "Ethereum",
            "family": "DemoCrypt",
            "source": "Local Threat Dataset",
            "source_type": "ransomware_intelligence",
            "reported_date": "2024-05-12",
            "confidence": "MEDIUM",
            "reference": "https://example.com/report/2",
            "data_mode": "demo"
        }
    ]
    with open(ransomware_dir / "ransomware_addresses.json", "w", encoding="utf-8") as f:
        json.dump(rw_data, f)
        
    # Threat intel dummy data
    threat_data = [
        {
            "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", # Exact match, case sensitive? For EVM should be insensitive
            "blockchain": "Ethereum",
            "finding": "Source-reported phishing association",
            "source": "PhishIntel Demo",
            "source_type": "phishing_intelligence",
            "reported_date": "2025-02-15",
            "confidence": "HIGH",
            "reference": "https://example.com/phish/1",
            "data_mode": "demo"
        },
        {
            "address": "0xBadAddressAgnosticNetwork",
            "blockchain": "agnostic",
            "finding": "Source-reported generalized fraud indicator",
            "source": "Agnostic Intel Demo",
            "source_type": "fraud_intelligence",
            "reported_date": "2025-03-01",
            "confidence": "MEDIUM",
            "reference": "https://example.com/fraud/agnostic",
            "data_mode": "demo"
        },
        {
            "address": "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4", # valid bech32 lower
            "blockchain": "Bitcoin",
            "finding": "Stolen funds",
            "source": "Bech32 Demo",
            "source_type": "theft",
            "reported_date": "2025-01-01",
            "confidence": "HIGH",
            "reference": "https://example.com/bech32",
            "data_mode": "demo"
        }
    ]
    with open(threat_dir / "address_reports.json", "w", encoding="utf-8") as f:
        json.dump(threat_data, f)
        
    return str(data_dir)

def test_no_match(temp_data_dir):
    res = check_address("unknown_address", "Bitcoin", temp_data_dir)
    assert res.status == ReputationStatus.NO_MATCH
    assert "No matching record" in res.message
    assert res.ransomware_reports == 0

def test_exact_ransomware_match(temp_data_dir):
    res = check_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin", temp_data_dir)
    assert res.status == ReputationStatus.MATCH
    assert res.ransomware_reports == 1
    assert res.findings[0].source_type == "ransomware_intelligence"
    assert "DemoRansom" in res.findings[0].finding

def test_multiple_findings_and_case_insensitive_evm(temp_data_dir):
    # Notice we change casing for EVM check
    res = check_address("0XD8DA6BF26964AF9D7EED9E03E53415D37AA96045", "Ethereum", temp_data_dir)
    assert res.status == ReputationStatus.MATCH
    assert len(res.findings) == 2
    assert res.ransomware_reports == 1
    assert res.other_reports == 1

def test_blockchain_specific_match(temp_data_dir):
    # Same address, different blockchain -> should NOT match
    res = check_address("0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "Bitcoin", temp_data_dir)
    assert res.status == ReputationStatus.NO_MATCH

def test_agnostic_blockchain_match(temp_data_dir):
    res = check_address("0xBadAddressAgnosticNetwork", "BNB Smart Chain", temp_data_dir)
    assert res.status == ReputationStatus.MATCH
    assert res.findings[0].blockchain == "agnostic"

def test_invalid_address_input(temp_data_dir):
    res = check_address("", "Bitcoin", temp_data_dir)
    assert res.status == ReputationStatus.ERROR

def test_unknown_blockchain(temp_data_dir):
    res = check_address("addr", "", temp_data_dir)
    assert res.status == ReputationStatus.ERROR

def test_bitcoin_bech32_casing(temp_data_dir):
    # Valid uppercase bech32 query against lowercase bech32 dataset
    res = check_address("BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4", "Bitcoin", temp_data_dir)
    assert res.status == ReputationStatus.MATCH
    
    # Mixed case should trigger error early
    res2 = check_address("bc1qW508d6QEJXTdg4Y5r3zarvary0c5XW7KV8F3T4", "Bitcoin", temp_data_dir)
    assert res2.status == ReputationStatus.ERROR
    assert "Invalid mixed-case" in res2.message
    
def test_demo_data_labeling(temp_data_dir):
    res = check_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "Bitcoin", temp_data_dir)
    assert res.data_mode == "demo"
    assert res.findings[0].data_mode == "demo"

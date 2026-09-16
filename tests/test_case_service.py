import pytest
from services.case_service import CaseService
from database.schema import initialize_database
from database.connection import get_connection
import os

@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    import database.connection
    db_path = tmp_path / "test_cryptonexis.db"
    
    # Store old values
    old_db_path = database.connection.DB_FILE
    
    # Override
    database.connection.DB_FILE = str(db_path)
    
    # Init
    initialize_database()
    
    yield
    
    # Restore
    database.connection.DB_FILE = old_db_path
    
def test_create_case():
    service = CaseService()
    case = service.create_case(title="Test Case 1", priority="HIGH")
    assert case is not None
    assert case.id > 0
    assert case.case_number.startswith("CNX-")
    assert case.title == "Test Case 1"
    assert case.priority == "HIGH"
    assert case.status == "OPEN"

def test_case_number_generation():
    service = CaseService()
    case1 = service.create_case(title="Case 1")
    case2 = service.create_case(title="Case 2")
    
    assert case1.case_number != case2.case_number
    # Extract sequential part
    c1_num = int(case1.case_number.split('-')[-1])
    c2_num = int(case2.case_number.split('-')[-1])
    assert c2_num == c1_num + 1

def test_add_wallet():
    service = CaseService()
    case = service.create_case(title="Wallet Case")
    
    assert service.add_wallet_to_case(case.id, "0x123", "ETHEREUM", "Target", "PRIMARY")
    
    # Fetch case
    loaded = service.get_case(case.id)
    assert len(loaded.wallets) == 1
    assert loaded.wallets[0].wallet_address == "0x123"
    
def test_add_evidence():
    service = CaseService()
    case = service.create_case(title="Evidence Case")
    
    assert service.add_evidence(
        case.id, "REPUTATION", "Reputation Alert", 
        "Suspicious address", "SourceX", "API", "LIVE"
    )
    
    loaded = service.get_case(case.id)
    assert len(loaded.evidence) == 1
    assert loaded.evidence[0].evidence_type == "REPUTATION"
    assert loaded.evidence[0].title == "Reputation Alert"

def test_get_case_summary():
    service = CaseService()
    case = service.create_case(title="Summary Case")
    service.add_wallet_to_case(case.id, "0x123", "ETHEREUM")
    service.add_transaction_to_case(case.id, "tx1", "ETHEREUM")
    
    summary = service.get_case_summary(case.id)
    assert summary is not None
    assert summary.num_wallets == 1
    assert summary.num_transactions == 1
    assert "ETHEREUM" in summary.observed_blockchains

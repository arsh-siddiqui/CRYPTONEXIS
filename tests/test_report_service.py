import pytest
import os
from services.case_service import CaseService
from services.report_service import ReportService
from database.schema import initialize_database

@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    import database.connection
    db_path = tmp_path / "test_cryptonexis.db"
    old_db_path = database.connection.DB_FILE
    database.connection.DB_FILE = str(db_path)
    initialize_database()
    yield
    database.connection.DB_FILE = old_db_path

def test_generate_html_report(tmp_path):
    case_service = CaseService()
    case = case_service.create_case(title="HTML Report Case")
    
    # Add dummy data
    case_service.add_wallet_to_case(case.id, "0xABC", "ETHEREUM")
    case_service.add_evidence(case.id, "NOTE", "Observation", "Test node", "Analyst", "USER", "LIVE")
    
    config = {"DATA_MODE": "DEMO"}
    report_service = ReportService(config)
    report_service.output_dir = str(tmp_path)
    
    filepath = report_service.generate_html(case.id)
    assert filepath is not None
    assert os.path.exists(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        assert "HTML Report Case" in content
        assert "0xABC" in content
        assert "DEMO DATA" in content

def test_generate_pdf_report(tmp_path):
    case_service = CaseService()
    case = case_service.create_case(title="PDF Report Case")
    
    config = {"DATA_MODE": "LIVE"}
    report_service = ReportService(config)
    report_service.output_dir = str(tmp_path)
    
    filepath = report_service.generate_pdf(case.id)
    
    # If reportlab is installed, this will succeed
    import services.report_service
    if services.report_service.REPORTLAB_AVAILABLE:
        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith(".pdf")
    else:
        assert filepath is None

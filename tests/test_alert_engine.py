import pytest
from unittest.mock import patch, MagicMock
from analysis.alert_models import AlertSeverity, AlertRecord
from analysis.alert_engine import AlertEngine

@pytest.fixture
def alert_engine():
    return AlertEngine()

@patch('analysis.alert_engine.CorrelationEngine')
@patch('analysis.alert_engine.RiskEngine')
@patch('analysis.alert_engine.check_address')
def test_evaluate_transaction_info(mock_check_addr, mock_risk_engine_cls, mock_corr_engine_cls, alert_engine):
    # Setup mocks
    mock_risk_engine = mock_risk_engine_cls.return_value
    
    # Return a low risk assessment
    mock_assessment = MagicMock()
    mock_assessment.level = "LOW"
    mock_risk_engine.evaluate.return_value = mock_assessment
    
    alert_engine.risk_engine = mock_risk_engine
    
    tx = {
        "tx_hash": "0x123",
        "direction": "INCOMING",
        "amount": 0.0,
        "asset": "BTC",
        "timestamp": "2026-01-01T00:00:00"
    }
    
    alert = alert_engine.evaluate_transaction(1, "addr", "Bitcoin", tx)
    
    assert alert.severity == AlertSeverity.INFO
    assert alert.tx_hash == "0x123"
    assert "New incoming transaction" in alert.message

@patch('analysis.alert_engine.CorrelationEngine')
@patch('analysis.alert_engine.RiskEngine')
@patch('analysis.alert_engine.check_address')
def test_evaluate_transaction_critical(mock_check_addr, mock_risk_engine_cls, mock_corr_engine_cls, alert_engine):
    mock_risk_engine = mock_risk_engine_cls.return_value
    
    # Return CRITICAL risk assessment
    mock_assessment = MagicMock()
    mock_assessment.level = "CRITICAL"
    mock_risk_engine.evaluate.return_value = mock_assessment
    
    alert_engine.risk_engine = mock_risk_engine
    
    tx = {
        "tx_hash": "0xABC",
        "direction": "OUTGOING",
        "amount": 5.0,
        "asset": "ETH",
        "data_mode": "DEMO"
    }
    
    alert = alert_engine.evaluate_transaction(1, "addr", "Ethereum", tx)
    
    assert alert.severity == AlertSeverity.CRITICAL
    assert "High risk indicators present" in alert.message
    assert "[DEMO]" in alert.message

import unittest
from unittest.mock import patch, Mock
from services.bitcoin_service import BitcoinService

class TestBitcoinService(unittest.TestCase):
    def setUp(self):
        self.service = BitcoinService()
        self.test_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        
    @patch('services.bitcoin_service.requests.get')
    def test_get_address_summary_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "address": self.test_address,
            "n_tx": 10,
            "total_received": 1000,
            "total_sent": 500,
            "final_balance": 500,
            "txs": [{"hash": "abc"}]
        }
        mock_get.return_value = mock_response
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertNotIn("error", result)
        self.assertEqual(result["blockchain"], "Bitcoin")
        self.assertEqual(result["address"], self.test_address)
        self.assertEqual(result["n_tx"], 10)
        self.assertEqual(len(result["transactions"]), 1)
        
    @patch('services.bitcoin_service.requests.get')
    def test_get_address_summary_http_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertIn("error", result)
        self.assertTrue("HTTP 500" in result["error"])
        
    @patch('services.bitcoin_service.requests.get')
    def test_get_address_summary_malformed(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Invalid address"}
        mock_get.return_value = mock_response
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertIn("error", result)

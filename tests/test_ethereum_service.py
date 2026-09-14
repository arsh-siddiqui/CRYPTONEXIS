import unittest
from unittest.mock import patch, Mock
from services.ethereum_service import EthereumService

class TestEthereumService(unittest.TestCase):
    def setUp(self):
        self.service = EthereumService(api_key="test_key")
        self.test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        
    @patch('services.ethereum_service.requests.get')
    def test_get_address_summary_success(self, mock_get):
        # We make requests.get return different responses for the 2 calls (balance, txs)
        mock_response_bal = Mock()
        mock_response_bal.status_code = 200
        mock_response_bal.json.return_value = {"status": "1", "message": "OK", "result": "1000000000000000000"}
        
        mock_response_txs = Mock()
        mock_response_txs.status_code = 200
        mock_response_txs.json.return_value = {"status": "1", "message": "OK", "result": [{"hash": "0xabc"}]}
        
        mock_get.side_effect = [mock_response_bal, mock_response_txs]
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertNotIn("error", result)
        self.assertEqual(result["blockchain"], "Ethereum")
        self.assertEqual(result["final_balance"], "1000000000000000000")
        self.assertEqual(result["n_tx"], 1)
        self.assertEqual(len(result["transactions"]), 1)
        
    @patch('services.ethereum_service.requests.get')
    def test_get_address_summary_api_error(self, mock_get):
        mock_response_bal = Mock()
        mock_response_bal.status_code = 200
        mock_response_bal.json.return_value = {"status": "0", "message": "NOTOK", "result": "Invalid API Key"}
        mock_get.return_value = mock_response_bal
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertIn("error", result)
        self.assertTrue("Invalid API Key" in result["error"])
        
    def test_missing_api_key(self):
        service = EthereumService(api_key="")
        result = service.get_address_summary(self.test_address)
        self.assertIn("error", result)
        self.assertTrue("ETHERSCAN_API_KEY" in result["error"])

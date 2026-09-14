import unittest
from unittest.mock import patch, Mock
from services.bsc_service import BscService

class TestBscService(unittest.TestCase):
    def setUp(self):
        self.service = BscService(api_key="test_ankr_key")
        self.test_address = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
        
    @patch('services.bsc_service.requests.post')
    def test_get_address_summary_success(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "transactions": [{"hash": "0xabc", "from": self.test_address}]
            }
        }
        mock_post.return_value = mock_response
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertNotIn("error", result)
        self.assertEqual(result["blockchain"], "BNB Smart Chain")
        self.assertEqual(result["n_tx"], 1)
        self.assertEqual(len(result["transactions"]), 1)
        
    @patch('services.bsc_service.requests.post')
    def test_get_address_summary_rpc_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32602, "message": "Invalid address"}
        }
        mock_post.return_value = mock_response
        
        result = self.service.get_address_summary(self.test_address)
        
        self.assertIn("error", result)
        self.assertTrue("Invalid address" in result["error"])
        
    def test_missing_api_key(self):
        service = BscService(api_key="")
        result = service.get_address_summary(self.test_address)
        self.assertIn("error", result)
        self.assertTrue("ANKR_API_KEY" in result["error"])

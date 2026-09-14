import requests
import logging

logger = logging.getLogger(__name__)

class EthereumService:
    def __init__(self, api_key):
        self.base_url = "https://api.etherscan.io/v2/api"
        self.api_key = api_key
        
    def get_address_summary(self, address):
        """
        Retrieves public address balance and normal transactions from Etherscan V2 API.
        """
        if not self.api_key:
            return {"error": "ETHERSCAN_API_KEY is not configured"}
            
        try:
            logger.info(f"Fetching Ethereum data for address: {address}")
            
            # 1. Get Balance
            bal_params = {
                "chainid": "1",
                "module": "account",
                "action": "balance",
                "address": address,
                "tag": "latest",
                "apikey": self.api_key
            }
            bal_response = requests.get(self.base_url, params=bal_params, timeout=10)
            if bal_response.status_code != 200:
                return {"error": f"API returned HTTP {bal_response.status_code}"}
                
            bal_data = bal_response.json()
            if bal_data.get("status") != "1":
                # Etherscan often returns "0" for status on valid empty addresses but with "OK" message
                # Or it returns "0" for rate limiting/invalid keys.
                if bal_data.get("message") == "NOTOK":
                    return {"error": f"Etherscan error: {bal_data.get('result', 'Unknown error')}"}
            
            balance_wei = bal_data.get("result", "0")
            
            # 2. Get Normal Transactions
            tx_params = {
                "chainid": "1",
                "module": "account",
                "action": "txlist",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": 50, # reasonable page size for Phase 4
                "sort": "desc",
                "apikey": self.api_key
            }
            tx_response = requests.get(self.base_url, params=tx_params, timeout=10)
            if tx_response.status_code != 200:
                return {"error": f"API returned HTTP {tx_response.status_code} on tx fetch"}
                
            tx_data = tx_response.json()
            if tx_data.get("status") == "0" and tx_data.get("message") == "NOTOK":
                return {"error": f"Etherscan error: {tx_data.get('result', 'Unknown error')}"}
                
            transactions = tx_data.get("result", [])
            # Sometimes Etherscan returns string "No transactions found" in result instead of list
            if not isinstance(transactions, list):
                transactions = []
            
            # Construct the result
            summary = {
                "blockchain": "Ethereum",
                "address": address,
                "final_balance": balance_wei,
                "n_tx": len(transactions),
                "transactions": transactions
            }
            return summary
            
        except requests.exceptions.Timeout:
            logger.error("Etherscan API timeout")
            return {"error": "Connection timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Etherscan API request error: {e}")
            return {"error": "Network error occurred"}
        except Exception as e:
            logger.error(f"EthereumService unexpected error: {e}")
            return {"error": "An unexpected error occurred parsing the data"}

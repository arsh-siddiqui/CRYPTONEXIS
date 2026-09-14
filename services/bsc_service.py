import requests
import logging

logger = logging.getLogger(__name__)

class BscService:
    def __init__(self, api_key):
        self.api_key = api_key
        
    def get_address_summary(self, address, page_size=50):
        """
        Retrieves public address transactions from Ankr Advanced Multichain API.
        """
        if not self.api_key:
            return {"error": "ANKR_API_KEY is not configured"}
            
        base_url = f"https://rpc.ankr.com/multichain/{self.api_key}"
        
        try:
            logger.info(f"Fetching BSC data for address: {address}")
            
            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "ankr_getTransactionsByAddress",
                "params": {
                    "address": address,
                    "blockchain": ["bsc"],
                    "pageSize": page_size
                }
            }
            
            response = requests.post(base_url, json=payload, timeout=15)
            if response.status_code != 200:
                return {"error": f"API returned HTTP {response.status_code}"}
                
            data = response.json()
            
            if "error" in data:
                err_msg = data["error"].get("message", "Unknown RPC error")
                return {"error": f"Ankr RPC error: {err_msg}"}
                
            result = data.get("result", {})
            transactions = result.get("transactions", [])
            
            # Ankr does not return a direct balance in this endpoint easily,
            # we rely on ankr_getAccountBalance for that, but for Phase 4 we 
            # might just return the transaction list if balance is not easily available.
            # We'll just return what we have.
            
            summary = {
                "blockchain": "BNB Smart Chain",
                "address": address,
                "n_tx": len(transactions),
                "transactions": transactions
            }
            return summary
            
        except requests.exceptions.Timeout:
            logger.error("Ankr API timeout")
            return {"error": "Connection timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Ankr API request error: {e}")
            return {"error": "Network error occurred"}
        except Exception as e:
            logger.error(f"BscService unexpected error: {e}")
            return {"error": "An unexpected error occurred parsing the data"}

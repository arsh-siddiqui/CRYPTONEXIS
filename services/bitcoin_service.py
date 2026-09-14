import requests
import logging

logger = logging.getLogger(__name__)

class BitcoinService:
    def __init__(self):
        self.base_url = "https://blockchain.info/rawaddr"
        
    def get_address_summary(self, address, limit=50, offset=0):
        """
        Retrieves public address data from Blockchain.com API.
        Does not require an API key for this endpoint.
        """
        try:
            url = f"{self.base_url}/{address}"
            params = {
                "limit": limit,
                "offset": offset
            }
            logger.info(f"Fetching Bitcoin data for address: {address}")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                logger.error(f"Blockchain.com API error: HTTP {response.status_code}")
                return {"error": f"API returned HTTP {response.status_code}"}
                
            data = response.json()
            
            # Ensure required basic fields exist
            if "address" not in data:
                return {"error": "Invalid address or malformed response"}
                
            # Filter and construct the result
            summary = {
                "blockchain": "Bitcoin",
                "address": data.get("address"),
                "n_tx": data.get("n_tx", 0),
                "total_received": data.get("total_received", 0),
                "total_sent": data.get("total_sent", 0),
                "final_balance": data.get("final_balance", 0),
                "transactions": data.get("txs", [])
            }
            return summary
            
        except requests.exceptions.Timeout:
            logger.error("Blockchain.com API timeout")
            return {"error": "Connection timed out"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Blockchain.com API request error: {e}")
            return {"error": "Network error occurred"}
        except Exception as e:
            logger.error(f"BitcoinService unexpected error: {e}")
            return {"error": "An unexpected error occurred parsing the data"}

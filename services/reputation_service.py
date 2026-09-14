import json
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LocalIntelligenceProvider:
    """Provider for local JSON-based threat intelligence."""
    
    def __init__(self, data_dir: str = "data"):
        self.ransomware_path = os.path.join(data_dir, "ransomware", "ransomware_addresses.json")
        self.threat_path = os.path.join(data_dir, "threat_intelligence", "address_reports.json")
        
    def _load_json(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            logger.warning(f"Local dataset not found at {path}")
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load dataset at {path}: {e}")
            return []
            
    def get_ransomware_records(self) -> List[Dict[str, Any]]:
        return self._load_json(self.ransomware_path)
        
    def get_threat_records(self) -> List[Dict[str, Any]]:
        return self._load_json(self.threat_path)

class ReputationService:
    """Service layer orchestrating intelligence providers."""
    
    def __init__(self, data_dir: str = "data"):
        self.local_provider = LocalIntelligenceProvider(data_dir)
        # Future: External providers could be initialized here
        
    def query_ransomware(self) -> List[Dict[str, Any]]:
        """Queries configured providers for ransomware datasets."""
        # Phase 7 only queries local provider
        return self.local_provider.get_ransomware_records()
        
    def query_threat_reports(self) -> List[Dict[str, Any]]:
        """Queries configured providers for general threat datasets."""
        # Phase 7 only queries local provider
        return self.local_provider.get_threat_records()

import logging
from typing import List, Dict, Any, Tuple
from analysis.reputation_models import ReputationFinding, ReputationSummary, ReputationStatus
from services.reputation_service import ReputationService

logger = logging.getLogger(__name__)

def _is_valid_bech32_casing(address: str) -> bool:
    """Returns True if the bech32 address is homogeneously cased (all lower or all upper)."""
    if not address.lower().startswith("bc1"):
        return True # Not bech32, casing rules don't apply here
    return address == address.lower() or address == address.upper()

def _address_matches(query_addr: str, query_chain: str, dataset_addr: str, dataset_chain: str) -> bool:
    """
    Safely determines if an address from a dataset matches the queried address,
    respecting blockchain-specific scoping and casing rules.
    """
    if not query_addr or not dataset_addr:
        return False
        
    query_chain_l = query_chain.lower()
    dataset_chain_l = dataset_chain.lower()
    
    # 1. Blockchain Scoping
    if dataset_chain_l != query_chain_l and dataset_chain_l != "agnostic":
        return False
        
    # 2. Address Casing Rules
    if query_chain_l == "bitcoin" or dataset_chain_l == "bitcoin":
        is_query_bech32 = query_addr.lower().startswith("bc1")
        is_ds_bech32 = dataset_addr.lower().startswith("bc1")
        
        # Base58 (exact match)
        if not is_query_bech32 and not is_ds_bech32:
            return query_addr == dataset_addr
            
        # Bech32 rules
        if is_query_bech32:
            if not _is_valid_bech32_casing(query_addr):
                return False # Invalid query casing
        if is_ds_bech32:
            if not _is_valid_bech32_casing(dataset_addr):
                return False # Invalid dataset casing
                
        # If one is bech32 and the other isn't, they don't match
        if is_query_bech32 != is_ds_bech32:
            return False
            
        # Valid Bech32 should be matched case-insensitively
        return query_addr.lower() == dataset_addr.lower()
    else:
        # EVM Chains (Ethereum, BSC, agnostic)
        return query_addr.lower() == dataset_addr.lower()

def check_address(address: str, blockchain: str, data_dir: str = "data") -> ReputationSummary:
    """
    Checks an address against all configured intelligence sources.
    Returns a unified ReputationSummary.
    """
    if not address:
        return ReputationSummary(address, blockchain, ReputationStatus.ERROR, message="Empty address provided.")
        
    if not blockchain:
        return ReputationSummary(address, blockchain, ReputationStatus.ERROR, message="Unknown blockchain.")
        
    # In Bitcoin, reject invalid bech32 up front
    if blockchain.lower() == "bitcoin" and address.lower().startswith("bc1"):
        if not _is_valid_bech32_casing(address):
            return ReputationSummary(
                address, blockchain, ReputationStatus.ERROR, 
                message="Invalid mixed-case representation for Bech32 Bitcoin address."
            )
            
    service = ReputationService(data_dir=data_dir)
    findings: List[ReputationFinding] = []
    
    ransomware_reports = 0
    other_reports = 0
    sources_checked = 1 # We check the LocalIntelligenceProvider
    
    try:
        # 1. Ransomware Checks
        ransomware_data = service.query_ransomware()
        for rec in ransomware_data:
            if _address_matches(address, blockchain, rec.get("address", ""), rec.get("blockchain", "")):
                finding_str = rec.get("finding", "Source-reported ransomware association")
                # Sometimes datasets provide a 'family'
                if "family" in rec:
                    finding_str += f" (Family: {rec['family']})"
                    
                finding = ReputationFinding(
                    address=rec.get("address", address),
                    blockchain=rec.get("blockchain", blockchain),
                    finding_type="ransomware",
                    finding=finding_str,
                    source=rec.get("source", "Unknown Source"),
                    source_type=rec.get("source_type", "ransomware_intelligence"),
                    reported_date=rec.get("reported_date"),
                    confidence=rec.get("confidence", "UNKNOWN"),
                    reference=rec.get("reference"),
                    data_mode=rec.get("data_mode", "demo")
                )
                findings.append(finding)
                ransomware_reports += 1
                
        # 2. General Threat Checks
        threat_data = service.query_threat_reports()
        for rec in threat_data:
            if _address_matches(address, blockchain, rec.get("address", ""), rec.get("blockchain", "")):
                finding = ReputationFinding(
                    address=rec.get("address", address),
                    blockchain=rec.get("blockchain", blockchain),
                    finding_type=rec.get("finding_type", "general_threat"),
                    finding=rec.get("finding", "Source-reported finding"),
                    source=rec.get("source", "Unknown Source"),
                    source_type=rec.get("source_type", "threat_intelligence"),
                    reported_date=rec.get("reported_date"),
                    confidence=rec.get("confidence", "UNKNOWN"),
                    reference=rec.get("reference"),
                    data_mode=rec.get("data_mode", "demo")
                )
                
                # Check for duplicates
                is_dup = False
                for f in findings:
                    if f.source == finding.source and f.finding == finding.finding:
                        is_dup = True
                        break
                        
                if not is_dup:
                    findings.append(finding)
                    other_reports += 1
                    
    except Exception as e:
        logger.error(f"Reputation lookup failed: {e}")
        return ReputationSummary(address, blockchain, ReputationStatus.ERROR, message=f"Lookup failed: {e}")
        
    status = ReputationStatus.NO_MATCH
    msg = "No matching record was found in the configured intelligence sources. This does not establish that the address is safe or benign."
    
    if findings:
        status = ReputationStatus.REPORTED
        # If any record exactly matched structurally (not just reported an association), we could flag MATCH,
        # but REPORTED is safe and adheres to neutral evidence requirements. Let's use MATCH if we want to be explicit.
        # The prompt requires: "MATCH: The address exactly matches a structured intelligence record."
        # Since our logic does exact string checks (after casing normalizations), we will use MATCH.
        status = ReputationStatus.MATCH
        msg = f"Found {len(findings)} matching record(s) across {sources_checked} source(s)."

    # Determine global data mode (if any real live data was mixed, it would be live, otherwise demo)
    global_mode = "demo"
    if any(f.data_mode.lower() == "live" for f in findings):
        global_mode = "live"

    return ReputationSummary(
        address=address,
        blockchain=blockchain,
        status=status,
        ransomware_reports=ransomware_reports,
        other_reports=other_reports,
        sources_checked=sources_checked,
        findings=findings,
        message=msg,
        data_mode=global_mode
    )

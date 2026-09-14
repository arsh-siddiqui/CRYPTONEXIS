import re

def detect_and_validate(identifier: str, selected_chain: str = "Auto Detect") -> dict:
    """
    Validates and detects the cryptocurrency type of a given identifier.
    Returns a structured dictionary with the validation result.
    """
    if not identifier:
        return _invalid_result("", "Input cannot be empty.")
        
    normalized = identifier.strip()
    
    if not normalized:
        return _invalid_result(normalized, "Input cannot be only whitespace.")
        
    # BTC Regex: Legacy P2PKH (1...), P2SH (3...), SegWit Bech32 (bc1q...), Taproot Bech32m (bc1p...)
    is_btc = bool(re.match(r'^(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[q|p][a-z0-9]{38,59})$', normalized))
    
    # EVM Regex: 0x followed by exactly 40 hex chars
    is_evm = bool(re.match(r'^0x[a-fA-F0-9]{40}$', normalized))
    
    # Transaction Hash logic (Basic 64 hex chars or 0x + 64 hex chars)
    is_tx = bool(re.match(r'^[a-fA-F0-9]{64}$', normalized)) or bool(re.match(r'^0x[a-fA-F0-9]{64}$', normalized))
    
    if selected_chain == "Bitcoin":
        if is_btc:
            return _btc_result(normalized)
        else:
            return _invalid_result(normalized, "Invalid Bitcoin address format.")
            
    elif selected_chain in ["Ethereum", "BNB Smart Chain"]:
        if is_evm:
            return _evm_result(normalized, selected_chain)
        else:
            return _invalid_result(normalized, f"Invalid {selected_chain} address format.")
            
    else: # Auto Detect
        if is_btc:
            return _btc_result(normalized)
        elif is_evm:
            return _evm_result(normalized, "EVM")
        else:
            if is_tx:
                return _invalid_result(normalized, "Input appears to be a transaction hash. Only wallet addresses are fully supported in Phase 3.")
            return _invalid_result(normalized, "Unsupported or malformed address format.")

def _btc_result(normalized: str) -> dict:
    return {
        "input": normalized,
        "normalized": normalized,
        "valid": True,
        "asset_type": "address",
        "detected_type": "Bitcoin",
        "confidence": "Format",
        "reason": "Valid Bitcoin address format.",
        "supported": True
    }

def _evm_result(normalized: str, chain: str) -> dict:
    if chain == "EVM":
        reason = "Blockchain cannot be determined from address syntax alone."
        possible = ["Ethereum", "BNB Smart Chain"]
        det_type = "EVM"
    else:
        reason = f"Valid EVM address format. On-chain existence on {chain} will be verified later."
        possible = [chain]
        det_type = chain
        
    return {
        "input": normalized,
        "normalized": normalized,
        "valid": True,
        "asset_type": "address",
        "detected_type": det_type,
        "possible_chains": possible,
        "confidence": "Format",
        "reason": reason,
        "supported": True
    }

def _invalid_result(normalized: str, reason: str) -> dict:
    return {
        "input": normalized,
        "normalized": normalized,
        "valid": False,
        "asset_type": "unknown",
        "detected_type": "Unknown",
        "confidence": "None",
        "reason": reason,
        "supported": False
    }

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional

from analysis.models import NormalizedTransaction, TransactionDirection, TransactionStatus

logger = logging.getLogger(__name__)

def _parse_timestamp(ts: Any) -> Optional[datetime]:
    if not ts:
        return None
    try:
        # Handle hex string timestamps (Ankr)
        if isinstance(ts, str) and ts.startswith("0x"):
            ts = int(ts, 16)
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except (ValueError, TypeError):
        return None

def normalize_bitcoin_transaction(raw_tx: Dict[str, Any], investigated_address: str) -> Optional[NormalizedTransaction]:
    try:
        tx_hash = raw_tx.get("hash", "")
        if not tx_hash:
            return None
            
        inv_addr_lower = investigated_address.lower()
        
        inputs = raw_tx.get("inputs", [])
        outputs = raw_tx.get("out", [])
        
        total_in_for_addr = Decimal(0)
        for i in inputs:
            prev_out = i.get("prev_out", {})
            if prev_out.get("addr", "").lower() == inv_addr_lower:
                val = prev_out.get("value", 0)
                total_in_for_addr += Decimal(val)
                
        total_out_for_addr = Decimal(0)
        for o in outputs:
            if o.get("addr", "").lower() == inv_addr_lower:
                val = o.get("value", 0)
                total_out_for_addr += Decimal(val)
                
        direction = TransactionDirection.UNKNOWN
        amount_satoshi = Decimal(0)
        
        if total_in_for_addr > 0 and total_out_for_addr == 0:
            direction = TransactionDirection.OUTGOING
            amount_satoshi = total_in_for_addr
        elif total_in_for_addr == 0 and total_out_for_addr > 0:
            direction = TransactionDirection.INCOMING
            amount_satoshi = total_out_for_addr
        elif total_in_for_addr > 0 and total_out_for_addr > 0:
            if total_in_for_addr > total_out_for_addr:
                direction = TransactionDirection.OUTGOING
                amount_satoshi = total_in_for_addr - total_out_for_addr
            elif total_out_for_addr > total_in_for_addr:
                direction = TransactionDirection.INCOMING
                amount_satoshi = total_out_for_addr - total_in_for_addr
            else:
                direction = TransactionDirection.INTERNAL
                amount_satoshi = total_in_for_addr
        elif total_in_for_addr == 0 and total_out_for_addr == 0:
            direction = TransactionDirection.RELATED
            amount_satoshi = Decimal(0)
            
        # BTC is represented as 1e8 satoshis
        amount_btc = amount_satoshi / Decimal(100_000_000)
        
        timestamp = _parse_timestamp(raw_tx.get("time"))
        
        block_number = raw_tx.get("block_height")
        fee = Decimal(raw_tx.get("fee", 0)) / Decimal(100_000_000) if raw_tx.get("fee") else None

        # BTC transactions represent confirmed state for their inclusion
        # In this limited scope, presence in the blockchain API indicates success
        status = TransactionStatus.SUCCESS 
        
        return NormalizedTransaction(
            blockchain="Bitcoin",
            tx_hash=tx_hash,
            from_address=None, # Ambiguous for BTC
            to_address=None,   # Ambiguous for BTC
            amount=amount_btc,
            asset="BTC",
            timestamp=timestamp,
            direction=direction,
            status=status,
            block_number=block_number,
            fee=fee,
            fee_asset="BTC" if fee else None,
            provider="blockchain.com",
            investigated_address=investigated_address,
            metadata={"inputs": inputs, "outputs": outputs, "raw": raw_tx}
        )
    except Exception as e:
        logger.error(f"Failed to normalize BTC transaction {raw_tx.get('hash')}: {e}")
        return None

def normalize_ethereum_transaction(raw_tx: Dict[str, Any], investigated_address: str) -> Optional[NormalizedTransaction]:
    try:
        tx_hash = raw_tx.get("hash", "")
        if not tx_hash:
            return None
            
        inv_addr_lower = investigated_address.lower()
        from_addr = str(raw_tx.get("from", "")).lower()
        to_addr = str(raw_tx.get("to", "")).lower()
        
        direction = TransactionDirection.UNKNOWN
        if from_addr == inv_addr_lower and to_addr == inv_addr_lower:
            direction = TransactionDirection.INTERNAL
        elif from_addr == inv_addr_lower:
            direction = TransactionDirection.OUTGOING
        elif to_addr == inv_addr_lower:
            direction = TransactionDirection.INCOMING
        else:
            direction = TransactionDirection.RELATED
            
        try:
            val_wei = Decimal(raw_tx.get("value", 0))
        except:
            val_wei = Decimal(0)
            
        amount_eth = val_wei / Decimal(10**18)
        
        timestamp = _parse_timestamp(raw_tx.get("timeStamp"))
        
        status = TransactionStatus.SUCCESS
        if raw_tx.get("isError") == "1":
            status = TransactionStatus.FAILED
            
        block_number = None
        if raw_tx.get("blockNumber"):
            try:
                block_number = int(raw_tx.get("blockNumber"))
            except ValueError:
                pass
                
        return NormalizedTransaction(
            blockchain="Ethereum",
            tx_hash=tx_hash,
            from_address=from_addr,
            to_address=to_addr,
            amount=amount_eth,
            asset="ETH",
            timestamp=timestamp,
            direction=direction,
            status=status,
            block_number=block_number,
            provider="etherscan",
            investigated_address=investigated_address,
            metadata={"raw": raw_tx}
        )
    except Exception as e:
        logger.error(f"Failed to normalize ETH transaction {raw_tx.get('hash')}: {e}")
        return None

def normalize_bsc_transaction(raw_tx: Dict[str, Any], investigated_address: str) -> Optional[NormalizedTransaction]:
    try:
        # Ankr uses 'hash' or 'transactionHash' depending on context
        tx_hash = raw_tx.get("hash") or raw_tx.get("transactionHash", "")
        if not tx_hash:
            return None
            
        inv_addr_lower = investigated_address.lower()
        from_addr = str(raw_tx.get("from", "")).lower()
        to_addr = str(raw_tx.get("to", "")).lower()
        
        direction = TransactionDirection.UNKNOWN
        if from_addr == inv_addr_lower and to_addr == inv_addr_lower:
            direction = TransactionDirection.INTERNAL
        elif from_addr == inv_addr_lower:
            direction = TransactionDirection.OUTGOING
        elif to_addr == inv_addr_lower:
            direction = TransactionDirection.INCOMING
        else:
            direction = TransactionDirection.RELATED
            
        val_str = raw_tx.get("value", "0")
        if isinstance(val_str, str) and val_str.startswith("0x"):
            val_wei = Decimal(int(val_str, 16))
        else:
            try:
                val_wei = Decimal(val_str)
            except:
                val_wei = Decimal(0)
                
        amount_bnb = val_wei / Decimal(10**18)
        
        # Ankr timestamp field could be hex or dec
        ts_val = raw_tx.get("timestamp") or raw_tx.get("timeStamp") or raw_tx.get("time")
        timestamp = _parse_timestamp(ts_val)
        
        status = TransactionStatus.SUCCESS
        status_val = raw_tx.get("status")
        if isinstance(status_val, str):
            if status_val.startswith("0x"):
                if int(status_val, 16) == 0:
                    status = TransactionStatus.FAILED
            elif status_val == "0":
                status = TransactionStatus.FAILED
                
        return NormalizedTransaction(
            blockchain="BNB Smart Chain",
            tx_hash=tx_hash,
            from_address=from_addr,
            to_address=to_addr,
            amount=amount_bnb,
            asset="BNB",
            timestamp=timestamp,
            direction=direction,
            status=status,
            provider="ankr",
            investigated_address=investigated_address,
            metadata={"raw": raw_tx}
        )
    except Exception as e:
        logger.error(f"Failed to normalize BSC transaction {raw_tx.get('hash')}: {e}")
        return None

def normalize_transactions(
    provider: str,
    transactions: List[Dict[str, Any]],
    investigated_address: str,
    blockchain: str
) -> List[NormalizedTransaction]:
    """
    Universal entry point for normalizing a list of raw provider transactions.
    """
    normalized_list = []
    
    for raw_tx in transactions:
        norm_tx = None
        
        if blockchain == "Bitcoin":
            norm_tx = normalize_bitcoin_transaction(raw_tx, investigated_address)
        elif blockchain == "Ethereum":
            norm_tx = normalize_ethereum_transaction(raw_tx, investigated_address)
        elif blockchain == "BNB Smart Chain":
            norm_tx = normalize_bsc_transaction(raw_tx, investigated_address)
        else:
            logger.warning(f"Unsupported blockchain for normalization: {blockchain}")
            
        if norm_tx:
            normalized_list.append(norm_tx)
            
    return normalized_list

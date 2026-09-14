import networkx as nx
import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal

from analysis.models import NormalizedTransaction, TransactionDirection

logger = logging.getLogger(__name__)

def build_graph(
    transactions: List[NormalizedTransaction], 
    direction_filter: Optional[TransactionDirection] = None,
    min_amount: Optional[Decimal] = None
) -> nx.MultiDiGraph:
    """
    Builds a directed multi-graph from normalized transactions.
    Supports filtering prior to graph construction.
    """
    graph = nx.MultiDiGraph()
    
    for tx in transactions:
        # 1. Apply Filters
        if direction_filter and tx.direction != direction_filter and direction_filter != "ALL":
            continue
            
        if min_amount is not None and tx.amount is not None:
            if tx.amount < min_amount:
                continue
                
        # 2. Extract Nodes and Edges
        if tx.blockchain == "Bitcoin":
            # Bitcoin UTXO mapping
            raw = tx.metadata.get("raw", {})
            inputs = raw.get("inputs", [])
            outputs = raw.get("out", [])
            
            # Gather all input addresses
            in_addrs = []
            for i in inputs:
                addr = i.get("prev_out", {}).get("addr")
                if addr:
                    in_addrs.append(addr)
                    
            # Gather all output addresses
            out_addrs = []
            for o in outputs:
                addr = o.get("addr")
                if addr:
                    out_addrs.append(addr)
                    
            # Create a full bipartite mapping for the UTXO candidate flow
            for src in set(in_addrs):
                graph.add_node(src, blockchain="Bitcoin")
                for dst in set(out_addrs):
                    graph.add_node(dst, blockchain="Bitcoin")
                    
                    graph.add_edge(
                        src, dst, 
                        key=tx.tx_hash,
                        tx_hash=tx.tx_hash,
                        amount=tx.amount, # Overall normalized amount
                        asset=tx.asset,
                        timestamp=tx.timestamp,
                        direction=tx.direction.value if tx.direction else "UNKNOWN",
                        status=tx.status.value if tx.status else "UNKNOWN",
                        blockchain=tx.blockchain,
                        provider=tx.provider,
                        metadata=tx.metadata
                    )
        else:
            # EVM mapping (Ethereum, BSC)
            src = tx.from_address
            dst = tx.to_address
            
            if not src or not dst:
                continue
                
            graph.add_node(src, blockchain=tx.blockchain)
            graph.add_node(dst, blockchain=tx.blockchain)
            
            graph.add_edge(
                src, dst,
                key=tx.tx_hash,
                tx_hash=tx.tx_hash,
                amount=tx.amount,
                asset=tx.asset,
                timestamp=tx.timestamp,
                direction=tx.direction.value if tx.direction else "UNKNOWN",
                status=tx.status.value if tx.status else "UNKNOWN",
                blockchain=tx.blockchain,
                provider=tx.provider,
                metadata=tx.metadata
            )
            
    return graph

import networkx as nx
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

@dataclass
class TraceResult:
    source: str
    target: str
    found: bool
    hops: int = 0
    candidate_paths: List[List[Dict[str, Any]]] = field(default_factory=list) # List of paths, where a path is a list of edge attributes
    shortest_path_edges: List[Dict[str, Any]] = field(default_factory=list)
    message: str = ""

def trace_path(
    graph: nx.MultiDiGraph, 
    source: str, 
    target: str, 
    max_hops: int = 5, 
    max_paths: int = 10
) -> TraceResult:
    """
    Traces paths between source and target in the MultiDiGraph.
    Returns edge-resolved paths (handling multiple edges between nodes safely).
    """
    if not graph.has_node(source):
        return TraceResult(source, target, False, message="Source node not found in graph.")
        
    if not graph.has_node(target):
        return TraceResult(source, target, False, message="Target node not found in graph.")
        
    if source == target:
        return TraceResult(source, target, True, hops=0, message="Source and target are the same.")

    try:
        # Use simple edge paths to resolve exact transactions in the MultiDiGraph
        paths_generator = nx.all_simple_edge_paths(graph, source, target, cutoff=max_hops)
        
        candidate_paths = []
        shortest_path = None
        min_hops = float('inf')
        
        for path_edges in paths_generator:
            if len(candidate_paths) >= max_paths:
                break
                
            resolved_path = []
            for u, v, k in path_edges:
                edge_data = graph.get_edge_data(u, v, key=k).copy()
                edge_data["_u"] = u
                edge_data["_v"] = v
                resolved_path.append(edge_data)
                
            candidate_paths.append(resolved_path)
            
            if len(resolved_path) < min_hops:
                min_hops = len(resolved_path)
                shortest_path = resolved_path
                
        if not candidate_paths:
            return TraceResult(source, target, False, message="No path found between the selected addresses in the loaded transaction graph.")
            
        return TraceResult(
            source=source,
            target=target,
            found=True,
            hops=min_hops,
            candidate_paths=candidate_paths,
            shortest_path_edges=shortest_path,
            message=f"Found {len(candidate_paths)} candidate path(s)."
        )
    except nx.NetworkXNoPath:
        return TraceResult(source, target, False, message="No path found.")
    except Exception as e:
        logger.error(f"Error during trace: {e}")
        return TraceResult(source, target, False, message=f"Trace error: {e}")

import pytest
from decimal import Decimal
from analysis.models import NormalizedTransaction, TransactionDirection, TransactionStatus
from analysis.graph_engine import build_graph
from analysis.tracing_engine import trace_path

def create_mock_tx(hash, frm, to, amt, blockchain="Ethereum"):
    return NormalizedTransaction(
        blockchain=blockchain,
        tx_hash=hash,
        from_address=frm,
        to_address=to,
        amount=Decimal(amt),
        asset="ETH",
        timestamp=None,
        direction=TransactionDirection.OUTGOING,
        status=TransactionStatus.SUCCESS
    )

def test_build_ethereum_graph():
    txs = [
        create_mock_tx("h1", "A", "B", "1.0"),
        create_mock_tx("h2", "B", "C", "2.0")
    ]
    graph = build_graph(txs)
    
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert graph.has_edge("A", "B")
    assert graph.has_edge("B", "C")
    
    edge_data = graph.get_edge_data("A", "B", key="h1")
    assert edge_data["amount"] == Decimal("1.0")

def test_build_bitcoin_graph():
    raw_btc = {
        "inputs": [{"prev_out": {"addr": "in1"}}, {"prev_out": {"addr": "in2"}}],
        "out": [{"addr": "out1"}, {"addr": "out2"}]
    }
    tx = NormalizedTransaction(
        blockchain="Bitcoin",
        tx_hash="btc_hash",
        from_address=None,
        to_address=None,
        amount=Decimal("5.0"),
        asset="BTC",
        direction=TransactionDirection.UNKNOWN,
        status=TransactionStatus.SUCCESS,
        timestamp=None,
        metadata={"raw": raw_btc}
    )
    
    graph = build_graph([tx])
    
    # 2 inputs, 2 outputs -> 4 edges
    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 4
    assert graph.has_edge("in1", "out1")
    assert graph.has_edge("in2", "out2")

def test_tracing_engine_simple_path():
    txs = [
        create_mock_tx("h1", "A", "B", "1.0"),
        create_mock_tx("h2", "B", "C", "2.0")
    ]
    graph = build_graph(txs)
    
    res = trace_path(graph, "A", "C")
    assert res.found
    assert res.hops == 2
    assert len(res.candidate_paths) == 1
    assert res.shortest_path_edges[0]["tx_hash"] == "h1"
    assert res.shortest_path_edges[1]["tx_hash"] == "h2"

def test_tracing_engine_multiple_edges():
    txs = [
        create_mock_tx("h1", "A", "B", "1.0"),
        create_mock_tx("h2", "A", "B", "2.0"),
        create_mock_tx("h3", "B", "C", "3.0")
    ]
    graph = build_graph(txs)
    
    res = trace_path(graph, "A", "C")
    assert res.found
    # Since A->B has two edges, there should be two candidate paths to C.
    assert len(res.candidate_paths) == 2

def test_tracing_engine_max_hops():
    txs = [
        create_mock_tx("h1", "A", "B", "1.0"),
        create_mock_tx("h2", "B", "C", "2.0"),
        create_mock_tx("h3", "C", "D", "3.0")
    ]
    graph = build_graph(txs)
    
    res = trace_path(graph, "A", "D", max_hops=2)
    assert not res.found
    assert "No path found" in res.message

def test_tracing_engine_cycles():
    txs = [
        create_mock_tx("h1", "A", "B", "1.0"),
        create_mock_tx("h2", "B", "C", "2.0"),
        create_mock_tx("h3", "C", "A", "3.0")
    ]
    graph = build_graph(txs)
    
    # Trace from A to C. Path is A->B->C. Cycle A->B->C->A shouldn't break simple paths algorithm
    res = trace_path(graph, "A", "C", max_hops=5)
    assert res.found
    assert len(res.candidate_paths) == 1

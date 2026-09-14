import pytest
from decimal import Decimal
from datetime import datetime, timezone
from analysis.models import TransactionDirection, TransactionStatus
from analysis.transaction_normalizer import (
    normalize_bitcoin_transaction,
    normalize_ethereum_transaction,
    normalize_bsc_transaction,
    normalize_transactions
)

# BITCOIN TESTS
def test_bitcoin_normalization_incoming():
    raw_tx = {
        "hash": "btc_hash_1",
        "time": 1789158719,
        "fee": 1000,
        "inputs": [{"prev_out": {"addr": "other_guy", "value": 100000000}}],
        "out": [{"addr": "my_wallet", "value": 99999000}]
    }
    
    norm = normalize_bitcoin_transaction(raw_tx, "my_wallet")
    assert norm is not None
    assert norm.blockchain == "Bitcoin"
    assert norm.tx_hash == "btc_hash_1"
    assert norm.direction == TransactionDirection.INCOMING
    assert norm.amount == Decimal("0.99999")
    assert norm.asset == "BTC"
    assert norm.fee == Decimal("0.00001")
    assert norm.timestamp == datetime.fromtimestamp(1789158719, tz=timezone.utc)
    
def test_bitcoin_normalization_outgoing_with_change():
    raw_tx = {
        "hash": "btc_hash_2",
        "inputs": [
            {"prev_out": {"addr": "my_wallet", "value": 200000000}} # 2 BTC
        ],
        "out": [
            {"addr": "receiver", "value": 150000000}, # 1.5 BTC
            {"addr": "my_wallet", "value": 49000000}  # 0.49 BTC change
        ]
    }
    
    norm = normalize_bitcoin_transaction(raw_tx, "my_wallet")
    assert norm.direction == TransactionDirection.OUTGOING
    # Spent 2.0, received 0.49 back. Net sent = 1.51 BTC.
    assert norm.amount == Decimal("1.51")
    assert norm.status == TransactionStatus.SUCCESS
    
def test_bitcoin_normalization_internal():
    raw_tx = {
        "hash": "btc_hash_3",
        "inputs": [{"prev_out": {"addr": "my_wallet", "value": 100000}}],
        "out": [{"addr": "my_wallet", "value": 100000}]
    }
    norm = normalize_bitcoin_transaction(raw_tx, "my_wallet")
    assert norm.direction == TransactionDirection.INTERNAL
    assert norm.amount == Decimal("0.001")

def test_bitcoin_normalization_missing_hash():
    raw_tx = {"inputs": []}
    assert normalize_bitcoin_transaction(raw_tx, "my_wallet") is None

# ETHEREUM TESTS
def test_ethereum_normalization_incoming():
    raw_tx = {
        "hash": "eth_hash_1",
        "from": "0xSender",
        "to": "0xMyWallet",
        "value": "1500000000000000000", # 1.5 ETH
        "timeStamp": "1789158719",
        "isError": "0"
    }
    norm = normalize_ethereum_transaction(raw_tx, "0xMyWallet")
    assert norm is not None
    assert norm.direction == TransactionDirection.INCOMING
    assert norm.amount == Decimal("1.5")
    assert norm.asset == "ETH"
    assert norm.status == TransactionStatus.SUCCESS

def test_ethereum_normalization_failed():
    raw_tx = {
        "hash": "eth_hash_2",
        "from": "0xMyWallet",
        "to": "0xReceiver",
        "value": "0",
        "isError": "1"
    }
    norm = normalize_ethereum_transaction(raw_tx, "0xMyWallet")
    assert norm.direction == TransactionDirection.OUTGOING
    assert norm.status == TransactionStatus.FAILED
    assert norm.amount == Decimal(0)

def test_ethereum_missing_optional_fields():
    raw_tx = {"hash": "eth_hash_3"}
    norm = normalize_ethereum_transaction(raw_tx, "0xMyWallet")
    assert norm is not None
    assert norm.timestamp is None
    assert norm.amount == Decimal(0)
    assert norm.direction == TransactionDirection.RELATED

# BSC TESTS
def test_bsc_normalization_hex_values():
    raw_tx = {
        "hash": "bsc_hash_1",
        "from": "0xMyWallet",
        "to": "0xReceiver",
        "value": "0xde0b6b3a7640000", # 1 ETH/BNB in wei
        "timestamp": "0x6a9b203e", # hex timestamp
        "status": "0x1"
    }
    norm = normalize_bsc_transaction(raw_tx, "0xmywallet")
    assert norm.blockchain == "BNB Smart Chain"
    assert norm.amount == Decimal("1.0")
    assert norm.asset == "BNB"
    assert norm.direction == TransactionDirection.OUTGOING
    assert norm.status == TransactionStatus.SUCCESS
    assert norm.timestamp is not None
    
def test_bsc_normalization_failed_hex():
    raw_tx = {
        "hash": "bsc_hash_2",
        "value": "0",
        "status": "0x0"
    }
    norm = normalize_bsc_transaction(raw_tx, "0xmywallet")
    assert norm.status == TransactionStatus.FAILED

# UNIVERSAL ROUTER
def test_universal_normalizer():
    txs = [
        {"hash": "h1", "time": 123},
        {"no_hash_here": True} # Should be skipped
    ]
    results = normalize_transactions("blockchain.com", txs, "addr", "Bitcoin")
    assert len(results) == 1
    assert results[0].provider == "blockchain.com"

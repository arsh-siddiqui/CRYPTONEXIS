# API Plan: Cryptonexis

## 1. Bitcoin API Integration
- **Primary Source**: Blockchain.com (Explorer API)
- **Expected Purpose**: Retrieve BTC wallet balances, unspent outputs (UTXOs), and historical transaction data.
- **Authentication**: `BLOCKCHAIN_API_KEY` (Conditional/Optional, depending on specific endpoint tier requirements).
- **Data Retrieval**: Address activity, Tx inputs/outputs.
- **Rate Limit Considerations**: The free tier has strict rate limits. Implement exponential backoff and caching.
- **Abstraction**: `services/bitcoin_service.py`

## 2. Ethereum API Integration
- **Primary Source**: Etherscan API V2
- **Expected Purpose**: Retrieve ETH wallet balances, normal transactions, internal transactions, and ERC-20 token transfers.
- **Authentication**: `ETHERSCAN_API_KEY` (Required).
- **Data Retrieval**: Action-oriented block ranges for address histories.
- **Rate Limit Considerations**: Standard free tier is ~5 calls/sec. Service layer must enqueue requests or sleep appropriately.
- **Abstraction**: `services/ethereum_service.py`

## 3. BNB Smart Chain API Integration
- **Primary Source**: BscScan API
- **Expected Purpose**: Retrieve BSC wallet balances, standard transactions, and BEP-20 token transfers.
- **Authentication**: `BSCSCAN_API_KEY` (Required).
- **Data Retrieval**: Address histories, similar schema to Etherscan.
- **Rate Limit Considerations**: Similar to Etherscan; ~5 calls/sec.
- **Abstraction**: `services/bsc_service.py`

## Threat Intelligence (Reputation) Integrations
- **Potential Sources**: AMLBot, CryptoScamDB, Chainabuse
- **Authentication**: Handled dynamically based on which modules are activated by the user. Keys stored in `.env`.
- **Abstraction**: `services/reputation_service.py`

## Abstraction Strategy
All external API calls must be wrapped in `try-except` blocks handling `requests.exceptions.RequestException`. 
The services must return either the raw data payload or standard Error dictionary objects. They must never crash the main application. 
The application must respect the `DATA_MODE=demo` environment variable, returning mock responses if Live mode is disabled.

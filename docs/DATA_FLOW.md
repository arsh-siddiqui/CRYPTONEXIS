# Data Flow: Cryptonexis

The following represents the lifecycle of a target wallet investigation.

```mermaid
flowchart TD
    A[Wallet Input via GUI] --> B{Cryptocurrency Type Detector}
    
    B -->|Valid BTC| C1[Blockchain.com API Service]
    B -->|Valid ETH| C2[Etherscan API Service]
    B -->|Valid BSC| C3[BscScan API Service]
    B -->|Ambiguous EVM| C_USER[Prompt User for Network Selection]
    C_USER --> C2
    C_USER --> C3
    
    C1 --> D[Transaction Normalization Layer]
    C2 --> D
    C3 --> D
    
    D --> E[Analysis Engine / Cache in SQLite]
    
    E --> F[Graph / Tracing Engine]
    E --> G[Reputation / Threat Intel Service]
    
    G --> H[Risk Engine]
    F --> H
    
    H --> I[Investigation Dashboard / GUI]
    
    I --> J[Report Generator]
    
    subgraph Monitoring Cycle
        M1[Add Wallet to Watchlist] --> M2[Monitoring Service Polling]
        M2 --> M3{New Activity?}
        M3 -- Yes --> M4[Alert Generation]
        M4 --> M5[Update Dashboard]
    end
```

## Flow Description
1. **Input**: User enters a wallet address.
2. **Detection**: `crypto_detector.py` validates format. If ambiguous (e.g., `0x`), GUI asks the user to clarify ETH vs BSC.
3. **Retrieval**: Service layer fetches data from the respective block explorer API.
4. **Normalization**: `transaction_parser.py` maps the network-specific JSON into a standard dictionary.
5. **Storage/Analysis**: Transactions are evaluated for volume/velocity and saved to the Case database.
6. **Correlation**: 
   - `graph_engine.py` builds the multi-hop visualization.
   - `reputation_service.py` checks intelligence feeds for associated tags.
7. **Risk Scoring**: `risk_engine.py` consumes all findings to produce a defined risk assessment score.
8. **Presentation & Reporting**: Results are shown in the GUI and can be exported as a comprehensive report.
9. **Monitoring**: If flagged for monitoring, the background service periodically queries the API for delta changes, generating alerts upon new blocks/transactions.

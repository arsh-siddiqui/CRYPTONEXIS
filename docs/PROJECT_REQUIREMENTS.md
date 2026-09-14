# Project Requirements: Cryptonexis

## Full Project Title
Cryptonexis: Blockchain OSINT & Cryptocurrency Forensic Intelligence Platform

## Tagline
"Trace. Correlate. Investigate."

## Project Purpose
To provide investigators and analysts with a unified, robust, and extensible platform for cryptocurrency tracking, risk analysis, and forensic intelligence. 

## Problem Statement
Cryptocurrency investigations currently require analysts to manually traverse block explorers, copy-paste addresses into disjointed threat intelligence feeds, and visually construct graphs using external tools. This fragmented workflow is error-prone, time-consuming, and difficult to document for evidentiary purposes.

## Proposed Solution
Cryptonexis is a unified desktop platform that automates blockchain data retrieval, normalizes transaction data across multiple networks, integrates threat intelligence and reputation scoring, visualizes transaction graphs, and generates comprehensive investigation reports. 

## Target Users
- Law Enforcement and Forensics Investigators
- Cybersecurity Analysts
- Anti-Money Laundering (AML) Compliance Officers
- Private Intelligence Analysts
- Blockchain Researchers

## Objectives
- Unify multi-blockchain investigations into a single interface.
- Automate multi-hop transaction tracing and visualization.
- Correlate blockchain data with external OSINT and threat intelligence.
- Provide a persistent case-management and reporting system.
- Ensure data integrity by clearly distinguishing raw facts from heuristic risk indicators.

## Mandatory Video Enhancements (Scope)
1. **Proper Tool GUI with all options**
2. **Wallet Address Tracker**
   - Bitcoin wallet tracking
   - Ethereum wallet tracking
   - BNB Smart Chain wallet tracking
3. **Cryptocurrency Type Detector**
4. **Address Reputation Checker**
   - ransomware/scam/threat reputation
   - integration design for sources such as AMLBot, CryptoScamDB, Chainabuse or other authorized intelligence sources
5. **Transaction Visualization Dashboard**
   - wallet nodes
   - transaction edges
   - transaction amounts
   - transaction direction
   - multi-hop transaction tracing
   - path highlighting
6. **Alert System for New Transactions**
   - monitored wallets
   - new transaction detection
   - alert generation
   - alert history

## Supporting Features
- Blockchain OSINT investigation
- Wallet validation
- Transaction retrieval and normalization
- Incoming/outgoing analysis
- Related wallet/address analysis
- Transaction graph construction
- Ransomware intelligence correlation
- Risk analysis and heuristic scoring
- Investigation case management
- Monitoring and configurable alerts
- Investigation reporting and export (JSON, PDF, CSV)
- External blockchain explorer linking

## Live vs Demo Mode
The application must support two conceptual modes:
1. **LIVE MODE**: Interacts with real blockchain APIs and configured intelligence sources to fetch live operational data.
2. **DEMO MODE**: Uses safe, synthetic, or sample transaction data for demonstrations, training, and testing without hitting real APIs. Demo data must never be represented as real blockchain evidence.

## Functional Requirements
- **Validation**: System must accurately identify BTC, ETH, and BSC address formats and support explicit network selection for ambiguous EVM addresses.
- **Normalization**: System must ingest varying API responses and map them to a common transaction model.
- **Tracing**: System must trace funds across configurable multi-hop paths.
- **Alerting**: System must monitor specified addresses and trigger internal alerts upon new transactions.
- **Reporting**: System must compile findings into an exportable summary report.

## Non-Functional Requirements
- **Architecture**: Must use a modular, multi-layered architecture (GUI, Services, Analysis, etc.). No monolithic scripts.
- **Storage**: Must utilize local SQLite for case and configuration data.
- **Security**: Must handle API keys securely via environment variables (`.env`). Keys must never be hardcoded.
- **Extensibility**: Threat intelligence and blockchain services must be pluggable.

## Limitations
- Do not claim actual dark-web crawling unless a legitimate integrated source provides it.
- Heuristic risk scores must be explicitly labeled as "Application-generated investigative risk score" and not legal determinations.
- Permanent hardcoded ransomware dictionaries should only be used as stand-ins during demo mode testing, not as the final live architecture.

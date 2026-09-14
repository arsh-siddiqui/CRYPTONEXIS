# Module Specification: Cryptonexis

## Core Modules

### `app.py`
- **Responsibility**: Entry point of the application. Bootstraps the database, loads environment variables, configures logging, and launches the root GUI window.
- **Dependencies**: `dotenv`, GUI modules, DB initialization.

---

## GUI Modules (`gui/`)

### `dashboard.py`
- **Responsibility**: Main landing screen showing active cases, recent alerts, and quick actions.
- **Dependencies**: Controller layer, `ttkbootstrap`.

### `investigation.py`
- **Responsibility**: Interface for creating/loading cases, entering target addresses, and displaying aggregated findings.

### `transactions.py`
- **Responsibility**: Displays tabular views of transaction histories, filterable by direction, amount, and date.

### `graph_view.py`
- **Responsibility**: Embeds a `Matplotlib` canvas to render `NetworkX` graphs representing transaction hops.

### `reputation.py`
- **Responsibility**: Interface for displaying OSINT, ransomware associations, and threat intelligence matches.

### `alerts.py`
- **Responsibility**: UI for configuring monitored addresses and viewing historical notifications.

### `reports.py`
- **Responsibility**: UI for configuring and triggering report generation (PDF, CSV, JSON).

---

## Service Modules (`services/`)

### `bitcoin_service.py`
- **Responsibility**: Interacts with Blockchain.com API. Retrieves UTXOs, histories, and balances.
- **Input**: BTC Address.
- **Output**: Raw JSON API response.
- **Dependencies**: `requests`.

### `ethereum_service.py`
- **Responsibility**: Interacts with Etherscan API V2. Retrieves internal and normal transactions.
- **Input**: ETH Address.
- **Output**: Raw JSON API response.

### `bsc_service.py`
- **Responsibility**: Interacts with BscScan API.
- **Input**: BSC Address.
- **Output**: Raw JSON API response.

### `reputation_service.py`
- **Responsibility**: Calls configured external threat feeds (e.g., CryptoScamDB).
- **Input**: Normalized Address.
- **Output**: Threat indicators, confidence scores.

### `monitoring_service.py`
- **Responsibility**: Background task/polling loop that checks watched addresses for new transactions.
- **Dependencies**: Blockchain services, Alert database layer.

---

## Analysis Modules (`analysis/`)

### `crypto_detector.py`
- **Responsibility**: Uses RegEx and checksum logic to validate addresses and determine probable networks. Returns ambiguity flags for overlapping formats (e.g., EVM `0x`).
- **Input**: Raw address string.
- **Output**: List of possible blockchain networks.

### `transaction_parser.py`
- **Responsibility**: Normalizes raw JSON from various `services/` into the unified Transaction schema.
- **Input**: Raw API JSON, network identifier.
- **Output**: Standardized Dictionary/Object.

### `graph_engine.py`
- **Responsibility**: Constructs and mutates `NetworkX` graphs.
- **Input**: List of normalized transactions.
- **Output**: `NetworkX` DiGraph object.

### `tracing_engine.py`
- **Responsibility**: Executes pathfinding and multi-hop tracing queries on the graph.
- **Input**: Graph, Source Node, Target Node, Max Hops.
- **Output**: List of paths.

### `risk_engine.py`
- **Responsibility**: Combines heuristics and reputation flags to generate a risk score.
- **Input**: Wallet data, tracing results, reputation results.
- **Output**: Risk score (0-100) and list of risk factors.

---

## Data & Database (`data/` & `database/`)
- **Responsibility**: Manage static assets (demo datasets, local mock threat intelligence) and the SQLite schema abstractions / ORM logic.

## Reports (`reports/`)
- **Responsibility**: Export logic (PDF builders, CSV dumpers).

## Utils (`utils/`)
- **Responsibility**: Shared helpers (time formatters, logging setup, safe dictionary access).

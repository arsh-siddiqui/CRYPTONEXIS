# Database Plan: Cryptonexis

Cryptonexis uses SQLite for lightweight, reliable, local data persistence.

## Conceptual Schema

### `Cases`
- `id` (PK)
- `case_name`
- `investigator_name`
- `created_at`
- `updated_at`
- `status` (Open, Closed, Archived)
- `risk_assessment_summary`

### `Wallets`
- `address` (PK)
- `blockchain_network` (BTC, ETH, BSC)
- `first_seen_tx`
- `last_seen_tx`
- `total_received`
- `total_sent`

### `Transactions`
- `tx_hash` (PK)
- `blockchain_network`
- `from_address` (FK -> Wallets.address)
- `to_address` (FK -> Wallets.address)
- `amount`
- `asset`
- `timestamp`
- `confirmations`
- `raw_metadata` (JSON blob)

### `Case_Transactions` (Mapping)
- `case_id` (FK -> Cases.id)
- `tx_hash` (FK -> Transactions.tx_hash)

### `Reputation_Findings`
- `id` (PK)
- `wallet_address` (FK -> Wallets.address)
- `source` (e.g., CryptoScamDB, RansomwareList)
- `category` (Scam, Ransomware, High-Risk Exchange)
- `confidence_score`
- `finding_date`

### `Monitored_Wallets`
- `id` (PK)
- `wallet_address` (FK -> Wallets.address)
- `blockchain_network`
- `last_checked_timestamp`
- `last_known_block`
- `is_active` (Boolean)

### `Alerts`
- `id` (PK)
- `monitored_wallet_id` (FK -> Monitored_Wallets.id)
- `alert_type` (New Transaction, High Value Transfer)
- `severity` (Low, Medium, High)
- `message`
- `timestamp`
- `is_read` (Boolean)

### `Reports`
- `id` (PK)
- `case_id` (FK -> Cases.id)
- `file_path`
- `generated_at`
- `format` (PDF, CSV, JSON)

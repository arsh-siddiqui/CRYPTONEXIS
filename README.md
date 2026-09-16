# CRYPTONEXIS

Cryptonexis: Blockchain OSINT & Cryptocurrency Forensic Intelligence Platform

**Trace. Correlate. Investigate.**

## Purpose
To provide investigators and analysts with a unified, robust, and extensible platform for cryptocurrency tracking, risk analysis, and forensic intelligence.

## Current Phase
**Phase 9: Real-Time Wallet Monitoring & Alerts**
*(Note: Cryptonexis now supports persistent tracking of address activity, evaluating incoming/outgoing transfers against internal baseline histories. Alerts safely run through staggered background daemons to avoid freezing the GUI or blowing through rate limits.)*

## Architecture Summary
Cryptonexis uses a modular architecture separating the GUI from external APIs, normalization, analysis, and storage logic. The system uses local SQLite for database storage and an external `.env` file for configuration.

## Technology Stack
- **Language**: Python
- **GUI**: Tkinter + ttkbootstrap
- **API Requests**: requests
- **Graph Processing**: NetworkX
- **Visualization**: Matplotlib
- **Database**: SQLite
- **Configuration**: python-dotenv

## Setup Instructions

1. **Clone the repository**
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configuration**:
   Copy `.env.example` to `.env` and fill in the placeholders if you are preparing for future phases.

## How to Run the Application
```bash
python app.py
```

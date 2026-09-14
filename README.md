# CRYPTONEXIS

Cryptonexis: Blockchain OSINT & Cryptocurrency Forensic Intelligence Platform

**Trace. Correlate. Investigate.**

## Purpose
To provide investigators and analysts with a unified, robust, and extensible platform for cryptocurrency tracking, risk analysis, and forensic intelligence.

## Current Phase
**Phase 8: OSINT Correlation & Risk Analysis**
*(Note: Cryptonexis now aggregates findings across graph metrics, reputation, and OSINT into a unified, clamped risk score (0-100) governed by v1.0 methodology. All factors are transparently documented as non-criminal investigative indicators rather than legal classifications.)*

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

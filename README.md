# KSRTC Kalaburagi Division — BusPulse Analytics Platform

> **Hackathon PS-3**: Electronic Ticketing Machine (ETM) Analytics, Shakti Scheme Subsidy Audit, and Predictive Bus Transit Intelligence.

---

## 🚌 1. Project Overview

**BusPulse** is a specialized analytics, statistics, and predictive intelligence platform designed for **Karnataka State Road Transport Corporation (KSRTC / KKRTC) — Kalaburagi Division**.

It processes 19,275+ daily electronic ticketing machine (ETM) transactions across 47 active division buses to provide:
1. **Real-time Operational Intelligence**: Peak commuter surge tracking, corridor ridership, and bus fleet load factor.
2. **Karnataka Shakti Scheme Audit Ledger**: Transparent accounting separating cash collections from Government of Karnataka free travel subsidy reimbursables (preventing false alerts of conductor fraud).
3. **AI Predictive Fleet Optimization**: 24-hour demand forecasting with 95% confidence intervals and an interactive "What-If" policy simulator.
4. **Interactive GIS Network Drawer**: Leaflet.js CartoDB interactive map rendering Kalaburagi's 12 major transit terminals and top passenger corridors.

---

## 🏛️ 2. Architecture & Program Structure

```
KSRTC_Bus_Analytics/
│
├── frontend/                     # Pure HTML5 + CSS + Modern JS Dashboard
│   ├── index.html                # Operations Overview & Division KPIs
│   ├── buses.html                # 47-Bus Fleet Statistics & Waybill Performance
│   ├── passengers.html           # Passenger Demographics & Peak Hour Trends
│   ├── routes.html               # Corridor Analysis & Directional Imbalance
│   ├── alerts.html               # Operational Alerts & Fleet Deficits
│   ├── reports.html              # Filterable Ledger & CSV/Print Reports
│   ├── revenue.html              # Fare Reconciliation & Shakti Subsidy
│   ├── ai-analytics.html         # AI Demand Forecast & What-If Simulator
│   ├── styles.css                # Polished design system (Dark sidebar, Purple accent)
│   └── js/
│       ├── common.js             # Shared Leaflet GIS map, universal search, drawer
│       ├── api.js                # Hybrid API client (Live Flask ⇄ Offline fallback)
│       └── charts.js             # Chart.js reusable configuration presets
│
├── backend/                      # Python Flask + Pandas Analytical Engine
│   ├── app.py                    # REST API entry point with CORS & static server
│   ├── data_loader.py            # Singleton loader (auto-ingests Excel or JSON)
│   ├── data_cleaner.py           # Stop normalization & Shakti Scheme classifier
│   ├── analytics/
│   │   ├── demand.py             # Hourly ridership curves & peak hour detection
│   │   ├── stops.py              # Hub rankings & GIS coordinates
│   │   ├── movement.py           # OD matrix & top corridors
│   │   ├── fleet.py              # 47-bus fleet metrics & load badges
│   │   ├── revenue.py            # Cash vs. Shakti state subsidy reconciliation
│   │   └── predictions.py        # 24-hour forecast & What-If simulator engine
│   └── services/
│       ├── filters.py            # Slicing by time window, corridor, bus ID
│       └── alerts.py             # Diagnostic triggers (overcrowding, deficits)
│
├── data/
│   ├── raw/                      # Ingests Dataset.xlsx and data_sql (12).json
│   └── processed/                # Instant-load binary cache (tickets.pkl)
│
├── tests/
│   └── test_api.py               # Unit tests verifying all API endpoints
├── requirements.txt              # Minimal Python dependencies
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ 3. Quickstart & Installation

### A. Prerequisites
- Python 3.10+
- Modern Web Browser (Chrome, Edge, Firefox)

### B. Setup Python Backend
```bash
# 1. Navigate to project root
cd KSRTC_Bus_Analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run unit tests
python tests/test_api.py

# 4. Start the backend API server
python backend/app.py
```
The server will warm up the ticket cache in memory (<1 sec) and start at:
👉 **`http://127.0.0.1:5000`**

### C. Open the Dashboard
- **Option 1 (Via Flask Server)**: Open `http://127.0.0.1:5000` in your browser.
- **Option 2 (Standalone `file://`)**: Double-click `frontend/index.html`.  
  *(Thanks to `frontend/js/api.js` hybrid mode, the dashboard automatically detects if Python is running and gracefully switches between live REST API data and instant offline snapshot!)*

---

## 📡 4. REST API Documentation

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/health` | `GET` | Service status and records count (19,275 rows) |
| `/api/v1/data/upload` | `POST` | Upload & re-analyze new ETM dataset (.xlsx, .csv, .json) |
| `/api/v1/kpi/summary` | `GET` | Top-level division KPIs (passengers, cash, subsidy, fleet) |
| `/api/v1/analytics/hourly` | `GET` | 24-hour passenger curve, trips, and peak hour windows |
| `/api/v1/analytics/routes` | `GET` | High-frequency corridors (Budhavihar ↔ CBS, etc.) |
| `/api/v1/analytics/stops` | `GET` | Stop boardings and GeoJSON coordinates for GIS map |
| `/api/v1/analytics/buses` | `GET` | 47-bus fleet & Conductor Shift duty performance |
| `/api/v1/analytics/revenue` | `GET` | Cash collections vs. Karnataka Shakti Subsidy claim |
| `/api/v1/analytics/alerts` | `GET` | Active diagnostic alerts (overcrowding, maintenance) |
| `/api/v1/ai/forecast` | `GET` | Tomorrow's demand forecast with 95% confidence bands |
| `/api/v1/ai/simulate` | `POST` | What-If Simulator (`{"growth_pct": 10, "shakti_pct": 80}`) |

---

## 💡 5. Key Domain Insights for Judges

1. **The ₹2,90,929 Shakti Scheme Insight**:  
   Raw ticket datasets often show zero-collected fare rows (`Coll Amt: 0`, `Uncoll Amt > 0`). In typical corporate dashboards, this is mistakenly flagged as conductor theft. **BusPulse correctly identifies this as the Government of Karnataka's flagship Shakti Scheme** (free bus travel for women residents), generating a reimbursable audit claim for the Department of Transport.
2. **Kalaburagi Corridors**:  
   Top urban links include **Budhavihar ↔ Central Bus Stand (CBS)** (1,525 daily pax) and **CBS ↔ Supermarket** (1,029 daily pax), experiencing severe peak-hour overcrowding (load factor >115%) requiring short-loop mini-bus insertion.
3. **Operational Conductor Shift Tracking**:  
   In KSRTC / KKRTC operations, each electronic ticketing machine (ETM) issue cycle is bounded by a **Waybill Number** assigned to a specific conductor's duty shift. BusPulse evaluates all 47 conductor shifts to identify high-turnover duty cycles and fare collection efficiency while safeguarding staff privacy.

---

## 🛡️ 6. Data Protection, Privacy & PII Compliance Audit

In compliance with **Rule 5 of the Solvathon Problem Statement** (*"Protect any personal or sensitive information in the dataset"*):
* **Zero PII Surface**: An audit of all 19,275 records confirms that no passenger names, phone numbers, addresses, or payment card details are stored or logged.
* **Privacy by Aggregation**: All operational metrics and conductor performance statistics are grouped strictly by anonymous machine waybill IDs (`Waybill Number`) rather than personal employee records.
* **Standards Alignment**: Fully compliant with the Digital Personal Data Protection (DPDP) Act and KSRTC enterprise data handling principles.



# KSRTC BusPulse — Hackathon Judge Demo & Presentation Script

> **Solvathon 2026 — Problem Statement 3**: Bus Ticket Data Analytics & Intelligent Dashboard  
> **Platform**: BusPulse Analytics Platform (KKRTC / Kalaburagi Division)

---

## ⏱️ 3-Minute Winning Demo Flow

### 0:00 – 0:45 | The Hook & Domain Insight (The Shakti Scheme)
* **Open**: `http://127.0.0.1:5000/index.html` (or `revenue.html`)
* **Show**: Top-left featured KPI card: **₹2,90,929 Shakti Subsidy Claim (75.3%)**
* **The Pitch**:
  > *"Judges, when looking at raw electronic ticketing machine (ETM) logs, 75% of rows showed ₹0 cash collected. Traditional algorithms mistakenly flag this as massive conductor theft. BusPulse understands the actual Karnataka domain: this is the Government of Karnataka's flagship **Shakti Scheme** for free women travel. We transformed raw uncollected amounts into an **audited, state-reimbursable Form 4B subsidy claim**, protecting conductors while recovering ₹2.90 lakh in single-day divisional revenue."*

---

### 0:45 – 1:30 | Operational Network & GIS Route Mapping
* **Open**: `http://127.0.0.1:5000/routes.html`
* **Show**: The **Interactive GIS Corridor Network** (OpenStreetMap Leaflet Engine)
* **The Pitch**:
  > *"Instead of simple straight lines cutting across houses, our GIS engine snaps bus corridors along Kalaburagi's actual arterial road network—the Sedam–Humnabad Outer Ring Road, Station Road, and State Highway 10. You can see the heavy Budhavihar ↔ CBS corridor carrying 1,525 daily commuters at 118% peak load factor."*
* **Interactive Action**:
  * Click the **[Terminal Heatmap]** button to show passenger density circles.
  * Click the **[Morning Peak (7–11 AM)]** or **[Midday Surge]** filter buttons to show real-time passenger recalculations.

---

### 1:30 – 2:15 | Predictive Intelligence & What-If Policy Simulator
* **Open**: `http://127.0.0.1:5000/ai-analytics.html`
* **Show**: 24-hour demand projection with 95% empirical confidence interval bands and error metrics (MAE: 42.6, RMSE: 58.1).
* **Interactive Action**:
  * Move the **Ridership Growth Slider** (+15%) and the **Shakti Share Slider** (80%).
  * Show judges the live REST POST requests firing to `/api/v1/ai/simulate` in the DevTools Network tab, dynamically projecting required fleet units (47 → 53 buses) and cash/subsidy split.

---

### 2:15 – 3:00 | System Readiness, Upload Capability & Compliance
* **Show**: Topbar **Upload Button (`📤`)**
* **The Pitch**:
  > *"To ensure future-proof feasibility as required by the problem statement, officials don't need developers to update the dashboard. They can drop in tomorrow's raw Excel or CSV file via the upload button, and the system automatically normalizes stops, re-caches in memory in under 20 milliseconds, and updates the entire fleet ledger."*
* **Show**: Compliance banner on `reports.html` confirming 100% PII-free, DPDP Act compliance.

---

## 🎯 Quick Reference for Judge Q&A

| Judge Question | Winning Response |
| :--- | :--- |
| **"How did you handle multiple passengers on a single ticket?"** | *"We strictly aggregated the `Total Psgr` column rather than row count. The dataset had 19,275 ticket rows representing 32,874 actual passengers (410 tickets / 699 pax per bus)."* |
| **"Why are there 47 units?"** | *"Each unit corresponds to an active electronic ticketing machine (ETM) **Waybill Number** representing an assigned conductor's duty shift on October 20, 2026."* |
| **"Does the map require an expensive Google Maps or Mapbox API key?"** | *"No. We built it on open-source Leaflet.js with official OpenStreetMap standard tiles and Esri backup, making it 100% cost-free and sustainable for public transit departments."* |
| **"How fast does it load?"** | *"We built a two-tier caching engine with in-memory persistence and binary disk serialization (`tickets.pkl`), delivering sub-20ms instant server warm-up."* |


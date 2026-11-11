"""
<<<<<<< Updated upstream
KSRTC Kalaburagi Division - Operational Alerts & Diagnostic Engine
Detects peak overcrowding, corridor deficits, and subsidy reconciliation notices.
=======
KSRTC Kalaburagi Division - System Alerts & Diagnostics
Scans the ticket dataset for anomalies, operational issues,
and generates actionable alerts for division management.
>>>>>>> Stashed changes
"""
import pandas as pd
from typing import List, Dict, Any

<<<<<<< Updated upstream
def get_system_alerts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Evaluates real-time threshold conditions and returns prioritized operational alerts.
    """
    alerts = []

    # 1. State Subsidy Claim Notice (Govt of Karnataka Shakti Scheme)
    subsidy_amt = float(df['subsidy_fare'].sum())
    shakti_pax = int(df[df['is_shakti_scheme']]['passengers'].sum())
    alerts.append({
        "id": "ALT-001",
        "severity": "info",
        "title": "State Subsidy Receivable: Shakti Scheme",
        "category": "Revenue & State Reimbursement",
        "timestamp": "Daily Audit Generated",
        "summary": f"₹{subsidy_amt:,.2f} recorded across {shakti_pax:,} female passengers. Claim file ready for Department of Transport reimbursement submission.",
        "action_required": "Export form 4B to Karnataka State Accounts Portal"
    })

    # 2. Overcrowded Corridors
    corridors = df.groupby('route')['passengers'].sum().sort_values(ascending=False)
    top_route = corridors.index[0]
    top_pax = int(corridors.iloc[0])
    if top_pax > 1000:
        alerts.append({
            "id": "ALT-002",
            "severity": "critical",
            "title": f"Critical Overcrowding: {top_route}",
            "category": "Fleet Capacity",
            "timestamp": "Peak Load Exceeded",
            "summary": f"Recorded {top_pax:,} passengers on corridor. Peak load factor exceeds 118% of rated seating capacity.",
            "action_required": "Inject 3 short-loop shuttle buses from Central Bus Stand"
        })

    # 3. Midday Congestion Window
    hourly = df.groupby('hour')['passengers'].sum()
    peak_hr = hourly.idxmax()
    peak_pax = int(hourly.max())
    alerts.append({
        "id": "ALT-003",
        "severity": "warning",
        "title": f"Midday Passenger Surge at {peak_hr}:00 hrs",
        "category": "Schedule Adherence",
        "timestamp": "Recurring Pattern",
        "summary": f"Heavy concentration of {peak_pax:,} passengers at midday. Bus headways stretching beyond 14 minutes at SVP Circle.",
        "action_required": "Compress headway from 12 mins to 7 mins between 11:30 AM and 1:30 PM"
    })

    # 4. Bus Fleet Maintenance / High Mileage Alert
    bus_pax = df.groupby('waybill_id')['passengers'].sum().sort_values(ascending=False)
    heavy_buses = (bus_pax >= 1100).sum()
    if heavy_buses > 0:
        alerts.append({
            "id": "ALT-004",
            "severity": "warning",
            "title": f"{heavy_buses} Buses Operating Under Heavy Stress",
            "category": "Depot Fleet Health",
            "timestamp": "Shift End Inspection Due",
            "summary": f"{heavy_buses} vehicles carried over 1,100 passengers each during continuous urban duty cycles.",
            "action_required": "Schedule brake & suspension check at Kalaburagi Depot-1 tonight"
=======

def get_system_alerts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Analyses the dataset and returns a list of alerts/warnings.
    Each alert has a severity level, category, message, and recommendation.
    """
    alerts = []

    if df.empty:
        alerts.append({
            "severity": "critical",
            "category": "Data",
            "title": "No Data Loaded",
            "message": "The ticket dataset is empty. Upload ETM data to begin analysis.",
            "recommendation": "Upload a valid .xlsx, .csv, or .json dataset via the Settings page."
        })
        return alerts

    total_pax = int(df['passengers'].sum())
    total_buses = int(df['waybill_id'].nunique())

    # 1. Check for buses with very low ridership (potential breakdown / missed trips)
    if total_buses > 0:
        bus_pax = df.groupby('waybill_id')['passengers'].sum()
        avg_pax_per_bus = bus_pax.mean()
        low_threshold = avg_pax_per_bus * 0.3  # less than 30% of average

        low_buses = bus_pax[bus_pax < low_threshold]
        if len(low_buses) > 0:
            bus_list = ', '.join(low_buses.index[:5].tolist())
            alerts.append({
                "severity": "warning",
                "category": "Fleet",
                "title": f"{len(low_buses)} Bus(es) with Unusually Low Ridership",
                "message": f"Waybills {bus_list} carried fewer than {int(low_threshold)} passengers (division avg: {int(avg_pax_per_bus)}).",
                "recommendation": "Investigate for mechanical issues, route coverage gaps, or missed conductor shifts."
            })

    # 2. Check for buses with very high ridership (overcrowding risk)
    if total_buses > 0:
        bus_pax = df.groupby('waybill_id')['passengers'].sum()
        high_threshold = 1100
        overloaded = bus_pax[bus_pax >= high_threshold]
        if len(overloaded) > 0:
            bus_list = ', '.join(overloaded.index[:5].tolist())
            alerts.append({
                "severity": "critical",
                "category": "Safety",
                "title": f"{len(overloaded)} Bus(es) Exceeding Safe Capacity",
                "message": f"Waybills {bus_list} carried {high_threshold}+ passengers. Risk of overcrowding and safety incidents.",
                "recommendation": "Deploy additional shuttle buses on these routes during peak hours."
            })

    # 3. Revenue anomaly: zero collected fare with many passengers (beyond Shakti scheme)
    non_shakti = df[df['is_shakti_scheme'] == False]
    if not non_shakti.empty:
        zero_fare = non_shakti[(non_shakti['collected_fare'] == 0) & (non_shakti['passengers'] > 0)]
        if len(zero_fare) > 10:
            alerts.append({
                "severity": "warning",
                "category": "Revenue",
                "title": f"{len(zero_fare)} Non-Shakti Tickets with Zero Fare",
                "message": "Multiple tickets show zero collection outside the Shakti scheme. Possible ETM errors or fare evasion.",
                "recommendation": "Cross-verify with conductor duty reports and ETM device logs."
            })

    # 4. Shakti scheme participation rate
    shakti_pax = int(df.loc[df['is_shakti_scheme'] == True, 'passengers'].sum())
    if total_pax > 0:
        shakti_pct = round(shakti_pax / total_pax * 100, 1)
        if shakti_pct > 80:
            alerts.append({
                "severity": "info",
                "category": "Policy",
                "title": f"Shakti Scheme at {shakti_pct}% of Total Ridership",
                "message": f"{shakti_pax:,} of {total_pax:,} passengers travelled under the state free-fare scheme.",
                "recommendation": "Ensure timely subsidy reimbursement claims are filed with the Karnataka Transport Department."
            })

    # 5. Data quality: check for unknown stops
    unknown_from = df[df['from_stop_clean'] == 'Unknown Stop']
    unknown_to = df[df['to_stop_clean'] == 'Unknown Stop']
    unknown_count = len(unknown_from) + len(unknown_to)
    if unknown_count > 0:
        alerts.append({
            "severity": "info",
            "category": "Data Quality",
            "title": f"{unknown_count} Ticket(s) with Unrecognised Stop Names",
            "message": "Some stop names could not be normalised. These appear as 'Unknown Stop' in analytics.",
            "recommendation": "Update the stop normalisation map in data_cleaner.py or correct raw ETM entries."
        })

    # 6. Hourly coverage gaps
    active_hours = df['hour'].nunique()
    if active_hours < 12:
        alerts.append({
            "severity": "warning",
            "category": "Operations",
            "title": f"Bus Activity in Only {active_hours} of 24 Hours",
            "message": "The dataset shows ridership concentrated in a narrow time window.",
            "recommendation": "Verify if this reflects actual operations or incomplete data capture."
        })

    # Always add a healthy status if no critical alerts
    if not any(a['severity'] == 'critical' for a in alerts):
        alerts.insert(0, {
            "severity": "success",
            "category": "System",
            "title": "All Systems Operational",
            "message": f"Analytics engine processing {total_pax:,} passengers across {total_buses} buses.",
            "recommendation": "Continue monitoring. Next recommended data refresh: end of shift."
>>>>>>> Stashed changes
        })

    return alerts


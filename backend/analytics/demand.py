"""
<<<<<<< Updated upstream
KSRTC Kalaburagi Division - Hourly Passenger Demand Analytics
Calculates hourly passenger demand curves, peak passenger spikes, and load factors.
"""
import pandas as pd
from typing import Dict, Any, List

def get_hourly_demand(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes hourly aggregation: passengers, ticket count, cash fare, and Shakti subsidy.
    Filters to operating hours 6 AM - 11 PM (6 to 23).
    """
    grouped = df.groupby('hour').agg(
        passengers=('passengers', 'sum'),
        trips=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum'),
        shaktiPassengers=('is_shakti_scheme', lambda x: (x * df.loc[x.index, 'passengers']).sum())
    ).reset_index()

    # Filter standard transit day (6:00 to 23:00)
    grouped = grouped[(grouped['hour'] >= 6) & (grouped['hour'] <= 23)]
    grouped = grouped.sort_values('hour')

    results = []
    for _, row in grouped.iterrows():
        hr = int(row['hour'])
        # Format 12-hour AM/PM label
        period = "AM" if hr < 12 else "PM"
        display_hr = 12 if hr in [0, 12] else hr % 12
        label = f"{display_hr}:00 {period}"

        results.append({
            "hour": hr,
            "label": label,
            "passengers": int(row['passengers']),
            "trips": int(row['trips']),
            "collected": float(round(row['collected'], 2)),
            "subsidy": float(round(row['subsidy'], 2)),
            "totalFare": float(round(row['totalFare'], 2)),
            "shaktiPassengers": int(row['shaktiPassengers'])
        })

    return results

def get_peak_demand_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Finds peak commuter windows (morning and afternoon/evening)."""
    hourly = get_hourly_demand(df)
    if not hourly:
        return {}

    sorted_pax = sorted(hourly, key=lambda x: x['passengers'], reverse=True)
    peak = sorted_pax[0]

    morning_peak = max([h for h in hourly if 7 <= h['hour'] <= 11], key=lambda x: x['passengers'], default=None)
    midday_peak = max([h for h in hourly if 12 <= h['hour'] <= 16], key=lambda x: x['passengers'], default=None)
    evening_peak = max([h for h in hourly if 17 <= h['hour'] <= 21], key=lambda x: x['passengers'], default=None)

    return {
        "overall_peak_hour": peak['label'],
        "peak_hour_passengers": peak['passengers'],
        "morning_rush": morning_peak['label'] if morning_peak else "11:00 AM",
        "morning_pax": morning_peak['passengers'] if morning_peak else 0,
        "midday_peak": midday_peak['label'] if midday_peak else "12:00 PM",
        "midday_pax": midday_peak['passengers'] if midday_peak else 0,
        "evening_rush": evening_peak['label'] if evening_peak else "5:00 PM",
        "evening_pax": evening_peak['passengers'] if evening_peak else 0
=======
KSRTC Kalaburagi Division - Passenger Demand Analytics
Computes hourly ridership distribution, trip counts, revenue per hour,
and identifies peak/off-peak demand windows for scheduling optimisation.
"""
import pandas as pd
from typing import List, Dict, Any


def get_hourly_demand(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Aggregates passenger demand, ticket count, and fare by hour of day (0–23).
    Returns a list of 24 dicts suitable for Chart.js rendering.
    """
    if df.empty:
        return []

    grouped = df.groupby('hour').agg(
        passengers=('passengers', 'sum'),
        tickets=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum'),
        trips=('waybill_id', 'nunique')
    ).reindex(range(24), fill_value=0).reset_index()

    hourly = []
    for _, row in grouped.iterrows():
        hr = int(row['hour'])
        # Human-readable label: "6 AM", "12 PM", "5 PM", etc.
        if hr == 0:
            label = "12 AM"
        elif hr < 12:
            label = f"{hr} AM"
        elif hr == 12:
            label = "12 PM"
        else:
            label = f"{hr - 12} PM"

        hourly.append({
            "hour": hr,
            "label": label,
            "passengers": int(row['passengers']),
            "tickets": int(row['tickets']),
            "trips": int(row['trips']),
            "collected": float(round(row['collected'], 2)),
            "subsidy": float(round(row['subsidy'], 2)),
            "totalFare": float(round(row['totalFare'], 2))
        })

    return hourly


def get_peak_demand_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Identifies the peak hour, off-peak hour, and overall demand concentration.
    Used by the dashboard to highlight scheduling recommendations.
    """
    hourly = get_hourly_demand(df)
    if not hourly:
        return {
            "peak_hour": "N/A",
            "peak_passengers": 0,
            "off_peak_hour": "N/A",
            "off_peak_passengers": 0,
            "peak_concentration_pct": 0
        }

    sorted_by_pax = sorted(hourly, key=lambda h: h['passengers'], reverse=True)
    peak = sorted_by_pax[0]
    off_peak = sorted_by_pax[-1]
    total_pax = sum(h['passengers'] for h in hourly)
    concentration = round((peak['passengers'] / total_pax * 100), 1) if total_pax > 0 else 0

    return {
        "peak_hour": peak['label'],
        "peak_passengers": peak['passengers'],
        "off_peak_hour": off_peak['label'],
        "off_peak_passengers": off_peak['passengers'],
        "peak_concentration_pct": concentration
>>>>>>> Stashed changes
    }


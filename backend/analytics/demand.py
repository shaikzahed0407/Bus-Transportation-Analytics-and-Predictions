"""
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
    }


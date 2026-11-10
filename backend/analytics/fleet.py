"""
KSRTC Kalaburagi Division - Bus Fleet Statistics & Waybill Performance
Aggregates vehicle utilization, passenger load factors, and revenue across the 47-bus fleet.
"""
import pandas as pd
from typing import List, Dict, Any

def get_fleet_statistics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Computes performance metrics for each active bus/waybill in the division.
    """
    grouped = df.groupby('waybill_id').agg(
        passengers=('passengers', 'sum'),
        tickets=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum'),
        distinct_stops=('from_stop_clean', lambda x: x.nunique()),
        hours_active=('hour', lambda x: x.nunique()),
        shaktiPassengers=('is_shakti_scheme', lambda x: (x * df.loc[x.index, 'passengers']).sum())
    ).reset_index()

    grouped = grouped.sort_values('passengers', ascending=False)
    max_pax = grouped['passengers'].max() if not grouped.empty else 1

    fleet_records = []
    for rank, row in enumerate(grouped.itertuples(), start=1):
        pax = int(row.passengers)
        tkts = int(row.tickets)
        pax_per_tkt = round(pax / tkts, 2) if tkts > 0 else 0.0

        # Load badge categorization
        if pax >= 1100:
            badge_color, badge_label = "red", "Overloaded"
        elif pax >= 800:
            badge_color, badge_label = "purple", "Heavy"
        elif pax >= 500:
            badge_color, badge_label = "green", "Moderate"
        else:
            badge_color, badge_label = "yellow", "Light"

        pct_capacity = int(round((pax / max_pax) * 100))

        fleet_records.append({
            "rank": rank,
            "waybill": str(row.waybill_id),
            "passengers": pax,
            "capacity_pct": pct_capacity,
            "tickets": tkts,
            "pax_per_ticket": pax_per_tkt,
            "collected": float(round(row.collected, 2)),
            "subsidy": float(round(row.subsidy, 2)),
            "totalFare": float(round(row.totalFare, 2)),
            "shakti_passengers": int(row.shaktiPassengers),
            "stops_covered": int(row.distinct_stops),
            "hours_active": int(row.hours_active),
            "badge_color": badge_color,
            "badge_label": badge_label
        })

    return fleet_records

def get_fleet_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes division-wide fleet totals and averages."""
    fleet = get_fleet_statistics(df)
    total_buses = len(fleet)
    total_pax = sum(b['passengers'] for b in fleet)
    avg_pax = round(total_pax / total_buses, 1) if total_buses > 0 else 0

    overloaded_count = sum(1 for b in fleet if b['badge_label'] == 'Overloaded')
    heavy_count = sum(1 for b in fleet if b['badge_label'] == 'Heavy')

    return {
        "active_fleet_count": total_buses,
        "total_fleet_passengers": total_pax,
        "average_passengers_per_bus": avg_pax,
        "overloaded_buses": overloaded_count,
        "heavy_buses": heavy_count,
        "top_performing_bus": fleet[0]['waybill'] if fleet else None
    }


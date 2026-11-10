"""
KSRTC Kalaburagi Division - Passenger Movement & Corridor Analytics
Computes Origin-Destination (OD) trip flows and high-density passenger corridors.
"""
import pandas as pd
from typing import List, Dict, Any

def get_top_corridors(df: pd.DataFrame, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Computes top Origin-Destination corridors by passenger volume.
    """
    grouped = df.groupby(['from_stop_clean', 'to_stop_clean']).agg(
        passengers=('passengers', 'sum'),
        trips=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum'),
        shaktiPassengers=('is_shakti_scheme', lambda x: (x * df.loc[x.index, 'passengers']).sum())
    ).reset_index()

    grouped['route'] = grouped['from_stop_clean'] + ' → ' + grouped['to_stop_clean']
    grouped = grouped.sort_values('passengers', ascending=False)

    if limit:
        grouped = grouped.head(limit)

    results = []
    for _, row in grouped.iterrows():
        pax = int(row['passengers'])
        trips = int(row['trips'])
        pax_per_trip = round(pax / trips, 1) if trips > 0 else 0.0

        results.append({
            "from_stop": row['from_stop_clean'],
            "to_stop": row['to_stop_clean'],
            "route": row['route'],
            "passengers": pax,
            "trips": trips,
            "pax_per_trip": pax_per_trip,
            "collected": float(round(row['collected'], 2)),
            "subsidy": float(round(row['subsidy'], 2)),
            "totalFare": float(round(row['totalFare'], 2)),
            "shakti_passengers": int(row['shaktiPassengers'])
        })

    return results

def get_corridor_directional_balance(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Compares forward vs return passenger volumes for top 2-way corridors
    e.g., Budhavihar → CBS vs CBS → Budhavihar.
    """
    corridors = get_top_corridors(df, limit=50)
    pairs_seen = set()
    balanced_results = []

    lookup = {(c['from_stop'], c['to_stop']): c for c in corridors}

    for (orig, dest), c1 in lookup.items():
        pair_key = tuple(sorted([orig, dest]))
        if pair_key in pairs_seen:
            continue
        pairs_seen.add(pair_key)

        c2 = lookup.get((dest, orig), None)
        pax_forward = c1['passengers']
        pax_return = c2['passengers'] if c2 else 0
        total_2way = pax_forward + pax_return

        imbalance_pct = round(abs(pax_forward - pax_return) / total_2way * 100, 1) if total_2way > 0 else 0

        balanced_results.append({
            "corridor": f"{orig} ↔ {dest}",
            "forward_route": f"{orig} → {dest}",
            "forward_pax": pax_forward,
            "return_route": f"{dest} → {orig}",
            "return_pax": pax_return,
            "total_2way_pax": total_2way,
            "imbalance_pct": imbalance_pct
        })

    balanced_results.sort(key=lambda x: x['total_2way_pax'], reverse=True)
    return balanced_results[:10]


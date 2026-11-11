"""
<<<<<<< Updated upstream
KSRTC Kalaburagi Division - Passenger Movement & Corridor Analytics
Computes Origin-Destination (OD) trip flows and high-density passenger corridors.
=======
KSRTC Kalaburagi Division - Route & Corridor Movement Analytics
Identifies top passenger corridors, directional flow imbalance,
and origin-destination patterns across the Kalaburagi urban network.
>>>>>>> Stashed changes
"""
import pandas as pd
from typing import List, Dict, Any

<<<<<<< Updated upstream
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
=======

def get_top_corridors(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Ranks bus corridors (from_stop ↔ to_stop pairs) by total passenger volume.
    Merges both directions into a single bidirectional corridor.
    """
    if df.empty:
        return []

    # Build a canonical corridor key so A→B and B→A are grouped together
    def canonical_corridor(row):
        a = row['from_stop_clean']
        b = row['to_stop_clean']
        return ' ↔ '.join(sorted([a, b]))

    temp = df.copy()
    temp['corridor'] = temp.apply(canonical_corridor, axis=1)

    grouped = temp.groupby('corridor').agg(
        passengers=('passengers', 'sum'),
        tickets=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum'),
        distinct_buses=('waybill_id', 'nunique')
    ).reset_index()

    grouped = grouped.sort_values('passengers', ascending=False).head(limit)

    corridors = []
    for rank, (_, row) in enumerate(grouped.iterrows(), start=1):
        corridors.append({
            "rank": rank,
            "corridor": row['corridor'],
            "passengers": int(row['passengers']),
            "tickets": int(row['tickets']),
            "collected": float(round(row['collected'], 2)),
            "subsidy": float(round(row['subsidy'], 2)),
            "totalFare": float(round(row['totalFare'], 2)),
            "buses_serving": int(row['distinct_buses'])
        })

    return corridors


def get_corridor_directional_balance(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Analyses directional passenger flow for each corridor.
    A balanced corridor has roughly equal A→B and B→A ridership;
    imbalanced corridors suggest potential for express / deadhead optimisation.
    """
    if df.empty:
        return []

    # Group by ordered route (from → to)
    dir_grouped = df.groupby(['from_stop_clean', 'to_stop_clean']).agg(
        passengers=('passengers', 'sum')
    ).reset_index()

    # Build bidirectional pairs
    pairs: Dict[str, Dict] = {}
    for _, row in dir_grouped.iterrows():
        a, b = row['from_stop_clean'], row['to_stop_clean']
        key = ' ↔ '.join(sorted([a, b]))
        if key not in pairs:
            pairs[key] = {'a_to_b': 0, 'b_to_a': 0, 'stop_a': sorted([a, b])[0], 'stop_b': sorted([a, b])[1]}
        if a == pairs[key]['stop_a']:
            pairs[key]['a_to_b'] += int(row['passengers'])
        else:
            pairs[key]['b_to_a'] += int(row['passengers'])

    results = []
    for corridor, data in pairs.items():
        total = data['a_to_b'] + data['b_to_a']
        if total == 0:
            continue
        imbalance = abs(data['a_to_b'] - data['b_to_a']) / total
        results.append({
            "corridor": corridor,
            "direction_a": f"{data['stop_a']} → {data['stop_b']}",
            "direction_b": f"{data['stop_b']} → {data['stop_a']}",
            "pax_a_to_b": data['a_to_b'],
            "pax_b_to_a": data['b_to_a'],
            "total_passengers": total,
            "imbalance_ratio": round(imbalance, 3),
            "balance_status": "Balanced" if imbalance < 0.2 else ("Moderate" if imbalance < 0.4 else "Imbalanced")
        })

    results.sort(key=lambda x: x['total_passengers'], reverse=True)
    return results
>>>>>>> Stashed changes


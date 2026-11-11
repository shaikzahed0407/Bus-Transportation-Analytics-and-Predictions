"""
<<<<<<< Updated upstream
KSRTC Kalaburagi Division - Financial & Shakti Subsidy Intelligence
Reconciles passenger fare collections, cash accounting, and Government of Karnataka subsidy claims.
"""
import pandas as pd
from typing import Dict, Any, List

def get_revenue_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes divisional revenue KPIs including Shakti Scheme reimbursement ledger.
    """
    total_collected = float(df['collected_fare'].sum())
    total_subsidy = float(df['subsidy_fare'].sum())
    total_gross = total_collected + total_subsidy
    total_passengers = int(df['passengers'].sum())
    total_tickets = len(df)

    # Shakti scheme counts
    shakti_rows = df[df['is_shakti_scheme']]
    shakti_pax = int(shakti_rows['passengers'].sum())
    shakti_pax_share_pct = round((shakti_pax / total_passengers * 100), 1) if total_passengers > 0 else 0
    shakti_revenue_share_pct = round((total_subsidy / total_gross * 100), 1) if total_gross > 0 else 0

    avg_fare_per_pax = round(total_gross / total_passengers, 2) if total_passengers > 0 else 0
    avg_fare_per_tkt = round(total_gross / total_tickets, 2) if total_tickets > 0 else 0

    return {
        "total_gross_revenue": round(total_gross, 2),
        "cash_collected": round(total_collected, 2),
        "shakti_subsidy_receivable": round(total_subsidy, 2),
        "total_passengers": total_passengers,
        "shakti_beneficiary_passengers": shakti_pax,
        "shakti_pax_share_pct": shakti_pax_share_pct,
        "shakti_revenue_share_pct": shakti_revenue_share_pct,
        "avg_fare_per_passenger": avg_fare_per_pax,
        "avg_fare_per_ticket": avg_fare_per_tkt,
        "claim_status": "AUDITED_RECEIVABLE_FROM_GOK"
    }

def get_revenue_by_route(df: pd.DataFrame, limit: int = 15) -> List[Dict[str, Any]]:
    """Ranks corridors by cash collected vs state subsidy receivable."""
    grouped = df.groupby('route').agg(
        total_fare=('total_fare', 'sum'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        passengers=('passengers', 'sum')
    ).reset_index()

    grouped = grouped.sort_values('total_fare', ascending=False)
    if limit:
        grouped = grouped.head(limit)

    results = []
    for _, row in grouped.iterrows():
        gross = float(row['total_fare'])
        sub = float(row['subsidy'])
        shakti_pct = round((sub / gross * 100), 1) if gross > 0 else 0

        results.append({
            "route": row['route'],
            "total_fare": round(gross, 2),
            "cash_collected": round(float(row['collected']), 2),
            "shakti_subsidy": round(sub, 2),
            "passengers": int(row['passengers']),
            "subsidy_share_pct": shakti_pct
        })

    return results
=======
KSRTC Kalaburagi Division - Revenue Analytics
Computes cash collection, Karnataka Shakti Scheme subsidy claims,
fare-per-km efficiency, and per-route revenue breakdowns.
"""
import pandas as pd
from typing import List, Dict, Any


def get_revenue_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Division-wide revenue summary: cash vs Shakti subsidy,
    average fare per passenger, and scheme participation rate.
    """
    if df.empty:
        return {
            "total_collected": 0,
            "total_subsidy": 0,
            "total_gross": 0,
            "avg_fare_per_pax": 0,
            "shakti_pax": 0,
            "non_shakti_pax": 0,
            "shakti_pct": 0
        }

    total_collected = float(df['collected_fare'].sum())
    total_subsidy = float(df['subsidy_fare'].sum())
    total_gross = total_collected + total_subsidy
    total_pax = int(df['passengers'].sum())
    avg_fare = round(total_gross / total_pax, 2) if total_pax > 0 else 0.0

    shakti_mask = df['is_shakti_scheme'] == True
    shakti_pax = int(df.loc[shakti_mask, 'passengers'].sum())
    non_shakti_pax = total_pax - shakti_pax
    shakti_pct = round((shakti_pax / total_pax * 100), 1) if total_pax > 0 else 0

    return {
        "total_collected": round(total_collected, 2),
        "total_subsidy": round(total_subsidy, 2),
        "total_gross": round(total_gross, 2),
        "avg_fare_per_pax": avg_fare,
        "shakti_pax": shakti_pax,
        "non_shakti_pax": non_shakti_pax,
        "shakti_pct": shakti_pct
    }


def get_revenue_by_route(df: pd.DataFrame, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Revenue breakdown per route, sorted by gross fare descending.
    Useful for identifying the most commercially valuable corridors
    vs subsidy-heavy routes for state reimbursement claims.
    """
    if df.empty:
        return []

    grouped = df.groupby('route').agg(
        passengers=('passengers', 'sum'),
        tickets=('ticket_number', 'count'),
        collected=('collected_fare', 'sum'),
        subsidy=('subsidy_fare', 'sum'),
        totalFare=('total_fare', 'sum')
    ).reset_index()

    grouped = grouped.sort_values('totalFare', ascending=False).head(limit)

    routes = []
    for rank, (_, row) in enumerate(grouped.iterrows(), start=1):
        pax = int(row['passengers'])
        gross = float(row['totalFare'])
        avg = round(gross / pax, 2) if pax > 0 else 0.0
        subsidy_share = round((float(row['subsidy']) / gross * 100), 1) if gross > 0 else 0

        routes.append({
            "rank": rank,
            "route": row['route'],
            "passengers": pax,
            "tickets": int(row['tickets']),
            "collected": float(round(row['collected'], 2)),
            "subsidy": float(round(row['subsidy'], 2)),
            "totalFare": round(gross, 2),
            "avg_fare": avg,
            "subsidy_share_pct": subsidy_share
        })

    return routes
>>>>>>> Stashed changes


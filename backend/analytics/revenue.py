"""
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


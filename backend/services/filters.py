"""
KSRTC Kalaburagi Division - Slicing and Filtering Services
Provides unified query filtering across all analytical endpoints.
"""
import pandas as pd
from typing import Optional

def apply_filters(
    df: pd.DataFrame,
    start_hour: Optional[int] = None,
    end_hour: Optional[int] = None,
    bus_id: Optional[str] = None,
    route_name: Optional[str] = None,
    stop_name: Optional[str] = None,
    shakti_only: Optional[bool] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    data_status: Optional[str] = None,
) -> pd.DataFrame:
    """
    Applies optional query filters to the ticket DataFrame.
    """
    filtered = df

    if from_date and 'date' in filtered.columns:
        filtered = filtered[filtered['date'].astype(str) >= from_date]
    if to_date and 'date' in filtered.columns:
        filtered = filtered[filtered['date'].astype(str) <= to_date]
    if data_status and data_status != 'all' and 'data_status' in filtered.columns:
        filtered = filtered[filtered['data_status'] == data_status]

    if start_hour is not None:
        filtered = filtered[filtered['hour'] >= start_hour]

    if start_hour is None and end_hour is None:
        filtered = filtered[filtered['hour'] >= 0]
    if end_hour is not None:
        filtered = filtered[filtered['hour'] <= end_hour]

    if bus_id:
        filtered = filtered[filtered['waybill_id'] == str(bus_id)]

    if route_name:
        filtered = filtered[filtered['route'].str.contains(route_name, case=False, na=False)]

    if stop_name:
        filtered = filtered[
            filtered['from_stop_clean'].str.contains(stop_name, case=False, na=False) |
            filtered['to_stop_clean'].str.contains(stop_name, case=False, na=False)
        ]

    if shakti_only is not None:
        filtered = filtered[filtered['is_shakti_scheme'] == shakti_only]

    return filtered

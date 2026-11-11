"""
<<<<<<< Updated upstream
KSRTC Kalaburagi Division - Slicing and Filtering Services
Provides unified query filtering across all analytical endpoints.
=======
KSRTC Kalaburagi Division - Data Filtering Service
Applies query-parameter filters (hour range, bus, route, stop, Shakti scheme)
to the in-memory Pandas DataFrame before analytics computation.
>>>>>>> Stashed changes
"""
import pandas as pd
from typing import Optional

<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
def apply_filters(
    df: pd.DataFrame,
    start_hour: Optional[int] = None,
    end_hour: Optional[int] = None,
    bus_id: Optional[str] = None,
    route_name: Optional[str] = None,
    stop_name: Optional[str] = None,
    shakti_only: Optional[bool] = None
) -> pd.DataFrame:
    """
<<<<<<< Updated upstream
    Applies optional query filters to the ticket DataFrame.
    """
    filtered = df

    if start_hour is not None:
        filtered = filtered[filtered['hour'] >= start_hour]

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
=======
    Returns a filtered copy of the DataFrame based on supplied criteria.
    All parameters are optional; omitted filters pass through everything.
    """
    filtered = df.copy()

    # Hour range filter
    if start_hour is not None:
        filtered = filtered[filtered['hour'] >= start_hour]
    if end_hour is not None:
        filtered = filtered[filtered['hour'] <= end_hour]

    # Specific bus / waybill
    if bus_id is not None:
        filtered = filtered[filtered['waybill_id'] == str(bus_id)]

    # Route name (partial, case-insensitive match)
    if route_name is not None:
        route_lower = route_name.lower()
        filtered = filtered[filtered['route'].str.lower().str.contains(route_lower, na=False)]

    # Stop name (matches either from or to stop, case-insensitive)
    if stop_name is not None:
        stop_lower = stop_name.lower()
        filtered = filtered[
            filtered['from_stop_clean'].str.lower().str.contains(stop_lower, na=False) |
            filtered['to_stop_clean'].str.lower().str.contains(stop_lower, na=False)
        ]

    # Shakti Scheme only
    if shakti_only is True:
        filtered = filtered[filtered['is_shakti_scheme'] == True]
    elif shakti_only is False:
        filtered = filtered[filtered['is_shakti_scheme'] == False]
>>>>>>> Stashed changes

    return filtered


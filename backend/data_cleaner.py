"""
KSRTC Kalaburagi Division - BusPulse Data Cleaning Pipeline
Standardizes raw ETM ticket transactions from Excel or JSON.
"""
import pandas as pd
import numpy as np
from datetime import datetime, time

# Stop name normalization map for Kalaburagi Division
STOP_NORM_MAP = {
    'cbs': 'CBS (Central Bus Stand)',
    'central bus stand': 'CBS (Central Bus Stand)',
    'budhavihar': 'Budhavihar',
    'supermarket': 'Supermarket',
    'sedam r r': 'Sedam Road',
    'sedam road': 'Sedam Road',
    'ruknuddin darga': 'Ruknuddin Dargah',
    'ruknuddin dargah': 'Ruknuddin Dargah',
    's v p circle': 'SVP Circle',
    'svp circle': 'SVP Circle',
    'madiwala vritta': 'Madiwala Vritta',
    'railway station': 'Railway Station',
    'gulbarga university': 'Gulbarga University',
    'ram mandir': 'Ram Mandir Circle',
    'high court': 'High Court Bench'
}

def clean_ticket_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw ticket data, handles Excel/JSON date-time differences,
    normalizes stop names, and flags Karnataka Shakti Scheme subsidy.
    """
    df = df.copy()

    # 1. Standardize column names
    col_map = {
        'Waybill Number': 'waybill_number',
        'Ticket Number': 'ticket_number',
        'From Stop': 'from_stop',
        'To Stop': 'to_stop',
        'Date': 'date',
        'Time': 'time',
        'Total Psgr': 'passengers',
        'Coll Amt': 'collected_fare',
        'Uncoll Amt': 'subsidy_fare',
        'Unnamed: 9': 'notes'
    }
    df = df.rename(columns=lambda c: col_map.get(str(c).strip(), str(c).strip().lower().replace(' ', '_')))

    # Drop unneeded notes column if present
    if 'notes' in df.columns:
        df = df.drop(columns=['notes'])
    if 'unnamed:_9' in df.columns:
        df = df.drop(columns=['unnamed:_9'])

    # 2. Handle numeric types
    df['passengers'] = pd.to_numeric(df['passengers'], errors='coerce').fillna(1).astype(int)
    df['collected_fare'] = pd.to_numeric(df['collected_fare'], errors='coerce').fillna(0.0)
    df['subsidy_fare'] = pd.to_numeric(df['subsidy_fare'], errors='coerce').fillna(0.0)
    df['total_fare'] = df['collected_fare'] + df['subsidy_fare']

    # 3. Classify Shakti Scheme (Govt of Karnataka Women Free Travel)
    # Zero fare collected with valid passenger count is state-reimbursable subsidy
    df['is_shakti_scheme'] = (df['collected_fare'] == 0) & (df['subsidy_fare'] > 0)

    # 4. Normalize Stop Names
    def norm_stop(val):
        if not isinstance(val, str) or not val.strip():
            return 'Unknown Stop'
        s = val.strip()
        return STOP_NORM_MAP.get(s.lower(), s.title())

    df['from_stop_clean'] = df['from_stop'].apply(norm_stop)
    df['to_stop_clean'] = df['to_stop'].apply(norm_stop)
    df['route'] = df['from_stop_clean'] + ' → ' + df['to_stop_clean']

    # 5. Extract Hours
    def parse_hour(t_val):
        if isinstance(t_val, time):
            return t_val.hour
        elif isinstance(t_val, datetime):
            return t_val.hour
        elif isinstance(t_val, (int, float)):
            # Excel fraction of day: 0.5 = 12:00 PM
            if 0 <= t_val <= 1:
                return int((t_val * 24)) % 24
            elif 0 <= t_val <= 23:
                return int(t_val)
        elif isinstance(t_val, str):
            try:
                parts = t_val.strip().split(':')
                return int(parts[0])
            except Exception:
                pass
        return 12  # default midday fallback

    df['hour'] = df['time'].apply(parse_hour)

    # 6. Waybill to Bus Number string mapping
    df['waybill_id'] = df['waybill_number'].astype(str)

    return df


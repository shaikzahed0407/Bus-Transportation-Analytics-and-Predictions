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
        'waybill_no': 'waybill_number',
        'waybill': 'waybill_number',
        'Ticket Number': 'ticket_number',
        'ticket_no': 'ticket_number',
        'From Stop': 'from_stop',
        'from_stage_name': 'from_stop',
        'origin': 'from_stop',
        'source': 'from_stop',
        'To Stop': 'to_stop',
        'to_stage_name': 'to_stop',
        'destination': 'to_stop',
        'dest': 'to_stop',
        'Date': 'date',
        'txn_date': 'date',
        'Time': 'time',
        'txn_time': 'time',
        'Total Psgr': 'passengers',
        'total_psgr': 'passengers',
        'total_seats': 'passengers',
        'psgr': 'passengers',
        'pax': 'passengers',
        'Coll Amt': 'collected_fare',
        'coll_amt': 'collected_fare',
        'fare': 'collected_fare',
        'ticket_amount': 'collected_fare',
        'Uncoll Amt': 'subsidy_fare',
        'uncoll_amt': 'subsidy_fare',
        'subsidy': 'subsidy_fare',
        'subsidy_amount': 'subsidy_fare',
        'Unnamed: 9': 'notes'
    }
    df = df.rename(columns=lambda c: col_map.get(str(c).strip(), col_map.get(str(c).strip().lower().replace(' ', '_'), str(c).strip().lower().replace(' ', '_'))))

    # Fallback column creation if missing
    if 'passengers' not in df.columns:
        df['passengers'] = 1
    if 'collected_fare' not in df.columns:
        df['collected_fare'] = 0.0
    if 'subsidy_fare' not in df.columns:
        df['subsidy_fare'] = 0.0
    if 'time' not in df.columns:
        df['time'] = '12:00:00'
    if 'date' not in df.columns:
        df['date'] = str(datetime.now().date())
    if 'waybill_id' not in df.columns:
        if 'waybill_number' in df.columns:
            df['waybill_id'] = df['waybill_number'].astype(str)
        else:
            df['waybill_id'] = 'WB-1'

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
    df['from_stop'] = df['from_stop'].fillna('Unknown Stop').astype(str)
    df['to_stop'] = df['to_stop'].fillna('Unknown Stop').astype(str)

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


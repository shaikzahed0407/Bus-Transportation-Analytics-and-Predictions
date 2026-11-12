"""Deterministic, explicitly synthetic extension of the supplied one-day sample."""
import json
import gzip
from pathlib import Path

import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'data' / 'raw' / 'data_sql (12).json'
OUTPUT = ROOT / 'data' / 'raw' / 'sample_history.json.gz'
MARKER = 'Data Status'


def generate_history(days=31):
    """Preserve the source day and synthesize a compact, reproducible preceding history."""
    if days < 15:
        raise ValueError('Generate at least 15 days to support chronological evaluation.')
    raw = pd.DataFrame(json.loads(SOURCE.read_text(encoding='utf-8')))
    dates = pd.to_datetime(raw['Date'], unit='D', origin='1899-12-30')
    source_day = dates.min()
    raw[MARKER] = 'Source sample'
    samples = []
    # Seeded noise and weekday effects create varied demo days while remaining reproducible.
    rng = np.random.default_rng(20261112)
    weekday_effect = {0: 0.98, 1: 1.00, 2: 1.02, 3: 1.04, 4: 1.08, 5: 1.12, 6: 0.86}
    serial_origin = pd.Timestamp('1899-12-30')
    for offset in range(-(days - 1), 0):
        day = raw.copy()
        date = source_day + pd.Timedelta(days=offset)
        factor = weekday_effect[date.weekday()] * rng.normal(1.0, 0.045)
        hour = (day['Time'] * 24).astype(int).clip(0, 23)
        # Add a small, deterministic commuter-hour profile variation, avoiding uniform clones.
        hour_effect = hour.map({7: 1.04, 8: 1.07, 9: 1.03, 12: 0.97, 15: 1.05, 17: 1.04, 18: 1.06}).fillna(1.0)
        passenger_factor = factor * hour_effect * rng.normal(1.0, 0.012, len(day))
        day['Date'] = (date - serial_origin).days
        day['Total Psgr'] = (day['Total Psgr'] * passenger_factor).round().clip(lower=1).astype(int)
        fare_factor = day['Total Psgr'] / raw['Total Psgr'].clip(lower=1)
        day['Coll Amt'] = (day['Coll Amt'] * fare_factor).round().astype(int)
        day['Uncoll Amt'] = (day['Uncoll Amt'] * fare_factor).round().astype(int)
        day[MARKER] = 'Synthetic demo data'
        samples.append(day)
    combined = pd.concat([*samples, raw], ignore_index=True)
    payload = combined.to_json(orient='records', double_precision=4).encode('utf-8')
    with gzip.open(OUTPUT, 'wb', compresslevel=6) as stream:
        stream.write(payload)
    return combined


if __name__ == '__main__':
    frame = generate_history()
    print(f'Wrote {len(frame)} rows across {frame.Date.nunique()} days to {OUTPUT}')

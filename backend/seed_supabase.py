"""
KSRTC Kalaburagi Division - Supabase Migration & Seeder Script
Reads raw Excel/CSV/JSON dataset, standardizes via data_cleaner,
and batch-inserts all records into the Supabase `tickets` table.
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
from supabase import create_client, Client

# Ensure backend directory is in path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

from data_cleaner import clean_ticket_data

# Optional: Load .env if present
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def seed_data(file_path: str = None, batch_size: int = 1000, truncate_first: bool = True):
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("\n❌ Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set!")
        print("Set them in your PowerShell session or create a .env file:\n")
        print("  $env:SUPABASE_URL = 'https://xxxx.supabase.co'")
        print("  $env:SUPABASE_SERVICE_ROLE_KEY = 'your-service-role-key'\n")
        return

    # Locate source dataset
    if not file_path:
        candidates = [
            BASE_DIR / "Ticket data_1 Day_City Service.xlsx",
            BASE_DIR / "data_sql (12).json",
            BASE_DIR / "data" / "raw" / "data_sql (12).json",
            BASE_DIR / "data" / "raw" / "Dataset.xlsx"
        ]
        for c in candidates:
            if c.exists():
                file_path = str(c)
                break

    if not file_path or not Path(file_path).exists():
        print(f"\n❌ Dataset file not found! Checked locations: {file_path}")
        return

    print(f"📁 Source file: {file_path}")
    print("⏳ Reading dataset...")

    fp_lower = file_path.lower()
    if fp_lower.endswith(".xlsx") or fp_lower.endswith(".xls"):
        raw_df = pd.read_excel(file_path)
    elif fp_lower.endswith(".csv"):
        raw_df = pd.read_csv(file_path)
    elif fp_lower.endswith(".json"):
        import json
        with open(file_path, "r", encoding="utf-8") as f:
            raw_df = pd.DataFrame(json.load(f))
    else:
        print("❌ Unsupported format. Provide .xlsx, .csv, or .json")
        return

    print(f"📊 Raw rows loaded: {len(raw_df):,}")
    print("🧹 Cleaning and standardizing data...")
    cleaned_df = clean_ticket_data(raw_df)

    # Format date and time explicitly as strings to prevent serialization issues
    if 'date' in cleaned_df.columns:
        cleaned_df['date'] = cleaned_df['date'].astype(str)
    if 'time' in cleaned_df.columns:
        cleaned_df['time'] = cleaned_df['time'].astype(str)

    # Ensure required columns
    cols_to_insert = [
        'waybill_number', 'waybill_id', 'ticket_number', 'from_stop', 'to_stop',
        'from_stop_clean', 'to_stop_clean', 'route', 'date', 'time', 'hour',
        'passengers', 'collected_fare', 'subsidy_fare', 'total_fare', 'is_shakti_scheme'
    ]
    available_cols = [c for c in cols_to_insert if c in cleaned_df.columns]
    upload_df = cleaned_df[available_cols].copy()

    # Fill and clean any NaN/None to guarantee JSON-compliance (no float('nan'))
    upload_df['from_stop'] = upload_df['from_stop'].fillna('Unknown Stop').astype(str)
    upload_df['to_stop'] = upload_df['to_stop'].fillna('Unknown Stop').astype(str)
    upload_df['passengers'] = upload_df['passengers'].fillna(1).astype(int)
    upload_df['collected_fare'] = upload_df['collected_fare'].fillna(0.0).astype(float)
    upload_df['subsidy_fare'] = upload_df['subsidy_fare'].fillna(0.0).astype(float)
    upload_df['total_fare'] = upload_df['total_fare'].fillna(0.0).astype(float)
    upload_df = upload_df.where(pd.notnull(upload_df), None)

    records = upload_df.to_dict(orient="records")
    # Extra safety pass: replace any leftover float NaN with None
    import math
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and math.isnan(v):
                r[k] = None

    total_records = len(records)
    print(f"🚀 Prepared {total_records:,} cleaned ticket records for Supabase.")

    # Connect to Supabase
    print(f"🔌 Connecting to Supabase at: {url[:30]}...")
    supabase: Client = create_client(url, key)

    # Optionally truncate existing tickets
    if truncate_first:
        print("🗑️  Cleaning existing records from 'tickets' table...")
        try:
            # Delete in Supabase (delete without filter requires condition or rpc)
            supabase.table("tickets").delete().neq("id", 0).execute()
        except Exception as e:
            print(f"   (Notice during table clear: {e})")

    # Batch insertion
    print(f"⬆️  Uploading in batches of {batch_size}...")
    start_time = time.time()
    inserted_count = 0

    for i in range(0, total_records, batch_size):
        batch = records[i : i + batch_size]
        try:
            supabase.table("tickets").insert(batch).execute()
            inserted_count += len(batch)
            pct = round((inserted_count / total_records) * 100, 1)
            print(f"   ✅ Inserted {inserted_count:,} / {total_records:,} ({pct}%)")
        except Exception as e:
            print(f"   ❌ Batch failed at row {i}: {e}")
            break

    elapsed = round(time.time() - start_time, 2)
    print(f"\n🎉 Migration finished in {elapsed}s! Total inserted: {inserted_count:,}")


if __name__ == "__main__":
    seed_data()


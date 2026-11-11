"""
KSRTC Kalaburagi Division - Singleton Data Loader & Supabase Sync
Supports Ticket data_1 Day_City Service.xlsx, Dataset.xlsx, CSV, and data_sql (12).json.
Caches cleaned records in data/processed/tickets.pkl for sub-20ms instant server startup
and synchronizes with Supabase cloud database when available.
"""
import os
import json
import pickle
from pathlib import Path
import pandas as pd
try:
    from .data_cleaner import clean_ticket_data
    from .supabase_client import supabase, is_supabase_configured
except ImportError:
    from data_cleaner import clean_ticket_data
    from supabase_client import supabase, is_supabase_configured

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
BACKUP_DIR = BASE_DIR / "data" / "backups"
CACHE_PATH = PROCESSED_DIR / "tickets.pkl"

# File candidates in order of priority
CANDIDATE_FILES = [
    RAW_DIR / "data_sql (12).json",
    BASE_DIR / "data_sql (12).json",
    BASE_DIR / "Ticket data_1 Day_City Service.xlsx",
    RAW_DIR / "Dataset.xlsx",
    BASE_DIR / "Dataset.xlsx",
]

_cached_df = None


def load_raw_data() -> pd.DataFrame:
    """Loads raw data from available local file (JSON/Excel/CSV)."""
    for candidate in CANDIDATE_FILES:
        if candidate.exists():
            c_str = str(candidate).lower()
            try:
                if c_str.endswith(".json"):
                    with open(candidate, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return pd.DataFrame(data)
                elif c_str.endswith(".xlsx") or c_str.endswith(".xls"):
                    return pd.read_excel(candidate)
                elif c_str.endswith(".csv"):
                    return pd.read_csv(candidate)
            except Exception as e:
                print(f"Warning: Failed reading {candidate}: {e}")

    raise FileNotFoundError(
        "No raw dataset found! Place 'Ticket data_1 Day_City Service.xlsx' or 'data_sql (12).json' in project folder."
    )


def load_from_supabase() -> pd.DataFrame:
    """Attempts to fetch the dataset from the Supabase tickets table (paginated)."""
    if not is_supabase_configured():
        return None
    try:
        print("🌐 Querying tickets from Supabase...")
        all_records = []
        offset = 0
        page_size = 1000
        while True:
            res = supabase.table("tickets").select("*").range(offset, offset + page_size - 1).execute()
            if not res.data:
                break
            all_records.extend(res.data)
            if len(res.data) < page_size:
                break
            offset += page_size

        if all_records:
            df = pd.DataFrame(all_records)
            print(f"✅ Fetched all {len(df):,} tickets from Supabase cloud database!")
            return df
    except Exception as e:
        print(f"⚠️ Could not pull data from Supabase: {e}")
    return None


def get_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Returns the cleaned Pandas DataFrame.
    1. In-memory cache
    2. Local pickle cache (sub-20ms)
    3. Supabase cloud database
    4. Local raw file re-cleaning
    """
    global _cached_df
    if _cached_df is not None and not force_reload:
        return _cached_df

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Check disk cache
    if CACHE_PATH.exists() and not force_reload:
        try:
            with open(CACHE_PATH, "rb") as f:
                _cached_df = pickle.load(f)
            return _cached_df
        except Exception:
            pass

    # 2. Try Supabase cloud database if configured
    if is_supabase_configured():
        cloud_df = load_from_supabase()
        if cloud_df is not None and not cloud_df.empty:
            _cached_df = cloud_df
            with open(CACHE_PATH, "wb") as f:
                pickle.dump(_cached_df, f)
            return _cached_df

    # 3. Fallback to re-cleaning raw local files
    print("Loading and cleaning raw KSRTC ticket dataset...")
    raw_df = load_raw_data()
    cleaned_df = clean_ticket_data(raw_df)

    # Cache to disk
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cleaned_df, f)

    _cached_df = cleaned_df
    print(f"Dataset cached successfully! Total transactions: {len(_cached_df):,}")
    return _cached_df


def update_dataset(raw_df: pd.DataFrame, mode: str = "replace") -> pd.DataFrame:
    """Updates dataset from an uploaded DataFrame (Excel/CSV/JSON), cleans, and syncs.
    If mode == 'replace', creates an automatic local backup in data/backups/ before overwriting.
    If mode == 'merge', concatenates with existing data and drops duplicate ticket records.
    """
    global _cached_df
    import datetime

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_new = clean_ticket_data(raw_df)

    if mode == "merge":
        try:
            current_df = get_data()
        except Exception:
            current_df = None

        if current_df is not None and not current_df.empty:
            merged_df = pd.concat([current_df, cleaned_new], ignore_index=True)
            subset_cols = [c for c in ['ticket_number', 'waybill_number', 'route', 'time'] if c in merged_df.columns]
            if subset_cols:
                merged_df = merged_df.drop_duplicates(subset=subset_cols, keep='last')
            else:
                merged_df = merged_df.drop_duplicates()
            cleaned_df = merged_df
        else:
            cleaned_df = cleaned_new
    else:
        # replace mode: create backup of current data first
        try:
            current_df = get_data()
            if current_df is not None and not current_df.empty:
                ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = BACKUP_DIR / f"tickets_backup_{ts}.csv"
                current_df.to_csv(backup_file, index=False)
                print(f"📦 Local backup snapshot saved: {backup_file}")
        except Exception as e:
            print(f"⚠️ Failed to create local backup: {e}")

        cleaned_df = cleaned_new

    # Cache locally
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(cleaned_df, f)
    _cached_df = cleaned_df

    # Sync to Supabase in background/thread if configured
    if is_supabase_configured():
        try:
            import math
            # Upload records
            print("Syncing newly updated dataset to Supabase...")
            safe_df = cleaned_df.where(pd.notnull(cleaned_df), None)
            records = safe_df.to_dict(orient="records")
            for r in records:
                for k, v in r.items():
                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                        r[k] = None
            if mode == "replace":
                try:
                    supabase.table("tickets").delete().neq("id", 0).execute()
                except Exception:
                    pass
            for i in range(0, len(records), 1000):
                supabase.table("tickets").insert(records[i : i + 1000]).execute()
            print("✅ Uploaded data synced to Supabase successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not sync to Supabase: {e}")

    return _cached_df


if __name__ == "__main__":
    df = get_data()
    print(f"Loaded {len(df)} rows. Columns: {df.columns.tolist()}")
    print(df[['route', 'passengers', 'collected_fare', 'subsidy_fare', 'is_shakti_scheme']].head(5))

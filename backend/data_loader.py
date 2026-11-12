"""
KSRTC Kalaburagi Division - Singleton Data Loader
Supports both Dataset.xlsx and data_sql (12).json.
Caches cleaned records in data/processed/tickets.pkl for sub-20ms instant server startup.
"""
import os
import json
import gzip
import pickle
import pandas as pd
<<<<<<< Updated upstream
from pathlib import Path
from data_cleaner import clean_ticket_data
=======
try:
    from .data_cleaner import clean_ticket_data
    from .supabase_client import supabase, is_supabase_enabled
except ImportError:
    from data_cleaner import clean_ticket_data
    from supabase_client import supabase, is_supabase_enabled
>>>>>>> Stashed changes

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXCEL_PATH = RAW_DIR / "Dataset.xlsx"
JSON_PATH = RAW_DIR / "data_sql (12).json"
CACHE_PATH = PROCESSED_DIR / "tickets.pkl"

<<<<<<< Updated upstream
=======
# File candidates in order of priority
CANDIDATE_FILES = [
    RAW_DIR / "sample_history.json.gz",
    RAW_DIR / "data_sql (12).json",
    BASE_DIR / "data_sql (12).json",
    BASE_DIR / "Ticket data_1 Day_City Service.xlsx",
    RAW_DIR / "Dataset.xlsx",
    BASE_DIR / "Dataset.xlsx",
]

>>>>>>> Stashed changes
_cached_df = None

def load_raw_data() -> pd.DataFrame:
<<<<<<< Updated upstream
    """Loads raw data preferring JSON if present (faster), otherwise Excel."""
    if JSON_PATH.exists():
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Warning: JSON load failed ({e}), falling back to Excel.")

    if EXCEL_PATH.exists():
        return pd.read_excel(EXCEL_PATH)
=======
    """Loads raw data from available local file (JSON/Excel/CSV)."""
    for candidate in CANDIDATE_FILES:
        if candidate.exists():
            c_str = str(candidate).lower()
            try:
                if c_str.endswith(".json"):
                    with open(candidate, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    return pd.DataFrame(data)
                elif c_str.endswith(".json.gz"):
                    with gzip.open(candidate, "rt", encoding="utf-8") as f:
                        return pd.DataFrame(json.load(f))
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
    if not is_supabase_enabled():
        return None
    try:
        print("Querying tickets from Supabase...")
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
            print(f"Fetched {len(df):,} tickets from Supabase cloud database.")
            return df
    except Exception as e:
        print(f"Could not pull data from Supabase: {e}")
    return None
>>>>>>> Stashed changes

    raise FileNotFoundError(f"Neither {JSON_PATH} nor {EXCEL_PATH} found!")

def get_data(force_reload: bool = False) -> pd.DataFrame:
    """
    Returns the cleaned Pandas DataFrame.
    Uses in-memory cache first, then disk pickle cache, then re-cleans raw files.
    """
    global _cached_df
    if _cached_df is not None and not force_reload:
        return _cached_df

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Generate the reproducible demo week before resolving data sources.
    if not (RAW_DIR / "sample_history.json.gz").exists():
        try:
            from .sample_data import generate_history
        except ImportError:
            from sample_data import generate_history
        generate_history()

    # 1. Check disk cache
    if CACHE_PATH.exists() and not force_reload:
        try:
            with open(CACHE_PATH, 'rb') as f:
                _cached_df = pickle.load(f)
            if ('data_status' not in _cached_df.columns or
                    not pd.api.types.is_string_dtype(_cached_df['date']) or
                    _cached_df['date'].nunique() < 15):
                _cached_df = None
            else:
                return _cached_df
        except Exception:
            pass

<<<<<<< Updated upstream
    # 2. Re-process from raw
=======
    # 2. Try Supabase cloud database if configured
    if is_supabase_enabled():
        cloud_df = load_from_supabase()
        if cloud_df is not None and not cloud_df.empty and cloud_df['date'].nunique() >= 7:
            _cached_df = cloud_df
            with open(CACHE_PATH, "wb") as f:
                pickle.dump(_cached_df, f)
            return _cached_df

    # 3. Fallback to re-cleaning raw local files
>>>>>>> Stashed changes
    print("Loading and cleaning raw KSRTC ticket dataset...")
    raw_df = load_raw_data()
    cleaned_df = clean_ticket_data(raw_df)

    # 3. Cache to disk
    with open(CACHE_PATH, 'wb') as f:
        pickle.dump(cleaned_df, f)

    _cached_df = cleaned_df
    print(f"Dataset cached successfully! Total transactions: {len(_cached_df):,}")
    return _cached_df

def update_dataset(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Updates dataset from an uploaded DataFrame, cleans and recaches."""
    global _cached_df
    cleaned_df = clean_ticket_data(raw_df)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, 'wb') as f:
        pickle.dump(cleaned_df, f)
    _cached_df = cleaned_df
<<<<<<< Updated upstream
=======

    # Sync to Supabase in background/thread if configured
    if is_supabase_enabled():
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

>>>>>>> Stashed changes
    return _cached_df

if __name__ == "__main__":
    df = get_data()
    print(f"Loaded {len(df)} rows. Columns: {df.columns.tolist()}")
    print(df[['route', 'passengers', 'collected_fare', 'subsidy_fare', 'is_shakti_scheme']].head(5))


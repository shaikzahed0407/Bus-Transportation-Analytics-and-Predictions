"""
KSRTC Kalaburagi Division - Singleton Data Loader
Supports both Dataset.xlsx and data_sql (12).json.
Caches cleaned records in data/processed/tickets.pkl for sub-20ms instant server startup.
"""
import os
import json
import pickle
import pandas as pd
from pathlib import Path
from data_cleaner import clean_ticket_data

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EXCEL_PATH = RAW_DIR / "Dataset.xlsx"
JSON_PATH = RAW_DIR / "data_sql (12).json"
CACHE_PATH = PROCESSED_DIR / "tickets.pkl"

_cached_df = None

def load_raw_data() -> pd.DataFrame:
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

    # 1. Check disk cache
    if CACHE_PATH.exists() and not force_reload:
        try:
            with open(CACHE_PATH, 'rb') as f:
                _cached_df = pickle.load(f)
            return _cached_df
        except Exception:
            pass

    # 2. Re-process from raw
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
    return _cached_df

if __name__ == "__main__":
    df = get_data()
    print(f"Loaded {len(df)} rows. Columns: {df.columns.tolist()}")
    print(df[['route', 'passengers', 'collected_fare', 'subsidy_fare', 'is_shakti_scheme']].head(5))


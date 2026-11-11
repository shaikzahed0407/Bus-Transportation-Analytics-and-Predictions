import os
from pathlib import Path
from supabase import create_client, Client

# Auto-load .env file from project root if present
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = None

if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    except Exception as e:
        print(f"⚠️ Warning: Could not connect to Supabase: {e}")
else:
    print("ℹ️ Supabase credentials not set. Running in local/offline cache mode.")

def is_supabase_configured() -> bool:
    """Returns True if Supabase client is actively configured."""
    return supabase is not None

def exec_sql(sql: str):
    """Execute arbitrary SQL using a Supabase RPC wrapper `exec_sql(sql TEXT)`."""
    if not supabase:
        raise RuntimeError("Supabase is not configured.")
    return supabase.rpc("exec_sql", {"sql": sql}).execute()

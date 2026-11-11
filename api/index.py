import sys
from pathlib import Path

# Ensure root directory and backend directory are in path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "backend"))

from backend.app import app

# Vercel entrypoint
handler = app


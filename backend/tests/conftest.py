from __future__ import annotations

import sys
from pathlib import Path

# Ensure "backend/" is on sys.path so "import app" works in any runner/cwd
ROOT = Path(__file__).resolve().parents[1]  # backend/
sys.path.insert(0, str(ROOT))
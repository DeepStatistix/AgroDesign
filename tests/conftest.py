import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")

# Add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

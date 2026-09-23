import sys
from pathlib import Path


LAB02_DIR = Path(__file__).resolve().parents[1]
if str(LAB02_DIR) not in sys.path:
    sys.path.insert(0, str(LAB02_DIR))
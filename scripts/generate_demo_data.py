import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import pipeline as _
from src.synthetic.generator import generate_all
from src.constants import DATA_SYNTHETIC

if __name__ == "__main__":
    truth, fc = generate_all()
    DATA_SYNTHETIC.mkdir(parents=True, exist_ok=True)
    truth.to_parquet(DATA_SYNTHETIC / "truth.parquet", index=False)
    fc.to_parquet(DATA_SYNTHETIC / "forecasts.parquet", index=False)
    print(f"Synthetic truth rows: {len(truth)}, forecast rows: {len(fc)} -> {DATA_SYNTHETIC}")

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import pipeline

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--quick", action="store_true")
    p.add_argument("--disable", nargs="*", default=None, help="Simulate source failure")
    args = p.parse_args()
    avail = None
    if args.disable:
        from src.constants import SOURCES
        avail = [s for s in SOURCES if s not in args.disable]
    r = pipeline.run_pipeline(available_sources=avail, quick=args.quick)
    print("Run:", r["run_id"], "duration:", r["duration_s"], "s")
    print("Fallback:", r["fallback"])
    print("Coverage:", r["coverage"])

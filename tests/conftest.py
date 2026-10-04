import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def small_truth():
    from src import config
    from src.synthetic.generator import generate_truth_and_context
    cfg = dict(config.pipeline(), cycles_days=6)
    return generate_truth_and_context(cfg, seed=1)


@pytest.fixture(scope="session")
def small_fc(small_truth):
    from src import config
    from src.synthetic.generator import generate_source_forecasts
    return generate_source_forecasts(small_truth, config.sources(), seed=2)

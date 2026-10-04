"""KiWi core constants. All values demo/synthetic labelled."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIGS = ROOT / "configs"
DATA = ROOT / "data"
DATA_SYNTHETIC = DATA / "synthetic"
DATA_PROCESSED = DATA / "processed"
DATA_ARTIFACTS = DATA / "artifacts"
MODELS = ROOT / "models"
MODELS_GATES = MODELS / "gates"
MODELS_CALIBRATION = MODELS / "calibration"
MODELS_METADATA = MODELS / "metadata"
REPORTS = ROOT / "reports"

APP_VERSION = "1.0"
DATA_MODE = "DEMO"
TREEGATE_VERSION = "treegate-1.0"
BIAS_VERSION = "bias-1.0"
CAL_VERSION = "calibration-1.0"
REGIME_VERSION = "regime-1.0"

VARIABLES = ["rainfall", "temperature", "wind"]
UNITS = {"rainfall": "mm", "temperature": "degC", "wind": "m/s"}
LEAD_BUCKETS = [6, 12, 24, 48, 72]

SOURCES = {
    "GFS": {"type": "NWP", "version": "gfs-demo-1.0"},
    "ECMWF": {"type": "NWP", "version": "ecmwf-demo-1.0"},
    "IMD-WRF": {"type": "NWP", "version": "imdwrf-demo-1.0"},
    "GraphCast": {"type": "AI/ML", "version": "graphcast-demo-1.0"},
    "Pangu": {"type": "AI/ML", "version": "pangu-demo-1.0"},
    "ENS": {"type": "ENSEMBLE", "version": "ens-demo-1.0"},
}

REGIMES = ["Stable", "Normal Rain", "Convective", "Heavy Rain",
           "Heatwave", "High Wind", "Transition"]

REGIONS = ["North", "West", "Central", "South", "East"]

# Synthetic grid: India-focused, coarse but inspectable
LAT_MIN, LAT_MAX, LAT_STEP = 10.0, 30.0, 2.5
LON_MIN, LON_MAX, LON_STEP = 70.0, 88.0, 2.5

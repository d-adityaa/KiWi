"""Synthetic India-focused weather simulation engine (DEMO data only).

Produces: truth, source forecasts (with context-dependent errors),
ensemble members, context fields, regime labels. All deterministic.
"""
from __future__ import annotations
import itertools
import numpy as np
import pandas as pd
from scipy.ndimage import uniform_filter

from src.constants import (SOURCES, LEAD_BUCKETS, VARIABLES, LAT_MIN, LAT_MAX,
                           LAT_STEP, LON_MIN, LON_MAX, LON_STEP)


def make_grid():
    lats = np.arange(LAT_MIN, LAT_MAX + 1e-6, LAT_STEP)
    lons = np.arange(LON_MIN, LON_MAX + 1e-6, LON_STEP)
    cells = [(round(float(a), 2), round(float(o), 2)) for a, o in itertools.product(lats, lons)]
    return cells


def region_of(lat, lon):
    if lat >= 26.0:
        return "North"
    if lat < 20.0 and lon >= 75.0:
        return "South"
    if lon < 76.5 and lat < 26.0:
        return "West"
    if lon >= 83.0 and lat >= 20.0:
        return "East"
    return "Central"


def _smooth(field, it=3):
    out = field.copy()
    for _ in range(it):
        out = uniform_filter(out, size=3, mode="nearest")
    return out


def season_of(dayofyear: int) -> str:
    if dayofyear in range(60, 91):
        return "pre_monsoon"
    if dayofyear in range(91, 243):
        return "monsoon"
    if dayofyear in range(243, 335):
        return "post_monsoon"
    return "winter"


def generate_truth_and_context(cfg: dict, seed: int = 42) -> pd.DataFrame:
    """Daily truth fields on grid for cfg['cycles_days'] cycles."""
    rng = np.random.default_rng(seed)
    cells = make_grid()
    n_days = cfg.get("cycles_days", 60)
    start = pd.Timestamp("2026-01-01")
    lats = np.array([c[0] for c in cells])
    lons = np.array([c[1] for c in cells])
    n = len(cells)
    lat2d = lats.reshape(int(len(set(lats))), int(len(set(lons))))
    rows = []
    for d in range(n_days):
        t = start + pd.Timedelta(days=d)
        doy = t.timetuple().tm_yday
        seas = season_of(doy)
        # wet season modulation
        wet = {"monsoon": 1.0, "pre_monsoon": 0.6, "post_monsoon": 0.4, "winter": 0.12}[seas]
        base_rain = _smooth(rng.gamma(shape=1.2, scale=8.0 * wet + 0.2, size=lat2d.shape))
        rain = np.clip(base_rain * (lat2d > 26) * 0.7 + base_rain, 0, 220).ravel()
        temp = (28 - (lats - 20) * 0.25 + 6 * np.sin((doy - 80) / 365 * 2 * np.pi)
                + _smooth(rng.normal(0, 1.4, size=lat2d.shape)).ravel()
                + np.where(rain > 40, -3.0, 0.0))
        wind = np.clip(_smooth(rng.gamma(shape=2.0, scale=2.6, size=lat2d.shape)).ravel()
                       + np.where(rain > 40, 4.0, 0.0), 0, 25)
        humid = np.clip(55 + wet * 35 + _smooth(rng.normal(0, 6, lat2d.shape)).ravel(), 15, 100)
        cape = np.clip(_smooth(rng.gamma(1.4, 220 * wet + 40, lat2d.shape)).ravel(), 0, 2500)
        for i, (lat, lon) in enumerate(cells):
            rows.append({
                "time": t, "latitude": lat, "longitude": lon,
                "cell_id": f"{lat:.1f}_{lon:.1f}", "region": region_of(lat, lon),
                "rainfall": round(float(rain[i]), 2),
                "temperature": round(float(temp[i]), 2),
                "wind": round(float(wind[i]), 2),
                "humidity": round(float(humid[i]), 1),
                "cape": round(float(cape[i]), 1),
                "season": seas, "dayofyear": doy,
            })
    df = pd.DataFrame(rows)
    df["regime"] = df.apply(classify_regime, axis=1)
    return df


def regime_from_row(r: pd.Series) -> str:
    return classify_regime(r)


def classify_regime(r) -> str:
    rain = r["rainfall"]; temp = r["temperature"]; wind = r["wind"]; humid = r["humidity"]
    if rain >= 64:
        return "Heavy Rain"
    if wind >= 12:
        return "High Wind"
    if temp >= 40:
        return "Heatwave"
    if rain >= 15 and humid >= 70:
        return "Convective"
    if rain >= 1:
        return "Normal Rain"
    if rain < 1 and temp < 38:
        return "Stable"
    return "Transition"


def generate_source_forecasts(truth: pd.DataFrame, sources_cfg: dict, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    profiles = sources_cfg["profiles"]
    out = []
    truth = truth.copy()
    truth["regime"] = truth.apply(classify_regime, axis=1)
    regime_mult = {s: p["regime_strength"] for s, p in profiles.items()}
    for sid, prof in profiles.items():
        n_members = prof.get("members", 1)
        for m in range(max(n_members, 1)):
            for var in VARIABLES:
                bias = prof["bias"][var]
                base_noise = prof["noise"][var]
                lead_bias = 0.0
                for r in LEAD_BUCKETS:
                    sub = truth[truth["rainfall"] >= 0]
                    # deterministic pseudo lead-effect: error grows with lead
                    scale = base_noise * (1 + prof["lead_penalty"] * (r / 24.0))
                    err_mult = truth["regime"].map(regime_mult[sid]).fillna(1.0)
                    noise = rng.normal(0, 1, size=len(truth)) * scale * err_mult
                    val = truth[var].to_numpy() + bias * (r / 24.0) + noise
                    if var == "rainfall":
                        val = np.clip(val, 0, 400)
                    elif var == "temperature":
                        val = np.clip(val, -10, 50)
                    else:
                        val = np.clip(val, 0, 40)
                    df = pd.DataFrame({
                        "source_id": sid, "source_type": prof["source_type"],
                        "source_version": prof["version"],
                        "initialization_time": truth["time"] - pd.to_timedelta(r, unit="h"),
                        "valid_time": truth["time"], "lead_time": r,
                        "latitude": truth["latitude"].to_numpy(),
                        "longitude": truth["longitude"].to_numpy(),
                        "cell_id": truth["cell_id"].to_numpy(),
                        "region": truth["region"].to_numpy(),
                        "variable": var, "forecast_value": np.round(val, 2),
                        "unit": {"rainfall": "mm", "temperature": "degC", "wind": "m/s"}[var],
                        "ensemble_member": m if n_members > 1 else 0,
                        "regime": truth["regime"].to_numpy(),
                        "season": truth["season"].to_numpy(),
                    })
                    out.append(df)
    fc = pd.concat(out, ignore_index=True)
    fc["lead_bucket"] = fc["lead_time"]
    fc["metadata"] = "DEMO/SYNTHETIC"
    fc["week"] = (fc["valid_time"] - fc["valid_time"].min()).dt.days // 7
    fc["timestamp"] = fc["valid_time"]
    fc["cycle_id"] = fc["initialization_time"].dt.strftime("%Y%m%d") + "_" + fc["lead_time"].astype(str)
    return fc


def generate_all(cfg: dict | None = None, seed: int | None = None):
    from src import config
    cfg = cfg or config.pipeline()
    pipe = config.pipeline()
    seed = seed if seed is not None else pipe.get("seed", 42)
    truth = generate_truth_and_context(cfg, seed=seed)
    fc = generate_source_forecasts(truth, config.sources(), seed=seed + 5)
    return truth, fc

"""
observatory_v3.py
==================

NQ Market Behavior Observatory, v3 -- frozen spec:
research/studies/observatory-v3-design-spec.md.

Structurally different event family from v1 (reference-level touches)
and v2 (round numbers / swing pivots / open retest): OCCURRENCE events
-- a meaningful overnight gap, or an unusual volume-spike bar -- rather
than price touching a specific level. Baseline/ranking machinery
unchanged from v1/v2. Non-trading, exploratory ONLY.

HOW TO RUN:
    python3 src/observatory_v3.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_bar_behavior_batch1 import build_daily_bars
from volatility_conditioning import build_conditioning_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

HORIZONS = [1, 3, 5, 10, 15, 30]
TIME_BUCKETS = [
    ("open", "09:30", "10:30"),
    ("mid_morning", "10:30", "12:00"),
    ("midday", "12:00", "14:00"),
    ("afternoon", "14:00", "16:00"),
]
GAP_THRESH_MULT = 0.5
VOLUME_SPIKE_MULT = 3.0
VOLUME_LOOKBACK = 20
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_PROMISING = 40


def time_bucket_for(ts):
    t = ts.strftime("%H:%M")
    for name, start, end in TIME_BUCKETS:
        if start <= t < end:
            return name
    return None


def bootstrap_diff_ci(cond, base, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    c, b = np.asarray(cond, dtype=float), np.asarray(base, dtype=float)
    if len(c) < 2 or len(b) < 2:
        return float("nan"), float("nan")
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        cs = rng.choice(c, size=len(c), replace=True)
        bs = rng.choice(b, size=len(b), replace=True)
        diffs[i] = cs.mean() - bs.mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def main():
    print("=" * 78)
    print("NQ MARKET BEHAVIOR OBSERVATORY -- v3 (exploratory, non-trading)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/observatory-v3-design-spec.md\n")

    df, is_synthetic = load_price_data(context="observatory_v3.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    idx = discovery.index
    daily_bars = build_daily_bars(discovery)
    conditioning = build_conditioning_frame(discovery)
    day_groups = {d: g for d, g in discovery.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())
    print(f"Discovery days available: {len(days_sorted)}")

    def regime_for(day):
        if day not in conditioning.index:
            return "normal"
        row = conditioning.loc[day]
        if bool(row["prior_day_narrow"]):
            return "narrow"
        if bool(row["prior_day_wide"]):
            return "wide"
        return "normal"

    event_measurements = {}
    baseline_measurements = {}
    n_events_total = 0
    n_baseline_bars_total = 0

    def add(store, key, ret, mfe, mae):
        d = store.setdefault(key, {"return": [], "mfe": [], "mae": []})
        d["return"].append(ret)
        d["mfe"].append(mfe)
        d["mae"].append(mae)

    max_h = max(HORIZONS)

    for day_num, day in enumerate(days_sorted):
        if day_num == 0:
            continue
        prior_day = days_sorted[day_num - 1]
        if prior_day not in daily_bars.index:
            continue
        prior_close = float(daily_bars.loc[prior_day, "Close"]) if "Close" in daily_bars.columns else None
        prior_range = float(daily_bars.loc[prior_day, "High"] - daily_bars.loc[prior_day, "Low"])

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty or len(rth) < max_h + VOLUME_LOOKBACK + 5:
            continue

        regime = regime_for(day)
        high = rth["High"].values
        low = rth["Low"].values
        close = rth["Close"].values
        volume = rth["Volume"].values
        times = rth.index
        n = len(rth)

        if n - 1 - max_h < 1:
            continue
        fwd_high_windows = np.lib.stride_tricks.sliding_window_view(high[1:], max_h)
        fwd_low_windows = np.lib.stride_tricks.sliding_window_view(low[1:], max_h)
        n_valid = fwd_high_windows.shape[0]

        def measure(i):
            out = {}
            for h in HORIZONS:
                fwd_close_idx = i + h
                if fwd_close_idx >= n:
                    return None
                ret = float(close[fwd_close_idx] - close[i])
                mfe = float(fwd_high_windows[i, :h].max() - close[i])
                mae = float(close[i] - fwd_low_windows[i, :h].min())
                out[h] = (ret, mfe, mae)
            return out

        event_bar_idxs = set()

        # --- gap event: measured once, at the open bar (i=0) ---
        if prior_close is not None and prior_range > 0:
            gap = float(close[0] - prior_close)
            if abs(gap) >= GAP_THRESH_MULT * prior_range and 0 < n_valid:
                et = "overnight_gap_up" if gap > 0 else "overnight_gap_down"
                bucket = time_bucket_for(times[0])
                m = measure(0)
                if bucket is not None and m is not None:
                    n_events_total += 1
                    for h, (ret, mfe, mae) in m.items():
                        add(event_measurements, (et, regime, bucket, h), ret, mfe, mae)
                    for k in range(0, min(n_valid, max_h + 1)):
                        event_bar_idxs.add(k)

        # --- volume spike: first occurrence per day ---
        for i in range(VOLUME_LOOKBACK, n_valid):
            avg_vol = float(volume[i - VOLUME_LOOKBACK:i].mean())
            if avg_vol <= 0:
                continue
            if volume[i] >= VOLUME_SPIKE_MULT * avg_vol:
                bucket = time_bucket_for(times[i])
                if bucket is None:
                    continue
                m = measure(i)
                if m is None:
                    continue
                n_events_total += 1
                for h, (ret, mfe, mae) in m.items():
                    add(event_measurements, ("volume_spike", regime, bucket, h), ret, mfe, mae)
                for k in range(max(0, i - max_h), min(n_valid, i + max_h + 1)):
                    event_bar_idxs.add(k)
                break

        for i in range(0, n_valid, 5):
            if i in event_bar_idxs:
                continue
            bucket = time_bucket_for(times[i])
            if bucket is None:
                continue
            m = measure(i)
            if m is None:
                continue
            n_baseline_bars_total += 1
            for h, (ret, mfe, mae) in m.items():
                add(baseline_measurements, (regime, bucket, h), ret, mfe, mae)

    print(f"\nTotal events measured (all types): {n_events_total}")
    print(f"Total baseline bars measured: {n_baseline_bars_total}")

    combos_scanned = 0
    candidates = []

    for (et, regime, bucket, h), ev in event_measurements.items():
        base_key = (regime, bucket, h)
        base = baseline_measurements.get(base_key)
        if base is None or len(base["return"]) < 20:
            continue
        combos_scanned += 1
        n_ev = len(ev["return"])
        if n_ev < 5:
            continue
        cond_ret = np.array(ev["return"])
        base_ret = np.array(base["return"])
        effect_size = float(cond_ret.mean() - base_ret.mean())
        ci = bootstrap_diff_ci(cond_ret, base_ret)
        third = max(1, n_ev // 3)
        thirds_means = [
            float(cond_ret[:third].mean() - base_ret.mean()) if third > 0 else float("nan"),
            float(cond_ret[third:2 * third].mean() - base_ret.mean()) if n_ev > third else float("nan"),
            float(cond_ret[2 * third:].mean() - base_ret.mean()) if n_ev > 2 * third else float("nan"),
        ]
        signs = [np.sign(x) for x in thirds_means if not np.isnan(x)]
        consistent_sign = len(set(signs)) <= 1 and len(signs) >= 2
        concentration = float(np.max(np.abs(cond_ret - cond_ret.mean())) / (np.abs(effect_size) * n_ev)) if effect_size != 0 else float("inf")
        concentrated = concentration > 0.5

        if n_ev >= MIN_N_FOR_PROMISING and (ci[0] > 0 or ci[1] < 0) and consistent_sign and not concentrated:
            label = "Promising"
        elif n_ev >= 15 and (ci[0] > 0 or ci[1] < 0):
            label = "Interesting"
        elif abs(effect_size) > 0.05 * (abs(base_ret.mean()) + 1e-9):
            label = "Weak"
        else:
            label = "No meaningful difference"

        candidates.append({
            "event_type": et, "regime": regime, "time_bucket": bucket, "horizon_min": h,
            "n": n_ev, "conditional_mean_return": float(cond_ret.mean()),
            "baseline_mean_return": float(base_ret.mean()), "effect_size": effect_size,
            "ci_90_diff": ci, "consistent_sign_across_thirds": consistent_sign,
            "concentration_ratio": concentration, "label": label,
        })

    candidates.sort(key=lambda c: (0 if c["label"] == "Promising" else 1 if c["label"] == "Interesting" else 2, -c["n"]))
    label_counts = {}
    for c in candidates:
        label_counts[c["label"]] = label_counts.get(c["label"], 0) + 1

    print(f"\nCombinations scanned: {combos_scanned}")
    print(f"Label breakdown: {label_counts}")
    print("\nTop 15 candidates:")
    for c in candidates[:15]:
        print(f"  [{c['label']}] {c['event_type']} | {c['regime']} | {c['time_bucket']} | {c['horizon_min']}min | "
              f"n={c['n']} effect={c['effect_size']:.3f} ci={c['ci_90_diff']}")

    out = {
        "spec": "research/studies/observatory-v3-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "combinations_scanned": combos_scanned,
        "total_events": n_events_total,
        "total_baseline_bars": n_baseline_bars_total,
        "label_breakdown": label_counts,
        "candidates": candidates,
    }
    out_path = DATA_DIR / "observatory_v3_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full candidate list to {out_path}.")


if __name__ == "__main__":
    main()

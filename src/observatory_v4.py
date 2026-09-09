"""
observatory_v4.py
==================

NQ Market Behavior Observatory, v4 -- frozen spec:
research/studies/observatory-v4-design-spec.md.

New event family vs v1/v2/v3: first RTH touch of the prior CALENDAR
WEEK's or prior CALENDAR MONTH's high/low (multi-day reference levels,
a different time scale from anything scanned before). Baseline/ranking
machinery unchanged from v1, plus a new ATR-normalized effect-size
column used only to flag LOW-PRIORITY candidates for hypothesis-writing
triage (does not discard or alter statistical labels).

Non-trading, exploratory ONLY. Discovery data only.

HOW TO RUN:
    python3 src/observatory_v4.py
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
EVENT_TYPES = ["prior_week_high", "prior_week_low", "prior_month_high", "prior_month_low"]
N_BOOTSTRAP = 3000
RANDOM_SEED = 7
MIN_N_FOR_PROMISING = 40
ATR_WINDOW = 14
ATR_NORMALIZED_FLOOR = 0.05


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


def build_weekly_monthly_levels(daily_bars: pd.DataFrame) -> pd.DataFrame:
    """For each day, the prior FULLY-COMPLETED calendar week's and
    calendar month's High/Low, known as of that day's open (no
    lookahead: only weeks/months strictly before the current one)."""
    idx = pd.to_datetime(pd.Series(daily_bars.index))
    week_key = idx.dt.to_period("W-FRI").values
    month_key = idx.dt.to_period("M").values
    df = daily_bars.copy()
    df["week_key"] = week_key
    df["month_key"] = month_key

    week_hl = df.groupby("week_key").agg(week_high=("High", "max"), week_low=("Low", "min"))
    month_hl = df.groupby("month_key").agg(month_high=("High", "max"), month_low=("Low", "min"))

    weeks_sorted = list(week_hl.index)
    months_sorted = list(month_hl.index)
    week_prior_map = {weeks_sorted[i]: weeks_sorted[i - 1] for i in range(1, len(weeks_sorted))}
    month_prior_map = {months_sorted[i]: months_sorted[i - 1] for i in range(1, len(months_sorted))}

    df["prior_week_high"] = df["week_key"].map(week_prior_map).map(week_hl["week_high"])
    df["prior_week_low"] = df["week_key"].map(week_prior_map).map(week_hl["week_low"])
    df["prior_month_high"] = df["month_key"].map(month_prior_map).map(month_hl["month_high"])
    df["prior_month_low"] = df["month_key"].map(month_prior_map).map(month_hl["month_low"])
    return df[["prior_week_high", "prior_week_low", "prior_month_high", "prior_month_low"]]


def main():
    print("=" * 78)
    print("NQ MARKET BEHAVIOR OBSERVATORY -- v4 (multi-day levels, exploratory)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/observatory-v4-design-spec.md\n")

    df, is_synthetic = load_price_data(context="observatory_v4.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    tz = discovery.index.tz
    idx = discovery.index

    daily_bars = build_daily_bars(discovery)
    daily_bars = daily_bars.copy()
    daily_bars["range"] = daily_bars["High"] - daily_bars["Low"]
    daily_bars["atr14"] = daily_bars["range"].rolling(ATR_WINDOW).mean()
    conditioning = build_conditioning_frame(discovery)
    levels = build_weekly_monthly_levels(daily_bars)

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

    def add(store, key, ret):
        store.setdefault(key, []).append(ret)

    max_h = max(HORIZONS)

    for day_num, day in enumerate(days_sorted):
        if day not in daily_bars.index or day not in levels.index:
            continue
        lv = levels.loc[day]
        if lv.isna().any():
            continue
        atr = daily_bars.loc[day, "atr14"]
        if pd.isna(atr) or atr <= 0:
            continue
        atr = float(atr)

        day_df = day_groups[day]
        rth = day_df.between_time("09:30", "16:00")
        if rth.empty or len(rth) < max_h + 5:
            continue

        regime = regime_for(day)
        high = rth["High"].values
        low = rth["Low"].values
        close = rth["Close"].values
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
                out[h] = float(close[fwd_close_idx] - close[i])
            return out

        touched = {et: False for et in EVENT_TYPES}
        levels_vals = {
            "prior_week_high": float(lv["prior_week_high"]), "prior_week_low": float(lv["prior_week_low"]),
            "prior_month_high": float(lv["prior_month_high"]), "prior_month_low": float(lv["prior_month_low"]),
        }
        for i in range(n_valid):
            bucket = time_bucket_for(times[i])
            if bucket is None:
                continue
            levels_hit = []
            for et, lvl in levels_vals.items():
                if not touched[et] and high[i] >= lvl >= low[i]:
                    levels_hit.append(et)
            if not levels_hit:
                continue
            m = measure(i)
            if m is None:
                continue
            for et in levels_hit:
                touched[et] = True
                n_events_total += 1
                for h, ret in m.items():
                    add(event_measurements, (et, regime, bucket, h), ret)

        event_bar_idxs = set()
        touched2 = {et: False for et in EVENT_TYPES}
        for i in range(n_valid):
            if all(touched2.values()):
                break
            hit_any = False
            for et, lvl in levels_vals.items():
                if not touched2[et] and high[i] >= lvl >= low[i]:
                    touched2[et] = True
                    hit_any = True
            if hit_any:
                for k in range(max(0, i - max_h), min(n_valid, i + max_h + 1)):
                    event_bar_idxs.add(k)

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
            for h, ret in m.items():
                add(baseline_measurements, (regime, bucket, h), ret)

    print(f"\nTotal events measured (all types): {n_events_total}")
    print(f"Total baseline bars measured: {n_baseline_bars_total}")

    avg_atr = float(daily_bars["atr14"].dropna().mean())
    print(f"Average ATR(14) over Discovery (for normalization): {avg_atr:.2f} pts")

    combos_scanned = 0
    candidates = []

    for (et, regime, bucket, h), cond_ret_list in event_measurements.items():
        base_key = (regime, bucket, h)
        base_ret_list = baseline_measurements.get(base_key)
        if base_ret_list is None or len(base_ret_list) < 20:
            continue
        combos_scanned += 1

        n_ev = len(cond_ret_list)
        if n_ev < 5:
            continue

        cond_ret = np.array(cond_ret_list)
        base_ret = np.array(base_ret_list)
        effect_size = float(cond_ret.mean() - base_ret.mean())
        ci = bootstrap_diff_ci(cond_ret, base_ret)
        atr_normalized_effect = abs(effect_size) / avg_atr if avg_atr > 0 else float("nan")

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

        priority = "LOW_PRIORITY_COST_DOMINATED" if atr_normalized_effect < ATR_NORMALIZED_FLOOR else "NORMAL"

        candidates.append({
            "event_type": et, "regime": regime, "time_bucket": bucket, "horizon_min": h,
            "n": n_ev, "conditional_mean_return": float(cond_ret.mean()),
            "baseline_mean_return": float(base_ret.mean()), "effect_size": effect_size,
            "atr_normalized_effect": atr_normalized_effect, "cost_priority": priority,
            "ci_90_diff": ci, "consistent_sign_across_thirds": consistent_sign,
            "concentration_ratio": concentration, "label": label,
        })

    candidates.sort(key=lambda c: (0 if c["label"] == "Promising" else 1 if c["label"] == "Interesting" else 2, -c["n"]))

    label_counts = {}
    for c in candidates:
        label_counts[c["label"]] = label_counts.get(c["label"], 0) + 1

    print(f"\nCombinations scanned (event x regime x bucket x horizon, with usable baseline): {combos_scanned}")
    print(f"Label breakdown: {label_counts}")
    print("\nTop 15 candidates:")
    for c in candidates[:15]:
        print(f"  [{c['label']}][{c['cost_priority']}] {c['event_type']} | {c['regime']} | {c['time_bucket']} | {c['horizon_min']}min | "
              f"n={c['n']} effect={c['effect_size']:.3f} atr_norm={c['atr_normalized_effect']:.4f} ci={c['ci_90_diff']}")

    out = {
        "spec": "research/studies/observatory-v4-design-spec.md",
        "status": "EXPLORATORY -- not a finding, not a strategy",
        "combinations_scanned": combos_scanned,
        "total_events": n_events_total,
        "total_baseline_bars": n_baseline_bars_total,
        "avg_atr14": avg_atr,
        "label_breakdown": label_counts,
        "candidates": candidates,
    }
    out_path = DATA_DIR / "observatory_v4_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full candidate list to {out_path}.")


if __name__ == "__main__":
    main()

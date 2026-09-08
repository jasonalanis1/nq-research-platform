"""
study_pre_move_behavior_batch1.py
=================================

exp-100/101 -- frozen spec: research/studies/pre-move-behavior-batch1-spec.md.
Two FRESH setups (detection + entry/stop/target built from scratch, not
overlays on existing signals): volume-vacuum continuation and
multi-timeframe trend alignment. Per Jason's direction: build around a
"something is about to happen" behavior, not conditioning old setups.

STEP 1 + STEP 2 together (real entry/stop/target, costed via
backtest.simulate_trade). Search batch ID:
batch-2026-09-08-pre-move-behavior-1.

REUSED, UNMODIFIED: backtest.simulate_trade, backtest.ROUND_TRIP_COST_POINTS,
detect_level_sweep.TARGET_R_MULTIPLE.

HOW TO RUN:
    python3 src/study_pre_move_behavior_batch1.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from backtest import simulate_trade, ROUND_TRIP_COST_POINTS
from detect_level_sweep import TARGET_R_MULTIPLE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
SEARCH_BATCH_ID = "batch-2026-09-08-pre-move-behavior-1"
MIN_PROSPECTIVE_N = 40
MIN_ECONOMIC_R = 0.05

# exp-100 settings
VACUUM_LOOKBACK_BARS = 60
VACUUM_PCTL = 20
VACUUM_WINDOW_BARS = 5
VACUUM_WATCH_BARS = 15

# exp-101 settings
CHECKPOINTS = [(10, 30), (11, 30), (12, 30), (13, 30), (14, 30)]


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    if n < 2:
        return float("nan"), float("nan")
    means = np.empty(n_bootstrap)
    idx_pool = np.arange(n)
    for i in range(n_bootstrap):
        idx = rng.choice(idx_pool, size=n, replace=True)
        means[i] = arr[idx].mean()
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def analyze_r_multiples(r_multiples):
    n = len(r_multiples)
    if n < 2:
        return {"n": n, "statistically_credible": False, "economically_meaningful": False}
    arr = np.array(r_multiples, dtype=float)
    ci_low, ci_high = bootstrap_mean_ci(arr)
    credible = ci_low > 0
    mean_r = float(arr.mean())
    econ = mean_r >= MIN_ECONOMIC_R
    return {
        "n": n, "mean_r_multiple_net": mean_r, "ci_90": (ci_low, ci_high),
        "statistically_credible": bool(credible), "economically_meaningful": bool(econ),
    }


def simulate_signal(day_df, sig):
    """Run one signal through simulate_trade and return net R-multiple."""
    sig_series = pd.Series(sig)
    outcome = simulate_trade(day_df, sig_series, "signal_time")
    risk_points = abs(sig["entry"] - sig["stop"])
    if risk_points <= 0:
        return None
    if sig["direction"] == "long":
        pnl_gross = outcome["exit_price"] - sig["entry"]
    else:
        pnl_gross = sig["entry"] - outcome["exit_price"]
    is_resolved = not outcome["exit_reason"].startswith("unresolved")
    pnl_net = pnl_gross - ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
    return pnl_net / risk_points


def detect_vacuum_signals_for_day(day_df):
    """exp-100: volume vacuum continuation, one day's worth of 1-min bars."""
    signals = []
    n = len(day_df)
    if n < VACUUM_LOOKBACK_BARS + VACUUM_WINDOW_BARS + VACUUM_WATCH_BARS:
        return signals
    vol = day_df["Volume"].values
    high = day_df["High"].values
    low = day_df["Low"].values
    close = day_df["Close"].values

    i = VACUUM_LOOKBACK_BARS
    while i <= n - VACUUM_WINDOW_BARS - VACUUM_WATCH_BARS:
        trailing = vol[i - VACUUM_LOOKBACK_BARS:i]
        thresh = np.percentile(trailing, VACUUM_PCTL)
        window_vol = vol[i:i + VACUUM_WINDOW_BARS]
        if np.all(window_vol <= thresh):
            w_high = high[i:i + VACUUM_WINDOW_BARS].max()
            w_low = low[i:i + VACUUM_WINDOW_BARS].min()
            if w_high > w_low:
                watch_start = i + VACUUM_WINDOW_BARS
                watch_end = watch_start + VACUUM_WATCH_BARS
                fired = False
                for j in range(watch_start, watch_end):
                    if close[j] > w_high:
                        signals.append({
                            "signal_time": day_df.index[j], "direction": "long",
                            "entry": float(close[j]), "stop": float(w_low),
                            "target": float(close[j] + TARGET_R_MULTIPLE * (close[j] - w_low)),
                        })
                        fired = True
                        break
                    if close[j] < w_low:
                        signals.append({
                            "signal_time": day_df.index[j], "direction": "short",
                            "entry": float(close[j]), "stop": float(w_high),
                            "target": float(close[j] - TARGET_R_MULTIPLE * (w_high - close[j])),
                        })
                        fired = True
                        break
                if fired:
                    i = watch_end  # don't re-detect overlapping windows after a fired signal
                    continue
        i += 1
    return signals


def build_15min_bars(day_df):
    rows = []
    tz = day_df.index.tz
    day = day_df.index[0].date()
    bar_start = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
    day_end = pd.Timestamp(day, tz=tz).replace(hour=16, minute=0)
    while bar_start < day_end:
        bar_end = bar_start + pd.Timedelta(minutes=15)
        bar = day_df[(day_df.index >= bar_start) & (day_df.index < bar_end)]
        if not bar.empty:
            rows.append({"bar_start": bar_start, "Open": bar["Open"].iloc[0], "Close": bar["Close"].iloc[-1],
                         "High": bar["High"].max(), "Low": bar["Low"].min()})
        bar_start = bar_end
    return pd.DataFrame(rows).set_index("bar_start") if rows else pd.DataFrame()


def build_60min_bars_simple(day_df):
    rows = []
    tz = day_df.index.tz
    day = day_df.index[0].date()
    bar_start = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30)
    day_end = pd.Timestamp(day, tz=tz).replace(hour=16, minute=0)
    while bar_start < day_end:
        bar_end = bar_start + pd.Timedelta(minutes=60)
        bar = day_df[(day_df.index >= bar_start) & (day_df.index < bar_end)]
        if not bar.empty:
            rows.append({"bar_start": bar_start, "Open": bar["Open"].iloc[0], "Close": bar["Close"].iloc[-1]})
        bar_start = bar_end
    return pd.DataFrame(rows).set_index("bar_start") if rows else pd.DataFrame()


def detect_alignment_signal_for_day(day_df):
    """exp-101: multi-timeframe trend alignment, one signal max per day."""
    tz = day_df.index.tz
    day = day_df.index[0].date()
    day_open_bars = day_df[day_df.index <= pd.Timestamp(day, tz=tz).replace(hour=9, minute=31)]
    if day_open_bars.empty:
        return None
    day_open = day_open_bars["Open"].iloc[0]

    bars15 = build_15min_bars(day_df)
    bars60 = build_60min_bars_simple(day_df)
    if bars15.empty or bars60.empty:
        return None

    for hh, mm in CHECKPOINTS:
        checkpoint_ts = pd.Timestamp(day, tz=tz).replace(hour=hh, minute=mm)
        prior15 = bars15[bars15.index + pd.Timedelta(minutes=15) <= checkpoint_ts]
        prior60 = bars60[bars60.index + pd.Timedelta(minutes=60) <= checkpoint_ts]
        if prior15.empty or prior60.empty:
            continue
        last15 = prior15.iloc[-1]
        last60 = prior60.iloc[-1]
        fast_dir = 1 if last15["Close"] > last15["Open"] else (-1 if last15["Close"] < last15["Open"] else 0)
        med_dir = 1 if last60["Close"] > last60["Open"] else (-1 if last60["Close"] < last60["Open"] else 0)

        at_checkpoint = day_df[day_df.index <= checkpoint_ts]
        if at_checkpoint.empty:
            continue
        cur_price = at_checkpoint["Close"].iloc[-1]
        day_dir = 1 if cur_price > day_open else (-1 if cur_price < day_open else 0)

        if fast_dir != 0 and fast_dir == med_dir == day_dir:
            entry_bars = day_df[day_df.index > checkpoint_ts]
            if entry_bars.empty:
                continue
            entry_bar = entry_bars.iloc[0]
            entry_price = float(entry_bar["Open"])
            if fast_dir == 1:
                stop = float(last15["Low"])
                risk = entry_price - stop
                if risk <= 0:
                    continue
                target = entry_price + TARGET_R_MULTIPLE * risk
                direction = "long"
            else:
                stop = float(last15["High"])
                risk = stop - entry_price
                if risk <= 0:
                    continue
                target = entry_price - TARGET_R_MULTIPLE * risk
                direction = "short"
            return {
                "signal_time": entry_bars.index[0], "direction": direction,
                "entry": entry_price, "stop": stop, "target": target,
            }
    return None


def main():
    print("=" * 78)
    print("EXP-100/101: FRESH PRE-MOVE BEHAVIOR SETUPS")
    print("=" * 78)
    print("\nFrozen spec: research/studies/pre-move-behavior-batch1-spec.md\n")

    df, is_synthetic = load_price_data(context="study_pre_move_behavior_batch1.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    session = discovery.between_time("09:30", "16:00")
    day_groups = {d: g for d, g in session.groupby(session.index.date)}
    print(f"Discovery RTH days: {len(day_groups)}")

    vacuum_r = []
    alignment_r = []

    for day, day_df in day_groups.items():
        vac_signals = detect_vacuum_signals_for_day(day_df)
        for sig in vac_signals:
            r = simulate_signal(day_df, sig)
            if r is not None:
                vacuum_r.append(r)

        align_sig = detect_alignment_signal_for_day(day_df)
        if align_sig is not None:
            r = simulate_signal(day_df, align_sig)
            if r is not None:
                alignment_r.append(r)

    print(f"\nexp-100 volume vacuum: {len(vacuum_r)} signals")
    print(f"exp-101 trend alignment: {len(alignment_r)} signals")

    results = {
        "exp100_volume_vacuum_continuation": analyze_r_multiples(vacuum_r),
        "exp101_multi_timeframe_alignment": analyze_r_multiples(alignment_r),
    }

    verdicts = {}
    for key, r in results.items():
        n = r.get("n", 0)
        if n == 0:
            verdicts[key] = "NO_DATA"
        elif r["statistically_credible"] and r["economically_meaningful"]:
            verdicts[key] = "STEP_1+2_PASS" if n >= MIN_PROSPECTIVE_N else "PASS_TOO_THIN_FOR_PROSPECTIVE"
        else:
            verdicts[key] = "STEP_1+2_FAIL"

    print()
    for key, r in results.items():
        print(f"{key}: {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")

    out = {"search_batch_id": SEARCH_BATCH_ID, "results": results, "verdicts": verdicts}
    out_path = DATA_DIR / "study_pre_move_behavior_batch1_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()

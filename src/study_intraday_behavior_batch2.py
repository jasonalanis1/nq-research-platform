"""
study_intraday_behavior_batch2.py
=====================================

exp-078/079/080 -- frozen spec: research/studies/intraday-behavior-batch2-spec.md.
First batch sourced from the Market Behavior Advisor role
(docs/MARKET_BEHAVIOR_ADVISOR.md) rather than Claude's own reasoning over
the ledger. All three conditions use only 1-min/daily OHLCV (no
order-book/tick data). Checked against the ledger for overlap first.

STEP 1 ONLY (statistical, no costs). Search batch ID:
batch-2026-09-08-intraday-behavior-2. No predicted sign pinned in
advance for any condition -- reports honestly either way.

HOW TO RUN:
    python3 src/study_intraday_behavior_batch2.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_overnight_gap import get_reference_close
from study_intraday_behavior_batch1 import bootstrap_mean_ci, build_daily_frame

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# exp-078
EFFORT_MULTIPLE = 3.0
EFFORT_TRAILING_BARS = 20
STALL_WINDOW_MIN = 5
STALL_RANGE_FRACTION = 0.5
STALL_MOVE_FRACTION = 0.3
FORWARD_HORIZON_MIN = 30

# exp-079
BASE_DAYS = 5
BASE_RANGE_MULTIPLE = 1.5

# exp-080
SHAPE_PCTL = 25


def analyze_effort_absorption(df: pd.DataFrame) -> dict:
    """exp-078: effort bars (range+volume >= 3x trailing 20-bar avg),
    classified stalled (absorbed) vs continued by their own next-5-min
    behavior, then measured over the following 30 minutes."""
    session = df.between_time("09:30", "16:00").copy()
    session["range"] = session["High"] - session["Low"]
    session["trailing_avg_range"] = session["range"].rolling(EFFORT_TRAILING_BARS, min_periods=EFFORT_TRAILING_BARS).mean().shift(1)
    session["trailing_avg_vol"] = session["Volume"].rolling(EFFORT_TRAILING_BARS, min_periods=EFFORT_TRAILING_BARS).mean().shift(1)
    session["bar_return"] = np.log(session["Close"] / session["Close"].shift(1))
    is_effort = (
        (session["range"] >= EFFORT_MULTIPLE * session["trailing_avg_range"])
        & (session["Volume"] >= EFFORT_MULTIPLE * session["trailing_avg_vol"])
        & session["trailing_avg_range"].notna() & (session["trailing_avg_range"] > 0)
        & session["trailing_avg_vol"].notna() & (session["trailing_avg_vol"] > 0)
        & session["bar_return"].notna() & (session["bar_return"] != 0)
    )
    effort_times = session.index[is_effort]
    close = session["Close"]

    stalled_rets, continued_rets = [], []
    for t in effort_times:
        direction = np.sign(session.loc[t, "bar_return"])
        effort_range = session.loc[t, "range"]
        effort_move = abs(session.loc[t, "bar_return"])

        stall_end = t + pd.Timedelta(minutes=STALL_WINDOW_MIN)
        stall_window = session[(session.index > t) & (session.index <= stall_end)]
        if stall_window.empty:
            continue
        stall_net_range = stall_window["High"].max() - stall_window["Low"].min()
        stall_net_move = abs(np.log(stall_window["Close"].iloc[-1] / close.loc[t]))
        is_stalled = (stall_net_range < STALL_RANGE_FRACTION * effort_range) and \
                     (stall_net_move < STALL_MOVE_FRACTION * effort_move)

        fwd_end = t + pd.Timedelta(minutes=FORWARD_HORIZON_MIN)
        future = close[(close.index > t) & (close.index <= fwd_end)]
        if future.empty:
            continue
        fwd_ret = np.log(future.iloc[-1] / close.loc[t])

        if is_stalled:
            stalled_rets.append(-direction * fwd_ret)  # reversal test: signed AGAINST effort direction
        else:
            continued_rets.append(direction * fwd_ret)  # continuation test: signed WITH effort direction

    results = {}
    for label, rets in (("stalled_reversal_test", stalled_rets), ("continued_continuation_test", continued_rets)):
        mean = float(np.mean(rets)) if rets else float("nan")
        ci = bootstrap_mean_ci(rets) if rets else (float("nan"), float("nan"))
        credible = bool(rets) and (ci[0] > 0 or ci[1] < 0)
        results[label] = {"n": len(rets), "mean": mean, "ci_90": ci, "statistically_credible": credible}
    return results


def analyze_base_breakout(daily: pd.DataFrame) -> dict:
    """exp-079: 5-day tight bases -> breakout-day direction -> next-day
    (breakout+1) return, signed with breakout day's own direction."""
    days_sorted = sorted(daily.index)
    day_to_idx = {d: i for i, d in enumerate(days_sorted)}
    rets = []
    for i in range(BASE_DAYS, len(days_sorted) - 1):
        base_days = days_sorted[i - BASE_DAYS:i]
        base_high = daily.loc[base_days, "High"].max()
        base_low = daily.loc[base_days, "Low"].min()
        base_range = base_high - base_low
        avg_single_day_range = daily.loc[base_days, "range"].mean()
        if avg_single_day_range <= 0 or np.isnan(avg_single_day_range):
            continue
        is_tight_base = base_range <= BASE_RANGE_MULTIPLE * avg_single_day_range
        if not is_tight_base:
            continue
        breakout_day = days_sorted[i]
        bo_close = daily.loc[breakout_day, "Close"]
        breaks_out = (daily.loc[breakout_day, "High"] > base_high) or (daily.loc[breakout_day, "Low"] < base_low)
        if not breaks_out:
            continue
        prior_close = daily.loc[days_sorted[i - 1], "Close"]
        breakout_direction = np.sign(np.log(bo_close / prior_close))
        if breakout_direction == 0:
            continue
        next_day = days_sorted[i + 1]
        next_ret = np.log(daily.loc[next_day, "Close"] / daily.loc[breakout_day, "Close"])
        rets.append(breakout_direction * next_ret)

    mean = float(np.mean(rets)) if rets else float("nan")
    ci = bootstrap_mean_ci(rets) if rets else (float("nan"), float("nan"))
    credible = bool(rets) and (ci[0] > 0 or ci[1] < 0)
    return {"n": len(rets), "mean_signed_next_day_return": mean, "ci_90": ci, "statistically_credible": credible}


def analyze_trend_day_shape(df: pd.DataFrame) -> dict:
    """exp-080: first-hour MAE% (retracement vs net move) -> afternoon
    continuation (10:30 to close), signed with first-hour's own direction."""
    rows = []
    for day, day_df in df.groupby(df.index.date):
        first_hour = day_df.between_time("09:30", "10:30")
        rest = day_df.between_time("10:30", "16:00")
        if len(first_hour) < 30 or rest.empty:
            continue
        open_px = first_hour["Open"].iloc[0]
        close_1h = first_hour["Close"].iloc[-1]
        net_move = np.log(close_1h / open_px)
        if net_move == 0:
            continue
        direction = np.sign(net_move)
        # MAE: worst point against the net move's direction, within the first hour
        cum_log = np.log(first_hour["Close"] / open_px)
        if direction > 0:
            mae = -cum_log.min() if cum_log.min() < 0 else 0.0
        else:
            mae = cum_log.max() if cum_log.max() > 0 else 0.0
        mae_pct = mae / abs(net_move)
        session_close = rest["Close"].iloc[-1]
        afternoon_ret = np.log(session_close / close_1h)
        rows.append({"date": day, "mae_pct": mae_pct, "direction": direction, "afternoon_ret": afternoon_ret})

    shape_df = pd.DataFrame(rows)
    if shape_df.empty:
        return {"trend_like": {"n": 0}, "choppy": {"n": 0}}
    low_thresh = np.percentile(shape_df["mae_pct"], SHAPE_PCTL)
    high_thresh = np.percentile(shape_df["mae_pct"], 100 - SHAPE_PCTL)

    results = {}
    for label, mask in (
        ("trend_like", shape_df["mae_pct"] <= low_thresh),
        ("choppy", shape_df["mae_pct"] >= high_thresh),
    ):
        subset = shape_df[mask]
        signed_rets = (subset["direction"] * subset["afternoon_ret"]).tolist()
        mean = float(np.mean(signed_rets)) if signed_rets else float("nan")
        ci = bootstrap_mean_ci(signed_rets) if signed_rets else (float("nan"), float("nan"))
        credible = bool(signed_rets) and (ci[0] > 0 or ci[1] < 0)
        results[label] = {"n": len(signed_rets), "mean_signed_afternoon_return": mean, "ci_90": ci, "statistically_credible": credible}
    return results


def main():
    print("=" * 78)
    print("INTRADAY BEHAVIOR BATCH 2 (Market Behavior Advisor-sourced):")
    print("exp-078 (effort/absorption), exp-079 (base breakout), exp-080")
    print("(trend-day shape) -- Step 1 only")
    print("=" * 78)
    print("\nFrozen spec: research/studies/intraday-behavior-batch2-spec.md")
    print("search_batch_id: batch-2026-09-08-intraday-behavior-2\n")

    df, is_synthetic = load_price_data(context="study_intraday_behavior_batch2.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_frame(discovery)

    print("--- exp-078: Effort-vs-result absorption ---")
    absorption = analyze_effort_absorption(discovery)
    for label, r in absorption.items():
        print(f"  {label}: n={r['n']} mean={r['mean']:.6f} ci_90={r['ci_90']} credible={r['statistically_credible']}")

    print("\n--- exp-079: Multi-day base-building breakout ---")
    base_breakout = analyze_base_breakout(daily)
    print(f"  n={base_breakout['n']} mean_signed_next_day_return={base_breakout['mean_signed_next_day_return']:.6f} "
          f"ci_90={base_breakout['ci_90']} credible={base_breakout['statistically_credible']}")

    print("\n--- exp-080: Trend-day character from first-hour shape ---")
    trend_shape = analyze_trend_day_shape(discovery)
    for label, r in trend_shape.items():
        if r.get("n", 0) == 0:
            print(f"  {label}: n=0, skipped")
            continue
        print(f"  {label}: n={r['n']} mean_signed_afternoon_return={r['mean_signed_afternoon_return']:.6f} "
              f"ci_90={r['ci_90']} credible={r['statistically_credible']}")

    print("\n" + "=" * 78)
    verdicts = {}
    for key, r in absorption.items():
        verdicts[f"absorption_{key}"] = "STEP_1_PASS" if r["statistically_credible"] else "STEP_1_FAIL"
    verdicts["base_breakout"] = "STEP_1_PASS" if base_breakout["statistically_credible"] else "STEP_1_FAIL"
    for key, r in trend_shape.items():
        if r.get("n", 0) == 0:
            verdicts[f"trend_shape_{key}"] = "SKIPPED_NO_DATA"
        else:
            verdicts[f"trend_shape_{key}"] = "STEP_1_PASS" if r["statistically_credible"] else "STEP_1_FAIL"
    for k, v in verdicts.items():
        print(f"  {k}: {v}")

    out = {
        "search_batch_id": "batch-2026-09-08-intraday-behavior-2",
        "effort_absorption": absorption,
        "base_breakout": base_breakout,
        "trend_day_shape": trend_shape,
        "verdicts": verdicts,
    }
    out_path = DATA_DIR / "study_intraday_behavior_batch2_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()

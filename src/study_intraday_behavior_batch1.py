"""
study_intraday_behavior_batch1.py
=====================================

exp-072/073/074 -- frozen spec: research/studies/intraday-behavior-batch1-spec.md.
First batch of genuinely intraday-resolution (1-min bar) characterization
studies, per Jason's 2026-09-08 "professional systematic trader" framing:
observe market behavior -> identify recurring condition -> measure what
happens next. All three conditions use only 1-min OHLCV (no order-book/
tick data). Checked against the ledger for overlap first (opening-range,
VWAP mean reversion, and gap-fill are all already-tested ground and were
excluded from this batch -- see the frozen spec's "why these three" section).

STEP 1 ONLY (statistical, no costs). Search batch ID:
batch-2026-09-08-intraday-behavior-1. No predicted sign pinned for
exp-072/074 (lesson from bar-behavior-batch1); exp-073 predicts continuation
but reports honestly either way.

HOW TO RUN:
    python3 src/study_intraday_behavior_batch1.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_overnight_gap import get_reference_close
from study_volatility_regime import compute_daily_log_returns
from study_futures_expiration import bootstrap_mean_diff_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

N_BOOTSTRAP = 3000
RANDOM_SEED = 7
LOOKBACK_DAYS = 20

FRONT_LOAD_WINDOW_MIN = 90       # 9:30-11:00 AM ET
BURST_MULTIPLE = 3.0
BURST_HORIZON_MIN = 15
BURST_TRAILING_BARS = 20
RANGE_NARROW_PCTL = 20
RANGE_WIDE_PCTL = 80


def bootstrap_mean_ci(values, null=0.0, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    if len(values) == 0:
        return float("nan"), float("nan")
    boot_means = rng.choice(values, size=(n_bootstrap, len(values)), replace=True).mean(axis=1)
    lo, hi = np.percentile(boot_means, [5, 95])
    return float(lo), float(hi)


def build_daily_frame(df: pd.DataFrame) -> pd.DataFrame:
    """One row per day: Close (4pm ref), High, Low, total_volume,
    first_90min_volume_fraction. Days with no usable reference close dropped."""
    tz = df.index.tz
    rows = []
    for day, day_df in df.groupby(df.index.date):
        ref_close = get_reference_close(day_df, day, tz)
        if ref_close is None or ref_close <= 0:
            continue
        session = day_df.between_time("09:30", "16:00")
        if session.empty:
            continue
        total_vol = float(session["Volume"].sum())
        window_end = pd.Timestamp(day, tz=tz).replace(hour=9, minute=30) + pd.Timedelta(minutes=FRONT_LOAD_WINDOW_MIN)
        front_vol = float(session[session.index < window_end]["Volume"].sum())
        front_frac = front_vol / total_vol if total_vol > 0 else float("nan")
        rows.append({
            "date": day, "Close": ref_close,
            "High": float(session["High"].max()), "Low": float(session["Low"].min()),
            "total_volume": total_vol, "front90_frac": front_frac,
        })
    out = pd.DataFrame(rows).set_index("date").sort_index()
    out["range"] = out["High"] - out["Low"]
    out["trailing_avg_front_frac"] = out["front90_frac"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    out["trailing_std_front_frac"] = out["front90_frac"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).std().shift(1)
    out["trailing_avg_range"] = out["range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    return out


def analyze_volume_skew(daily: pd.DataFrame, log_returns: dict) -> dict:
    """exp-072: front-loaded / back-loaded volume days vs next-day return,
    tested as a DIFFERENCE against the complement (normal) days -- NQ has a
    positive unconditional drift over this Discovery period (mean +0.00074,
    90% CI entirely above zero, checked separately), so comparing a bucket's
    raw mean to zero would just detect that baseline drift, not a real
    differentiated effect. Diff-vs-complement is the correct test, same
    convention as study_daily_volume_level.py's HIGH-vs-LOW test."""
    valid = daily.dropna(subset=["trailing_avg_front_frac", "trailing_std_front_frac"]).copy()
    valid = valid[valid["trailing_std_front_frac"] > 0]
    z = (valid["front90_frac"] - valid["trailing_avg_front_frac"]) / valid["trailing_std_front_frac"]
    days_sorted = sorted(daily.index)
    day_to_idx = {d: i for i, d in enumerate(days_sorted)}

    def next_day_returns(day_index):
        rets = []
        for day in day_index:
            idx = day_to_idx.get(day)
            if idx is None or idx + 1 >= len(days_sorted):
                continue
            nr = log_returns.get(days_sorted[idx + 1])
            if nr is not None:
                rets.append(nr)
        return rets

    results = {}
    for label, mask in (("front_loaded", z > 1.0), ("back_loaded", z < -1.0)):
        bucket_rets = next_day_returns(valid.index[mask])
        complement_rets = next_day_returns(valid.index[~mask])
        mean_bucket = float(np.mean(bucket_rets)) if bucket_rets else float("nan")
        mean_complement = float(np.mean(complement_rets)) if complement_rets else float("nan")
        diff = mean_bucket - mean_complement
        ci = bootstrap_mean_diff_ci(bucket_rets, complement_rets) if bucket_rets and complement_rets else (float("nan"), float("nan"))
        credible = bool(bucket_rets) and bool(complement_rets) and (ci[0] > 0 or ci[1] < 0)
        results[label] = {
            "n": len(bucket_rets), "n_complement": len(complement_rets),
            "mean_next_day_return": mean_bucket, "mean_complement_next_day_return": mean_complement,
            "diff_vs_complement": diff, "ci_90_diff": ci, "statistically_credible": credible,
        }
    return results


def analyze_momentum_burst(df: pd.DataFrame) -> dict:
    """exp-073: 1-min burst bars (range + volume both >= 3x trailing 20-bar avg)
    -> signed cumulative return over the following 15 minutes."""
    session = df.between_time("09:30", "16:00").copy()
    session["range"] = session["High"] - session["Low"]
    session["trailing_avg_range"] = session["range"].rolling(BURST_TRAILING_BARS, min_periods=BURST_TRAILING_BARS).mean().shift(1)
    session["trailing_avg_vol"] = session["Volume"].rolling(BURST_TRAILING_BARS, min_periods=BURST_TRAILING_BARS).mean().shift(1)
    session["bar_return"] = np.log(session["Close"] / session["Close"].shift(1))
    is_burst = (
        (session["range"] >= BURST_MULTIPLE * session["trailing_avg_range"])
        & (session["Volume"] >= BURST_MULTIPLE * session["trailing_avg_vol"])
        & session["trailing_avg_range"].notna() & (session["trailing_avg_range"] > 0)
        & session["trailing_avg_vol"].notna() & (session["trailing_avg_vol"] > 0)
        & session["bar_return"].notna() & (session["bar_return"] != 0)
    )
    burst_times = session.index[is_burst]
    close = session["Close"]
    signed_fwd_returns = []
    for t in burst_times:
        direction = np.sign(session.loc[t, "bar_return"])
        target_t = t + pd.Timedelta(minutes=BURST_HORIZON_MIN)
        future = close[(close.index > t) & (close.index <= target_t)]
        if future.empty:
            continue
        fwd_ret = np.log(future.iloc[-1] / close.loc[t])
        signed_fwd_returns.append(direction * fwd_ret)

    mean = float(np.mean(signed_fwd_returns)) if signed_fwd_returns else float("nan")
    ci = bootstrap_mean_ci(signed_fwd_returns) if signed_fwd_returns else (float("nan"), float("nan"))
    credible = bool(signed_fwd_returns) and (ci[0] > 0 or ci[1] < 0)
    return {"n_bursts": len(signed_fwd_returns), "mean_signed_15min_fwd_return": mean,
            "ci_90": ci, "statistically_credible": credible}


def analyze_range_contraction(daily: pd.DataFrame) -> dict:
    """exp-074: narrow/wide-range days (own trailing 20-day distribution) ->
    next day's range ratio (next range / its own trailing 20-day avg range)."""
    valid = daily.dropna(subset=["trailing_avg_range"]).copy()
    valid["next_range_ratio"] = (daily["range"].shift(-1) / daily["trailing_avg_range"])
    valid = valid.dropna(subset=["next_range_ratio"])

    days_sorted = sorted(daily.dropna(subset=["trailing_avg_range"]).index)
    trailing_hist = daily["range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS)

    results = {}
    narrow_thresh = daily["range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, RANGE_NARROW_PCTL), raw=True).shift(1)
    wide_thresh = daily["range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, RANGE_WIDE_PCTL), raw=True).shift(1)

    for label, mask_series in (
        ("narrow", valid["range"] <= narrow_thresh.reindex(valid.index)),
        ("wide", valid["range"] >= wide_thresh.reindex(valid.index)),
    ):
        ratios = valid.loc[mask_series.fillna(False), "next_range_ratio"].dropna().tolist()
        mean = float(np.mean(ratios)) if ratios else float("nan")
        ci = bootstrap_mean_ci(ratios) if ratios else (float("nan"), float("nan"))
        credible = bool(ratios) and (ci[0] > 1.0 or ci[1] < 1.0)
        results[label] = {"n": len(ratios), "mean_next_range_ratio": mean, "ci_90": ci, "statistically_credible": credible}
    return results


def main():
    print("=" * 78)
    print("INTRADAY BEHAVIOR BATCH 1: exp-072 (volume skew), exp-073 (momentum")
    print("burst), exp-074 (range contraction) -- Step 1 only")
    print("=" * 78)
    print("\nFrozen spec: research/studies/intraday-behavior-batch1-spec.md")
    print("search_batch_id: batch-2026-09-08-intraday-behavior-1\n")

    df, is_synthetic = load_price_data(context="study_intraday_behavior_batch1.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_frame(discovery)
    log_returns = compute_daily_log_returns({d: row["Close"] for d, row in daily.iterrows()})

    print("--- exp-072: Volume-profile skew (first-90-min volume fraction) ---")
    print("  (tested as diff vs. complement days, not vs. zero -- NQ has a positive")
    print("   unconditional drift over this Discovery period, checked separately)")
    vol_skew = analyze_volume_skew(daily, log_returns)
    for label, r in vol_skew.items():
        print(f"  {label}: n={r['n']} (complement n={r['n_complement']}) "
              f"mean={r['mean_next_day_return']:.6f} complement_mean={r['mean_complement_next_day_return']:.6f} "
              f"diff={r['diff_vs_complement']:.6f} ci_90_diff={r['ci_90_diff']} credible={r['statistically_credible']}")

    print("\n--- exp-073: Momentum-burst bars (15-min signed forward continuation) ---")
    burst = analyze_momentum_burst(discovery)
    print(f"  n_bursts={burst['n_bursts']} mean_signed_15min_fwd_return={burst['mean_signed_15min_fwd_return']:.6f} "
          f"ci_90={burst['ci_90']} credible={burst['statistically_credible']}")

    print("\n--- exp-074: Range-contraction cycle (next-day range ratio) ---")
    range_cycle = analyze_range_contraction(daily)
    for label, r in range_cycle.items():
        print(f"  {label}: n={r['n']} mean_next_range_ratio={r['mean_next_range_ratio']:.6f} "
              f"ci_90={r['ci_90']} credible={r['statistically_credible']}")

    print("\n" + "=" * 78)
    verdicts = {}
    for key, r in vol_skew.items():
        verdicts[f"volume_skew_{key}"] = "STEP_1_PASS" if r["statistically_credible"] else "STEP_1_FAIL"
    verdicts["momentum_burst"] = "STEP_1_PASS" if burst["statistically_credible"] else "STEP_1_FAIL"
    for key, r in range_cycle.items():
        verdicts[f"range_contraction_{key}"] = "STEP_1_PASS" if r["statistically_credible"] else "STEP_1_FAIL"
    for k, v in verdicts.items():
        print(f"  {k}: {v}")

    out = {
        "search_batch_id": "batch-2026-09-08-intraday-behavior-1",
        "volume_skew": vol_skew,
        "momentum_burst": burst,
        "range_contraction": range_cycle,
        "verdicts": verdicts,
    }
    out_path = DATA_DIR / "study_intraday_behavior_batch1_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()

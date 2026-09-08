"""
study_bar_behavior_batch2.py
=================================

exp-088/089/090 -- frozen spec: research/studies/bar-behavior-batch2-spec.md.
Second and final batch of daily-bar candle patterns Jason asked for:
engulfing (bullish/bearish) and a three-bar directional sequence tested
as momentum-continuation (a genuinely different mechanism from batch
1's reversal-style conditions).

STEP 1 ONLY. Search batch ID: batch-2026-09-08-bar-behavior-2.

REUSED, UNMODIFIED from study_bar_behavior_batch1.py:
  - build_daily_bars, bootstrap_mean_ci, analyze_condition

HOW TO RUN:
    python3 src/study_bar_behavior_batch2.py
"""

import json
from pathlib import Path

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_log_returns
from study_bar_behavior_batch1 import build_daily_bars, analyze_condition

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

SEARCH_BATCH_ID = "batch-2026-09-08-bar-behavior-2"
MIN_PROSPECTIVE_N = 40


def main():
    print("=" * 78)
    print("EXP-088/089/090: BAR-LEVEL BEHAVIOR BATCH 2 (engulfing, 3-bar")
    print("sequence) -- Step 1 only")
    print("=" * 78)
    print("\nFrozen spec: research/studies/bar-behavior-batch2-spec.md\n")

    df, is_synthetic = load_price_data(context="study_bar_behavior_batch2.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    discovery = get_discovery_data(df)
    daily = build_daily_bars(discovery)
    log_returns = compute_daily_log_returns({d: row["Close"] for d, row in daily.iterrows()})

    days_sorted = sorted(daily.index)

    bullish_engulf_returns = []
    bearish_engulf_returns = []
    three_bar_returns = []

    for i in range(2, len(days_sorted) - 1):
        day = days_sorted[i]
        prior_day = days_sorted[i - 1]
        next_day = days_sorted[i + 1]
        row = daily.loc[day]
        prior = daily.loc[prior_day]
        next_ret = log_returns.get(next_day)
        if next_ret is None:
            continue

        # exp-088/089: engulfing -- T's body fully contains T-1's body, opposite colors
        t_up = row["Close"] > row["Open"]
        t_down = row["Close"] < row["Open"]
        t1_up = prior["Close"] > prior["Open"]
        t1_down = prior["Close"] < prior["Open"]
        t_body_hi, t_body_lo = max(row["Open"], row["Close"]), min(row["Open"], row["Close"])
        t1_body_hi, t1_body_lo = max(prior["Open"], prior["Close"]), min(prior["Open"], prior["Close"])
        engulfs = (t_body_hi >= t1_body_hi) and (t_body_lo <= t1_body_lo) and (t_body_hi > t_body_lo)

        if engulfs and t1_down and t_up:
            bullish_engulf_returns.append(next_ret)
        if engulfs and t1_up and t_down:
            bearish_engulf_returns.append(next_ret)

        # exp-090: three consecutive same-direction days (T-2, T-1, T)
        day_t2 = days_sorted[i - 2]
        row_t2 = daily.loc[day_t2]
        t2_up = row_t2["Close"] > row_t2["Open"]
        t2_down = row_t2["Close"] < row_t2["Open"]
        if t2_up and t1_up and t_up:
            three_bar_returns.append(next_ret * 1)
        elif t2_down and t1_down and t_down:
            three_bar_returns.append(next_ret * -1)

    results = {}
    results["exp088_bullish_engulfing"] = analyze_condition(
        "exp-088 bullish engulfing", bullish_engulf_returns, direction=1)
    results["exp089_bearish_engulfing"] = analyze_condition(
        "exp-089 bearish engulfing", bearish_engulf_returns, direction=-1)
    # three_bar_returns already signed to the sequence's own direction
    results["exp090_three_bar_sequence"] = analyze_condition(
        "exp-090 three-bar directional sequence (continuation)", three_bar_returns, direction=1)

    verdicts = {}
    for key, r in results.items():
        n = r.get("n", 0)
        if n == 0:
            verdicts[key] = "NO_DATA"
        elif r["statistically_credible"]:
            verdicts[key] = "STEP_1_PASS" if n >= MIN_PROSPECTIVE_N else "STEP_1_PASS_TOO_THIN_FOR_PROSPECTIVE"
        else:
            verdicts[key] = "STEP_1_FAIL"

    print("\n" + "=" * 78)
    for key, r in results.items():
        print(f"{key}: n={r.get('n')} {r}")
    print()
    for key, v in verdicts.items():
        print(f"  {key}: {v}")

    out = {
        "search_batch_id": SEARCH_BATCH_ID,
        "results": results,
        "verdicts": verdicts,
    }
    out_path = DATA_DIR / "study_bar_behavior_batch2_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()

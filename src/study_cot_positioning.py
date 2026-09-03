"""
study_cot_positioning.py
=========================

Implements "CFTC Commitment-of-Traders Positioning -- Cheap
Characterization Check (exp-044)" frozen in
`research/studies/cot-positioning-check.md`. First hypothesis in this
project's history to use a data source other than NQ price action
itself. Deliberately narrow: Step 1 is a free descriptive
difference-of-means check (with a same-drift-environment control,
after this project's own VXN check caught a false positive from
skipping that control earlier this same day); Step 2 (a costed rule)
runs ONLY if Step 1 clears its pre-registered bar.

HOW TO RUN:
    python3 src/study_cot_positioning.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import compute_daily_ref_closes  # reused unmodified
from study_nq_trend_following import bootstrap_mean_ci  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
COT_CSV = DATA_DIR / "cftc_tff_nq_mini_2015_2018.csv"
N_BOOTSTRAP = 2000
RANDOM_SEED = 11


def load_cot_signal() -> pd.DataFrame:
    """Loads the mirrored TFF report rows, computes NetLevMoney and the
    week-over-week Signal (+1/-1, zero-delta weeks marked separately),
    and the point-in-time availability_date (Report_Date + 3 calendar
    days, rolled forward to the nearest classifiable day later, done in
    build_forward_returns once ref_closes is available)."""
    df = pd.read_csv(COT_CSV, parse_dates=["Report_Date_as_YYYY-MM-DD"])
    df = df.sort_values("Report_Date_as_YYYY-MM-DD").reset_index(drop=True)
    df["net_lev_money"] = df["Lev_Money_Positions_Long_All"] - df["Lev_Money_Positions_Short_All"]
    df["delta_net_lev_money"] = df["net_lev_money"].diff()
    df["signal"] = np.sign(df["delta_net_lev_money"])
    df["raw_availability_date"] = df["Report_Date_as_YYYY-MM-DD"] + pd.Timedelta(days=3)
    return df


def resolve_availability_dates(cot_df: pd.DataFrame, ref_closes: dict) -> pd.DataFrame:
    """Rolls each raw_availability_date FORWARD to the nearest actual
    classifiable NQ trading day at or after it (never backward, so the
    signal is never treated as available before it genuinely was)."""
    valid_days = sorted(d for d in ref_closes.keys() if ref_closes[d] is not None)
    cot_df = cot_df.copy()
    resolved = []
    for raw in cot_df["raw_availability_date"]:
        target = raw.date()
        match = next((d for d in valid_days if d >= target), None)
        resolved.append(match)
    cot_df["availability_date"] = resolved
    return cot_df


def build_forward_returns(cot_df: pd.DataFrame, ref_closes: dict) -> pd.DataFrame:
    """One row per report (except the last, which has no next report to
    measure a forward return to, and any report whose delta is NaN --
    the first row): forward_return = ref_close[next availability_date]
    - ref_close[this availability_date]."""
    cot_df = cot_df.dropna(subset=["availability_date"]).reset_index(drop=True)
    rows = []
    for i in range(len(cot_df) - 1):
        this_row = cot_df.iloc[i]
        next_row = cot_df.iloc[i + 1]
        if pd.isna(this_row["signal"]):
            continue
        this_avail = this_row["availability_date"]
        next_avail = next_row["availability_date"]
        if ref_closes.get(this_avail) is None or ref_closes.get(next_avail) is None:
            continue
        fwd_return = float(ref_closes[next_avail] - ref_closes[this_avail])
        rows.append({
            "report_date": this_row["Report_Date_as_YYYY-MM-DD"],
            "availability_date": this_avail,
            "signal": float(this_row["signal"]),
            "delta_net_lev_money": float(this_row["delta_net_lev_money"]),
            "forward_return": fwd_return,
        })
    return pd.DataFrame(rows)


def bootstrap_diff_ci(group_pos, group_neg, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED):
    """90% bootstrap CI on (mean(group_pos) - mean(group_neg)), each
    group resampled independently with replacement -- the control that
    isolates the signal's information content from any shared drift."""
    rng = np.random.default_rng(seed)
    pos = np.asarray(group_pos, dtype=float)
    neg = np.asarray(group_neg, dtype=float)
    diffs = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        p_sample = rng.choice(pos, size=len(pos), replace=True)
        n_sample = rng.choice(neg, size=len(neg), replace=True)
        diffs[i] = p_sample.mean() - n_sample.mean()
    return float(np.percentile(diffs, 5)), float(np.percentile(diffs, 95))


def run_step1(fwd_df: pd.DataFrame) -> dict:
    pos_group = fwd_df.loc[fwd_df["signal"] == 1.0, "forward_return"].tolist()
    neg_group = fwd_df.loc[fwd_df["signal"] == -1.0, "forward_return"].tolist()
    n_zero_excluded = int((fwd_df["signal"] == 0.0).sum())

    mean_pos = float(np.mean(pos_group)) if pos_group else float("nan")
    mean_neg = float(np.mean(neg_group)) if neg_group else float("nan")
    diff = mean_pos - mean_neg if pos_group and neg_group else float("nan")

    if len(pos_group) >= 2 and len(neg_group) >= 2:
        ci_low, ci_high = bootstrap_diff_ci(pos_group, neg_group)
    else:
        ci_low, ci_high = float("nan"), float("nan")

    step1_pass = bool(
        len(pos_group) >= 2 and len(neg_group) >= 2
        and not np.isnan(ci_low) and not np.isnan(ci_high)
        and (ci_low > 0 or ci_high < 0)
    )
    # which group is "long" if Step 1 passes: whichever group has the higher mean
    long_group = None
    if step1_pass:
        long_group = 1.0 if mean_pos > mean_neg else -1.0

    return {
        "n_signal_positive_weeks": len(pos_group),
        "n_signal_negative_weeks": len(neg_group),
        "n_zero_delta_weeks_excluded": n_zero_excluded,
        "mean_forward_return_signal_positive": mean_pos,
        "mean_forward_return_signal_negative": mean_neg,
        "diff_of_means": diff,
        "diff_ci_90": (ci_low, ci_high),
        "step1_pass": step1_pass,
        "long_group_if_pass": long_group,
    }


def run_step2(fwd_df: pd.DataFrame, long_group: float) -> dict:
    """Only called if Step 1 passes. Long the long_group's signal
    value, short the other, one round-trip cost charged per week."""
    df = fwd_df.copy()
    df["position"] = df["signal"].map(lambda s: 1 if s == long_group else (-1 if s in (1.0, -1.0) else 0))
    df = df[df["position"] != 0]
    df["net_pnl"] = df["position"] * df["forward_return"] - ROUND_TRIP_COST_POINTS
    n = len(df)
    net = df["net_pnl"].tolist()
    mean_net = float(np.mean(net)) if n else float("nan")
    ci_low, ci_high = bootstrap_mean_ci(net) if n >= 2 else (float("nan"), float("nan"))
    statistically_credible = bool(n >= 2 and ci_low > 0)
    economic_threshold = 2 * ROUND_TRIP_COST_POINTS
    economically_meaningful = bool(mean_net >= economic_threshold) if n else False
    return {
        "n": int(n),
        "mean_net_pnl": mean_net,
        "ci_90": (ci_low, ci_high),
        "statistically_credible": statistically_credible,
        "economic_threshold_points": economic_threshold,
        "economically_meaningful": economically_meaningful,
    }


def main():
    full_df, is_synthetic = load_price_data(context="study_cot_positioning.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return
    if not COT_CSV.exists():
        print(f"ABORT: {COT_CSV} not found.")
        return

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)

    cot_df = load_cot_signal()
    cot_df = resolve_availability_dates(cot_df, ref_closes)
    fwd_df = build_forward_returns(cot_df, ref_closes)

    print("=" * 78)
    print("CFTC COMMITMENT-OF-TRADERS POSITIONING -- Cheap Check (exp-044)")
    print("Leveraged Money category, NASDAQ-100 E-mini, 2015-2018 (partial Discovery)")
    print("=" * 78)
    print(f"\nWeekly reports loaded: {len(cot_df)}")
    print(f"Weeks with a usable forward return: {len(fwd_df)}")

    step1 = run_step1(fwd_df)
    print("\n--- STEP 1: descriptive, difference-of-means (drift-controlled) ---")
    for k, v in step1.items():
        print(f"  {k}: {v}")
    print(f"\n  Step 1 pass (90% CI on the difference entirely on one side of zero)? "
          f"{step1['step1_pass']}")

    out = {"step1": step1}

    if step1["step1_pass"]:
        print("\n--- STEP 2: costed directional rule (gated, triggered) ---")
        step2 = run_step2(fwd_df, step1["long_group_if_pass"])
        for k, v in step2.items():
            print(f"  {k}: {v}")
        out["step2"] = step2
    else:
        print("\n--- STEP 2: NOT RUN (Step 1 did not clear the pre-registered bar) ---")
        out["step2"] = None

    print("\n" + "=" * 78)

    csv_path = DATA_DIR / "study_cot_positioning_discovery.csv"
    fwd_df.to_csv(csv_path, index=False)
    json_path = DATA_DIR / "study_cot_positioning_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()

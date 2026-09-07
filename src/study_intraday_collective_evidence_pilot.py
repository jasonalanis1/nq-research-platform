"""
study_intraday_collective_evidence_pilot.py
====================================================

exp-057 -- the intraday follow-on to exp-055/056 (the trend-family
collective-evidence pilot). See
research/studies/intraday-collective-evidence-pilot-scoping.md for the
full frozen spec, provenance, and the Advisor's 3 required fixes
(all implemented below).

IMPLEMENTATION-TIME SCOPE NOTE (found while building this, not a
silent change -- disclosed here and in the run notes/ledger): the
scoping doc named 4 condition variables including "time-of-day of
entry." Checking the data revealed this can't be honestly computed
across all 4 lenses: the persisted Level Sweep Reversal results
(lenses 1-2) never saved an entry timestamp (only exit_time), and
Fade the Gap (lens 4) always enters at the same fixed moment (the
8:30am open) by its own frozen design, so it carries zero variation
on this condition. Rather than force a proxy across lenses that don't
actually support it, this condition is DROPPED from this pilot. The
remaining 3 conditions (volatility regime, prior-day direction,
opening-range width) still give 3+2+3 = 8 buckets, comfortably above
the pre-registered 30-distinct-day floor's ability to matter, and the
methodology's other guarantees (day-first aggregation, per-lens
beat-rate disclosure, per-lens trade-count eligibility, single
mechanical candidate selection) are all unchanged.

LENSES (Discovery slice, 2015-01-01 to 2021-10-03, all reused/re-run
unmodified from each setup's own frozen spec):
  1. Level Sweep Reversal, close_min_distance exit, not protected-level
     filtered -- read from the existing persisted CSV (exp-023's data).
  2. Level Sweep Reversal, full_bar_range exit, not protected-level
     filtered -- read from the existing persisted CSV (exp-024's data).
  3. Initial Balance Breakout (Continuation) -- re-run via
     detect_ib_breakout.py + backtest.py's simulate_trade(), both
     unmodified (exp-028's own method, no persisted per-trade CSV
     existed before this pilot).
  4. Fade the Gap -- re-run via detect_fade_the_gap.py +
     simulate_fade_the_gap_trade(), both unmodified (exp-033's own
     method, no persisted per-trade CSV existed before this pilot).

All 4 lenses report net R-multiples (not points), so "beat own
baseline" is directly comparable across lenses without a unit-mixing
caveat exp-055's pilot had to carry.

CONDITIONS (day-level, causal, point-in-time; all reused unmodified):
  - volatility_regime: classify_regimes() (study_volatility_regime.py)
  - prior_day_direction: sign of the immediately preceding day's own
    daily log return (trivial causal lookup)
  - opening_range_width: first-30-min (8:30-9:00 ET) high-low range as
    a % of the trailing 20-day average daily range, causal-expanding-
    tercile classified (causal_expanding_tercile(), exp-055)

AGGREGATION: by day first (so 2 correlated Level Sweep variants firing
on the same day can't double-count), then by lens -- exp-055's core
fix, applied at daily instead of weekly resolution.

ADVISOR FIXES (v2 scoping, all implemented here):
  1. Every bucket reports each lens's OWN beat-rate individually, not
     just the aggregated cross-lens fraction.
  2. A bucket is only eligible if it clears BOTH the 30-distinct-day
     floor AND has at least 3 of the 4 lenses with >=10 of their own
     trades in that bucket.
  3. If multiple buckets are eligible, only the single most extreme
     one (by proximity-to-0.5 z-score) is named as this pilot's one
     candidate for prospective validation -- no second attempt.

HOW TO RUN:
    python3 src/study_intraday_collective_evidence_pilot.py
"""

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import (  # reused unmodified
    compute_daily_ref_closes,
    compute_daily_log_returns,
    compute_trailing_volatility,
    classify_regimes,
)
from study_collective_evidence_pilot import causal_expanding_tercile  # reused unmodified, exp-055
from detect_ib_breakout import (  # reused unmodified
    detect_ib_breakout_for_day,
    OPEN_HOUR,
    OPEN_MINUTE,
    IB_MINUTES,
)
from detect_fade_the_gap import (  # reused unmodified
    detect_fade_the_gap_for_day,
    simulate_fade_the_gap_trade,
)
import backtest as bt  # reused unmodified -- simulate_trade(), cost constants

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

MIN_DISTINCT_DAYS = 30          # pre-registered eligibility floor
MIN_LENSES_WITH_TRADES = 3      # Advisor fix #2
MIN_TRADES_PER_LENS_IN_BUCKET = 10  # Advisor fix #2
N_BOOTSTRAP = 5000

LEVEL_SWEEP_CSVS = {
    "level_sweep_close_min_distance (exp-023)": "backtest_results_level_sweep_close_min_distance_not_protected_discovery.csv",
    "level_sweep_full_bar_range (exp-024)": "backtest_results_level_sweep_full_bar_range_not_protected_discovery.csv",
}


def build_ib_breakout_lens(day_groups: dict) -> pd.DataFrame:
    """Re-runs exp-028's unmodified detection + backtest logic, day by
    day (same performance pattern exp-028 itself used), and returns a
    per-trade DataFrame with date/r_multiple_net."""
    rows = []
    for day in sorted(day_groups.keys()):
        day_df = day_groups[day]
        sig = detect_ib_breakout_for_day(day_df, day)
        if sig is None:
            continue
        sig_series = pd.Series(sig)
        outcome = bt.simulate_trade(day_df, sig_series, "breakout_time")
        risk_points = abs(sig["entry"] - sig["stop"])
        if sig["direction"] == "long":
            pnl_gross = outcome["exit_price"] - sig["entry"]
        else:
            pnl_gross = sig["entry"] - outcome["exit_price"]
        is_resolved = not outcome["exit_reason"].startswith("unresolved")
        pnl_net = pnl_gross - bt.ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
        r_net = pnl_net / risk_points if risk_points else float("nan")
        rows.append({"date": day, "entry_time": sig["breakout_time"], "r_multiple_net": r_net})
    return pd.DataFrame(rows)


def build_fade_the_gap_lens(day_groups: dict) -> pd.DataFrame:
    """Re-runs exp-033's unmodified detection + noon-bounded backtest
    logic, day by day, and returns a per-trade DataFrame with
    date/r_multiple_net."""
    rows = []
    all_days = sorted(day_groups.keys())
    for i in range(1, len(all_days)):
        prior_day, day = all_days[i - 1], all_days[i]
        prior_day_df = day_groups[prior_day]
        day_df = day_groups[day]
        sig = detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)
        if sig is None:
            continue
        sig_series = pd.Series(sig)
        outcome = simulate_fade_the_gap_trade(day_df, sig_series)
        risk_points = abs(sig["entry"] - sig["stop"])
        if sig["direction"] == "long":
            pnl_gross = outcome["exit_price"] - sig["entry"]
        else:
            pnl_gross = sig["entry"] - outcome["exit_price"]
        is_resolved = not outcome["exit_reason"].startswith("unresolved")
        pnl_net = pnl_gross - bt.ROUND_TRIP_COST_POINTS if is_resolved else pnl_gross
        r_net = pnl_net / risk_points if risk_points else float("nan")
        rows.append({"date": day, "entry_time": sig["entry_time"], "r_multiple_net": r_net})
    return pd.DataFrame(rows)


def build_level_sweep_lens(filename: str) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / filename, parse_dates=["date"])
    df["date"] = df["date"].dt.date
    return df[["date", "r_multiple_net"]].copy()


def build_conditions(day_groups: dict) -> dict:
    """All 3 day-level condition variables, causal and point-in-time,
    reusing exp-053/055's existing pipeline unmodified for volatility
    regime, and computing opening-range width the same causal-tercile
    way exp-055 introduced."""
    ref_closes = compute_daily_ref_closes(day_groups)  # reused unmodified
    daily_returns = compute_daily_log_returns(ref_closes)  # reused unmodified
    all_days = sorted(day_groups.keys())
    vol_by_day = compute_trailing_volatility(daily_returns, all_days)  # reused unmodified
    volatility_regime = classify_regimes(vol_by_day)  # reused unmodified

    # Prior-day direction: sign of the immediately preceding day's own
    # daily log return (trivial causal lookup, same idea as exp-055's
    # prior-week-direction condition).
    prior_day_direction = {}
    valid_return_days = sorted(daily_returns.keys())
    for i, day in enumerate(all_days):
        prior_returns = [d for d in valid_return_days if d < day]
        if not prior_returns:
            continue
        last_return = daily_returns[prior_returns[-1]]
        prior_day_direction[day] = "up" if last_return > 0 else "down"

    # Opening-range width: first 30 min (8:30-9:00 ET) high-low range as
    # a % of the trailing 20-day average TRUE daily range (high-low of
    # the whole day), causal-expanding-tercile classified.
    daily_range = {}
    for day in all_days:
        day_df = day_groups[day]
        if len(day_df) == 0:
            continue
        daily_range[day] = float(day_df["High"].max() - day_df["Low"].min())

    ib_width_pct = {}
    for day in all_days:
        day_df = day_groups[day]
        if len(day_df) == 0:
            continue
        tz = day_df.index.tz
        open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
        ib_end_ts = open_ts + pd.Timedelta(minutes=IB_MINUTES)
        ib_bars = day_df[(day_df.index >= open_ts) & (day_df.index < ib_end_ts)]
        if ib_bars.empty:
            continue
        ib_width = float(ib_bars["High"].max() - ib_bars["Low"].min())
        prior_ranges = [daily_range[d] for d in all_days if d < day and d in daily_range][-20:]
        if len(prior_ranges) < 20:
            continue
        avg_prior_range = sum(prior_ranges) / len(prior_ranges)
        if avg_prior_range <= 0:
            continue
        ib_width_pct[day] = 100.0 * ib_width / avg_prior_range

    opening_range_width = causal_expanding_tercile(ib_width_pct)  # reused unmodified, exp-055

    return {
        "volatility_regime": volatility_regime,
        "prior_day_direction": prior_day_direction,
        "opening_range_width": opening_range_width,
    }


def bootstrap_ci_on_days(day_fractions: list, n_boot=N_BOOTSTRAP, seed=13) -> tuple:
    if len(day_fractions) < 2:
        return (None, None)
    rng = random.Random(seed)
    n = len(day_fractions)
    means = []
    for _ in range(n_boot):
        sample = [day_fractions[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo_idx = int(0.05 * n_boot)
    hi_idx = int(0.95 * n_boot) - 1
    return (means[lo_idx], means[hi_idx])


def analyze_bucket(label: str, days_in_bucket: set, lens_frames: dict) -> dict:
    """Day-first, then lens. For every day in the bucket, count how
    many lenses traded and how many beat their own baseline. Also
    tracks each lens's own trade count and beat-rate within the bucket
    (Advisor fix #1)."""
    day_fracs = []
    per_lens_trades = {name: 0 for name in lens_frames}
    per_lens_beats = {name: 0 for name in lens_frames}

    for day in sorted(days_in_bucket):
        lens_active = 0
        lens_beat = 0
        for name, frame in lens_frames.items():
            day_rows = frame[frame["date"] == day]
            if day_rows.empty:
                continue
            lens_active += 1
            per_lens_trades[name] += len(day_rows)
            beat = bool((day_rows["relative_outcome"] > 0).any())
            if beat:
                lens_beat += 1
                per_lens_beats[name] += len(day_rows[day_rows["relative_outcome"] > 0])
        if lens_active > 0:
            day_fracs.append(lens_beat / lens_active)

    n_distinct_days = len(day_fracs)
    lenses_with_min_trades = sum(1 for n in per_lens_trades.values() if n >= MIN_TRADES_PER_LENS_IN_BUCKET)
    eligible = n_distinct_days >= MIN_DISTINCT_DAYS and lenses_with_min_trades >= MIN_LENSES_WITH_TRADES

    mean_frac = sum(day_fracs) / len(day_fracs) if day_fracs else None
    ci = bootstrap_ci_on_days(day_fracs) if eligible else (None, None)

    per_lens_beat_rate = {
        name: (per_lens_beats[name] / per_lens_trades[name] if per_lens_trades[name] else None)
        for name in lens_frames
    }

    return {
        "label": label,
        "n_distinct_days": n_distinct_days,
        "lenses_with_min_trades": lenses_with_min_trades,
        "eligible": eligible,
        "mean_frac_beating_baseline": mean_frac,
        "ci_90": ci,
        "per_lens_trade_counts": per_lens_trades,
        "per_lens_beat_rate": per_lens_beat_rate,
    }


def z_score(result: dict) -> float:
    if not result["eligible"] or result["ci_90"][0] is None:
        return 0.0
    lo, hi = result["ci_90"]
    se = (hi - lo) / (2 * 1.645) if hi > lo else 1e-9
    return abs(result["mean_frac_beating_baseline"] - 0.5) / se if se > 0 else 0.0


def main():
    print("=" * 78)
    print("EXP-057: INTRADAY COLLECTIVE-EVIDENCE PILOT (Level Sweep x2, IB Breakout, Fade the Gap)")
    print("=" * 78)

    full_df, is_synthetic = load_price_data(context="study_intraday_collective_evidence_pilot.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this study requires real data.")
        return

    discovery_df = get_discovery_data(full_df)
    print(f"\nDiscovery slice: {len(discovery_df.index.normalize().unique())} trading day(s).")

    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}

    print("\nBuilding lenses...")
    lens_frames_raw = {}
    for name, filename in LEVEL_SWEEP_CSVS.items():
        lens_frames_raw[name] = build_level_sweep_lens(filename)
        print(f"  {name}: {len(lens_frames_raw[name])} trades (from persisted CSV)")

    ib_df = build_ib_breakout_lens(day_groups)
    lens_frames_raw["initial_balance_breakout (exp-028)"] = ib_df
    print(f"  initial_balance_breakout (exp-028): {len(ib_df)} trades (re-run this pilot)")

    fade_df = build_fade_the_gap_lens(day_groups)
    lens_frames_raw["fade_the_gap (exp-033)"] = fade_df
    print(f"  fade_the_gap (exp-033): {len(fade_df)} trades (re-run this pilot)")

    # "Won" = beat own baseline (exp-055's redefinition), computed per lens.
    lens_frames = {}
    baselines = {}
    for name, df in lens_frames_raw.items():
        baseline = df["r_multiple_net"].mean()
        baselines[name] = baseline
        df = df.copy()
        df["relative_outcome"] = df["r_multiple_net"] - baseline
        lens_frames[name] = df
    print("\nPer-lens baselines (own mean net R-multiple, Discovery slice):")
    for name, b in baselines.items():
        print(f"  {name}: {b:.4f}")

    print("\nBuilding conditions...")
    conditions = build_conditions(day_groups)

    all_days_set = set(day_groups.keys())
    results = []
    for cond_name, cond_map in conditions.items():
        values = sorted(set(cond_map.values()))
        for value in values:
            days_in_bucket = {d for d in all_days_set if cond_map.get(d) == value}
            label = f"{cond_name} = {value}"
            r = analyze_bucket(label, days_in_bucket, lens_frames)
            r["condition"] = cond_name
            r["value"] = value
            results.append(r)

    print(f"\n{len(results)} buckets scanned (pre-registered: 3+2+3 = 8).")
    print("\n" + "-" * 78)
    for r in results:
        print(f"\n{r['label']}")
        print(f"  n_distinct_days={r['n_distinct_days']}  lenses_with_>=10_trades={r['lenses_with_min_trades']}/4  eligible={r['eligible']}")
        if r["eligible"]:
            lo, hi = r["ci_90"]
            print(f"  mean_frac_beating_baseline={r['mean_frac_beating_baseline']:.4f}  ci_90=({lo:.4f}, {hi:.4f})")
        print(f"  per_lens_trade_counts={r['per_lens_trade_counts']}")
        print(f"  per_lens_beat_rate={ {k: (round(v,4) if v is not None else None) for k,v in r['per_lens_beat_rate'].items()} }")

    eligible_results = [r for r in results if r["eligible"]]
    candidate = None
    if eligible_results:
        candidate = max(eligible_results, key=z_score)
        cz = z_score(candidate)
        # Only treat it as a real candidate if its CI is entirely on one
        # side of 0.5 -- z alone doesn't guarantee that.
        lo, hi = candidate["ci_90"]
        if not (lo > 0.5 or hi < 0.5):
            candidate = None

    print("\n" + "=" * 78)
    if candidate:
        print(f"ONE CANDIDATE (mechanically selected, highest z-score among eligible buckets, "
              f"CI entirely off 0.5): {candidate['label']}")
        print(f"  n_distinct_days={candidate['n_distinct_days']}  "
              f"mean_frac={candidate['mean_frac_beating_baseline']:.4f}  ci_90={candidate['ci_90']}")
    else:
        print("NO CANDIDATE: no eligible bucket had a 90% CI entirely off the 0.5 baseline.")
    print("=" * 78)

    out = {
        "lens_baselines": baselines,
        "buckets": [
            {
                "label": r["label"],
                "condition": r["condition"],
                "value": r["value"],
                "n_distinct_days": r["n_distinct_days"],
                "lenses_with_min_trades": r["lenses_with_min_trades"],
                "eligible": r["eligible"],
                "mean_frac_beating_baseline": r["mean_frac_beating_baseline"],
                "ci_90": list(r["ci_90"]) if r["ci_90"][0] is not None else [None, None],
                "per_lens_trade_counts": r["per_lens_trade_counts"],
                "per_lens_beat_rate": r["per_lens_beat_rate"],
            }
            for r in results
        ],
        "candidate": candidate["label"] if candidate else None,
        "candidate_detail": candidate,
    }
    out_path = DATA_DIR / "study_intraday_collective_evidence_pilot_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()

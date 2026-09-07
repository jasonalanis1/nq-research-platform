"""
study_cross_asset_short_term_reversal.py
===========================================

Implements the frozen spec in
`research/studies/cross-asset-short-term-reversal-scoping.md` (v2,
Advisor-cleared 2026-09-07) -- exp-052. First test of a genuinely NEW
signal family in this project (short-term weekly reversal), not a
derivative of exp-047's trend family -- see the frozen spec's
Provenance and lineage-disclosure sections for why calendar-timing and
VWAP-reversion ideas were deliberately dropped from this round instead
of retested (both already killed on NQ alone, in prior experiments).

WHAT THIS TESTS (Step 1, primary): does betting AGAINST last week's
own return (short-term reversal), applied independently across the
same 4-instrument basket as exp-051 (NQ/ZN/6E/CL) and combined into
one inverse-volatility-weighted portfolio, clear this project's
promotion bar?

WHAT THIS TESTS (Step 2, gated behind a Step 1 pass): the same
signal, but skipping any week where the instrument's own trailing
volatility is in the top half of its point-in-time history (i.e. only
betting on reversal in relatively calm weeks). Step 2 is not run at
all if Step 1 does not clear the bar -- see frozen spec's
Confirmation-filter section.

REUSED, UNMODIFIED (this is the whole point -- almost nothing here is
new code):
  - resample_to_weekly_closes, compute_weekly_log_returns (from
    study_nq_weekly_trend_following.py)
  - compute_positions (from study_nq_trend_following.py) -- same
    sign/tie-break rule, just fed a different signal
  - compute_portfolio_pnl, load_instrument_signal (from
    study_cross_asset_weekly_trend.py) -- the exact same generic
    portfolio-construction machinery exp-051 used, imported and called
    unmodified. This script only supplies a DIFFERENT `positions` dict
    per instrument (reversal instead of trend-momentum) into the same
    combination logic.
  - analyze_primary, bootstrap_mean_ci, robustness_drop_largest_pnl_day,
    robustness_split_half (from study_nq_trend_following.py)
  - compute_trailing_volatility (from study_volatility_regime.py) --
    already causal/point-in-time by construction, reused for the Step
    2 filter's percentile-rank calculation.

NEW CODE (per the frozen spec): (1) the reversal signal itself --
literally one line, `-prior_week_return`, computed directly from the
`weekly_returns` dict already produced by
`compute_weekly_log_returns()`; (2) the Step-2 volatility-percentile
filter, built as an expanding point-in-time rank over `vol_by_day`
(never the full-sample distribution -- see frozen spec's explicit
no-lookahead requirement).

HOW TO RUN:
    python3 src/study_cross_asset_short_term_reversal.py
"""

import json
from pathlib import Path

import pandas as pd

from study_cross_asset_weekly_trend import (  # reused unmodified
    BASKET,
    load_instrument_signal,
    compute_portfolio_pnl,
)
from study_nq_trend_following import (  # reused unmodified
    compute_positions,
    analyze_primary,
    robustness_drop_largest_pnl_day,
    robustness_split_half,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Step 2's own warm-up, on top of compute_trailing_volatility's own 20-day
# warm-up (frozen spec: "fewer than 20 prior volatility observations").
FILTER_MIN_PRIOR_OBSERVATIONS = 20


def build_reversal_positions(weekly_returns: dict) -> dict:
    """Frozen spec's exact signal: reversal_signal[week_t] =
    -weekly_return[week_t - 1] (the immediately preceding week's own
    return, negated -- not a multi-week window). Then reuses
    compute_positions() UNMODIFIED for the sign/tie-break rule, exactly
    as exp-047 does with its own (different) signal."""
    weeks_sorted = sorted(weekly_returns.keys())
    reversal_signal = {}
    for i in range(1, len(weeks_sorted)):
        prev_week, week = weeks_sorted[i - 1], weeks_sorted[i]
        reversal_signal[week] = -weekly_returns[prev_week]
    return compute_positions(reversal_signal)  # reused unmodified


def build_volatility_percentile_ranks(vol_by_day: dict, day_to_week: dict) -> dict:
    """week_t -> point-in-time percentile rank (0-1) of THIS week's
    first-trading-day volatility against every vol_by_day value known
    strictly before week_t's first trading day -- an expanding,
    causal distribution, never the full-sample one (frozen spec's
    explicit no-lookahead requirement for the Step-2 filter). A week
    with fewer than FILTER_MIN_PRIOR_OBSERVATIONS prior volatility
    values has no entry here (frozen spec's stated warm-up rule: that
    week's raw Step-1 position is used unfiltered, not excluded)."""
    vol_days_sorted = sorted(vol_by_day.keys())
    ranks = {}
    for week, week_days in day_to_week.items():
        if not week_days:
            continue
        first_day = sorted(week_days)[0]
        prior_vols = sorted(vol_by_day[d] for d in vol_days_sorted if d < first_day)
        if len(prior_vols) < FILTER_MIN_PRIOR_OBSERVATIONS:
            continue
        this_vol = vol_by_day.get(first_day)
        if this_vol is None:
            continue
        # Fraction of prior (strictly earlier) observations this week's
        # vol is >= to -- a standard point-in-time percentile rank.
        rank = sum(1 for v in prior_vols if v <= this_vol) / len(prior_vols)
        ranks[week] = rank
    return ranks


def apply_calm_week_filter(positions: dict, vol_percentile_ranks: dict) -> dict:
    """Step 2: keep the Step-1 position only in weeks where the
    point-in-time volatility percentile rank is in the bottom half
    (<0.5) of the instrument's own history so far; a week with no rank
    yet (warm-up) keeps its unfiltered Step-1 position (frozen spec's
    explicit edge-case rule, not a silent exclusion). A week ranked in
    the top half (calm-week filter says "skip") is dropped from the
    returned dict entirely, same convention compute_positions() itself
    uses for "not yet classifiable."""
    filtered = {}
    for week, pos in positions.items():
        rank = vol_percentile_ranks.get(week)
        if rank is None:
            filtered[week] = pos  # warm-up: unfiltered, per frozen spec
        elif rank < 0.5:
            filtered[week] = pos  # calm week: keep the Step-1 bet
        # else: high-vol week, filter skips it (position omitted)
    return filtered


def build_instrument_data_with_positions(positions_by_symbol: dict) -> dict:
    """Reloads each instrument's signal data (via
    load_instrument_signal(), reused unmodified) and swaps in the
    ALREADY-COMPUTED reversal (or filtered-reversal) positions in
    place of exp-047's trend positions, so compute_portfolio_pnl() --
    which is generic over the positions dict -- combines THIS
    family's signal instead, with zero changes to that function."""
    out = {}
    for symbol, _label in BASKET:
        base = load_instrument_signal(symbol)
        if base is None:
            return None
        base = dict(base)  # shallow copy, don't mutate the cached loader's dict
        base["positions"] = positions_by_symbol[symbol]
        out[symbol] = base
    return out


def run_step(label: str, positions_by_symbol: dict) -> dict:
    instrument_data = build_instrument_data_with_positions(positions_by_symbol)
    pnl_df, dropped_no_vol = compute_portfolio_pnl(instrument_data)  # reused unmodified
    primary = analyze_primary(pnl_df)  # reused unmodified

    print(f"\n{'=' * 78}")
    print(f"{label}")
    print(f"{'=' * 78}")
    print(f"Portfolio weeks with a computed combined return: {len(pnl_df)} "
          f"({dropped_no_vol} dropped for missing volatility/position data)")
    print("\n--- PRIMARY: mean weekly portfolio net return ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")
    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['statistically_credible']}")
    print(f"  Step-2-gate check 2 (economically meaningful): {primary['economically_meaningful']}")

    drop_result = robustness_drop_largest_pnl_day(pnl_df)  # reused unmodified
    split_result = robustness_split_half(pnl_df)  # reused unmodified
    print("\n--- Robustness (a): drop largest-magnitude week ---")
    for k, v in drop_result.items():
        print(f"  {k}: {v}")
    print("\n--- Robustness (b): first-half vs second-half split ---")
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    return {
        "pnl_df": pnl_df,
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
    }


def main():
    print("=" * 78)
    print("CROSS-ASSET SHORT-TERM WEEKLY REVERSAL (exp-052)")
    print("=" * 78)

    # Load each instrument once (raw, exp-047-style loader output) to get
    # weekly_returns / vol_by_day / day_to_week for building signals --
    # reused unmodified via load_instrument_signal().
    raw = {}
    missing = []
    for symbol, label in BASKET:
        result = load_instrument_signal(symbol)
        if result is None:
            missing.append((symbol, label))
        else:
            raw[symbol] = result
    if missing:
        print("\nABORT: this test needs all 4 instruments' data, and the following "
              "are not available yet:")
        for symbol, label in missing:
            print(f"  - {symbol} ({label})")
        return

    print(f"\nAll 4 instruments loaded: {', '.join(sym for sym, _ in BASKET)}")

    # --- Step 1: raw reversal signal, per instrument ---
    step1_positions = {}
    for symbol, _label in BASKET:
        step1_positions[symbol] = build_reversal_positions(raw[symbol]["weekly_returns"])

    step1 = run_step("STEP 1: raw short-term reversal (unfiltered)", step1_positions)

    step1_pass = step1["primary"]["statistically_credible"] and step1["primary"]["economically_meaningful"]

    step2 = None
    if step1_pass:
        # --- Step 2: calm-week filter, gated behind Step 1 clearing the bar ---
        step2_positions = {}
        for symbol, _label in BASKET:
            ranks = build_volatility_percentile_ranks(raw[symbol]["vol_by_day"], raw[symbol]["day_to_week"])
            step2_positions[symbol] = apply_calm_week_filter(step1_positions[symbol], ranks)
        step2 = run_step("STEP 2: calm-week-filtered short-term reversal (gated on Step 1 pass)", step2_positions)
    else:
        print("\nStep 1 did not clear the promotion bar -- Step 2 (the calm-week "
              "filter) is NOT run, per the frozen spec's gating rule (don't chase "
              "a filtered version of something that already failed unfiltered).")

    print("\n" + "=" * 78)
    if step1_pass:
        step2_pass = step2["primary"]["statistically_credible"] and step2["primary"]["economically_meaningful"]
        if step2_pass:
            verdict = ("Step 1 AND Step 2 both clear the promotion bar -- this family's "
                       "first-ever pass in this project. Needs Validation/Holdout "
                       "corroboration before anything is promoted (same standard as "
                       "every other hypothesis here) -- not a live-authorization result.")
        else:
            verdict = ("Step 1 cleared the bar; Step 2 (calm-week filter) did not. "
                       "Per the frozen spec, the filtered version is not chased further "
                       "with additional filter variants -- report both results as-is.")
    else:
        verdict = "kill at Step 1 -- short-term reversal does not clear the bar on this basket, on this data."
    print(f"Verdict: {verdict}")

    out = {
        "step1": {k: v for k, v in step1.items() if k != "pnl_df"},
        "step2": ({k: v for k, v in step2.items() if k != "pnl_df"} if step2 else None),
        "verdict": verdict,
        "basket": [sym for sym, _ in BASKET],
    }
    json_path = DATA_DIR / "study_cross_asset_short_term_reversal_discovery_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    step1["pnl_df"].to_csv(DATA_DIR / "study_cross_asset_short_term_reversal_step1_discovery.csv", index=False)
    if step2:
        step2["pnl_df"].to_csv(DATA_DIR / "study_cross_asset_short_term_reversal_step2_discovery.csv", index=False)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()

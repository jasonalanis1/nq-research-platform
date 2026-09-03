"""
apply_larry_liquidity_filter_family.py
========================================

WHAT THIS FILE DOES (plain English):
First real application of larry_validate.py (DSR/PBO) to an actual
research result, rather than a synthetic sanity check. Evaluates the two
"protected liquidity filter" Level Sweep Reversal candidates already in
the research ledger -- hyp-000007 (close_min_distance variant) and
hyp-000008 (full_bar_range variant) -- against the full 4-config trial
family they were actually picked from.

WHY n_trials_override=4, NOT the lineage-based default: hyp-000007
(parent hyp-000001) and hyp-000008 (parent hyp-000003) have DIFFERENT
immediate parents, so larry_validate.py's automatic
_family_via_lineage() fallback would undercount each as belonging to a
2-hypothesis family (itself + its own direct parent), missing that all
FOUR configs below were actually searched together in one real script
run. This is the documented, disclosed gap in larry_validate.py's
docstring (see "TRIAL-COUNTING FIX"). The true trial family, read
directly from how the search was actually run
(src/_run_liquidity_filter_discovery_backtest.py's own main(), which
backtests all four variant x protection-bucket combinations in one
pass), is:

    1. level_sweep_reversal_close_min_distance, not protected (baseline)
    2. level_sweep_reversal_close_min_distance, protected  <- hyp-000007
    3. level_sweep_reversal_full_bar_range, not protected (baseline)
    4. level_sweep_reversal_full_bar_range, protected      <- hyp-000008

Both "not protected" baselines count as real trials searched (they are
what "protected" was compared against to decide the liquidity filter was
worth adding at all -- see research/experiments/exp-026 and exp-027),
so n_trials_override=4 for BOTH hyp-000007 and hyp-000008, not 2.
Documented here, per larry_validate.py's own discipline of never
inferring a trial count silently.

DATA: the 4 CSVs consumed here were regenerated fresh this session by
re-running src/_run_liquidity_filter_discovery_backtest.py against
Discovery data, and were verified to reproduce exp-026/027's originally
published trade counts exactly (44 resolved protected close_min_distance
trades, 59 resolved protected full_bar_range trades) before being
trusted for this step.

RETURN SERIES CONSTRUCTION: purgedcv's probability_of_backtest_overfitting()
requires all configs to share one common time axis, shape
(n_configs, n_obs). Each config's per-trade r_multiple_net is placed on
its ENTRY date within a daily series spanning every real Discovery
trading day (2,101 days, from data_loader+data_split -- the same
machinery every other study in this project uses, not a synthetic
business-day approximation); days with no trade for that config are 0
(flat, not in a trade). "unresolved_end_of_data" trades (2 in
close_min_distance_protected, 1 in full_bar_range_protected) are
excluded -- they never resolved to a real P&L, consistent with how
these were already excluded when counting "44 resolved" / "59 resolved"
trades in exp-026/027. The same daily-aligned series is used for both
the winner's own DSR input and the sibling matrix's var_sharpe input,
so the two numbers are internally consistent with each other.

This is a temporary driver script, matching this project's established
pattern (see _run_liquidity_filter_discovery_backtest.py) -- not part of
the reusable study/backtest library.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
import larry_validate as lv  # noqa: E402

PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"

# Fixed order -- this IS the trial family, n_trials_override=4 below
# assumes exactly this list.
VARIANT_FILES = [
    ("close_min_distance_not_protected", "level_sweep_reversal_close_min_distance"),
    ("close_min_distance_protected", "level_sweep_reversal_close_min_distance_protected_liquidity_filter"),
    ("full_bar_range_not_protected", "level_sweep_reversal_full_bar_range"),
    ("full_bar_range_protected", "level_sweep_reversal_full_bar_range_protected_liquidity_filter"),
]

# Which config index in VARIANT_FILES is each ledger hypothesis's own
# "winner" series.
HYPOTHESIS_TO_CONFIG_INDEX = {
    "hyp-000007": 1,  # close_min_distance_protected
    "hyp-000008": 3,  # full_bar_range_protected
}

N_TRIALS_OVERRIDE = 4  # see module docstring


def build_daily_return_series(csv_name: str, discovery_days: list) -> np.ndarray:
    """Loads one variant's trade CSV and places each resolved trade's
    r_multiple_net on its entry date within a daily series spanning
    every real Discovery trading day. Non-trade days are 0.0."""
    df = pd.read_csv(DATA_DIR / f"backtest_results_level_sweep_{csv_name}_discovery.csv")
    resolved = df[df["exit_reason"] != "unresolved_end_of_data"].copy()
    resolved["date"] = pd.to_datetime(resolved["date"]).dt.date

    by_date = dict(zip(resolved["date"], resolved["r_multiple_net"]))
    dupes = resolved["date"].duplicated().sum()
    assert dupes == 0, f"{csv_name}: expected at most one trade per entry date, found {dupes} duplicate(s)"

    series = np.array([by_date.get(d, 0.0) for d in discovery_days], dtype=float)
    n_trades_placed = sum(1 for d in discovery_days if d in by_date)
    assert n_trades_placed == len(resolved), (
        f"{csv_name}: placed {n_trades_placed} trades but {len(resolved)} resolved rows exist "
        f"-- some trade date(s) fell outside the discovery day list"
    )
    return series


def main():
    print("=" * 78)
    print("Larry DSR/PBO -- first real application: Level Sweep Reversal")
    print("liquidity-filter family (hyp-000007, hyp-000008)")
    print("=" * 78)

    full_df, is_synthetic = load_price_data(context="apply_larry_liquidity_filter_family.py")
    if is_synthetic:
        print("ABORT: only synthetic data is available -- this evaluation requires real data.")
        return
    discovery_df = get_discovery_data(full_df)
    discovery_days = sorted(set(discovery_df.index.date))
    print(f"\nDiscovery trading days: {len(discovery_days)} "
          f"({discovery_days[0]} -> {discovery_days[-1]})")

    series_list = []
    for csv_name, strategy_name in VARIANT_FILES:
        s = build_daily_return_series(csv_name, discovery_days)
        n_nonzero = int(np.count_nonzero(s))
        print(f"  {csv_name} ({strategy_name}): {n_nonzero} trade-days placed on the daily axis")
        series_list.append(s)

    sibling_returns = np.vstack(series_list)  # shape (4, n_discovery_days)
    assert sibling_returns.shape == (4, len(discovery_days))

    results = {}
    for hid, config_idx in HYPOTHESIS_TO_CONFIG_INDEX.items():
        winner_returns = sibling_returns[config_idx]
        verdict = lv.evaluate_candidate(
            hypothesis_id=hid,
            winner_returns=winner_returns,
            sibling_returns=sibling_returns,
            n_trials_override=N_TRIALS_OVERRIDE,
        )
        results[hid] = verdict
        print(f"\n--- {hid} ({VARIANT_FILES[config_idx][1]}) ---")
        print(f"  n_trials_considered: {verdict.n_trials_considered} (override, see module docstring)")
        print(f"  DSR: {verdict.dsr:.4f}  (pass threshold: {lv.DSR_PASS_THRESHOLD})")
        print(f"  PBO: {verdict.pbo:.4f}  (fail threshold: {lv.PBO_FAIL_THRESHOLD})")
        print(f"  Recommended status: {verdict.recommended_status}")
        print(f"  Reasoning: {verdict.reasoning}")

    print("\n" + "=" * 78)
    print("Applying verdicts to the research ledger (append-only, non-destructive)")
    print("=" * 78)
    for hid, verdict in results.items():
        rl_result = lv.apply_verdict(verdict)
        print(f"  {hid}: logged -> {verdict.recommended_status}")

    return results


if __name__ == "__main__":
    main()

"""
study_cross_asset_weekly_trend.py
====================================

Implements the frozen spec in
`research/studies/cross-asset-weekly-trend-scoping.md` (v2, Advisor-
cleared 2026-09-07) -- exp-051. Fourth test touching the exp-047
signal family (047: raw signal, near-miss -> 048: hard-cap overlay,
kill -> 049: trailing-stop overlay, kill -> 051: this test), and
explicitly NOT a fresh independent first test -- see the frozen spec's
Section 3 for the selection-bias disclosure this script's own verdict
logic honors (a pass here is an ELIGIBILITY result, not a promotion).

WHAT THIS TESTS: does exp-047's weekly momentum signal (sign of
trailing 52-week cumulative log return, weekly rebalance), applied
INDEPENDENTLY across 4 instruments spanning different asset classes
(NQ equity index, ZN rates, 6E currency, CL commodity) and combined
into ONE inverse-volatility-weighted portfolio, clear the same
two-part promotion bar that no single-instrument version ever has?

CANNOT RUN UNTIL DATA EXISTS: this script requires
ZN_1min_databento_*.csv, 6E_1min_databento_*.csv, and
CL_1min_databento_*.csv in data/ -- produced by
data_fetch_databento_cross_asset.py, which requires Jason's own
Databento API key entered on his own machine (see that script's
docstring). Running this before those files exist will abort cleanly
with a clear message, not a confusing crash.

REUSED, UNMODIFIED, PER INSTRUMENT:
  - compute_daily_ref_closes, compute_daily_log_returns,
    compute_trailing_volatility (from study_volatility_regime.py --
    the vol-sizing lookup is the EXACT SAME causal, 20-trading-day,
    strictly-before-day_t function already used for this project's
    volatility-regime work, not a new implementation)
  - resample_to_weekly_closes, compute_weekly_log_returns,
    compute_weekly_momentum_signal (from
    study_nq_weekly_trend_following.py -- exp-047's own functions)
  - compute_positions, analyze_primary, bootstrap_mean_ci,
    robustness_drop_largest_pnl_day, robustness_split_half (from
    study_nq_trend_following.py)

NEW CODE (per the frozen spec): combining the 4 instruments' signed
weekly returns into one inverse-volatility-weighted portfolio return
series, in RETURN SPACE (not points -- exp-047/048/049/050's raw-point
P&L convention is meaningless across instruments with different
contract multipliers; see frozen spec Section 5). Cost is modeled as a
disclosed 5-basis-point-of-notional drag per instrument per flip, the
same figure this project's own FLIP_COST_POINTS implies for NQ at
current price levels (1.5 points / ~29,628 ~= 5.1 bps) -- applied
uniformly to all 4 instruments as a conservative, disclosed assumption
per the frozen spec's cost-scaling requirement (Section 7), not
invented from an unrelated source.

NO-LOOKAHEAD: compute_trailing_volatility(day_t) already only uses
returns strictly before day_t (verified against its own docstring and
this project's existing volatility-regime study). Calling it with
day_t = each week's FIRST trading day gives exactly the "vol computed
through the prior week's last trading day" rule the frozen spec
requires -- reused, not reimplemented.

HOW TO RUN:
    python3 src/study_cross_asset_weekly_trend.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_discovery_data
from study_volatility_regime import (  # reused unmodified
    compute_daily_ref_closes,
    compute_daily_log_returns,
    compute_trailing_volatility,
)
from study_nq_weekly_trend_following import (  # reused unmodified
    resample_to_weekly_closes,
    compute_weekly_log_returns,
    compute_weekly_momentum_signal,
)
from study_nq_trend_following import (  # reused unmodified
    compute_positions,
    analyze_primary,
    robustness_drop_largest_pnl_day,
    robustness_split_half,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Frozen spec Section 7: disclosed, conservative per-flip cost assumption,
# derived from this project's OWN existing NQ cost convention
# (FLIP_COST_POINTS = 1.5 points at ~29,628 -- about 5.1 bps of notional),
# applied uniformly across all 4 instruments rather than inventing a
# separate unrelated number per instrument.
FLIP_COST_BPS = 5.0
FLIP_COST_FRACTION = FLIP_COST_BPS / 10_000.0

BASKET = [
    ("NQ", "Nasdaq-100 e-mini futures (equity index)"),
    ("ZN", "10-Year Treasury Note futures (rates)"),
    ("6E", "Euro FX futures (currency)"),
    ("CL", "WTI Crude Oil futures (commodity)"),
]


def load_instrument_signal(symbol: str) -> dict:
    """Everything needed for one instrument: causal weekly positions,
    weekly returns, and a causal daily-volatility lookup -- all via
    exp-047's and study_volatility_regime's existing functions,
    unmodified. Returns None if this instrument's data file doesn't
    exist yet (expected/normal while waiting on data_fetch_databento_
    cross_asset.py to be run, not an error)."""
    try:
        full_df, is_synthetic = load_price_data(
            context=f"study_cross_asset_weekly_trend.py ({symbol})", symbol=symbol
        )
    except FileNotFoundError:
        return None
    if is_synthetic:
        return None

    discovery_df = get_discovery_data(full_df)
    day_groups = {day: sub for day, sub in discovery_df.groupby(discovery_df.index.date)}
    ref_closes = compute_daily_ref_closes(day_groups)
    daily_returns = compute_daily_log_returns(ref_closes)  # reused unmodified
    days_sorted = sorted(ref_closes.keys())
    vol_by_day = compute_trailing_volatility(daily_returns, days_sorted)  # reused unmodified

    weekly_closes = resample_to_weekly_closes(ref_closes)
    weekly_returns = compute_weekly_log_returns(weekly_closes)
    all_weeks = sorted(weekly_closes.keys())
    mom_by_week = compute_weekly_momentum_signal(weekly_returns, all_weeks)
    positions = compute_positions(mom_by_week)  # reused unmodified

    day_to_week = {}
    for day in days_sorted:
        iso_year, iso_week, _ = day.isocalendar()
        day_to_week.setdefault((iso_year, iso_week), []).append(day)

    return {
        "positions": positions,
        "weekly_returns": weekly_returns,
        "weekly_closes": weekly_closes,
        "vol_by_day": vol_by_day,
        "day_to_week": day_to_week,
    }


def compute_portfolio_pnl(instrument_data: dict) -> tuple:
    """Combines the instruments present into one inverse-volatility-
    weighted portfolio weekly return series (frozen spec Section 5).
    Only weeks where EVERY instrument has a classifiable position AND a
    valid trailing volatility are included, so the combined series is
    never silently built from a partial basket for some weeks and a
    full one for others."""
    symbols = list(instrument_data.keys())

    # Weeks classifiable (position exists) for every instrument.
    common_weeks = None
    for sym in symbols:
        d = instrument_data[sym]
        weeks = set(w for w in d["positions"].keys() if d["weekly_returns"].get(w) is not None)
        common_weeks = weeks if common_weeks is None else (common_weeks & weeks)
    common_weeks = sorted(common_weeks)

    rows = []
    dropped_no_vol = 0
    for w in common_weeks:
        per_instrument = {}
        ok = True
        for sym in symbols:
            d = instrument_data[sym]
            week_days = sorted(d["day_to_week"].get(w, []))
            if not week_days:
                ok = False
                break
            first_day = week_days[0]
            vol = d["vol_by_day"].get(first_day)
            if vol is None or vol <= 0:
                ok = False
                break
            per_instrument[sym] = {
                "position": d["positions"][w],
                "weekly_return": d["weekly_returns"][w],
                "vol": vol,
            }
        if not ok:
            dropped_no_vol += 1
            continue

        # Inverse-volatility weights, renormalized to sum to 1 each week
        # (frozen spec Section 5: equal risk budget, not equal dollar).
        inv_vols = {sym: 1.0 / per_instrument[sym]["vol"] for sym in symbols}
        total_inv_vol = sum(inv_vols.values())
        weights = {sym: inv_vols[sym] / total_inv_vol for sym in symbols}

        portfolio_return = sum(
            weights[sym] * per_instrument[sym]["position"] * per_instrument[sym]["weekly_return"]
            for sym in symbols
        )

        # Cost: each instrument that flipped this week costs its own
        # weight * FLIP_COST_FRACTION -- turnover doesn't shrink just
        # because the portfolio is diversified (frozen spec Section 7).
        n_flips_this_week = 0
        portfolio_cost = 0.0
        for sym in symbols:
            d = instrument_data[sym]
            # determine flip by looking at this instrument's own previous classifiable week
            prior_weeks = sorted(pw for pw in d["positions"].keys() if pw < w)
            if prior_weeks:
                prev_position = d["positions"][prior_weeks[-1]]
                flipped = prev_position != per_instrument[sym]["position"]
            else:
                flipped = False
            if flipped:
                n_flips_this_week += 1
                portfolio_cost += weights[sym] * FLIP_COST_FRACTION

        rows.append({
            "date": f"{w[0]}-W{w[1]:02d}",
            "position": None,  # not meaningful at the portfolio level (4 instruments, mixed signs)
            "flipped": n_flips_this_week,  # count of instruments that flipped this week
            "price_change": portfolio_return,
            "pnl": portfolio_return,
            "cost": portfolio_cost,
            "net_pnl": portfolio_return - portfolio_cost,
        })

    return pd.DataFrame(rows), dropped_no_vol


def main():
    print("=" * 78)
    print("CROSS-ASSET DIVERSIFIED TEST OF THE WEEKLY TREND SIGNAL (exp-051)")
    print("=" * 78)

    instrument_data = {}
    missing = []
    for symbol, label in BASKET:
        result = load_instrument_signal(symbol)
        if result is None:
            missing.append((symbol, label))
        else:
            instrument_data[symbol] = result

    if missing:
        print("\nABORT: this test needs all 4 instruments' data, and the following are "
              "not available yet:")
        for symbol, label in missing:
            print(f"  - {symbol} ({label})")
        print("\nRun data_fetch_databento_cross_asset.py first (requires Jason's own "
              "Databento API key, entered on his own machine -- see that script's "
              "docstring). This is expected/normal until that's done, not an error in "
              "this script.")
        return

    print(f"\nAll 4 instruments loaded: {', '.join(sym for sym, _ in BASKET)}")

    pnl_df, dropped_no_vol = compute_portfolio_pnl(instrument_data)
    print(f"Portfolio weeks with a computed combined return: {len(pnl_df)} "
          f"({dropped_no_vol} week(s) dropped for missing volatility/position data across "
          f"the basket)")

    primary = analyze_primary(pnl_df)  # reused unmodified
    print("\n--- PRIMARY: mean weekly portfolio net return (inverse-vol-weighted, 4 instruments) ---")
    for k, v in primary.items():
        print(f"  {k}: {v}")

    print(f"\n  Step-2-gate check 1 (statistically credible): {primary['statistically_credible']}")
    print(f"  Step-2-gate check 2 (economically meaningful, >= 2x own realized cost drag): "
          f"{primary['economically_meaningful']}")
    print(f"\n  MANDATORY DISCLOSURE -- total instrument-flips across the basket: "
          f"{primary['n_flips']} across {primary['n']} portfolio weeks")

    print("\n--- Robustness (a): drop single largest-magnitude weekly net return week ---")
    drop_result = robustness_drop_largest_pnl_day(pnl_df)  # reused unmodified
    for k, v in drop_result.items():
        print(f"  {k}: {v}")

    print("\n--- Robustness (b): first-half vs second-half split-sample stability ---")
    split_result = robustness_split_half(pnl_df)  # reused unmodified
    print("  First half:", split_result["first_half"])
    print("  Second half:", split_result["second_half"])

    print("\n--- Per-instrument disclosure (frozen spec Section 6: no hiding behind one market) ---")
    per_instrument_results = {}
    for symbol, label in BASKET:
        d = instrument_data[symbol]
        weeks = sorted(w for w in d["positions"].keys() if d["weekly_returns"].get(w) is not None)
        rows = []
        for i in range(1, len(weeks)):
            prev_w, w = weeks[i - 1], weeks[i]
            position = d["positions"][w]
            prev_position = d["positions"][prev_w]
            weekly_return = d["weekly_returns"][w]
            flipped = position != prev_position
            cost = FLIP_COST_FRACTION if flipped else 0.0
            rows.append({
                "date": f"{w[0]}-W{w[1]:02d}",
                "flipped": bool(flipped),
                "pnl": position * weekly_return,
                "cost": cost,
                "net_pnl": position * weekly_return - cost,
            })
        inst_df = pd.DataFrame(rows)
        inst_primary = analyze_primary(inst_df)
        per_instrument_results[symbol] = inst_primary
        print(f"  {symbol} ({label}): mean={inst_primary['mean_net_pnl']:.6f}, "
              f"ci_90={inst_primary['ci_90']}, "
              f"statistically_credible={inst_primary['statistically_credible']}, "
              f"economically_meaningful={inst_primary['economically_meaningful']}")

    print("\n" + "=" * 78)
    if primary["statistically_credible"] and primary["economically_meaningful"]:
        verdict = (
            "ELIGIBLE FOR OUT-OF-SAMPLE CORROBORATION -- clears both gates on the "
            "combined portfolio. Per the frozen spec's Section 3 signal-family-lineage "
            "disclosure, this is NOT treated as confirmed edge or a promotion: it is "
            "the same status exp-047's raw signal would have earned had it passed "
            "outright. Next step is Validation-slice or prospective corroboration "
            "(same spirit as exp-050), not a live-authorization conversation."
        )
    else:
        verdict = (
            "kill -- does not clear the adapted statistical/economic gate on the "
            "combined portfolio. Diversification did not turn this near-miss into a "
            "pass on this basket, on this data."
        )
    print(f"Verdict: {verdict}")

    out = {
        "primary": primary,
        "robustness_drop_largest": drop_result,
        "robustness_split_half": split_result,
        "per_instrument": per_instrument_results,
        "verdict": verdict,
        "flip_cost_bps": FLIP_COST_BPS,
        "basket": [sym for sym, _ in BASKET],
    }
    json_path = DATA_DIR / "study_cross_asset_weekly_trend_discovery_results.json"
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    pnl_df.to_csv(DATA_DIR / "study_cross_asset_weekly_trend_discovery.csv", index=False)
    print(f"\nSaved full results to {json_path}.")


if __name__ == "__main__":
    main()

"""
study_midday_afternoon_persistence_holdout.py
==============================================

HOLDOUT GENERATION 2 test of hyp-000105/106 (OBS-FINDING-011), frozen spec:
research/studies/midday-lull-holdout-spec-frozen-2026-09-12.md.
Consumes Holdout Gen 2 slot 2 of 5 -- Jason's explicit sign-off given
September 11th, 7:27 pm CT ("Yes let's run the hold out session").

A verbatim copy of study_midday_afternoon_persistence_prospective.py with
ONLY the scored window switched to Holdout Gen 2 and the output filename
changed. Nothing retuned. --diagnostic runs the corrected-boundary
re-expression (afternoon window opened at 14:01 so the 14:00 bar is not
shared) on the SAME data as a disclosed diagnostic, per the blind Gate's
condition (a); it is not a second slot.

HOW TO RUN:
    python3 src/study_midday_afternoon_persistence_holdout.py
    python3 src/study_midday_afternoon_persistence_holdout.py --diagnostic
"""
import sys
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_holdout_gen2_data, _research_only
from research_ledger import log_hypothesis

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOOKBACK_DAYS = 20
NARROW_PCTL = 20
N_BOOTSTRAP = 3000
MIN_N = 40


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=7):
    if len(values) < 2:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    means = rng.choice(arr, size=(n_bootstrap, len(arr)), replace=True).mean(axis=1)
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def main():
    print("=" * 78)
    diagnostic = "--diagnostic" in sys.argv
    print("OBS-FINDING-011 HOLDOUT GENERATION 2 (slot 2 of 5)" + (" -- BOUNDARY DIAGNOSTIC" if diagnostic else ""))
    print("=" * 78)
    print("\nFrozen spec: research/studies/midday-lull-holdout-spec-frozen-2026-09-12.md\n")

    df, is_synthetic = load_price_data(context="study_midday_afternoon_persistence_holdout.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    research_df = _research_only(df, "study_midday_afternoon_persistence_holdout.py")
    combined = research_df  # warm-up continuous across Discovery + Validation + Holdout
    idx = combined.index
    day_groups = {d: g for d, g in combined.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    holdout = get_holdout_gen2_data(df)
    validation_days = set(holdout.index.date)   # variable name kept so the scoring code below is byte-identical
    print(f"Holdout-window days to score: {len(validation_days)}")

    rows = []
    for day in days_sorted:
        day_df = day_groups[day]
        midday = day_df.between_time("12:00", "14:00")
        afternoon = day_df.between_time("14:01" if diagnostic else "14:00", "16:00")
        if midday.empty or afternoon.empty:
            continue
        midday_range = float(midday["High"].max() - midday["Low"].min())
        afternoon_range = float(afternoon["High"].max() - afternoon["Low"].min())
        rows.append({"date": day, "midday_range": midday_range, "afternoon_range": afternoon_range})

    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["trailing_avg_afternoon_range"] = daily["afternoon_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).mean().shift(1)
    narrow_thresh = daily["midday_range"].rolling(LOOKBACK_DAYS, min_periods=LOOKBACK_DAYS).apply(
        lambda w: np.percentile(w, NARROW_PCTL), raw=True).shift(1)

    valid = daily.dropna(subset=["trailing_avg_afternoon_range"]).copy()
    valid["afternoon_range_ratio"] = valid["afternoon_range"] / valid["trailing_avg_afternoon_range"]
    valid["is_narrow_midday"] = valid["midday_range"] <= narrow_thresh.reindex(valid.index)
    valid = valid[valid.index.isin(validation_days)]

    narrow = valid.loc[valid["is_narrow_midday"], "afternoon_range_ratio"].dropna().tolist()
    not_narrow = valid.loc[~valid["is_narrow_midday"], "afternoon_range_ratio"].dropna().tolist()

    print(f"\nHoldout-slice narrow-midday days: {len(narrow)}, not-narrow: {len(not_narrow)}")

    result = {}
    for label, vals in (("narrow_midday", narrow), ("not_narrow_midday", not_narrow)):
        if len(vals) < 10:
            continue
        ci = bootstrap_mean_ci(vals)
        credible = bool(vals) and (ci[0] > 1.0 or ci[1] < 1.0)
        result[label] = {"n": len(vals), "mean_afternoon_range_ratio": float(np.mean(vals)), "ci_90": ci, "statistically_credible": credible}
        print(f"{label}: {result[label]}")

    verdict = "NO_DATA"
    if "narrow_midday" in result:
        n = result["narrow_midday"]["n"]
        cred = result["narrow_midday"]["statistically_credible"]
        mean_ratio = result["narrow_midday"]["mean_afternoon_range_ratio"]
        if cred and mean_ratio < 1.0 and n >= MIN_N:
            verdict = "HOLDOUT_PASS"
        elif cred and n >= MIN_N:
            verdict = "HOLDOUT_FAIL_WRONG_DIRECTION"
        else:
            verdict = "HOLDOUT_FAIL"
    print(f"\nVerdict: {verdict}")

    out = {"search_batch_id": "batch-2026-09-12-obs-finding-011-holdout-gen2", "diagnostic": diagnostic,
           "result": result, "verdict": verdict}
    out_path = DATA_DIR / ("study_midday_afternoon_persistence_holdout_diagnostic_results.json" if diagnostic
                           else "study_midday_afternoon_persistence_holdout_results.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")

    if not diagnostic and "narrow_midday" in result:
        r = result["narrow_midday"]
        status = "HOLDOUT PASSED" if verdict == "HOLDOUT_PASS" else "REJECTED"
        log_hypothesis(
            strategy_name="midday_lull_afternoon_expansion_holdout",
            strategy_origin="derivative",
            parameters={"n": r["n"], "mean_afternoon_range_ratio": r["mean_afternoon_range_ratio"],
                        "ci_90": r["ci_90"], "statistically_credible": r["statistically_credible"],
                        "lookback_days": LOOKBACK_DAYS, "narrow_pctl": NARROW_PCTL, "min_n": MIN_N},
            data_slice_used="holdout_gen2",
            trade_count=r["n"],
            strategy_status=status,
            parent_hypothesis_id="hyp-000106",
            notes=(f"hyp-000105/106 HOLDOUT GENERATION 2 (slot 2 of 5), Jason's explicit sign-off "
                   f"September 11th, 7:27 pm CT. Frozen spec research/studies/midday-lull-holdout-spec-frozen-2026-09-12.md, "
                   f"identical to the Validation test, nothing retuned. Holdout narrow n={r['n']}, mean ratio="
                   f"{r['mean_afternoon_range_ratio']:.3f}, ci_90={[round(x,3) for x in r['ci_90']]}. Verdict: {verdict}. "
                   f"Blind Integrity Gate CONDITIONAL PASS (conditions resolved in spec). Boundary diagnostic run separately."),
        )
        print("Logged to research/ledger/hypotheses.jsonl; set holdout_slot_id via research_ledger.update_status.")


if __name__ == "__main__":
    main()

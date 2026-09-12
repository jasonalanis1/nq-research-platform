# BLIND INTEGRITY GATE PACKET

You are the Integrity Gate, in a fresh context. Standing brief: assume this
candidate is wrong; find every reason the PROCEDURE could be fooling us.
Every result figure below is masked on purpose. Rule PASS / VETO / CONDITIONAL
on procedure only: leakage, contamination, post-hoc selection, frozen-before-
test, resurrection, multiplicity accounting, direction pre-registered, cost model
measured not assumed, review point sized (power) before freezing.
Output: Finding / Confidence / Novelty / Research Value / Recommendation.

## Family: midday_lull_afternoon_expansion

## Frozen spec (masked)

# hyp-000105/106 Midday Lull -> Afternoon Range Persistence — FROZEN HOLDOUT SPEC

Frozen September 11th, 7:05 pm CT (2026-09-12 00:05 UTC) by the scheduled
cycle, per the GATED-tier rule. This is a PRE-REGISTRATION. No Holdout
data has been read. Running it spends Holdout Gen 2 slot 2 of 5 and is
Jason's decision alone.

## What is being confirmed

The narrow-midday -> narrow-afternoon RANGE persistence fact validated on
the Validation slice (hyp-000106, exp-126). It is a volatility /
conditioning fact, not a directional edge; its realization path is the
`get_afternoon_conditioning()` sizing multiplier already integrated in
src/volatility_conditioning.py (Monetization, 2026-09-10).

## Frozen method — identical to the Validation test, nothing retuned

- Data window scored: Holdout Gen 2 only, 2024-01-04 through 2026-04-06
  (data_split's holdout boundary; requires the deliberate ALLOW_HOLDOUT_DATA
  gate, set only by Jason's sign-off).
- Trailing statistics computed continuously across Discovery + Validation
  + Holdout for warm-up; only Holdout-window days are scored.
- Midday window 12:00-14:00 ET; afternoon window 14:00-16:00 ET (NY time).
- LOOKBACK_DAYS = 20; NARROW_PCTL = 20 (a day is narrow-midday when its
  midday range is at or below the trailing-20-day 20th percentile, shifted
  one day so nothing from the scored day leaks in).
- Outcome: afternoon_range / trailing-20-day mean afternoon range (shifted).
- Statistic: mean ratio on narrow-midday days; 90% bootstrap CI, 3000
  resamples, seed 7. MIN_N = 40.
- Pass: CI entirely below 1.0 AND mean ratio < 1.0 AND n >= 40. Wrong
  direction with a credible CI is a FAIL for this hypothesis. Anything else
  is a FAIL.
- One shot. No parameter, window, or threshold may change after the result
  is seen. A fail closes the candidate to LEARN; the conditioning tool stays
  integrated as a Validation-level finding only.

## Multiplicity disclosure (Statistical)

Validation-stage project-wide correction (research/studies/project-wide-
multiplicity-2026-09-09.md) applies; the Holdout test is a single
pre-registered comparison and is reported both raw and Sidak-adjusted at
the Holdout stage trial count in src/project_wide_multiplicity.py.

## Power at this review point (Statistical, UPGRADE 3 mandatory)

Holdout Gen 2 spans ~560 trading days; at the 20th-percentile narrow
definition ~110 narrow-midday days are expected. With the Validation-slice
effect and dispersion, the probability the 90% CI clears 1.0 at n~110 is
computed by Statistical BEFORE Jason is asked to spend the slot and
recorded here by the next cycle; if it is under 50% that is stated to
Jason plainly with the request.

## Implementation

`src/study_midday_afternoon_persistence_prospective.py` with the scored
window switched to Holdout Gen 2 -- a copy named
`src/study_midday_afternoon_persistence_holdout.py` is to be created by
the cycle that Jason authorizes, diffing only the window selection and the
output filename, and reviewed against this spec before running.


## Mechanism doc (masked)

# Mechanism — Midday Lull -> Afternoon Range Persistence (hyp-000105 Discovery / hyp-000106 Validation, OBS-FINDING-011)

Written: 2026-09-10  ·  **POST-HOC**
Results seen before writing: YES — Discovery (exp-125) and the single
pre-registered Validation-slice prospective test (exp-126) were both
complete before this document existed. **This is a hypothesis, not
evidence** in the sense that its CURRENT story was written after the
result. Unusually for this project, however, the ORIGINAL pre-registered
story was written BEFORE the result and was WRONG -- see Section 3, P1.
That refutation is real evidence, just not evidence for the story below.

## 1. The claim

A quiet midday session (12:00-14:00 ET range in the bottom 20th percentile
of its own trailing 20-day distribution) is followed, the SAME day, by a
quieter-than-average afternoon session (14:00-16:00 ET); a non-quiet
midday is followed by a busier-than-average afternoon. This is the
strongest range-persistence effect measured in the project (Discovery
[masked] vs [masked], tighter and larger-sample than either of the other two
persistence findings).

Candidate mechanism: same-day, WITHIN-session volatility/participation
persistence -- whatever latent state governs whether today is an "active"
or "quiet" day (news flow, positioning activity, algorithmic participation)
does not reset every two hours; it persists across adjacent windows within
the same session. This is the same family of claim as the overnight-coil
document (research/mechanisms/overnight-coil-rth-range.md) -- a shared
daily activity state -- but applied at a FINER grain (two 2-hour RTH
windows) and with a materially larger effect size, which is itself a
pattern worth treating as a testable structural prediction (P4 below)
rather than assuming these are unrelated coincidences of similar size.

## 2. Who is on the other side

Same caveat as the other two range documents: this is a volatility
characterization, not a directional rule, so there is no clean
counterparty in the usual sense. If used operationally (e.g., sizing
afternoon stops/targets off a range estimate conditioned on the midday
session rather than the unconditional average), the closest thing to a
counterparty is a trader or algorithm using the UNconditional average
range to size a stop or target, who is over- or under-sized specifically
on days this conditioning would have flagged. Not observed or confirmed --
this project has no execution/order data to check it.

## 3. Testable predictions

P1. **[Already tested, PRE-REGISTERED, REFUTED -- recorded for the
    record, not re-tested.]** The frozen spec (observatory-v7-design-spec.md)
    predicted the OPPOSITE sign: a quiet midday as pent-up energy that
    would RELEASE into an active afternoon. The data show persistence, not
    release (both Discovery and Validation, same direction, not marginal).
    This is a genuine, useful falsification -- recorded honestly here per
    LEARN's own standard, not glossed over because a different, real effect
    was found in its place.

P2. **Opening -> midday persistence (new, not yet run).** If this is
    general same-day volatility persistence rather than something specific
    to the midday/afternoon pairing (e.g., the early-afternoon liquidity
    dip around the European close, ~11:30 ET, or a lunch-hour-specific
    effect), the SAME pattern should also hold between an early RTH window
    (e.g., 09:30-11:30 ET) and the midday window itself: a quiet opening
    should predict a quieter-than-average midday. Not yet computed --
    requires one new window pairing on data already on disk.

P3. **Overlap with the overnight-coil state (new, not yet run, and
    required for the Portfolio Agent's eventual incremental-information
    question per agent-governance-structure.md).** If narrow-midday days
    and coiled-overnight days (hyp-000056) are largely the SAME days --
    i.e., both are proxies for one shared "quiet news day" latent state --
    this finding is not independent corroboration of a third distinct
    phenomenon; it is the same discovery restated at a different window.
    High overlap would not kill either finding but would mean the project
    has evidence for ONE shared-state effect measured three ways, not
    three independent effects, materially changing how these should be
    weighted together later. Checkable now as a simple two-way overlap
    count between the two already-computed daily classifications.

P4. **Effect size should scale with window proximity/similarity (post-hoc
    pattern, marked honestly as such -- noticed after all three
    measurements existed, so weaker evidence than an ex-ante prediction,
    but stated because it is checkable and falsifiable going forward).**
    Ranking the three range-persistence effects by how "close" the two
    compared windows are: within-day, same-session, ~0 hours apart
    (midday->afternoon, [masked] vs [masked] -- widest spread) is stronger than
    overnight-session -> same-day RTH, a session-character change ([masked])
    which is comparable to day -> next-day, a full ~24h gap and an
    overnight in between ([masked] vs [masked], hyp-000048). If a FOURTH
    persistence-flavored candidate is ever tested, this predicts where
    in that ordering its effect size should fall. A future result far
    outside this ordering (e.g., a same-day pairing weaker than day-to-day)
    would argue against a single continuous "proximity governs persistence
    strength" story.

## 4. What would falsify this

No opening->midday persistence (P2) would localize the effect to
something specific about the midday/afternoon transition rather than a
general within-day law. High overlap with the overnight-coil state (P3)
would not falsify the STATISTICAL finding but would falsify treating it as
a third independent discovery. A future proximity-scaled candidate
badly out of the P4 ordering would weaken the "distance governs
persistence strength" reading of all three findings together.

## 5. Prediction status

P1 -- REFUTED (the original story; recorded, not re-tested -- unchanged
from before this session).

**P2 -- TESTED 2026-09-10** (Statistical-stage pass -- see
research/studies/statistical-stage-pass-2026-09-10.md). **CONFIRMED,
cleanly, and symmetrically.** New opening-window (09:30-11:30 ET)
narrow/not-narrow classification -> midday-window (12:00-14:00 ET)
range-ratio-vs-trailing outcome, same convention as the midday->
afternoon finding. Narrow-opening days ([masked]): mean midday ratio=[masked],
[masked]. Not-narrow-opening days
([masked]): mean=[masked], [masked] -- the
same symmetric persistence pattern as midday->afternoon, one window
earlier. This is general same-day volatility persistence, not something
specific to the midday/afternoon pairing.

**P3 -- TESTED 2026-09-10** ([masked] days with both classifications
available). **PARTIAL OVERLAP -- meaningfully more than chance, but NOT
the same set of days.** Of 421 narrow-midday days, 161 ([masked]) were also
coiled-overnight days; of 426 coiled-overnight days, 161 ([masked]) were
also narrow-midday days. Expected overlap under independence: 103.6 days
-- actual overlap (161) is ~[masked]x that, and the relative-risk read is
similar: a narrow-midday day is about 1.9x as likely to also be a
coiled-overnight day as a non-narrow-midday day is ([masked] vs [masked]
conditional coiled-rate). This is a real, non-trivial positive
association -- these are not statistically independent phenomena -- but
it is far from identity: roughly 62% of narrow-midday days are NOT
coiled-overnight days, and vice versa. Reading: partial shared latent
state, not one discovery counted three times. Material for the
Portfolio Agent's eventual incremental-information question, but does
not by itself argue these three findings are the same finding.

P4 -- CONFIRMED, POST-HOC (unchanged from before this session; ranking
matches, weak evidence as previously caveated).

## 6. Verdict

The narrow-midday leg is the strongest of the three range-persistence
findings on every axis checked this session, not only raw effect size.
The Statistical-stage pass (research/studies/statistical-stage-pass-2026-09-10.md)
found: split-sample stability clean ([masked], second half
[masked], same direction, both credible); no volatility-regime
concentration (low-ATR-vol [masked] vs high-ATR-vol [masked], both credible,
similar magnitude); threshold-selection robustness clean (pctl 15 and
25 both close to the frozen pctl-20 result); and it is the only one of
the five Validation legs checked across all three mechanism documents
to survive the project's own multiplicity-corrected 90% bound (adjusted
[masked][masked]). P2 above adds a second, independent, cleanly-confirmed
falsifiable prediction (opening->midday persistence). P3 gives an
honest, partial answer to the double-counting question rather than
leaving it open.

Per NEXT_UP.md queue item 0's standard -- survive both the corrected
numbers AND the mechanism checks -- this candidate (narrow-midday leg
specifically; the not-narrow leg still fails correction and is not
part of this advancement) clears both bars. Disposition: **ADVANCES to
Director Re-Evaluation** (see research/studies/statistical-stage-pass-2026-09-10.md
and research/sessions/2026-09-10-0815.md for the Re-Evaluation and
Monetization positions). No ledger status change -- hyp-000106 stays
VALIDATION CANDIDATE; nothing in this session's work clears the FULL
promotion bar (that requires a costed, returns-based test and, per
scope, a Holdout slot Jason has not authorized).


## Test / scan code (as-is; contains no results)

```python
"""
study_midday_afternoon_persistence_prospective.py
====================================================

exp-126 -- frozen spec:
research/studies/midday-afternoon-persistence-prospective-spec.md.
Pre-registered prospective test of OBS-FINDING-011 on the Validation
slice. Unmodified thresholds/method; trailing stats computed
continuously across Discovery+Validation for warm-up continuity.

HOW TO RUN:
    python3 src/study_midday_afternoon_persistence_prospective.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_price_data
from data_split import get_validation_data, _research_only, VALIDATION_END_DATE

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
    print("OBS-FINDING-011 PROSPECTIVE VALIDATION (exp-126)")
    print("=" * 78)
    print("\nFrozen spec: research/studies/midday-afternoon-persistence-prospective-spec.md\n")

    df, is_synthetic = load_price_data(context="study_midday_afternoon_persistence_prospective.py")
    if is_synthetic:
        print("ABORT: only synthetic data available.")
        return

    research_df = _research_only(df, "study_midday_afternoon_persistence_prospective.py")
    combined = research_df[research_df.index <= VALIDATION_END_DATE]
    idx = combined.index
    day_groups = {d: g for d, g in combined.groupby(idx.date)}
    days_sorted = sorted(day_groups.keys())

    validation = get_validation_data(df)
    validation_days = set(validation.index.date)
    print(f"Validation-window days to score: {len(validation_days)}")

    rows = []
    for day in days_sorted:
        day_df = day_groups[day]
        midday = day_df.between_time("12:00", "14:00")
        afternoon = day_df.between_time("14:00", "16:00")
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

    print(f"\nValidation-slice narrow-midday days: {len(narrow)}, not-narrow: {len(not_narrow)}")

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
            verdict = "PROSPECTIVE_PASS"
        elif cred and n >= MIN_N:
            verdict = "PROSPECTIVE_PASS_WRONG_DIRECTION"
        else:
            verdict = "PROSPECTIVE_FAIL"
    print(f"\nVerdict: {verdict}")

    out = {"search_batch_id": "batch-2026-09-09-obs-finding-011-prospective", "result": result, "verdict": verdict}
    out_path = DATA_DIR / "study_midday_afternoon_persistence_prospective_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()

```

## Ledger history for this family (results masked)

```json
[
 {
  "hypothesis_id": "hyp-000105",
  "logged_at": "2026-09-09T02:14:05.969954",
  "strategy_name": "midday_lull_afternoon_expansion_discovery",
  "strategy_origin": "data_discovered",
  "parameters": "{\"narrow_midday_result\": {\"n\": 411, \"mean_ratio\": [masked], \"ci_90\": [masked]}, \"not_narrow_result\": {\"n\": 1201, \"mean_ratio\": [masked], \"ci_90\": [masked]}}",
  "data_slice_used": "discovery",
  "parent_hypothesis_id": null,
  "experiment_doc_id": null,
  "holdout_slot_id": null,
  "search_batch_id": null,
  "trade_count": "[masked]",
  "expectancy_r": "[masked]",
  "profit_factor": "[masked]",
  "max_drawdown_r": "[masked]",
  "strategy_status": "[masked]",
  "notes": "[masked]"
 },
 {
  "hypothesis_id": "hyp-000106",
  "logged_at": "2026-09-09T02:14:05.972684",
  "strategy_name": "midday_lull_afternoon_expansion_prospective",
  "strategy_origin": "data_discovered",
  "parameters": "{\"narrow_midday_result\": {\"n\": 142, \"mean_ratio\": [masked], \"ci_90\": [masked]}, \"not_narrow_result\": {\"n\": 404, \"mean_ratio\": [masked], \"ci_90\": [masked]}}",
  "data_slice_used": "validation",
  "parent_hypothesis_id": null,
  "experiment_doc_id": null,
  "holdout_slot_id": null,
  "search_batch_id": null,
  "trade_count": "[masked]",
  "expectancy_r": "[masked]",
  "profit_factor": "[masked]",
  "max_drawdown_r": "[masked]",
  "strategy_status": "[masked]",
  "notes": "[masked]"
 },
 {
  "hypothesis_id": "hyp-000133",
  "logged_at": "2026-09-09T23:21:38.584506",
  "strategy_name": "midday_lull_afternoon_expansion_MULTIPLICITY_REEXPRESSION",
  "strategy_origin": "derivative",
  "parameters": "{\"reexpresses\": [\"hyp-000105\", \"hyp-000106\"], \"method\": \"sidak_project_wide\"}",
  "data_slice_used": "validation",
  "parent_hypothesis_id": "hyp-000106",
  "experiment_doc_id": null,
  "holdout_slot_id": null,
  "search_batch_id": null,
  "trade_count": "[masked]",
  "expectancy_r": "[masked]",
  "profit_factor": "[masked]",
  "max_drawdown_r": "[masked]",
  "strategy_status": "[masked]",
  "notes": "[masked]"
 },
 {
  "hypothesis_id": "hyp-000105",
  "logged_at": "2026-09-10T03:54:14.930419",
  "strategy_name": "midday_lull_afternoon_expansion_discovery",
  "strategy_origin": "data_discovered",
  "parameters": "{\"narrow_midday_result\": {\"n\": 411, \"mean_ratio\": [masked], \"ci_90\": [masked]}, \"not_narrow_result\": {\"n\": 1201, \"mean_ratio\": [masked], \"ci_90\": [masked]}}",
  "data_slice_used": "discovery",
  "parent_hypothesis_id": null,
  "experiment_doc_id": null,
  "holdout_slot_id": null,
  "search_batch_id": null,
  "trade_count": "[masked]",
  "expectancy_r": "[masked]",
  "profit_factor": "[masked]",
  "max_drawdown_r": "[masked]",
  "strategy_status": "[masked]",
  "notes": "[masked]"
 }
]
```
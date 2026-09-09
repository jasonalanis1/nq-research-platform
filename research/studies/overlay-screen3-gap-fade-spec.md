# Overlay Screen 3: Validated Volatility Findings on the Gap-Fade Near-Miss (H87/H89)

Frozen 2026-09-09. Same overlay-screen technique as exp-077 (hyp-000049)
and exp-086/087 (hyp-000058/059) -- test whether an already-validated
Layer-1 volatility/range-persistence fact conditions the economics of
an existing signal. Never before applied to H87/H89, the project's
closest-ever near-miss (long leg: n=128, mean_r=+0.068,
ci_90=(-0.015, 0.152)).

## Method (unchanged from prior overlay screens, frozen before result)

1. Reuse H89's exact signal/entry/stop/target logic (long-only gap-down
   fade, ATR(14)-scaled stop, unchanged) to regenerate its per-trade
   R-multiples on Discovery data, this time also keeping each trade's
   entry date.
2. Label each trade's date by two independent, pre-existing, unmodified
   classifiers:
   - Range-contraction: prior day range in the bottom 20th percentile
     of its own trailing 20-day distribution ("narrow") vs. not narrow
     -- same threshold/window as hyp-000046/048 (analyze_range_contraction,
     study_intraday_behavior_batch1.py, unchanged).
   - Overnight coil: overnight range in the bottom 20th percentile of
     its own trailing 20-day distribution ("coiled") vs. not coiled --
     same threshold/window as hyp-000056/057 (build_coil_lookup,
     study_intraday_behavior_batch3.py, unchanged).
3. For each classifier, bootstrap-compare the conditioned bucket's mean
   R-multiple against its complement (same 3000-resample technique as
   screen_condition() in study_overlay_screen2.py), minimum 10 trades
   per bucket to report.
4. This is Step 1 only (Discovery data). A credible, economically
   meaningful screen result is NOT itself a promotion -- per precedent
   it would still require its own single pre-registered prospective
   test on the Validation slice before being trusted, per the standing
   promotion bar.

## Pre-commitment

No new thresholds are introduced and none of the three existing signal
definitions (H89's trade design, the range-contraction classifier, the
coil classifier) are altered based on this result. If neither
classifier shows a credible split, this closes the H87/H89 gap-fade
line's remaining avenue -- entry/exit logic already exhausted (2
attempts), this was the last untried conditioning angle.

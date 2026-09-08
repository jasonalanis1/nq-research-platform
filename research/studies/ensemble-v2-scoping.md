# Multi-Factor Combination Model v2 -- Frozen Spec (exp-070)

## Status: FROZEN 2026-09-08. Jason authorized proceeding without further sign-off ("go for it, don't loop me in unless $ or 90%+"). Advisor-reviewed draft, both flagged gaps fixed below before this was frozen.

## Origin

v1 (exp-046, hyp-000016) combined 8 features via L1 logistic regression,
killed cleanly at Step 1 (AUC ~0.49, all coefficients zeroed). Of those
8, only one (event-day type) had any real signal behind it, and it was
included only as a coarse yes/no flag. This v2 swaps that flag for a
genuine magnitude: how large CPI/NFP release-day moves actually are.

## Both Advisor-flagged gaps, fixed before freezing

1. **Non-event-day fill rule (previously "0 or TBD").** Fixed: KEEP the
   existing `event_type` categorical column (cpi/nfp/fomc/normal)
   unchanged, ADD a new continuous `event_day_realized_move_zscore`
   column (0 on non-event days). The model sees both "is this an event
   day" and, conditionally, "how big was the move" -- not one sparse
   dummy standing in for both, which risked reproducing v1's exact
   failure mode.
2. **Disclose the premise is unconfirmed, explicitly, before running.**
   exp-063 (hyp-000036) already found NO credible implied-vs-realized
   gap on these same event days. This feature does not resurrect that
   claim -- it uses realized-move-alone as an ordinary feature (same
   epistemic status as overnight_gap_pts), which has never itself been
   tested. Expectations calibrated accordingly: this is a fair try, not
   an expected win.

## What's new vs. v1

New feature: `event_day_realized_move_zscore` = abs(daily log return) /
trailing 20-day realized-move stdev, populated only on CPI/NFP days (0
elsewhere), built entirely from existing free NQ price history (zero
new cost) -- src/build_multi_factor_features_v2.py.

Everything else identical to v1: same 7 other features, same target
(next-day close-to-close sign), same L1 logistic regression + purged
5-fold CV, same Step 1 gate (AUC 90% CI lower bound > 0.5), same Step
2 costed-rule gate (gated on Step 1), same stability check
(chronological half-split, sign-flip + AUC-floor checks) --
src/study_multi_factor_combination_v2.py, which imports and reuses
every function from v1's script unmodified except the input file and
the continuous-column list.

## No-retuning discipline

One frozen model, tested once on Discovery. If Step 1 fails, this is
REJECTED and closed -- no trying a 3rd feature-set variant, no
switching model type, no re-tuning C after seeing the result (C is
already chosen via CV inside the run, not tuned against the final
number).

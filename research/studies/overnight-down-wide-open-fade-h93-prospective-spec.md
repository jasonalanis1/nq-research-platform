# H93 Prospective Validation — Frozen Spec (exp-122)

Pre-registered prospective test of H93 (exp-121), the only candidate in
this project's history to pass Step 1+2 on Discovery data. Per standing
protocol, one single prospective test on the Validation slice, no
retuning regardless of result.

## Method

Identical signal/entry/stop/target to H93, completely unchanged:
overnight-down move following a wide-regime (top-20th-percentile
trailing-20-day range) prior day -> LONG at 09:30 open, fixed stop
13.125pts, fixed target 19.25pts (both frozen from H93's Discovery-
sample median 15-min MAE/MFE, not re-derived here). Regime classifier
(`prior_day_wide`) and daily bars computed CONTINUOUSLY across
Discovery+Validation for rolling-window warm-up continuity (no cold
restart at the Discovery/Validation boundary) -- only Validation-window
days (2021-10-04 to 2024-01-03) are scored. Never touches Holdout.

## Pre-commitment

No parameter is adjusted based on this result. Pass -> promotable
(pending Jason + Advisor sign-off per standing practice for anything
clearing the bar). Fail -> closes OBS-FINDING-009 to further
monetization attempts (H92 and H93 both attempted, project's
two-attempt limit reached either way).

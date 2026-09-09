# Pre-NFP Overnight Short, ATR-Scaled Exits -- H115 / exp-130 Frozen Spec

## Relationship to H114

H114 tested OBS-FINDING-012 (pre-NFP overnight short) with
excursion-derived fixed stop/target (median overnight MAE/MFE from the
same 74-event Discovery sample). It FAILED (n=74, mean_r=-0.102,
ci_90=(-0.272, 0.071) -- spans zero). Per the project's one-reshaped-
attempt precedent (H81->H82, H87->H89, H92->H93), this is a genuinely
different monetization design -- the project's standard ATR-scaled-
stop convention (1.0x daily ATR(14) stop, 1.35x risk target, unchanged
from H87/H89/H92) -- NOT a retune of H114's excursion values, frozen
before looking at this hypothesis's own result.

## Setup

Event: NFP day (first Friday of month), same as H114. **Entry:** prior
trading day's RTH close (16:00 ET), SHORT. **Stop:** entry + `1.0 *
prior day's ATR(14)` (same definition as H87/H89/H92 -- ATR computed
from RTH daily ranges, unmodified). **Target:** entry - `1.35 * risk`
(TARGET_R_MULTIPLE, unmodified). Exit: walks forward through the
overnight window bar-by-bar; if neither level hit, exits at NFP-day
RTH open (time-based fallback, same as H114). Cost:
ROUND_TRIP_COST_POINTS (unmodified, 0.75).

## Method

Step 1+2, costed. Bootstrap mean-R-multiple CI, N_BOOTSTRAP=3000,
seed=7, 90% CI. Credible = CI entirely above zero AND mean R-multiple
net of cost >= 0.05R.

## Pre-commitment

This is the SECOND AND FINAL monetization attempt for OBS-FINDING-012,
per the project's two-attempt limit. If this fails, the finding stands
as documented measurement (per protocol) but the behavior line is
CLOSED to further monetization attempts on this event definition --
same treatment as the gap-fade line (closed after H81/H82, H87/H89)
and OBS-FINDING-009 (closed after H92/H93).

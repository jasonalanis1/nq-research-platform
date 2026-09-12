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

## BLIND INTEGRITY GATE CHECKPOINT — RUN September 11th, 7:08 pm CT (fresh context, packet research/_blind/midday_lull_afternoon_expansion.md, all figures masked)

Ruling, verbatim: **CONDITIONAL PASS** — conditions: (a) fix the
between_time boundary overlap before running (the 14:00 bar is inclusive
in both the 12:00-14:00 midday window and the 14:00-16:00 afternoon
window, so one bar is counted in both ranges); (b) record and disclose the
mandatory power estimate to Jason before the slot is spent; (c) clarify the
duplicate hyp-000105 ledger entry.

Handling by the cycle (recorded here so the ruling and its resolution sit
together; the numbers below were unmasked only AFTER the ruling):

- (a) The overlap is REAL and is present identically in the Discovery and
  Validation runs (same code). It is one 1-minute bar shared by two
  ~120-bar windows. Changing the window boundary for the Holdout run alone
  would make the confirmatory test DIFFERENT from the test it confirms --
  a parameter change after results. Resolution: the Holdout run stays
  identical to Validation (defect disclosed, not silently fixed); a
  corrected-boundary re-expression is run on the SAME Holdout data
  immediately after, as a disclosed diagnostic, not a second slot. If the
  two disagree on pass/fail, the candidate FAILS. Logged as a LEARN
  failure-mode note ("inclusive pandas between_time boundaries") for every
  future intraday-window spec.
- (b) Power computed from the Validation-slice narrow-midday result
  (n=142, per-day sd of the ratio ~0.42): expected Holdout narrow days
  ~110; probability the 90% CI sits entirely below 1.0 if the Validation
  effect is real: **~99% at n=112, ~99% at n=80.** This review point is
  well sized. Disclosed to Jason with the slot request.
- (c) The second hyp-000105 row (2026-09-10) is a research_ledger
  update_status() correction (FORWARD VALIDATION -> PROMISING, ledger
  hygiene), not a re-test. Explained; no action.

Status: GATED -- frozen Holdout spec ready, blind Gate CONDITIONAL PASS
with conditions resolved as above. **Waiting on Jason to spend Holdout Gen
2 slot 2 of 5.**

## RESULT — run September 11th, 7:29 pm CT (2026-09-12 00:29 UTC), Jason's sign-off "Yes let's run the hold out session"

Holdout Gen 2 slot 2 of 5 CONSUMED. Ledger hyp-000141 (parent hyp-000106), holdout_slot_id holdout_gen2_slot_2.

| stage | narrow-midday n | mean afternoon-range ratio | 90% CI | verdict |
|---|---|---|---|---|
| Discovery (hyp-000105) | -- | 0.713 (per OBS-FINDING-011) | -- | credible |
| Validation (hyp-000106) | 142 | 0.816 | [0.762, 0.878] | PROSPECTIVE_PASS |
| **Holdout Gen 2 (hyp-000141)** | **130** | **0.739** | **[0.686, 0.796]** | **HOLDOUT_PASS** |

Not-narrow days, Holdout: n=420, ratio 1.130 [1.070, 1.194] -- the contrast holds in both directions.

Boundary diagnostic (afternoon window opened at 14:01, same data): n=130, ratio 0.739 [0.685, 0.797], HOLDOUT_PASS. Identical to three decimals; the shared 14:00 bar is immaterial. Condition (a) closed.

Reading: the narrow-midday -> narrow-afternoon RANGE persistence fact has now cleared Discovery, Validation and Holdout with the CI entirely below 1.0 each time and no retuning at any stage. It is a validated CONDITIONING fact (sizing input, get_afternoon_conditioning()), not a directional edge; it does not enter a forward test as a strategy and it is not a live candidate. Next owed: PORTFOLIO's first question -- does it carry incremental information beyond the two other validated range findings (range contraction, overnight coil), or is it the same latent volatility state restated? LEARN: KNOWN TRUE.

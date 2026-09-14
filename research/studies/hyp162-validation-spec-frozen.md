# hyp-000162 (M30) — frozen one-shot Validation spec

Frozen: September 14th, ~3:20 pm CT (3:00 pm scheduled cycle), **before the test was
run**. This document is committed before `src/validate_hyp162.py` is executed; the
result lands in a later commit.

Script: `src/validate_hyp162.py`
**sha256: `7a32377d74cf306f43c950f93a4a5fbaa8c64a0b3a04364961c39a14ea142462`**
If that hash does not match at run time, the run is not this pre-registered test.

Slice: **Validation only, 2021-10-04 → 2024-01-03** (700 sessions on disk). Discovery is
used only as warm-up history for the trailing statistics; it is never scored and never
enters either arm. Holdout is untouched.

## Why this is not "Scan 036 with the loader swapped"

The blind Integrity Gate (`hyp162-blind-gate-2026-09-14.md`) found two defects that change
the test itself, so re-running the Discovery construction out of sample would test a rule
the bot could never actually follow:

1. **Tercile edges.** Scan 036 cut them as full-Discovery percentiles — not knowable at
   10:00 ET on the day. This test uses **trailing 250-session percentiles, shifted one
   session**, built on the concatenated Discovery+Validation frame and only then restricted
   to Validation dates, so the first 250 Validation sessions warm up from the Discovery
   tail. No session is scored on a partial window; none is dropped for it.
2. **The CI of record.** Scan 036 resampled blocks of consecutive *within-arm*
   observations, independently per arm — ten consecutive HIGH sessions can span months, so
   the block never contained calendar clustering. This test uses a **calendar-time block
   bootstrap**: blocks of 10 consecutive *sessions*, arms split *after* resampling.
   N_BOOT = 20,000, seed 20260914.

Multiplicity: **Šidák N = 20**, the project's stage-specific Validation constant
(Discovery 467 / Validation 20 / Holdout 3), frozen as the constant rather than recomputed.

## Two gating predictions — both must pass

**V1.** The Šidák-adjusted interval on the HIGH−LOW midday-ratio spread lies entirely
above zero. Direction pre-registered positive; tested two-sided, the conservative choice.

**V2.** Holding the **previous session's opening range** fixed — the discriminating cell
the Gate demanded — the retained share's **lower 90% bound is ≥ 0.50**. The bar is cleared
by the interval, never by a point estimate; raw and stratified spreads come from the same
resample.

## Failure semantics, pre-declared

| outcome | closure |
|---|---|
| V1 fails | family closes **NULL** |
| V1 passes, V2 fails | family closes as a **DUPLICATE** of the multi-day volatility-regime family — not null, and not a second attempt with a redrawn stratifier |
| both pass | **Validation-passed as a SIZING fact**; owed Portfolio's incremental-information question before any Holdout slot is requested |

This is the Gate's own closure rule, moved out of sample. In every branch the candidate
may **not** attach to B2's live sizing until a **measured** cost figure exists (Gate
condition 7, still open — it needs the execution record, not more research).

## Power, computed before the run

From the Discovery per-arm variance and the Validation **session count** (a count, not an
outcome): pooled SD 0.602, ~233 sessions per arm, SE ≈ 0.079 after a √2 inflation for
serial dependence. At the Šidák z of 2.791:

- power **1.000** at the Discovery effect size (0.49)
- power **0.624** at half of it
- **MDE at 80% power: 0.287** — about 59% of the Discovery effect

Stated plainly: a null here would be informative against effects of ~0.29 and larger, and
would **not** cleanly rule out a genuinely halved effect. That limit is recorded before
the result, not after it.

## Non-gating diagnostics (reported always; cannot flip the verdict)

**D1** the same spread on Scan 036's original full-sample edges, so the cost of moving to
trailing edges is visible rather than assumed.
**D2** the spread inside each prior-day-range tercile, in ratio **and** in points —
Monetization found the ratio effect regime-stable while the points effect flips sign in
the MID stratum; that pattern either reappears out of sample or it does not.
**D3** n per arm, per year, and sessions dropped for a short midday window — a PASS driven
by a coverage artifact should be visible.

## Permanent disclosures (Gate-mandated; they travel with every result from here)

1. **P1 at Discovery was selection-confirmatory.** The state, outcome, window, tercile cut
   and direction were all chosen because a 1,045-cell descriptive sweep showed this family
   strongest on the same Discovery slice. Promotion rests on this out-of-sample test and on
   V2, never on the Discovery P1.
2. **The discriminating separability test was post-hoc at Discovery** — run after the
   mechanical placebo check flagged the candidate, not before. V2 is its pre-registered,
   out-of-sample form.

## Pre-run smoke test

The machinery (not the test) was exercised on **Discovery data only**, at N_BOOT=200, to
prove the code path runs: spread +0.493, retained share 0.888 (lower bound 0.828) —
consistent with the figures the Discovery-stage work already produced, which is the point
of a smoke test. No Validation outcome was touched.

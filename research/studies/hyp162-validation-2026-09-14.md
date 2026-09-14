# One-shot Validation — hyp-000162 (M30: opening-range width → midday range, NQ)

September 14th, 3:00 pm CT scheduled cycle. Ran
`src/validate_hyp162.py`, sha256 `7a32377d74cf306f43c950f93a4a5fbaa8c64a0b3a04364961c39a14ea142462`,
**matching the hash committed before the run** (commit `ee53308`, pre-registration).
Numbers: `research/studies/hyp162-validation-result-2026-09-14.json`.
Slice: Validation only, 2021-10-04 → 2024-01-03. Holdout untouched.

## Verdict: **PASS** — both gating predictions cleared

| | prediction | result |
|---|---|---|
| **V1** | Šidák-adjusted (N=20) spread entirely above zero | **+0.322, Šidák CI (+0.167, +0.486)** — clears |
| **V2** | retained share's **lower** 90% bound ≥ 0.50, holding the previous session's opening range fixed | **99.6%, CI (91.4%, 107.5%), lower bound 91.4%** — clears by a wide margin |

## The headline number, honestly

**The effect is a third smaller out of sample: +0.32 against Discovery's +0.49.**

That is the expected shape, not a surprise, and the spec said so in advance: the Discovery
estimate was **selection-confirmatory** — this family was chosen because a 1,045-cell sweep
showed it strongest, so its Discovery magnitude was the maximum of many draws and had to
shrink. It shrank to 66% and stayed credible after the Validation-stage multiplicity
correction. The pre-registered MDE was 0.287; the observed +0.322 sits above it, but not
by much, so the honest statement is **"credibly positive, materially smaller than
Discovery advertised"**, not "confirmed at the Discovery size".

## The Gate's doubt is answered out of sample

V2 is the whole point of this test. The blind Gate's central objection was that the
procedure could not tell a same-session opening-range effect from a multi-day volatility
regime, and that the test which addressed it had been run *after* the placebo flag rather
than before.

Holding the **previous session's** opening range fixed, on the same resample:
**99.6% of the effect survives, lower bound 91.4%.** At Discovery the same figure was 87%
(lower bound 82%). Out of sample it is *higher*, and this time it was pre-registered as a
gating condition with its bar and its failure semantics written down first.

The candidate is a same-session fact. The placebo red is now fully explained: volatility
persists (true, and the placebo was detecting it), and today's opening range still carries
essentially all of its own information about today's midday.

## Diagnostics (non-gating, reported as pre-registered)

**D1 — the edge change cost almost nothing.** On Scan 036's original full-sample edges the
spread is +0.313 (90% CI +0.219, +0.405) against +0.322 on the trailing real-time edges.
Moving to the edges the bot can actually compute at 10:00 ET did not buy the effect and did
not cost it. The Gate's defect was real; its consequence was small.

**D2 — the Discovery sign-flip did not reappear, and that is a correction.** Monetization
found the ratio effect regime-stable but the *points* effect flipping sign in the MID
prior-day-range stratum (−3.5 pts). Out of sample every stratum is positive in **both**
units:

| prior-day range | ratio spread | points spread |
|---|---:|---:|
| LOW | +0.386 | +23.8 |
| MID | +0.241 | +12.7 |
| HIGH | +0.272 | +15.7 |

The MID-stratum negative was Discovery noise. **That correction is recorded against this
morning's Monetization caveat**, which overstated the case. What survives from that stage
is the weaker and still-true claim: the multiplier applies to a trailing average, so the
ratio is the decision unit.

Also worth stating: the effect is **not** largest in the high-volatility stratum here. The
Director's "it scales with volatility" observation — carried forward from Discovery — does
**not** replicate. Out of sample the largest spread is in the LOW stratum.

**D3 — coverage.** 571 of 700 Validation sessions scored (129 lost to the 250-session
trailing-edge warm-up and the ratio's own warm-up), 177 HIGH / 201 LOW, spread across
2021–2023 with no single year carrying the result. 544 sessions were dropped across the
concatenated frame for a midday window shorter than 60 bars — a holiday/half-day filter
inherited from Scan 036's construction, unchanged here, and disclosed rather than tidied.

## What this candidate is now

A **Validation-passed sizing fact**: the width of the first 30 minutes says something real,
and same-session-specific, about how far price travels between 11:30 and 13:30 — worth
roughly a ±25% adjustment to the expected midday range, known at 10:00 ET.

## What it is still not allowed to do

1. **It may not attach to B2's live sizing.** Gate condition 7's cost clause is open: there
   is no measured slippage figure anywhere in this project because the order path has zero
   fills, ever. That is an execution-record dependency and no amount of research closes it.
2. **It is owed Portfolio's incremental-information question** before any Holdout slot is
   requested — the same question hyp-000105 and hyp-000142 were asked: does it add to the
   conditioning stack, or restate it? The Director's 75–88% and this stage's 99.6% both
   point to "adds", but Portfolio owns that call and the slot is scarce (3 of 5 Gen-2
   slots remain).

Both permanent disclosures travel with every future statement of this result: P1 was
selection-confirmatory, and the discriminating test was post-hoc at Discovery (V2 is its
pre-registered out-of-sample form, and it passed).

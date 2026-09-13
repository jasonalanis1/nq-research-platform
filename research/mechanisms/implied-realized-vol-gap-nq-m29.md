# Mechanism — Implied-minus-realized volatility gap (VXN vs NQ realized range), NQ (M29, observatory channel, state primitive)

Written: 2026-09-13, ~5:05 pm CT (interactive test cycle, UPGRADE QUEUE v3 item U4).
Results seen before writing: NO. No scan exists. No Observatory cut exists yet.
Origin: sourced to restore the shelf after M26 (Entry 30) was drawn this cycle, and
because outside review D named this as "the one state variable you have and haven't
used" — the closest proxy in Tony's on-disk data to dealer hedging behavior.

## 1. The claim (as a STATE PRIMITIVE, not a directional claim)
The gap between what options prices *expect* NQ to move (VXN, an implied-volatility
index, on disk daily) and what NQ has *actually* been moving (trailing realized range,
computed from the 1-minute bars already on disk) is a market state that conditions
subsequent behavior. Specifically: when implied sits well ABOVE realized (options are
"expensive" relative to recent movement), subsequent moves tend to be dampened —
intraday mean reversion is stronger and range expansion is rarer. When implied sits
well BELOW realized (options are "cheap"), the reverse — moves extend and range
expands.

This is filed as a **Layer-0 state variable**, in the same category as prior-day range
contraction, overnight coil, and VXN level. Its FIRST use is a descriptive Observatory
cut (U11 free-look mode), not a directional hypothesis. Directional or magnitude
claims come later, each as its own registered family.

## 2. Who is on the other side
Options market makers (dealers). When they have sold more options than they have
bought — which is what a high implied-vs-realized gap usually reflects — they hedge by
buying the underlying as it falls and selling as it rises, which mechanically dampens
moves ("long gamma" in dealer language). When the gap is negative they are positioned
the other way and their hedging amplifies moves. This is the participant Jason said
Tony "can't see" without paid order-flow data; the implied/realized gap is the price
shadow of their positioning. Named-participant story: strong. Direct observability:
proxy only (no positioning data on disk — that stays under the Data Acquisition
Trigger).

## 3. Why this is not the overfitting trap
- One variable, defined ONE way before any look: gap = VXN_close(t-1) −
  annualized_realized_vol(NQ, trailing N sessions). N frozen at 20 sessions (matches
  the trailing-20d convention used by every other state variable in this project).
  Tercile edges computed once on the Discovery slice, never refit.
- It is NOT the VXN-level variable (hyp-000142/144/151, KNOWN TRUE): that measures
  where implied sits relative to its own trailing average. This measures implied
  relative to *realized*. The two can disagree (VXN can be high and still below
  realized in a crash). Separability from VXN-level is the first thing the Observatory
  cut must report; if the gap tercile is >80% the same days as the VXN-level tercile,
  it is redundant and closes as a duplicate (closure form status "duplicate").
- Not a re-run of anything closed: no prior entry used realized volatility as a
  conditioning variable.

## 4. Testable predictions (for the FIRST registered family, after the free-look)
P1 (state → magnitude, GATING for the first family). HIGH-gap tercile days show
   credibly LOWER next-session RTH range (ratio to trailing-20d average) than LOW-gap
   tercile days. Block CI on the HIGH−LOW ratio difference entirely below zero.
P2 (reported). The effect is not explained by VXN level alone: after residualizing on
   the VXN-level tercile (same residual convention as the hyp-142 Portfolio review),
   ≥50% of the HIGH−LOW spread is retained.
P3 (exploratory, non-gating, descriptive only). Intraday path: on HIGH-gap days, the
   share of the RTH range realized in the first 30 minutes is higher and the
   afternoon extension lower (dampening shows up as "early, then nothing").

## 5. What would falsify this
(a) P1 fails → the gap carries no magnitude information beyond noise; closes the
    family, keeps the variable in the feature library as "tested, null."
(b) P1 passes but P2 fails → it IS the VXN-level fact restated; closes as duplicate.
(c) THIN-SAMPLE: not a concern — VXN and NQ overlap daily across the whole Discovery
    slice (~1,700 sessions, ~560 per tercile).
(d) DATA kill: VXN daily series must align to NQ session dates with no more than 2%
    missing; if worse, disclose and stop.

## 6. Information gain and edge potential
Information gain: HIGH either way. A pass gives the Risk/State Engine (U13) a fourth
range input with a distinct mechanism (dealer positioning vs. participant fatigue);
a null closes the only cheap proxy for dealer flow the project has and strengthens the
case that seeing dealers requires buying data (feeds the Data Acquisition Trigger).
Edge potential: as a state variable it improves sizing, stop distance, and
trade-permission decisions for every future candidate; as a filter it is the natural
condition for the fade-to-VWAP-on-compressed-days family (U5a) — "compressed AND
dealers dampening" is a sharper version of "compressed."

## 7. Resurrection ruling (LEARN + Integrity)
- NOT hyp-000142/144/151 (VXN level vs trailing average) — different denominator
  (realized, not VXN's own history); separability is P2.
- NOT M12 (basket correlation convergence, REFUTED) — different instrument set, no
  cross-asset input.
- NOT the closed VIX-term-structure idea (tabled, needs paid VX data) — this uses
  VXN spot only, already on disk.
RULING: NEW. Attempt 1 of 2 for the family; the state variable itself is a Layer-0
primitive and does not consume a family attempt until a claim is registered.

## 8. Instrument-choice gate
1. NQ only; VXN is NQ's own implied-vol index, no cross-instrument mapping needed.
2. Daily state, known at prior close; next-session horizon; no lookahead.
3. Magnitude (range ratio) first, not direction. NULL = unconditional next-session
   range ratio; TWO NULLS rule not triggered (no directional/cross-index claim).

## 9. Frozen scope
STAGE 0 (free-look, U11, not a scan, no ID): descriptive table — gap tercile ×
{next-session range ratio, first-30-min share, afternoon share, overlap with VXN-level
tercile}. Reported, not tested.
STAGE 1 (ONE scan, only if the free-look shows a footprint): four cells —
(1) HIGH−LOW next-session range ratio, block CI  <== GATING P1; (2) same, residualized
on VXN-level tercile (P2); (3) unconditional range ratio reference; (4) alignment /
missing-data disclosure. Block=10 (daily series), N_BOOT=3000, SEED=20260913, 90% CI.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
Not drawn this cycle. DRAWABLE for the free-look stage as soon as U11 exists; the
Stage-1 scan is registered only after the free-look reports a footprint.

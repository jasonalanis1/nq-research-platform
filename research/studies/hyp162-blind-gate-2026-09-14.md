# Blind Integrity Gate — hyp-000162 (M30: opening-range width → midday range, NQ)

September 14th, 1:00 pm CT scheduled cycle. Packet:
`research/_blind/opening_range_width_midday_m30_gate_packet.md` (built by
`src/integrity_blind_packet.py`, every result figure masked, plus the cycle's
own procedural disclosures on the U6 placebo red and the separability stage).
Ruled by a subagent with no prior context, per AMENDMENT v2.5 Rule 3. The
ruling below is recorded **verbatim, before any figure was unmasked.**

---

## Ruling (verbatim)

**Finding:** The frozen procedure cannot separate a same-session opening-range
effect from a multi-day volatility-regime effect, and its own gating cell
carries almost no evidential weight.

- **P3 residualizes the wrong variable.** It stratifies on prior-day
  `range_vs_atr`; the alternative hypothesis raised by the placebo is prior-day
  `opening_range_vs_atr`. No frozen cell addresses it. The doc's own
  falsification map (5b) therefore has a hole the authors correctly flag.
- **The shifted-signal red is the only check that bears on the question, and
  the packet's mitigation is backwards.** Low overlap between placebo and real
  selection makes a reproduced effect *more* damning, not less — if a largely
  different set of sessions reproduces 74% of the effect, persistence is the
  parsimonious explanation. "Roughly 1.5 points from not being raised at all"
  is a rhetorical discount of a blocking finding, not a procedural argument. It
  should be weighed as informative, not near-exonerating.
- **P1 is selection-confirmed, not tested.** The state, the outcome, the
  window, the tercile cut and the direction were all chosen because the
  2026-09-13 Idea Factory sweep showed this family strongest on what is
  presumably the same Discovery slice. "Descriptive, not evidence" is
  bookkeeping, not statistical independence. Cell 1 was near-certain to pass
  before it ran; the only informative cells are 4 and the placebo/separability
  work.
- **Multiplicity is not accounted.** The sweep's look-cell count is said to be
  "recorded in" another file and is *not* disclosed here, which the brief
  requires. Šidák N=467 is a project-wide constant applied downstream, not a
  correction for max-selection over the sweep that produced this entry.
- **Power was not sized before freezing** — status is already PROMISING with
  "Statistical (+POWER) owed." Worse, the two decision bars that actually
  matter (P3's 50%, separability's 50%) are compared against **bare point
  estimates**; a ratio of two noisy means crossing a 50% line is a coin-flip
  gate.
- **CI of record under-corrects for exactly the dependence at issue.**
  `_block_boot_means` resamples blocks of 10 *consecutive within-arm
  observations*, and HIGH and LOW arms are resampled independently. Ten
  consecutive HIGH sessions can span months of calendar time, so the block does
  not capture calendar-adjacent volatility clustering — the very mechanism the
  placebo suggests. Independent resampling of two interleaved arms also
  discards their contemporaneous correlation.
- **Possible outcome-in-denominator leakage in P2.** Cells 2/3 divide midday
  MFE/MAE by `atr14` reindexed to the same session, with no shift visible. If
  `atr14` includes the current session's true range, the excursion cells are
  normalized by a quantity containing the outcome.
- **Tercile edges are full-Discovery percentiles**, so group membership depends
  on the whole-sample distribution and is not knowable at 10:00 ET. Tolerable
  for a descriptive Discovery scan, not for the claimed real-time sizing input.
- **The separability stage is post-hoc**, run after the red. It is the right
  test and nothing was retuned, but it was added after a blocking finding and
  its bar has no uncertainty attached, so it cannot be allowed to rescue the
  claim in its current form.
- Clean: direction pre-registered one-sided and tested with a conservative
  two-sided CI; 90-minute state→outcome separation; trailing midday normaliser
  shifted; resurrection ruling sound; no cost model needed yet since no trade is
  claimed; the red was disclosed rather than buried.

**Confidence:** High on the procedural gaps. Moderate on the `atr14` leakage —
it depends on `market_state_primitives`, which I did not read.

**Novelty:** Low-to-moderate as procedure. The claim's novelty rests entirely on
specificity to the same session, which is precisely what the placebo puts in
doubt.

**Research Value:** Moderate, conditional. If the effect survives holding t−1
opening range fixed with an interval-based bar, it is a genuine intraday state
update at 10:00 ET with a direct sizing path. If not, the correct product is a
cheaper statement — "volatility regime persists" — and the family closes as a
duplicate of a regime fact.

**Recommendation: CONDITIONAL.** Not a VETO — the red was disclosed, no retuning
occurred, the discriminating test is cheap and well defined, and the family is
on attempt 1 of 2. Not a PASS — the claim's core distinction is currently
untested. Conditions 1–7 as listed below. *If condition 1 fails its pre-declared
bar, the correct closure status is "duplicate" against the multi-day
volatility-regime family — not "null," and not a second attempt with a redrawn
stratifier.*

---

## Conditions — status after unmasking

Run this cycle: `src/gate_conditions_hyp162.py` →
`research/studies/hyp162-gate-conditions-2026-09-14.json`.

| # | Condition | Status |
|---|---|---|
| 1 | Discriminating cell: stratify on the **prior session's opening range**, not prior-day range | **MET, with a permanent caveat** |
| 2 | Interval on the retention ratio; bar met only if the lower 90% bound clears it | **MET** |
| 3 | Calendar-time block bootstrap (blocks of consecutive sessions, split after resampling) | **MET** |
| 4 | Verify `atr14` excludes the current session | **MET — no leakage** |
| 5 | Disclose the sweep's look-cell count; apply a max-selection correction | **MET** |
| 6 | MDE/power for the retention bar before the re-run | **MET** |
| 7 | Real-time-estimable tercile edges **and** a measured cost figure | **HALF MET — cost clause OPEN** |

**1 and 2 — the discriminating cell, with an interval.** Holding the previous
session's opening range fixed, on the same resample, **87.4% of the effect is
retained, 90% CI (82.0%, 92.6%)**. The lower bound is 82%, against a 50% bar —
the bar is cleared by the *interval*, not by a point estimate. This confirms the
Director's 87.2% point estimate by a different method. The Gate's caveat stands
and is recorded permanently: **this test was run after the placebo red, not
before.** The Gate's own closure rule was pre-declared and the test did not fail
it.

**3 — calendar-time bootstrap.** Resampling blocks of 10 consecutive *sessions*
and splitting into HIGH/LOW afterwards: raw spread **+0.5196, 90% CI (+0.4489,
+0.5923)** — against the scan's within-arm construction of +0.5193 (+0.4475,
+0.5975). Materially identical. The interval was **not** an artifact of the
block construction, which was a live possibility worth checking.

**4 — the leakage the Gate flagged does not exist.**
`market_state_primitives.py:103`: `daily["atr14"] = daily["range"].rolling(14).mean().shift(1)`
— strictly trailing, current session excluded. P2's excursion cells are not
normalised by their own outcome. The Gate was right to flag it unread and right
about its own confidence level.

**5 — multiplicity.** The sourcing sweep ranked **1,045 descriptive cells** (315
more dropped as circular before ranking). Šidák-adjusted at K=1045 the raw
spread is **(+0.366, +0.689)** — lower bound still above zero. At the project's
standing Discovery N=467 it is (+0.370, +0.689). Survives either. **Recorded in
the ledger as the Gate demanded: P1 is selection-confirmatory, and promotion
rests on the discriminating cell, not on P1.**

**6 — power for the bar.** SE of the retained share is 0.032; the design
distinguishes a true retained share above **0.58** from the 50% bar at 80% power,
one-sided 5%. The observed 87% is far outside that. The bar was not a coin flip.

**7 — half met.** Re-cutting the terciles as **trailing 250-session percentiles,
shifted one session** (so membership is knowable at 10:00 ET on the day): 1,416
sessions, raw spread **+0.487 (+0.411, +0.566)**, retention **88.4% (82.7%,
93.7%)**. The effect is not an artifact of full-sample edges and the real-time
version is the one that should be specified. **The cost clause is OPEN and
cannot be closed by research:** there is no measured slippage figure anywhere in
this project because the order path has zero fills ever. That is the same
blocker the data refresh addresses.

## Disposition

**CONDITIONAL SATISFIED except the measured-cost clause.** Six of seven
conditions are met with numbers; the seventh is half met, and its open half is
an execution-record dependency, not a research one.

hyp-000162 may proceed to a **frozen one-shot Validation spec** — written against
the **trailing-edge** definition, not the full-Discovery edges — and the spec must
carry the Gate's two permanent disclosures: that P1 is selection-confirmatory,
and that the discriminating test was post-hoc. It may **not** attach to B2's live
sizing until a measured cost figure exists.

The Gate's ruling was sharper than the stages that preceded it, and two of its
findings (the bootstrap construction, the full-sample tercile edges) were real
defects that no prior stage had raised.

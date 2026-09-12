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
0.713 vs 1.160, tighter and larger-sample than either of the other two
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
    (midday->afternoon, 0.713 vs 1.160 -- widest spread) is stronger than
    overnight-session -> same-day RTH, a session-character change (0.894)
    which is comparable to day -> next-day, a full ~24h gap and an
    overnight in between (0.944 vs 1.081, hyp-000048). If a FOURTH
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
afternoon finding. Narrow-opening days (n=525): mean midday ratio=0.800,
ci_90 [0.768,0.833], credibly below 1.0. Not-narrow-opening days
(n=1639): mean=1.109, ci_90 [1.084,1.135], credibly ABOVE 1.0 -- the
same symmetric persistence pattern as midday->afternoon, one window
earlier. This is general same-day volatility persistence, not something
specific to the midday/afternoon pairing.

**P3 -- TESTED 2026-09-10** (n=1731 days with both classifications
available). **PARTIAL OVERLAP -- meaningfully more than chance, but NOT
the same set of days.** Of 421 narrow-midday days, 161 (38.2%) were also
coiled-overnight days; of 426 coiled-overnight days, 161 (37.8%) were
also narrow-midday days. Expected overlap under independence: 103.6 days
-- actual overlap (161) is ~1.55x that, and the relative-risk read is
similar: a narrow-midday day is about 1.9x as likely to also be a
coiled-overnight day as a non-narrow-midday day is (38.2% vs 20.2%
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
found: split-sample stability clean (first half mean=0.710, second half
0.764, same direction, both credible); no volatility-regime
concentration (low-ATR-vol 0.722 vs high-ATR-vol 0.752, both credible,
similar magnitude); threshold-selection robustness clean (pctl 15 and
25 both close to the frozen pctl-20 result); and it is the only one of
the five Validation legs checked across all three mechanism documents
to survive the project's own multiplicity-corrected 90% bound (adjusted
0.718-0.914). P2 above adds a second, independent, cleanly-confirmed
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

## Portfolio review (2026-09-12, closes the Holdout-passed FROZEN queue item)
Separability check vs. the overnight-coil finding (`overnight_range_vs_atr`):
82.5% of the raw narrow-vs-not spread retained after controlling for
overnight-range tercile; credible within every tercile individually; corr
only -0.19. Verdict: SEPARABLE, not the same latent state restated.
Disposition: KNOWN TRUE, incremental -- stays in
src/volatility_conditioning.py as its own conditioning input alongside the
overnight-coil fact, neither subsuming the other. Full record:
research/studies/portfolio-hyp105-separability-2026-09-12.md.

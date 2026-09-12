# Draft: Event-Conditioned Reference-Level Fade (exp-110/hyp-000081 re-cut)

**Date**: 2026-09-11
**Status**: DRAFT — for LEARN resurrection check + Mechanism + Director review before
formal Idea Inventory entry. Not pre-vetted. Do NOT pull event-calendar data until
this clears Mechanism/Director.
**Origin**: narrowed from a wider "event-conditioned intraday reversal" proposal
(Jason, 2026-09-11) after resurrection check found the wide version re-mines
already-closed ground. Wide version parked in docs/BACKLOG.md as
considered-and-declined. This is the one cell from that proposal not already
covered.

---

## The one open question

exp-110/hyp-000081 ("Opening-Hour Reference-Level Fade") tested fading
09:30-10:30 touches of 5 reference levels (prior-day high/low, overnight
high/low, VWAP) and was REJECTED as a trade (short leg ci_90=(-0.122,-0.009)
economically thin, long leg not credible, combined ci_90=(-0.091,0.004)).
But the Observatory scan that produced it found the underlying conditional-
return behavior real and credible on its own baseline-relative measure — the
trade design just didn't monetize it.

Question: does the SAME behavior, at the SAME reference levels, sharpen (or
appear at all) when the touch also falls inside a narrow window around a
scheduled catalyst (econ release / FOMC / opex), versus when it doesn't? If
the effect is genuinely event-driven, it should show up more cleanly in the
event-proximate subset than in exp-110's undifferentiated opening-hour
sample. If it's flat across both, the event-timing axis adds nothing beyond
what exp-110 already measured and rejected.

This is a re-cut of an existing closed hypothesis, conditioned on a variable
(event proximity) that has not been combined with it before — not a fresh
idea, and framed that way throughout.

## Resurrection check (LEARN)

- **Level-touch-and-reversal mechanism**: heavily mined. Level Sweep Reversal
  family (6 variants, closed), hyp-000013 vwap_mean_reversion (REJECTED,
  -0.628R), hyp-000084 vwap_narrow_open_fade (REJECTED), exp-110/hyp-000081
  (REJECTED as a trade, real underlying effect per Observatory). This draft
  does not reopen any of those — it reuses exp-110's own already-real
  Observatory-measured effect and asks one new question about it.
- **Event-timing-as-driver**: pre-FOMC drift (hyp-000111, thin/non-credible),
  pre-NFP drift (hyp-000112, credible but wrong-direction, 2 failed
  monetization attempts) both tested return-drift around events directly —
  neither combined event-timing with a reference-level touch. That specific
  combination is unexplored.
- **Ruling**: NOT cosmetic. Conditions an existing, real, already-measured
  effect (exp-110/Observatory) on a variable (event proximity) never applied
  to it before, and pre-registers the comparison against exp-110's own
  numbers as the falsification test — not a new shot in the dark.

## Proposed design (for Mechanism review — not yet frozen)

- **State variable**: touch of one of exp-110's 5 reference levels
  (prior-day high/low, overnight high/low, VWAP) during the 09:30-10:30
  window, split into two buckets: (a) touch falls within N minutes of a
  scheduled catalyst (econ release, FOMC, opex) — TBD N, proposed 30-60 min,
  to be fixed before any data is touched; (b) touch does not.
- **Mechanism claim**: exp-110's fade behavior is driven by informed order
  flow positioning ahead of/around scheduled information events (stops,
  resting orders, algos), which should be concentrated in the event-proximate
  bucket and thin or absent in the non-event bucket. Counterparty: whoever
  reads the touch as a stable level in the non-event bucket and gets faded
  only when real informed flow is present.
- **Pre-registered predictions** (write before touching event-calendar data):
  (1) PRIMARY — event-proximate bucket shows a credibly LARGER fade effect
  than exp-110's combined ci_90=(-0.091,0.004); (2) FALSIFYING — non-event
  bucket effect is flat/near-zero, i.e. exp-110's modest combined result was
  entirely carried by the event-proximate subset all along; (3) if both
  buckets look statistically indistinguishable from exp-110's undifferentiated
  result, event-timing adds nothing and this closes the line for good — no
  retuning the window N after seeing results.
- **Multiplicity cost**: 2 cells (event bucket, non-event bucket), reusing
  exp-110's existing entry/stop/target design unchanged — this is a
  conditioning re-cut, not a new trade-mechanics search. Needs a
  SCAN_REGISTRY entry before quoting any CI as final.

## Blocker (explicitly held)

No event-time data layer exists yet (scheduled econ release / FOMC / opex
calendar, timestamped, joinable to 1-minute bars). Per Jason's instruction,
**do not acquire this data** until this writeup has passed Mechanism and
Director review. Estimated cost was flagged in the original wide proposal as
likely under $5 — to be reconfirmed, not assumed, if/when this clears.

## Next step

Route to Mechanism for a pass on the pre-registered predictions above, then
Director for disposition (Idea Inventory entry vs. further narrowing vs.
decline). Only after Director sign-off does event-calendar data acquisition
get scoped.

---

## Staff meeting — Mechanism + Director review (2026-09-11)

**MECHANISM**: predictions are non-restating (fixed against exp-110's own
already-published numbers, not fit to anything seen after this draft was
written) and the design reuses exp-110's entry/stop/target unchanged, so
this tests the conditioning variable in isolation, not a re-tuned trade.
One gap: the event window N (proposed 30-60 min) must be fixed as a single
number before any data is touched, not swept -- currently a range, which
is a knob. Requires that closed out before this can be scanned.
**MECHANISM DISPOSITION**: CLEARS, conditional on freezing N at a single
value at draw time (recommend 30 min, the tighter of the two, since a
wider window dilutes the event-proximate bucket toward the null result
this is trying to distinguish from).

**DIRECTOR**: passes the standing test -- the question (is exp-110's real,
already-measured effect concentrated near scheduled events) was motivated
by exp-110's own prior result, not fit to any new data, and a null teaches
something concrete (that event-timing isn't the missing conditioning
variable, closing that angle on the reference-level-fade line for good).
2-cell multiplicity footprint, cheapest class on the shelf.

**BUT — not minted as a numbered Idea Inventory entry.** Every live shelf
entry (4, 5, 6) is drawable today with data already on disk. This draft
cannot be drawn or scanned without the event-calendar data layer, which
Jason has explicitly held pending this review (2026-09-11). Entering it
onto the numbered shelf now would misrepresent shelf readiness -- it would
read as "not yet drawn" alongside entries that are actually ready, when
this one has a real, unresolved acquisition gate in front of it.

**DISPOSITION**: design approved in principle (clears Mechanism + Director,
N-freeze condition noted above). Held as the queue-item-0a draft, not
promoted to a numbered entry, until Jason authorizes the event-calendar
data spend. At that point: freeze N=30min, add the SCAN_REGISTRY entry,
mint as the next Idea Inventory entry, and draw.

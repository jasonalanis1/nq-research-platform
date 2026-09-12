# Staff meeting — how much a cycle should do, vs. the 105-minute budget

Called: September 12th, ~4:10 pm CT, by Jason directly (asked "why didn't
this go through the 90-min threshold," then "staff meeting"). Not one of
the five automatic triggers — Jason-initiated, which is always sufficient.

## Question
The 3:00 pm cycle finished in ~7 minutes against a 105-minute budget. Is
"stop once the specifically owed item is done" the right rule, or should a
cycle keep working further down the queue until the budget is actually
used up?

## Positions

**OPERATIONS MANAGER**: The budget was written as a ceiling with one job —
stop a cycle that's still mid-task before it corrupts state, and let the
next cycle resume cleanly. It was never specified as a floor. Nothing in
`cycle_budget.py`'s own docstring or the September 11th direction that
created it ("use as much of the 2-hour cadence as is safe") requires
filling the clock; "as is safe" bounds it from above, not below. Finishing
early when the owed item is done is not a defect by the rule as written.

**RESEARCH DIRECTOR**: Disagrees on the practical point, not the letter of
the rule. The rule is silent on how much gets QUEUED per cycle, and that's
the actual lever. Right now the standing state hands each cycle exactly
one Observatory sub-step ("run this one characterization") rather than
"work item 4 until the budget or the item is exhausted." That's a scoping
choice made when writing the STANDING STATE each time, not a property of
the budget system. Two hours between cycles is a lot of idle time if each
one only spends 7 minutes of it — the queue should be sized to the budget,
not to what feels like one clean deliverable.

**STATISTICAL**: No objection on the substance, but flags a specific risk:
if "keep working until budget" becomes the rule, it must not become
license to run a second scan, add cells, or touch anything past the one
pre-registered stage a candidate is owed, just because time remains.
Multiple-testing exposure comes from EXTRA TESTS, not extra hours. More
budget usage should mean deeper or more numerous SOURCING and
characterization work (Observatory sub-steps, more literature/practitioner
entries drafted), never squeezing more looks out of the same data.

**INTEGRITY GATE**: Agrees with Statistical's caveat and adds one more:
a cycle that pads itself with marginal work to "use the time" is the
busy-work failure mode with a different trigger (calendar instead of
idleness). The guard already on file ("would we have proposed this before
seeing any data") applies exactly the same whether the cycle is filling 7
minutes or 90.

**LEARN**: Notes the actual bottleneck honestly: Observatory item 4 has
real remaining sub-steps (overnight session, other bar resolutions,
shock-conditioned view, the fixed state classifier) that were queued as
"next cycle" rather than "this cycle, time permitting." That's the
concrete fix available right now without inventing new work.

## Disposition

**The budget is a ceiling, not a target — that does not change.** What
changes: **a cycle scopes its STANDING STATE ask as "work through as much
of the current queue item as the budget allows," not "do this one
sub-step."** When a cycle finishes a sub-step with budget still open and
the same queued item has more honest, pre-specified sub-steps left (not
invented ones), it continues to the next sub-step rather than stopping and
handing the rest to two hours from now. It still stops the moment the item
is genuinely exhausted, sourcing is owed instead, or nothing further can
be done without new data or Jason's input — an early finish for THAT
reason stays correct and is not something to pad.

This is a scoping instruction, not a new pipeline rule, and it doesn't
touch anything the change freeze protects (no change to the promotion bar,
the shelf rule, the templates, or agent order). Implemented immediately by
updating `research/CYCLE_PROMPT.md` and the standing cycle message.

## What this would have looked like today
The 3:00 pm cycle, under the new instruction, would have continued past
the 15-min RTH lead-lag check into the next Observatory sub-step (overnight
session or another bar resolution) rather than stopping at ~7 minutes,
using more of the 105-minute window on real characterization work.

# Mechanism — Stack A: opening-range break inside a high-expected-range day (NQ)

Written: September 13th, ~9:40 pm CT  ·  Pre-registered / POST-HOC: **PRE-REGISTERED**
Results seen before writing: **no** — this document, the frozen spec and its hash are
written before the runner is allowed to execute.

Format: **CONDITIONAL STACK** (the first one; adopted at the September 13th ~9:00 pm CT
staff meeting, disposition MODIFY). Two layers, paired test, one stack in flight.
Look-cells examined before writing this spec: **0** — the Idea Factory's interaction
mode (U28) does not exist yet, so nothing was mined to produce this. The question comes
from the bot roadmap: it is the BASE vs BASE+B2 comparison the paper run requires.

## 1. The claim

An ordinary opening-range breakout is not one behaviour. On a session the market already
expects to be wide, a break of the first thirty minutes' range is the start of a day that
has room to travel; on a session expected to be narrow, the same break is the edge of the
day's range and reverts. If that is true, the *expected range* of the session — known at
the prior close, before any of it happens — carries information about what the break means,
and the bot's Risk/State Engine earns its place in front of the entry. If it is false, the
engine is a sizing layer and nothing more, and we will have learned that cheaply.

## 2. Who is on the other side

Two groups, one per side of the interaction. On expected-wide days: liquidity providers
who must widen quotes and step back as realised volatility arrives, and volatility-targeting
funds that mechanically reduce exposure into rising volatility — both of whom supply, rather
than absorb, movement after a break. On expected-narrow days: the same market makers, now
able to hold inventory through a probe because the day's realised range has been small,
absorbing the break and fading it back inside the range.

## 3. Testable predictions

P1. The realised R of the frozen B3 break differs between the top-tercile expected-range
    third of sessions and the rest — a difference of two disjoint samples of the same trigger.
P2. The difference has the sign the mechanism states (wide > narrow), not merely a
    magnitude. A significant difference with the opposite sign refutes the mechanism even
    if it "works".

## 4a. Mechanism per layer — CONDITIONAL STACKS ONLY
- context: **expected-range multiplier, combined (prior close)** — volatility persists
  session to session; a day following the conditions that historically precede a wide
  range is more likely to be wide. This is the project's own validated material
  (hyp-048 prior-day range, hyp-142/151 VXN vs trailing, combined as a residual).
- trigger: **B3 opening-range break (10:00–11:30 ET)** — participants who key on the first
  thirty minutes' high and low are a real, documented population; a close beyond that range
  is the public event they act on.

## 4b. Interaction claim — CONDITIONAL STACKS ONLY
The context layer is not a filter that removes losing trades; it changes what the trigger
*means*. The break is a continuation signal when the session has room left to travel and a
range-edge signal when it does not, so the same event should produce different forward
outcomes in the two regimes. Falsifier for the interaction specifically: the difference
between the in-context and out-of-context cells is not credibly different from zero — i.e.
the context layer carries no information the flat trigger does not already have.

## 4. What would falsify this

A Šidák-adjusted 90% interval on the in-minus-out difference that contains zero (the
mechanism adds nothing), or a credible difference with the wrong sign (the mechanism is
backwards). Either outcome closes the stack and is reported as the difference, never as
the placeholder entry's own P&L — the B3 entry is not a strategy and its returns are not
evidence of anything.

## 9a. Sample floor and minimum detectable effect — SET BEFORE ANY SCAN
Floor (occurrences on Discovery): **100 per cell** (project default; not lowered).
Minimum detectable effect at that floor: with the R distribution of a 1:1 stop/target
break entry (standard deviation ≈ 1.0R), two independent cells of n=100 give a standard
error on the difference of ≈ 0.14R, so the smallest difference this design can resolve at
90% confidence *before* the multiplicity correction is ≈ 0.23R, and materially more after
it. The trigger fires on roughly three sessions in four, so both cells are expected to
clear the floor comfortably on the Discovery slice — if either does not, the stack closes
UNDERPOWERED, consumes one of its two attempts, and the definition is not loosened.

## 5. Prediction status
P1 — **refuted**. The difference between the in-context and out-of-context cells is
+0.0247R with a bootstrap 90% CI of (−0.0496, +0.0976). It crosses zero before any
multiplicity correction; the Šidák-adjusted interval at the project's Discovery trial
count (N=460) is (−0.1401, +0.1896).
P2 — **not reached**. The sign is the one the mechanism predicted (wide-expected days
above narrow-expected days), but a sign is not a result when the magnitude is not credible.

## 6. Verdict
The mechanism is **not supported**. The context layer does not change what the opening-range
break means, at the resolution this test could see — and the test could see a good deal: with
n=566 and n=977 the adjusted interval excludes any difference larger than about +0.19R, and
the mechanism as written implied something on the order of +0.23R. This is a powered null,
not a thin one.

What it means for the bot: the Risk/State Engine (B2) remains a **sizing and permission**
layer, which is what its own validated facts support. It is not an entry filter, and nothing
in the paper run should treat it as one. The BASE vs BASE+B2 paper comparison stays on the
roadmap, because it measures something different — whether sizing and permission improve the
*distribution* of outcomes — but it starts with no expectation that B2 changes the entry's
edge, because this test says it does not.

## 12. Closure form (U8-1.0)

Closure status: **clean null** (powered; NOT underpowered — both cells cleared the floor
of 100 by a wide margin).
Primary outcome (as registered) and result: difference IN_CONTEXT − OUT_CONTEXT in realised
R of the frozen B3 break = +0.0247R, CI 90% (−0.0496, +0.0976), Šidák-adjusted at N=460
(−0.1401, +0.1896). Reference cell (unconditional, NOT evidence of anything): n=1543,
mean −0.0266R.
Sample adequacy: adequate — 566 in-context and 977 out-of-context occurrences against a
pre-registered floor of 100 per cell.
Mechanism verdict: falsified (the interaction claim specifically; the individual layers are
untouched by this result).
Robustness / cost / concentration flags: none run — a null does not earn further checks.
Cost model: per-trade cost cancels in a difference between two cells of the same entry.
Data-quality checks passed: Discovery slice only (2015-01-01..2021-10-03), 1,543 occurrences
over 2,101 sessions, no duplicate date+entry rows, entry strictly after the trigger bar by
construction, holdout boundary applied by the loader.
What was learned (one searchable sentence): *the expected-range regime known at the prior
close does not change the forward outcome of an opening-range breakout on NQ.*
What must NOT be retested: expected-range tercile crossed with the opening-range break,
in any variant of tercile edges, breakout windows or targets. That is the same question.
Permitted future retest condition (one): only if a DIFFERENT context variable — not a
volatility-expectation state — is proposed with its own mechanism, and only as a new stack.
Related facts / strategies: hyp-048, hyp-142/151 (the context layer's inputs, unaffected);
B2 Risk/State Engine; B3 placeholder entry.
Capacity action: **reduce** — volatility-expectation states are a sizing input, and the
family should not be spent again on entry-meaning questions.

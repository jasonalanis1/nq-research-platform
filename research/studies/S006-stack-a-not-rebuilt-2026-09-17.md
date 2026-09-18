# S006 — Stack A (B2 context × B3 breakout): closed to LEARN without a screen

9:00 pm scheduled cycle, September 17th 2026 (session file `research/sessions/2026-09-18-0200.md`).
No spec was written, no freeze was spent, no screen was run. This document records **why
that is the correct outcome**, on the record that already exists.

## What S006 asked

`research/ledger/strategies.jsonl` (S006, SOURCE, 2026-09-15): *"does the B3 opening-range
breakout make money when the Risk/State Engine's expected-range context is HIGH?"* — the
B2 × B3 conditional stack, lineage hyp-000161 / Scan 035.

## That question is already answered, and it was answered with power

`research/mechanisms/stack-a-b2-context-x-b3-breakout.md` is a **pre-registered** mechanism
document with a Section 12 closure form (U8-1.0):

- Primary outcome: IN_CONTEXT − OUT_CONTEXT realised R of the frozen B3 break =
  **+0.0247R, 90% CI (−0.0496, +0.0976)**; Šidák-adjusted at N=460 (−0.1401, +0.1896).
  The interval contains zero *before* any correction.
- Cells: n=566 in-context, n=977 out-of-context, against a pre-registered floor of 100.
  Closure status: **clean null, powered — not underpowered**. The design could exclude any
  difference larger than about +0.19R; the mechanism as written implied ≈ +0.23R.
- Mechanism verdict: **falsified** (the interaction claim specifically). P1 refuted, P2 not
  reached.
- The closure form's own binding line — *"What must NOT be retested: expected-range tercile
  crossed with the opening-range break, in any variant of tercile edges, breakout windows or
  targets. That is the same question."* Specifying S006 as written **is** that variant.
- Permitted future retest condition (one, and it is not met): a **different** context
  variable, not a volatility-expectation state, with its own mechanism, as a new stack.

## The trigger it would be built on loses money on its own

`research/integrity/mechanical-stack-a-2026-09-14.json`, n=1543 unconditional occurrences:
`raw_mean = −0.026599` — the flat B3 break is **negative before costs**. A HIGH-context
strategy can only be positive if the interaction supplies the difference, and the interval
above says the interaction is not there. Under the Amendment 2 cost model the 1.300 pt MNQ
round trip is then subtracted from an already-negative mean: there is no cost combination in
which this screens positive, which is why spending a screen on it would be spending it to
confirm arithmetic.

## And its mechanical integrity profile is the S004 failure twice over

Same file: **3 GREEN, 2 RED, 2 not run**.
- `5. subperiod_stability` — **RED**: first half mean −0.0603, CI (−0.1105, −0.0105),
  credible; second half +0.0070, CI (−0.0430, +0.0570), not credible. Only one half is
  credible **and the halves disagree in sign**.
- `6. concentration` — **RED**: the top 5% of observations (77 of 1543) carry **188%** of the
  effect (red above 50%) — i.e. the other 95% is net adverse.
- `2. overnight_intraday_split` and `7. placebo` **did not run**. A NOT APPLICABLE has not
  passed; the Gate is told so here.

These are precisely the two defects the S004 scrutiny caught in a different guise: an effect
that lives in one era and in a handful of observations.

## Directive s.9 applied honestly

s.9 lists "Stack A" among the top revamp entries — near-misses with a real mechanism that
earn a full strategy and a screen. That listing was made against Stack A's *pre-closure*
standing. The closure of September 14th supersedes it on the facts: the mechanism was not a
near-miss, it was **falsified with power**, and s.9's own bottom rule — *clean nulls stay
dead* — is the line that now applies. The revamp list exists for near-misses with a real
mechanism, not for reanimating a powered null. Recording that costs nothing and is the
valuable outcome.

## Verdict

**S006 → LEARN.** No SPECIFY, no FREEZE, no SCREEN. No salvage is owed: a null is not a loss,
and Section 7 salvage attaches to a strategy that lost money on a screen, not to a closed
mechanism. Capacity action carried forward from the closure form: **reduce** — volatility
expectation states are a sizing and permission input (B2's validated role), and the family is
not to be spent again on entry-meaning questions.

**What was learned (one searchable sentence):** *the last unblocked queue candidate was closed
without spending a screen, because its own pre-registered closure form had already answered its
question with power and had named the retest it forbids.*

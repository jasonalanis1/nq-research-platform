# Staff meeting — Conditional Stack hypothesis format (September 13th, ~9:00 pm CT)

Convened by the Research Director at Jason's request. Present: Jason (direction), Director,
Mechanism, Statistical, Integrity Gate (fresh subagent, adversarial, read the proposal only),
Operations, LEARN. Input: research/infrastructure/conditional-stack-implementation-proposal-2026-09-13.md
and Jason's original methodology proposal. Standing rule: a proposal is judged the way a hypothesis
is — would we have adopted it before seeing data, and will a null teach us something.

## Positions

**Mechanism.** Supports the format on one condition already in the proposal: one mechanism per
layer and an explicit interaction claim, with "it filters out losers" rejected as fitting. Adds: the
interaction claim must make a prediction that is not a restatement (the proposal's own example —
continuation strength rising with pullback depth — is the right shape). Wants the ICC pullback
(Stack B) kept as the second candidate only; on novelty it is weak, on the format it is a clean test.

**Statistical.** Supports with the occurrence floor owned per candidate and a project-wide default
of 100 on Discovery, plus a written minimum detectable effect BEFORE the scan. Insists the paired
design (trigger alone vs trigger in context) is the only honest first test of the format — a single
stack passing tells you nothing about whether the context layer did the work. Notes the paired test
is two registered trials, not one, and the proposal's "one stack, one trial" language must be
reconciled: a stack is one trial; a paired family is two.

**LEARN.** Confirms nothing on the shelf or in the closed families is a stack; the closest prior
work is the conditional-retest protocol (one condition on a dead pattern) and the B2/B3 pairing in
the bot roadmap. Flags that the ICC trigger family (trend pullback continuation) has cousins in the
closed backlog (momentum continuation, exp-series) — Stack B's resurrection ruling must address
them by name.

**Integrity Gate (verbatim summary of the written review).**
1. Spec hash — CONCERN: detects layer shopping after the fact; preventive form is registration
   BEFORE any interaction table for that state pair is opened, a per-family `stacks_attempted`
   counter, and the viewed interaction table attached to the blind packet (mandatory).
2. Free-look pre-screen — BLOCKING as written: "descriptive, costs nothing" is not honest when the
   table's purpose is to choose which stack gets registered. A stack selected from K interaction
   cells enters with K logged as look-cells in a separate multiplicity column; a stack registered
   from mechanism reasoning alone, with no table viewed, is exempt and says so.
3. UNDERPOWERED — CONCERN: must consume an attempt for every variable in the stack, or it becomes
   the soft landing. One underpowered close per format variant, maximum.
4. Stack A circularity — CONCERN: reusing the validated volatility fact as context is legitimate,
   but the packet must show the B2 validation target (next-session range) and the Stack A outcome
   (breakout follow-through) are not the same quantity; identical cost model in both cells.
5. Stack B trigger — BLOCKING until pinned: swing lookback, close-vs-wick confirmation, ATR period
   and bar size, pullback depth X, session window, entry bar, 4H/1H boundaries.
6. Other: state Stack A's prior as a number; freeze the format's own closure rule ("two stacks null
   with adequate power → close the format"); reconcile the trial count.
   **Verdict: CONDITIONAL, six conditions.**

**Operations.** Build is three cycles (S1–S6), no data, no spend. Placement: after the hyp-156
Gate conditions (first research item next cycle) and always after any bot milestone that can move.
One stack in flight at a time. The runner must be year-chunked (device shell limit). The
underpowered status needs a closure-form value and an ops_checks line so it can never be silent.

**Director.** Adopts the format as a second admissible shape, not a replacement. Accepts all six
Gate conditions as binding rules of the format — they are the difference between "a richer
hypothesis" and "a nicer way to fish." Chooses Stack A first because it is the bot's own question
and the cheapest way to learn whether B2 improves B3; Stack B second, only if A closes, and only
once its parameters are pinned. Sets the 2-layer ceiling until one stack has produced a result.
Sets the format's own kill rule now: two stacks closed null with adequate power → the format
closes.

## Disposition: MODIFY — adopted with the following binding rules

1. **A stack is one trial; a paired family is two.** Registered with a spec hash BEFORE the runner
   executes and BEFORE any interaction table for its state pair is opened.
2. **Look-cells are counted.** A stack chosen from an Idea Factory interaction pre-screen of K cells
   records K in a separate `look_cells` column of the multiplicity ledger; Statistical states the
   Discovery threshold conditional on K. A stack written from mechanism alone records K = 0 and
   the packet says so. The viewed table is attached to the blind packet.
3. **Per-family `stacks_attempted` counter** in SCAN_REGISTRY; the 2-attempt limit applies to every
   variable in the stack.
4. **UNDERPOWERED consumes an attempt** for every variable in the stack; one underpowered close per
   format variant, maximum; the definition is never loosened to reach the floor.
5. **Floor and minimum detectable effect pre-registered** by Statistical per candidate; project
   default 100 occurrences on Discovery.
6. **One mechanism per layer + an interaction claim** with a non-restatement prediction; rejected
   at Mechanism otherwise. Timing rule holds per layer.
7. **2-layer ceiling** until the format produces one result; 3 thereafter.
8. **Stack A first** (breakout alone vs breakout in HIGH-expected-range context), prior stated as a
   number in its mechanism doc, cost model identical in both cells, packet showing the B2 target and
   the stack outcome are different quantities. **Stack B second**, only if A closes and only after
   every trigger parameter is pinned in writing.
9. **Format kill rule:** two stacks closed null with adequate power → the format closes.
10. **Placement:** builds S1–S6 queued as U25–U30, after the hyp-156 Gate conditions and after any
    bot milestone that can move; one stack in flight at a time.

Nothing in the promotion bar, slices, one-shot Validation, Holdout rule, or bot ordering changes.

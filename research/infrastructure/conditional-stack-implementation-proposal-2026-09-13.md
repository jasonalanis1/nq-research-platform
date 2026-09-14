# Conditional Stack — implementation proposal for staff-meeting review

Written: September 13th, ~8:50 pm CT. Status: **PROPOSAL — nothing changed, nothing built,
no trial spent.** For review at a staff meeting (Director · Mechanism · Statistical · Integrity
Gate · Operations) with Jason. Inputs: Jason's methodology proposal
(`conditional-stack-proposal-2026-09-13.pdf`) and the two ICC videos (Indication / Correction /
Continuation — 4H direction → 1H pullback → 5–15 min structure turn, shown on NQ).

## 1. What is being proposed, in one paragraph

Every hypothesis Tony has ever tested is *flat*: one state, bucketed, one forward outcome. Jason's
proposal adds a second admissible **format** — a *conditional stack* of 2–3 layers (context →
location → trigger) evaluated in fixed order, pre-registered as ONE hypothesis costing ONE trial,
frozen as a whole. The claim is not that the bar is too high; it is that a flat instrument may be too
blunt to see an effect that only exists when several conditions hold at once. The ICC videos are the
source of the *shape*, not a candidate — the setup they show is an ordinary trend pullback and the
proposal says so.

**Director's read:** adopt, as a format, under the existing discipline, with the guards below. It is
the same idea the project already accepted in two places — the eight-condition conditional-retest
protocol (one pre-chosen condition on a dead pattern) and the Risk/State Engine (a validated state
changing how an entry is handled) — generalised into a hypothesis shape. And it answers a question
the bot needs answered: the bot's signal layer *is* a stack (context = B2 state, location = opening
range, trigger = B3 breakout). This format is how that gets tested honestly.

## 2. Where it plugs into what already runs

| Existing piece | What a stack does there | Change needed |
|---|---|---|
| **Idea Factory / free-look** (Look) | Can pre-screen 2-layer interactions descriptively — a state × state × window cross-tab — before anything is registered. Costs nothing, proves nothing, surfaces candidate stacks. | Add an `--interactions` mode to `src/idea_factory.py`: pairwise state cross-tabs, timing rule applied to BOTH layers, same circularity guard, same "queue is not evidence" rule. |
| **Timing rule** | Each layer has its own known-at; every layer must be known before the trigger fires, and the context layer before the location layer. | `KNOWN_AT` already exists; the stack spec lists it per layer and the runner refuses a stack whose layers are out of time order. |
| **Mechanism doc** (Explain) | One mechanism line **per layer** plus an **interaction claim** (why together ≠ separately) and a **minimum occurrence count**. "It filters out losers" is rejected at Mechanism as fitting. | Template gets Sections 4a (per-layer mechanism), 4b (interaction claim), 9a (min occurrences + minimum detectable effect, set BEFORE Discovery). |
| **SCAN_REGISTRY / multiplicity** | One stack = one registered trial. Any variant of any layer evaluated = another registered trial, every time. | No code change; a `stack_id` field and a spec **hash** recorded at registration so layer-shopping is detectable, not just forbidden. |
| **Discovery** (Test) | A stack scan is a per-occurrence (trade-level) scan, not a daily aggregation → year-chunked, like Scan 033. | New `src/stack_scan_runner.py`: takes a frozen stack spec (JSON), evaluates layers in order, emits occurrences with entry timestamp, runs the pre-registered cells. One runner, every stack. |
| **Statistical** | Adds the **UNDERPOWERED** outcome: if the frozen definition yields fewer than the pre-registered floor on Discovery, close as underpowered — not null, not loosened. States the minimum detectable effect at the floor before the scan runs. | New closure status `underpowered` (closure form already has `data limitation`; keep them distinct — underpowered is the format's own failure mode). |
| **Integrity Gate (blind)** | Checks: every layer coded without interpretation; each layer has its own mechanism; the interaction claim is stated; no layer added after a null; spec hash matches the registered one. | Two lines added to the Gate's standing brief. |
| **Conditional-retest protocol** | A stack whose layers are each individually closed variables is a resurrection unless the *interaction* is the novel claim, stated explicitly. | Already rule 3 of the protocol; restated for stacks. |
| **The bot** | A stack that passes is the first candidate shape that hands the bot a complete entry (context + location + trigger), i.e. a real replacement for B3. | None now; that is the payoff. |

Nothing in the promotion bar, the chronological splits, the two-attempt limit, the one-shot
Validation, or the Holdout rule changes. The stack is a richer *object* under the same rules.

## 3. The two guards that make it legal, spelled out

**Layer shopping is the trap.** Three layers with five candidate variables each is 125 stacks; test
them and pick the winner and you have spent 125 trials while registering one. Guard: the stack's
full spec (variables, edges, order, trigger, horizon, exit, cost model) is hashed and the hash is
written into SCAN_REGISTRY before the runner will execute. A different hash is a different trial.
The free-look may *look* at interactions freely — that is what it is for — but looking produces a
queue entry, never a registered stack.

**Sample starvation is the cost.** Three thirds is 1/27 of the data. Guard: the floor (proposal
suggests 100 occurrences on Discovery) and the minimum detectable effect are pre-registered by
Statistical before the scan; below the floor the stack closes UNDERPOWERED and the definition is
never loosened to reach it. Intraday stacks count occurrences, not days, which is why this format
and the short-horizon priority pull the same way.

## 4. Answers to the four Director questions in the proposal

1. **Ceiling: 2 layers until the format has produced one result**, then 3. The ICC shape is three;
   the first Tony stacks should be two (context + trigger) so that sample starvation and layer
   shopping are both smaller problems while the runner is new.
2. **Paired first test: yes.** The first stack runs as ONE pre-registered family of two cells —
   trigger alone, and trigger inside context — and the gating claim is the *difference*. That costs
   two trials and answers the methodology question directly ("does the context layer carry
   information the flat version does not?") instead of by accumulation. This is also exactly the
   BASE vs BASE+B2 comparison the bot roadmap already requires.
3. **Both formats run.** Flat scans keep the shelf stocked; stacks are drawn when the queue
   surfaces an interaction footprint or when Sourcing Rule v3 reaches a family whose mechanism is
   inherently conditional. Explicit split: at most one stack in flight at a time until the runner
   has closed two stacks cleanly.
4. **Floor ownership: Statistical, per candidate, with a project-wide default of 100** and a
   written minimum detectable effect each time. The default is a floor, not a target.

## 5. The first two candidate stacks (for the meeting to choose from — not registered)

**Stack A — the bot's own question (recommended first).**
Context: B2 `expected_range_mult` tercile (known prior close). Location: the 09:30–10:00 opening
range (known 10:00 ET). Trigger: B3's breakout close with next-bar-open entry (10:00–11:30).
Paired cells: trigger alone vs trigger inside HIGH-expected-range context. Interaction claim: a
breakout of a wide-expected day has room to run; the same breakout on a compressed-expected day
is the fade the project's own facts predict. Per-layer mechanism: volatility persistence (context,
validated) · inventory imbalance from an unbalanced open (location, M30 queue family) · momentum
participants keyed to the opening range (trigger, public). Honest prior: modest; but it is the
question the whole bot rests on, and a null with power is the cheapest possible way to learn that
B2 does not improve B3. Occurrence count is not a problem (the trigger fires on ~75% of sessions).

**Stack B — the ICC shape, done honestly (second, on novelty grounds only if A closes).**
Context: daily directional regime (RTH close vs 20-day mean, or the existing
`directional_persistence` state). Location: a 1-hour pullback of ≥ X ATR against it, X frozen.
Trigger: 5-minute structure turn (higher low, then close above the last swing high) — deterministic,
coded, no discretion. Prediction that is not a restatement: continuation strength rises with
pullback depth. Falsifier: equal effect with the context layer removed. Prior stated plainly in the
proposal: trend-pullback entries are heavily studied and usually fail costs. It is included because
it is the source shape and because the paired design will say cleanly whether the context layer
does anything.

## 6. Build plan (only if adopted)

| Step | What | Where in the cycle | Effort |
|---|---|---|---|
| S1 | Stack spec schema (JSON) + hash-at-registration in `project_wide_multiplicity.py` | Operations, one cycle | small |
| S2 | `src/stack_scan_runner.py` — layer evaluation in order, year-chunked occurrences, pre-registered cells, paired mode | Discovery, one to two cycles | medium |
| S3 | Mechanism template additions (per-layer mechanism, interaction claim, floor + MDE) and the `underpowered` closure status | Mechanism + Statistical, same cycle as S1 | small |
| S4 | `idea_factory.py --interactions` (pairwise state cross-tabs, timing rule on both layers) | Observatory, one cycle | small–medium |
| S5 | Gate brief additions; blind packet carries per-layer mechanisms | Integrity, same cycle as S3 | small |
| S6 | First stack (A), paired, registered as two trials | Discovery → the ladder | one cycle to run |

Total: roughly three cycles of build before the first stack runs. No data purchase. No new rule
weakened. Trials spent: two (the paired first test).

## 7. What this does not change (restated from the proposal, confirmed)

Promotion bar · chronological slices · frozen-spec discipline (now applied to the whole stack) ·
two-attempt limit (a stack engages it for every variable it contains) · project-wide multiplicity
(one stack, one trial) · the Mechanism Gate (strengthened: one claim per layer) · agent order ·
the bot roadmap's ordering (this is research; B4 still comes first each cycle until Jason unblocks it).

## 8. Proposed staff-meeting agenda and disposition

1. Mechanism: is "one mechanism per layer + an interaction claim" a real bar or paperwork?
2. Statistical: the floor (100) and how the minimum detectable effect is stated before the scan.
3. Integrity Gate: is the spec hash sufficient against layer shopping, or does the Gate need to see
   the free-look's interaction table to know what was *looked at*? (Recommendation: yes, attach it.)
4. Director: 2-layer ceiling first; paired first test; both formats run; Stack A first.
5. Operations: build order S1–S6 and where it sits relative to B4 (blocked on Jason) and the
   hyp-156 Gate conditions (first research item next cycle).

**Recommended disposition: MODIFY** — adopt the format with the 2-layer ceiling, the paired first
test, the spec hash, and the underpowered closure status; first stack is the bot's own question.
Judge the format on whether it finds anything a flat scan would have missed; if two stacks close
null with adequate power, close the format.

## 9. One honest note from the Director

The format's real value is not the ICC pullback. It is that Tony can finally state the question its
own facts keep pointing at — *what does this trigger do inside this state?* — as one honest,
countable hypothesis instead of either (a) never asking it or (b) fishing across states until one
works. The guards above exist because (b) is the easiest thing in the world to do with a stack.

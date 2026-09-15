# Batch screening built — Lever C, queue item 0-ACCEL (2026-09-15)

Built per research/infrastructure/acceleration-plan-2026-09-14.md's "Lever C"
and research/NEXT_UP.md's "0-ACCEL" queue entry (Jason, September 14th ~8 pm
CT: "push this as fast as possible", methodology intact). `src/batch_screen.py`,
`tests/test_batch_screen.py` (15 tests). This doc records what we built, the
design choices we made, and the first real batch's result.

## Why this exists

The Idea Factory (src/idea_factory.py) already ranked 143 CANDIDATE cells
(research/observatory/idea-factory-2026-09-14.md) but every cell in that
queue only carries a raw iid z-score against its own window -- no
confidence interval, no multiplicity correction at any principled K, no
placebo check, no check against the conditioning stack this project already
runs. The old pipeline runs ONE candidate through six ceremonial stages
(Director, Mechanism, Discovery scan, Statistical, blind Gate, Validation)
per session. At that rate, working through 143 candidates one at a time
would take most of a season. Batch screening exists to do BREADTH cheaply --
four fast, frozen checks per cell, 20-30 cells a cycle -- and leave DEPTH
(everything from Director triage onward) exactly where it already was, for
survivors only.

## The four gates, and why each one is shaped the way it is

**Gate 1, block-CI effect.** The Idea Factory's own "mean minus all_mean"
effect, recomputed with a calendar-time block bootstrap CI instead of a bare
z-score. We followed src/gate_conditions_hyp162.py's `calendar_block_bootstrap`
and src/baseline_relative.py's `block_bootstrap_diff_ci` pattern closely: each
replicate resamples whole `BLOCK_SESSIONS=10`-day chunks, in chronological
order, and the HIGH/LOW/MID split happens AFTER resampling -- never before.
This project already paid for the alternative mistake once: an earlier
version of `gate_conditions_hyp162.py` resampled each arm independently, and
Condition 3 of the hyp-000162 blind Gate (2026-09-14) caught that it breaks
the very calendar clustering the block bootstrap exists to preserve. We did
not repeat that here, and `tests/test_batch_screen.py` pins the resample
construction down directly (fixed-start RNG stub, hand-computed expected
indices) so a future edit that reintroduces per-arm resampling would fail a
test, not just a code review.

**Gate 2, Sidak at the batch's own K.** Folded into Gate 1's own output as a
second, wider percentile interval on the same bootstrap draw (same pattern
as `gate_conditions_hyp162.py`'s `sidak()` helper). K is `len(batch)` for
THIS run -- 20-30 -- never the 143-cell sweep this batch was drawn from and
never a cumulative count across cycles. The acceleration plan says "Sidak at
the BATCH K" explicitly; a cumulative K would make an early cycle's survivor
bar move every time a later cycle ran, which is not how a pre-registered
look-count correction is supposed to work, and a 143-cell (or eventual
1045-cell) K would make each batch's own 20-30 looks invisible inside a much
larger number that was never the actual multiplicity this batch spent.

**Gate 3, shifted-signal placebo.** Delegates straight to
`src/integrity_checks.py`'s `check_placebo()` -- not reimplemented. Population
is the full outcome-column array for the eligible day-set, mask is the
boolean level-selector, both in real chronological order (order matters:
the shifted leg is `np.roll(mask, 1)`, and check_placebo's own docstring
says a scrambled order defeats the entire point of the check). `null_value`
is the population's own mean -- the correct null for a "subgroup minus
population" effect -- not 0.0, which `integrity_checks.py`'s docstring
explicitly names as "the one thing the suite cannot catch for you" if
passed wrong. A RED here is logged as a flag the survivor carries forward,
never an auto-reject. This mirrors exactly how the blind Integrity Gate
treated hyp-000162's own placebo red at Discovery
(research/studies/hyp162-blind-gate-2026-09-14.md): a blocking finding for a
later, more expensive stage to weigh, not something a cheap mechanical
check gets to unilaterally kill.

**Gate 4, joint separability vs the stack.** `src/portfolio_hyp162.py`'s T1
form (`t1_joint_residual`), adapted: fit the three existing stack members
(`vxn_level_vs_trailing`, `overnight_range_vs_atr`, prior-day `range_vs_atr`)
against the cell's own outcome column by OLS, Discovery only; take the
residual; re-measure the cell's group-vs-population spread on the residual
with the same block bootstrap (90% CI only, matching T1's own reporting --
no Sidak here, since this gate is diagnostic, not itself the survival bar).
This is the standard set by research/NEXT_UP.md's "0-NEW" queue item:
single-fact separability at a 50% bar was shown too weak a test on
hyp-000162 itself (75-88% retained one-at-a-time, only 18-52% jointly) --
so this gate holds the whole stack fixed at once from the start, never the
old Director one-at-a-time method. When a cell's own state variable IS one
of the three stack members, Gate 4 reports `NOT_APPLICABLE` rather than a
misleading number (regressing a variable on itself is not a separability
test).

**Survival is Gate 1 alone.** We deliberately did not fold Gates 3 or 4 into
the pass/fail bar. The acceleration plan's own wording is "the block-CI
effect clears the Sidak-adjusted bar" -- singular, Gate 1. Making survival
also depend on Gates 3/4 would move goalposts the Idea Factory itself never
applied and, worse, would make this script's own definition of "survive"
something we could not have written down before seeing what a placebo or a
separability test found -- which AMENDMENT v3.1 forbids. Gates 3 and 4 are
attached to every survivor's shelf entry as flags instead, so a Director
weighing a candidate later sees the full picture without this cheap screen
having silently pre-judged it.

## Entry-bar handling: TBD anchors are written, not skipped

`research/idea_inventory.md`'s ENTRY BAR requires five items, including a
map anchor naming a `research/market_structure_map.md` row. Six of the ten
state variables the Idea Factory can produce cells for (`range_vs_atr`,
`gap_vs_atr`, `day_of_week`, `directional_persistence`, and — with caveats —
`overnight_range_vs_atr`, which HAS an anchor, M2, but whose 2-attempt
resurrection limit is already exhausted) do not have an obvious, checked
market_structure_map.md row. We considered two options: skip writing the
entry for a survivor whose state lacks an anchor, or write it anyway with
the gap stated honestly. We chose to always write it. A fabricated anchor
would be worse than an honest gap (the task's own instruction), but a
silently dropped real survivor is worse still -- it is exactly the one class
of cell where "every screened cell is logged" matters most, since a
survivor is by definition a cell that cleared a real statistical bar. Every
`MAP_ANCHORS` entry in `src/batch_screen.py` was checked against
`market_structure_map.md`'s actual table, never guessed from the state's
name; where no row exists, the entry says so verbatim ("TBD -- Director/
LEARN call") with the specific reason, and the mechanism-claim line is
marked either PROVISIONAL (inherited from a real anchor's forced-participant
story) or NOT YET CLAIMED (no anchor at all) rather than writing a claim
this cheap screen never actually defended. `tests/test_batch_screen.py`
covers both paths directly (`test_survivor_entry_written_even_with_a_tbd_map_anchor_not_skipped`).

## State tracking across cycles

`research/_batch_screen_state.json` -- a single JSON object, not append-only
jsonl, keyed by `CELL_ID = "{state}|{level}|{window}|{outcome}"` (the same
four fields the Idea Factory itself uses to define a cell, so the two can
never drift apart). `screened` maps every already-screened CELL_ID to a
short summary (survived, placebo status, which report file); `history`
records one row per run. The audit trail with full per-cell detail lives in
`research/observatory/batch-screen-<date>.md` instead, one dated file per
run, never overwritten -- the state file only needs to answer "has this cell
been screened," not replay what happened. On every run, `main()` filters the
143-cell candidate_queue (in the Idea Factory's own `|z|`-descending order)
down to CELL_IDs not already in `screened`, and takes the next
`BATCH_SIZE=25` of those. `tests/test_batch_screen.py` exercises this
filtering directly (`select_unscreened`) without paying for a real data load.

## First real run, 2026-09-15

`python3 src/batch_screen.py`, ~30 seconds wall clock (N_BOOT=2000 per
bootstrap call, two calls per cell for most cells).

- **25 cells screened** (batch K = 25). **25/25 survived** Gate 1.
- **18/25 (72%) placebo RED.** This is the single most important honest
  finding from the first batch, and it is NOT a defect in the screen -- it
  is the same structural issue hyp-000162 already taught this project:
  the strongest cells in the Idea Factory's ranking cluster on a small
  number of slow-moving, persistent daily states (`vxn_minus_realized`:
  10/25 of this batch; `opening_range_vs_atr`: 9/25; `volume_vs_expected`:
  5/25), where a day's level is highly likely to still hold the next day,
  so the shifted (t+1) placebo often reproduces a large fraction of the
  real effect. Every RED is carried forward on its survivor's shelf entry,
  not hidden and not auto-rejected -- it is exactly the kind of blocking
  finding the blind Integrity Gate is built to weigh at the appropriate
  (much more expensive) stage, the same disposition hyp-000162 itself got.
- Gate 4 (joint separability) came back `still_credible_after_stack: true`
  for every one of the 25 survivors whose own state was not itself a stack
  member -- none of this batch's effects visibly collapsed to "restates
  vxn_level_vs_trailing / overnight_range_vs_atr / prior-day range_vs_atr."
  That is a genuinely informative result, not assumed: it means this
  batch's candidates are not simply the existing three-fact stack
  relabeled, though it says nothing about whether Gate 3's placebo issue
  is itself a restatement of ONE of those facts specifically (a question
  for Director/Mechanism, since Gate 4 residualizes the whole stack at
  once and would not isolate that).
- Cumulative: **25 / 143** candidate cells screened project-wide after one
  run. All 25 entries were written to `research/idea_inventory.md` as
  ENTRY 37 through ENTRY 61 -- SOURCED/DRAWABLE, screened only, not scanned;
  Director triage, mechanism-doc writing, Statistical, the blind Gate and
  Validation remain entirely unchanged and still owed for every one of
  them, per this script's own stated scope.
- Full per-cell detail: `research/observatory/batch-screen-2026-09-15.md`.

## Open question for Jason / the Director

25/25 survived Gate 1 on this first batch, which is unsurprising (these are
literally the 25 highest-|z| cells out of 143 in the Idea Factory's own
ranking, so a real block-CI effect surviving a K=25 Sidak bar was close to
expected for most of them) -- but the 72% placebo red rate means a large
share of this shelf is going to need the Gate's placebo-aware judgment
before any of it is worth a registered scan, exactly as hyp-000162 needed.
We are NOT recommending the Director skip straight to scanning these 25;
they are shelf-ready candidates for triage, in the Idea Factory's own
words, "a candidate for a mechanism document, not a finding." The next
batch (cells 26-50 by rank) is expected to look similar, since `vxn_minus_
realized` alone accounts for 44 of the 143 candidate cells.

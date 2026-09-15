# Why 72% of the batch-screen survivors flagged placebo RED — the one-time explanation (directive s.9)

Written 2026-09-15 (Day One of the standing operating directive,
research/infrastructure/standing-directive-2026-09-15.md s.9: "Tony explains the
placebo rate once, in writing, then either uses those survivors as stop/sizing inputs
or closes them. It does not run batch_screen.py to generate more.") Data:
research/observatory/batch-screen-2026-09-15.md (25 cells, 25 Gate-1 survivors, 18 RED
on Gate 3). This is the explanation; the disposition of Entries 37-61 is at the end.

## The finding, stated plainly

The 72% RED rate is a property of how Gate 3 (the "shifted placebo") is BUILT when it
is pointed at a MAGNITUDE cell measured against the all-days mean, not evidence that
the 25 effects are spurious. Every one of the 18 REDs is produced by one of two
arithmetic facts about the placebo legs, and both facts hold whether or not the
underlying effect is real. Read against the table in the observatory file
(research/observatory/batch-screen-2026-09-15.md:15-120 and following):

### Cause 1 — the "inverted" leg is the complement, and the complement is about half the effect by construction (11 of 18 REDs)

Each cell is "days in state X" (a tercile, ~1/3 of days) and the effect is the mean
range of those days minus the all-days mean. The "inverted" placebo leg is the same
statistic on the complement (the other ~2/3 of days). But the all-days mean is a
weighted average of the two: a·μ_X + (1−a)·μ_rest = 0 with a ≈ 1/3, so
μ_rest = −a/(1−a)·μ_X ≈ −0.5·μ_X. The inverted leg therefore reaches about −50% of
the real effect EVERY time, and Gate 3's threshold is "a leg reaching 50% of the
real effect is RED". The data show exactly that ratio on every inverted-leg RED:

| cell (Entry) | real | inverted | ratio |
|---|---:|---:|---:|
| `volume_vs_expected` HIGH / first30 (42) | +0.076 | −0.039 | −0.52 |
| `volume_vs_expected` HIGH / morning (45) | +0.092 | −0.047 | −0.52 |
| `volume_vs_expected` HIGH / midday (48) | +0.086 | −0.044 | −0.51 |
| `vxn_minus_realized` HIGH / morning (50) | +0.074 | −0.037 | −0.50 |
| `vxn_minus_realized` HIGH / rth (51) | +0.144 | −0.073 | −0.51 |
| `vxn_minus_realized` HIGH / first30 (52) | +0.058 | −0.029 | −0.50 |
| `volume_vs_expected` HIGH / overnight (53) | +0.129 | −0.065 | −0.50 |
| `vxn_minus_realized` HIGH / next_rth (54) | +0.149 | −0.075 | −0.50 |
| `volume_vs_expected` HIGH / rth (56) | +0.165 | −0.085 | −0.52 |
| `vxn_minus_realized` HIGH / last_hour (58) | +0.052 | −0.026 | −0.50 |
| `location_in_range` LOW / last_hour (60) | +0.052 | −0.026 | −0.50 |

A ratio pinned at −0.50 across eleven unrelated cells is arithmetic, not a placebo
result. The LOW-tercile cells of the same states (41, 43, 46, 49, 59) show the same
ratio and came out GREEN only by rounding: their inverted legs sit at 0.4995-0.4997 of
the real effect (e.g. Entry 41: real −0.0694, inverted +0.0347), a hair UNDER the
50% threshold in src/integrity_checks.py:378 (`worst >= PLACEBO_COMPARABLE * abs(real)`),
while the HIGH cells sit at 0.50-0.52, a hair over. Which side of 50% a cell lands on
is decided by the tercile's exact day count, not by anything about the market.

### Cause 2 — the "shifted t+1" leg re-selects the same days because the state persists (7 of 18 REDs)

The shifted leg applies the state mask one day late. For a state that persists from
day to day, that mask re-selects most of the SAME days (the observatory file reports
the overlap: 51% for `opening_range_vs_atr`, 60% for `volume_vs_expected`, 84-88% for
`vxn_minus_realized` and `location_in_range`), so the "placebo" inherits most of the
real effect and clears 50% of it. This is the failure research/KNOWLEDGE.md already
recorded on 2026-09-14 for hyp-000142 (a VXN tercile re-selects 79% of itself at t+1,
so t+1 is not an independent placebo) -- the batch screen marked the shifted leg
"reported but NOT gating" for the states whose overlap it had measured (M29, M31),
but left it GATING for `opening_range_vs_atr`, whose overlap (51%) it printed on the
LOW cells and did not apply to the HIGH cells. All seven shifted-leg REDs are
`opening_range_vs_atr` cells (Entries 37, 39, 40, 44, 55, 57, 61): the top-ranked
cells cluster on slow-moving persistent states, so the t+1 mask re-selects most of
the same days.

### What this does and does not say

It does NOT say the 25 effects are real edges. They are magnitude (range) facts of
the same family as the three already-validated sizing facts, and 22 of them are
re-cuts of states this project already holds as conditioning inputs (M29's
VXN-minus-realized gap, M30's opening-range width, M31's prior-day volume). It says
only that the RED flags carry no information here, and that a placebo built for a
directional signal was applied to a magnitude state it cannot test. The 25-cell
batch will not be extended: batch_screen.py is not run again (directive s.9).

## Disposition of Entries 37-61 (research/idea_inventory.md)

Directive s.9: use as stop/sizing inputs or close. None of these is a strategy;
none gets a scan, a hypothesis id, or a paper slot of its own.

- **SIZING-INPUT CANDIDATES, M30 `opening_range_vs_atr` (Entries 37, 38, 39, 40, 44,
  47, 55, 57, 61):** folded into registry candidate **S005** (hyp-000162's opening-range
  effect as a stop/sizing input). Usable by a host strategy's SPECIFY or FIX ONCE
  as a midday/afternoon stop-width or size rule (wide open -> wider midday, the
  directive's third named magnitude fact). Never drawn as a scan.
- **SIZING-INPUT CANDIDATES, M29 `vxn_minus_realized` (Entries 41, 43, 46, 49, 50,
  51, 52, 54, 58, 59):** the implied-minus-realized gap is a state primitive already
  adjacent to the Risk/State Engine's VXN fact (hyp-000142, HOLDOUT PASSED). Usable
  as a refinement of the VXN -> next-session-range stop input if a host strategy's
  Salvage or FIX ONCE names it. Never drawn as a scan.
- **SIZING-INPUT CANDIDATES, M31 `volume_vs_expected` (Entries 42, 45, 48, 53, 56):**
  prior-day volume vs expected -> next-session range. Same use, same rule.
- **CLOSED, Entry 60 `location_in_range` LOW / last_hour -> range:** a single cell,
  the smallest effect in the batch (+0.052), no mechanism doc for location-in-range
  as a range predictor, and no host strategy trades the last hour. Closed, not
  resurrected.

The inventory titles are updated to say this; the entries' full screen tables stay
as written. No number above was recomputed -- every figure is copied from
research/observatory/batch-screen-2026-09-15.md.

"""
batch_screen.py -- LEVER C (acceleration plan, September 14th 2026: "push this
as fast as possible"). Queue item 0-ACCEL, per
research/infrastructure/acceleration-plan-2026-09-14.md's "Lever C" and
research/NEXT_UP.md's "0-ACCEL" queue entry.

WHAT IT DOES
  Screens a BATCH of BATCH_SIZE (20-30) not-yet-screened cells from the Idea
  Factory's candidate queue (data/idea_factory_2026-09-14.json, key
  "candidate_queue", 143 CANDIDATE-classified cells) through a CHEAP,
  Discovery-only gate, once per invocation:

    GATE 1  Block-CI effect. The cell's effect, redefined here as
            (subgroup mean - population mean) exactly like the Idea Factory's
            own "mean" vs "all_mean", but with a proper CALENDAR-TIME block
            bootstrap confidence interval instead of the Idea Factory's raw
            z-score (which has no CI at all -- it assumes iid days). Follows
            the RESAMPLE-THEN-SPLIT pattern in
            src/gate_conditions_hyp162.py's calendar_block_bootstrap() and
            src/baseline_relative.py's block_bootstrap_diff_ci(): blocks of
            BLOCK_SESSIONS=10 consecutive TRADING DAYS, in chronological
            order, are resampled as whole units, and the HIGH/LOW/MID split
            is applied AFTER resampling, not before. Resampling the two arms
            independently (as an earlier version of this project's own
            gate_conditions_hyp162.py did, before Condition 3 of the
            hyp-000162 blind Gate caught it on 2026-09-14) breaks the very
            calendar clustering a block bootstrap exists to preserve, and
            that defect is not repeated here.

    GATE 2  Sidak multiplicity correction AT THE BATCH'S OWN K. K = the
            number of cells actually screened THIS RUN (this batch's
            len(), e.g. 20-30) -- never the 143-cell idea-factory sweep this
            batch was drawn from, and never a running cumulative total
            across cycles. Each batch stands on its own look-count, exactly
            as the acceleration plan specifies ("Sidak at the BATCH K").
            Implemented as a widened bootstrap-percentile interval, the same
            sidak() pattern as src/gate_conditions_hyp162.py's helper of the
            same name -- folded into Gate 1's own output (same resample, two
            interval widths reported: the raw 90% CI and the Sidak-adjusted
            one that gates survival).

    GATE 3  Shifted-signal placebo, via src/integrity_checks.py's
            check_placebo(). population = the full outcome-column array for
            the eligible day-set (every day with a valid value in that
            window/outcome, matching the Idea Factory's own "all days"
            denominator), in chronological day order; mask = the boolean
            selector for the cell's HIGH/LOW/MID level, same order -- order
            matters, because check_placebo's shifted leg is np.roll(mask, 1)
            and a scrambled order would shift the wrong pair of days against
            each other. null_value is the population's own mean (the correct
            null for a "subgroup minus population" effect, not 0.0 -- 0.0
            would be the wrong null here and check_placebo cannot catch that
            for us, per its own documented input contract).
            A RED here is LOGGED AS A FLAG the survivor carries forward. It
            does NOT auto-reject. This is the same disposition the blind
            Integrity Gate gave hyp-000162's placebo red at Discovery
            (research/studies/hyp162-blind-gate-2026-09-14.md): a blocking
            finding for a later, more expensive stage to weigh, not a reason
            to drop a cell this cheap gate cannot itself adjudicate.

    GATE 4  Joint separability vs the existing conditioning stack, using
            src/portfolio_hyp162.py's T1 form (t1_joint_residual) as the
            template -- the standard set by NEXT_UP.md's "0-NEW" queue item:
            "SINGLE-FACT SEPARABILITY AT THE 50% BAR IS TOO WEAK A TEST ...
            hold the whole stack fixed at once", not the old Director
            one-at-a-time method. The three existing stack members
            (vxn_level_vs_trailing, overnight_range_vs_atr, prior-day
            range_vs_atr) are fit by OLS against the cell's OWN outcome
            column, on Discovery only; the residual is taken; the cell's
            HIGH/LOW/MID-vs-population spread is re-measured on that
            residual with the same block-bootstrap machinery as Gate 1
            (raw 90% CI only, no Sidak -- matching T1's own reporting, which
            is descriptive-diagnostic here, not itself the survival bar).
            If the cell's own state variable IS one of the three stack
            members, this gate is skipped as NOT_APPLICABLE (regressing a
            variable on itself is not a separability test) rather than
            silently reporting a misleading number.

  SURVIVAL is decided by GATE 1 ALONE: a cell "survives" the batch screen
  if its block-CI effect clears the Sidak-adjusted bar at the batch's own K
  (interval entirely on one side of zero) -- exactly the wording in the
  acceleration plan and in this file's own docstring above. Gates 3 and 4
  are diagnostic flags carried forward on every survivor's shelf entry, not
  additional pass/fail bars; conflating them with survival would silently
  move the goalposts on gates the Idea Factory itself never applied, and
  would make this script's own definition of "survive" depend on results it
  had not seen when it was written -- forbidden by AMENDMENT v3.1 below.

WHAT IT DOES NOT DO (same discipline src/idea_factory.py's own "WHAT IT
DOES" section states for itself, and preserved here on purpose)
  - Spends no hypothesis ID. Registers no scan.
  - Never touches Validation or Holdout data -- build_frame() (imported,
    not reimplemented, from src/idea_factory.py) is Discovery-only via
    src/data_split.py's get_discovery_data(), transitively.
  - Never re-screens a cell that state tracking (see below) shows already
    screened, survivor or not.
  - Never writes a mechanism document, runs a registered scan, or performs
    Director triage / Statistical / the blind Integrity Gate / Validation.
    A survivor's inventory entry is shelf-ready, not tested. Everything
    downstream of the shelf is UNCHANGED for a survivor of this script.
  - Never retroactively touches a cell already written to
    research/idea_inventory.md by an earlier run of this script, and never
    edits its own gate logic (block length, Sidak formula, survival rule)
    in response to what any batch finds. This script is FROZEN in spirit:
    a fixed gate applied uniformly to every cell, exactly like
    src/gate_conditions_hyp162.py's or src/idea_factory.py's own frozen
    thresholds. AMENDMENT v3.1: nothing frozen is edited on results, and
    this file was written and its constants fixed BEFORE its first real
    run ever looked at which of the 143 candidate cells would pass.

STATE TRACKING ACROSS CYCLES
  research/_batch_screen_state.json (created on first run) is a small JSON
  document, NOT append-only jsonl (chosen for this file because the state
  it holds -- which cells have been screened -- is naturally a dictionary
  keyed by a stable identifier, and a single JSON object is simpler to load
  and query than replaying an unbounded jsonl log on every one of the many
  overnight cycles this script will see; a full jsonl AUDIT TRAIL is instead
  the per-batch research/observatory/batch-screen-<date>.md file, one per
  run, which never gets overwritten). Its shape:

    {
      "schema": 1,
      "screened": {
        "<state>|<level>|<window>|<outcome>": {
          "screened_date": "YYYY-MM-DD",
          "batch_k": <int, this cell's OWN batch's K>,
          "survived": <bool>,
          "gate1_credible_sidak": <bool>,
          "placebo_status": "GREEN" | "RED" | "INSUFFICIENT" | "NOT APPLICABLE",
          "report_file": "research/observatory/batch-screen-<date>.md"
        }, ...
      },
      "history": [
        {"run_date": ..., "report_file": ..., "n_screened": ..., "n_survivors": ...,
         "n_placebo_red": ..., "cumulative_screened": ...}, ...
      ]
    }

  The key is CELL_ID = "{state}|{level}|{window}|{outcome}" -- the same four
  fields the Idea Factory itself uses to define a cell, so a cell can never
  drift between what the Idea Factory generated and what this state file
  tracks. On every run, main() loads this file, filters the 143-cell
  candidate_queue down to cells whose CELL_ID is NOT already a key in
  "screened", and takes the next BATCH_SIZE of THOSE (in the Idea Factory's
  own ranking order, |z| descending -- the order the candidate_queue array
  is already sorted in). A cell is marked "screened" here the moment it is
  run through all four gates in one call, survivor or not -- so a re-run
  after a crash mid-write is the only case that could re-screen a cell, and
  even then produces the same answer (every bootstrap below is seeded
  deterministically per cell, not per run).

DETERMINISM
  Every bootstrap in this file is seeded from SEED (dated 2026-09-15, the
  day this script was written) combined deterministically with the cell's
  own CELL_ID via zlib.crc32 -- NOT with the cell's position in a given
  batch, so the exact same cell screened in a future re-run (which should
  never happen, per the state file above, but is guarded anyway) reproduces
  bit-identical results regardless of what else was in its batch.

THE IDEA FACTORY DATA FILE IS PINNED, NOT "LATEST"
  IDEA_FACTORY_FILE below names data/idea_factory_2026-09-14.json
  explicitly rather than globbing for whatever idea_factory_*.json is
  newest on disk. The candidate_queue is a frozen sourcing artifact for as
  long as this multi-cycle screen is in progress; silently switching to a
  freshly regenerated queue partway through (which could renumber or
  redefine cells, and would break the CELL_ID state-tracking contract
  above) would be exactly the kind of silent definition drift
  src/idea_factory.py's own build_frame() exists to prevent between
  generation and screening. If a new Idea Factory sweep is ever meant to
  replace this one, that is a deliberate decision (bump IDEA_FACTORY_FILE
  by hand, in its own commit, not an automatic side effect of this file).

MAP ANCHOR HANDLING (ENTRY BAR, research/idea_inventory.md)
  The inventory's ENTRY BAR requires five items: state variable, mechanism
  claim, horizon, Integrity Gate resurrection ruling, and a map anchor
  naming a research/market_structure_map.md row. This script does NOT skip
  writing a survivor's entry when no anchor obviously fits -- per this
  task's own instruction, a fabricated anchor is worse than an honest gap,
  but a SILENTLY DROPPED SURVIVOR is worse still (it would violate "every
  screened cell is logged" for the one class of cell -- a real survivor --
  where losing the record matters most). MAP_ANCHORS below is a hand-
  written, read-only lookup from each of the ten states the Idea Factory
  can produce cells for to either a real market_structure_map.md row
  number (cited, never invented) or the literal string "TBD -- Director/
  LEARN call" with the reason stated inline. A TBD-anchored survivor entry
  is written anyway, with that gap stated in the MAP ANCHOR line itself, so
  the Director sees exactly what is missing instead of finding a plausible-
  looking anchor that was never actually checked against the map. The
  MECHANISM CLAIM line on every entry this script writes is likewise marked
  PROVISIONAL -- inherited from the map anchor's own forced-participant
  story where one exists, or left explicitly unclaimed where it does not --
  because a full, defended mechanism claim is Director/Mechanism-stage
  work this cheap screen does not do (see "WHAT IT DOES NOT DO" above).

HOW TO RUN
    python3 src/batch_screen.py

  Runs exactly one batch (BATCH_SIZE cells, or fewer if the candidate queue
  is nearly exhausted) end to end: screens, updates the state file, writes
  research/observatory/batch-screen-<date>.md (every screened cell, four-
  gate table, survivor or not), appends any survivor to
  research/idea_inventory.md, and prints a short human-readable summary.
  Run it again (same command) on the next cycle to pick up the next batch.
"""
from __future__ import annotations

import json
import re
import sys
import zlib
from datetime import date as _date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from production_paths import assert_writable, enable_production
import idea_factory as IF          # noqa: E402  build_frame(), WINDOWS, KNOWN_AT -- reused, not reimplemented
import integrity_checks as IC      # noqa: E402  check_placebo()

# ---------------------------------------------------------------------------
# frozen constants -- written and fixed BEFORE this script's first real run
# ever looked at the candidate queue's contents (AMENDMENT v3.1)
# ---------------------------------------------------------------------------
BATCH_SIZE = 25            # 20-30 per the Lever C spec; one fixed number, not tuned per cycle
BLOCK_SESSIONS = 10         # consecutive CALENDAR trading days, matches gate_conditions_hyp162.py
N_BOOT = 2000                # per bootstrap call; two calls (Gate 1, Gate 4) per cell, 25 cells/batch
SEED = 20260915              # dated to when this script was written
ALPHA = 0.10                  # 90% CI, project convention (integrity_checks.CI = 90)
MIN_CELL_N = 30                # floor below which a bootstrap arm reports INSUFFICIENT, never a number
STACK = ["vxn_level_vs_trailing", "overnight_range_vs_atr", "range_vs_atr"]  # portfolio_hyp162.py's STACK

IDEA_FACTORY_FILE = ROOT.parent / "data" / "idea_factory_2026-09-14.json"
STATE_FILE = ROOT.parent / "research" / "_batch_screen_state.json"
INVENTORY_FILE = ROOT.parent / "research" / "idea_inventory.md"
OBSERVATORY_DIR = ROOT.parent / "research" / "observatory"
RUN_DATE = _date.today().isoformat()
REPORT_FILE = OBSERVATORY_DIR / f"batch-screen-{RUN_DATE}.md"

# state -> market_structure_map.md anchor, or an honest TBD with the reason
# stated. Never invented; every real anchor below was checked against
# research/market_structure_map.md's own table, not guessed from the name.
MAP_ANCHORS = {
    "opening_range_vs_atr": (
        "M30 (opening-range width -> midday range/excursion, NQ; "
        "market_structure_map.md row M30)"),
    "volume_vs_expected": (
        "M31 (prior-day volume vs expected -> first-30-minute range, NQ; "
        "market_structure_map.md row M31)"),
    "vxn_minus_realized": (
        "M29 (implied-minus-realized volatility gap, VXN vs NQ trailing "
        "realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). "
        "NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile "
        "scan; a survivor here should be cross-checked against that entry's "
        "own construction before a mechanism doc is drafted, not assumed to "
        "be the same cell."),
    "vxn_level_vs_trailing": (
        "M7 (vol-control/risk-parity deleveraging -- RANGE use already "
        "HOLDOUT PASSED as hyp-000151/M7; market_structure_map.md row M7). "
        "NOTE: vxn_level_vs_trailing is also one of THIS SCRIPT's own Gate 4 "
        "stack members -- a survivor with this state variable will show its "
        "Gate 4 as NOT_APPLICABLE (regressing a variable on itself), which "
        "is expected, not a defect."),
    "overnight_range_vs_atr": (
        "M2 (RTH-open overnight-inventory resolution; market_structure_map.md "
        "row M2) -- CLOSED, and per the map's own LEARN pre-check, "
        "overnight_range_vs_atr's 2-attempt resurrection limit is EXHAUSTED "
        "(H116 + idea_inventory Entry 1). A survivor with this state cannot "
        "get a fresh Integrity Gate resurrection ruling without a new "
        "staff-meeting-level justification -- flagged here, NOT blocked; "
        "this is a Director call, not this script's to make."),
    "location_in_range": (
        "M32 (open's location in the prior day's range -> later-session "
        "range, NQ; per idea_inventory.md ENTRY 36, which sourced and drew "
        "this anchor). NOTE: as of this script's writing, "
        "market_structure_map.md's own table has not yet been updated to "
        "add an M32 row -- a pre-existing maintenance gap this script did "
        "not create and is not the file to fix (out of scope: this script "
        "may only append to idea_inventory.md, never edit "
        "market_structure_map.md). Flagged for LEARN/Director."),
    "range_vs_atr": (
        "TBD -- Director/LEARN call. Prior-day range_vs_atr is referenced "
        "elsewhere in the ledger only as shorthand ('F-048'), not as a "
        "numbered market_structure_map.md row; no anchor is fabricated "
        "here."),
    "gap_vs_atr": (
        "TBD -- Director/LEARN call. No market_structure_map.md row "
        "visibly anchors the overnight gap as its own forced-participant "
        "claim; no anchor is fabricated here."),
    "day_of_week": (
        "TBD -- Director/LEARN call. Turn-of-month (M6) and the closed "
        "day-of-week-adjacent families are a different calendar mechanism; "
        "no market_structure_map.md row anchors day-of-week directly; no "
        "anchor is fabricated here."),
    "directional_persistence": (
        "TBD -- Director/LEARN call. No market_structure_map.md row "
        "anchors this state; no anchor is fabricated here."),
}

# window -> human-readable ET span, for the entry text
_SPAN = {w: span for w, (_start, span) in IF.WINDOWS.items()}


def window_label(window: str) -> str:
    span = _SPAN.get(window)
    if span:
        return f"{span[0]}-{span[1]} ET"
    if window == "overnight":
        return "prior 18:00 -> 09:30 ET (overnight)"
    if window == "next_rth":
        return "following session's RTH, 09:30-16:00 ET"
    return window


_KNOWN_AT_LABEL = {
    IF.PRIOR_CLOSE: "the previous evening's close",
    IF.OPEN_0930: "09:30 ET (RTH open)",
    IF.TEN_AM: "10:00 ET",
    IF.CLOSE_1600: "16:00 ET (session close)",
}


def known_at_label(state: str) -> str:
    return _KNOWN_AT_LABEL.get(IF.KNOWN_AT[state], f"{IF.KNOWN_AT[state]} minutes from midnight")


def cell_id(cell: dict) -> str:
    return f"{cell['state']}|{cell['level']}|{cell['window']}|{cell['outcome']}"


def cell_seed(cell: dict) -> int:
    """Deterministic per-cell seed: SEED plus a stable hash of CELL_ID, NOT
    the cell's position in whatever batch it happens to land in."""
    return (SEED + zlib.crc32(cell_id(cell).encode())) % (2**31 - 1)


def select_unscreened(candidate_queue: list, screened_ids) -> list:
    """The candidate queue, in its own existing order (|z| descending, the
    order the Idea Factory itself ranked it in), filtered down to cells
    whose CELL_ID is not already a key of `screened_ids`. A cell already
    screened -- survivor or not -- is never re-screened; this is the whole
    of the state-tracking contract, isolated into one small function so it
    can be tested without paying for a real build_frame() load."""
    screened_ids = set(screened_ids)
    return [c for c in candidate_queue if cell_id(c) not in screened_ids]


# ---------------------------------------------------------------------------
# state file
# ---------------------------------------------------------------------------
def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"schema": 1, "screened": {}, "history": []}


def save_state(state: dict) -> None:
    assert_writable(STATE_FILE, "batch-screen state")
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str))


# ---------------------------------------------------------------------------
# the four cheap gates
# ---------------------------------------------------------------------------
def ols_fit(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Matches src/portfolio_hyp162.py's ols_fit exactly."""
    return np.linalg.lstsq(np.column_stack([np.ones(len(X)), X]), y, rcond=None)[0]


def ols_pred(beta: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.column_stack([np.ones(len(X)), X]) @ beta


def block_bootstrap_effect(values: np.ndarray, mask: np.ndarray, block: int,
                            n_boot: int, rng, min_arm_n: int = MIN_CELL_N) -> np.ndarray:
    """RESAMPLE-THEN-SPLIT calendar block bootstrap of (group mean - overall
    mean). `values` and `mask` MUST already be in chronological day order --
    this function trusts its caller, exactly like
    src/gate_conditions_hyp162.py's calendar_block_bootstrap and
    src/portfolio_hyp162.py's _blocks/t1_joint_residual, which make the same
    assumption about their own inputs. Each replicate draws whole
    `block`-day chunks of CONSECUTIVE ROWS (never individual days), tiles
    them to length n, and ONLY THEN splits by `mask` -- so within-arm
    clustering and cross-arm contemporaneous correlation are both preserved,
    the defect Condition 3 of the hyp-000162 blind Gate found in an earlier
    (per-arm-independent) resampling scheme."""
    n = len(values)
    n_blocks = int(np.ceil(n / block))
    max_start = max(n - block + 1, 1)
    effects = []
    for _ in range(n_boot):
        starts = rng.integers(0, max_start, size=n_blocks)
        idx = (starts[:, None] + np.arange(min(block, n))[None, :]).reshape(-1)[:n]
        v, m = values[idx], mask[idx]
        if m.sum() < min_arm_n or (~m).sum() < min_arm_n:
            continue
        effects.append(float(v[m].mean() - v.mean()))
    return np.array(effects)


def sidak_ci(effects: np.ndarray, k: int, alpha: float = ALPHA) -> tuple:
    """Two-sided Sidak-adjusted percentile interval for one of k simultaneous
    looks -- same formula as src/gate_conditions_hyp162.py's sidak()."""
    alpha_adj = 1 - (1 - alpha) ** (1.0 / k)
    lo = float(np.percentile(effects, 100 * alpha_adj / 2))
    hi = float(np.percentile(effects, 100 * (1 - alpha_adj / 2)))
    return lo, hi


def cell_arrays(both: pd.DataFrame, cell: dict):
    """The population (outcome column, all eligible days) and the boolean
    group mask, both in CHRONOLOGICAL DAY ORDER -- the shared input every
    gate below is built from. Returns None if the cell's columns are
    missing (should not happen: the candidate queue was generated from this
    same build_frame())."""
    col = f"{cell['outcome']}_{cell['window']}"
    grp_col = f"{cell['state']}_g"
    if col not in both.columns or grp_col not in both.columns:
        return None
    sub = both[[col, grp_col]].sort_index()
    sub = sub.replace([np.inf, -np.inf], np.nan).dropna(subset=[col, grp_col])
    values = sub[col].to_numpy(dtype=float)
    mask = (sub[grp_col].astype(str) == str(cell["level"])).to_numpy(dtype=bool)
    return values, mask


def gate1_block_ci(values: np.ndarray, mask: np.ndarray, k: int, seed: int) -> dict:
    if mask.sum() < MIN_CELL_N or (~mask).sum() < MIN_CELL_N:
        return {"status": "INSUFFICIENT", "n_group": int(mask.sum()), "n_population": int(len(values))}
    raw_point = float(values[mask].mean() - values.mean())
    rng = np.random.default_rng(seed)
    effects = block_bootstrap_effect(values, mask, BLOCK_SESSIONS, N_BOOT, rng)
    if len(effects) < 30:
        return {"status": "INSUFFICIENT", "n_replicates_used": int(len(effects)),
                "n_group": int(mask.sum()), "n_population": int(len(values))}
    ci90 = (float(np.percentile(effects, 100 * ALPHA / 2)),
            float(np.percentile(effects, 100 * (1 - ALPHA / 2))))
    lo, hi = sidak_ci(effects, k)
    return {
        "status": "OK",
        "n_replicates_used": int(len(effects)),
        "n_group": int(mask.sum()), "n_population": int(len(values)),
        "raw_point": round(raw_point, 6),
        "bootstrap_point": round(float(np.mean(effects)), 6),
        "ci_90_unadjusted": [round(ci90[0], 6), round(ci90[1], 6)],
        "sidak_k": int(k),
        "sidak_alpha_adjusted": round(1 - (1 - ALPHA) ** (1.0 / k), 6),
        "ci_sidak": [round(lo, 6), round(hi, 6)],
        "credible_sidak": bool(lo > 0 or hi < 0),
    }


def gate3_placebo(values: np.ndarray, mask: np.ndarray, raw_point, seed: int) -> dict:
    """population/mask in the SAME chronological day order cell_arrays()
    already put them in -- check_placebo's shifted leg (np.roll(mask, 1))
    depends on that order being real calendar order, not a scramble.
    null_value is the population's OWN mean: the correct null for a
    'subgroup minus population' effect (NOT 0.0 -- integrity_checks.py's own
    docstring says passing the wrong null is the one thing it cannot catch)."""
    if raw_point is None:
        return IC.check_placebo(population=values, mask=mask, null_value=float(np.mean(values)), seed=seed)
    return IC.check_placebo(population=values, mask=mask, null_value=float(np.mean(values)),
                             real_effect=float(raw_point), seed=seed)


def gate4_joint_separability(both: pd.DataFrame, cell: dict, seed: int) -> dict:
    """portfolio_hyp162.py's T1 form, adapted: fit the three STACK members
    against the cell's own outcome column on Discovery only, take the
    residual, and re-measure the cell's group-vs-population spread on the
    residual with the same block bootstrap as Gate 1 (90% CI only, no
    Sidak -- matching T1's own reporting)."""
    state = cell["state"]
    if state in STACK:
        return {"status": "NOT_APPLICABLE",
                "detail": "cell's own state is a Gate-4 stack member; regressing a "
                          "variable on itself is not a separability test"}
    col = f"{cell['outcome']}_{cell['window']}"
    grp_col = f"{state}_g"
    needed = [col, grp_col] + STACK
    if not all(c in both.columns for c in needed):
        return {"status": "INSUFFICIENT", "detail": "missing stack or outcome column"}
    sub = both[needed].sort_index()
    sub = sub.replace([np.inf, -np.inf], np.nan).dropna()
    if len(sub) < MIN_CELL_N * 2:
        return {"status": "INSUFFICIENT", "n": int(len(sub))}
    y = sub[col].to_numpy(dtype=float)
    X = sub[STACK].to_numpy(dtype=float)
    beta = ols_fit(X, y)
    resid = y - ols_pred(beta, X)
    mask = (sub[grp_col].astype(str) == str(cell["level"])).to_numpy(dtype=bool)
    if mask.sum() < MIN_CELL_N or (~mask).sum() < MIN_CELL_N:
        return {"status": "INSUFFICIENT", "n": int(len(sub)), "n_group": int(mask.sum())}
    rng = np.random.default_rng(seed)
    effects = block_bootstrap_effect(resid, mask, BLOCK_SESSIONS, N_BOOT, rng)
    if len(effects) < 30:
        return {"status": "INSUFFICIENT", "n": int(len(sub)), "n_group": int(mask.sum())}
    ci90 = (float(np.percentile(effects, 100 * ALPHA / 2)),
            float(np.percentile(effects, 100 * (1 - ALPHA / 2))))
    raw_point = float(resid[mask].mean() - resid.mean())
    return {
        "status": "OK", "n": int(len(sub)), "n_group": int(mask.sum()),
        "stack": STACK,
        "raw_point": round(raw_point, 6),
        "bootstrap_point": round(float(np.mean(effects)), 6),
        "ci_90": [round(ci90[0], 6), round(ci90[1], 6)],
        "still_credible_after_stack": bool(ci90[0] > 0 or ci90[1] < 0),
    }


def screen_cell(both: pd.DataFrame, cell: dict, batch_k: int) -> dict:
    seed = cell_seed(cell)
    arr = cell_arrays(both, cell)
    out = {"cell_id": cell_id(cell), "state": cell["state"], "level": cell["level"],
           "window": cell["window"], "outcome": cell["outcome"],
           "idea_factory": {"n": cell["n"], "mean": cell["mean"], "all_mean": cell["all_mean"], "z": cell["z"]},
           "map_anchor": MAP_ANCHORS.get(cell["state"], "TBD -- Director/LEARN call (state not in MAP_ANCHORS)")}
    if arr is None:
        out.update(gate1_block_ci=({"status": "INSUFFICIENT", "detail": "missing columns"}),
                    gate3_placebo={"check": "7. placebo", "status": "NOT APPLICABLE"},
                    gate4_joint_separability={"status": "INSUFFICIENT"}, survived=False)
        return out
    values, mask = arr
    g1 = gate1_block_ci(values, mask, batch_k, seed)
    raw_point = g1.get("raw_point")
    g3 = gate3_placebo(values, mask, raw_point, seed + 1)
    g4 = gate4_joint_separability(both, cell, seed + 2)
    out.update(gate1_block_ci=g1, gate3_placebo=g3, gate4_joint_separability=g4,
                survived=bool(g1.get("credible_sidak", False)))
    return out


# ---------------------------------------------------------------------------
# output: observatory report, inventory entries, state, summary
# ---------------------------------------------------------------------------
def _fmt_ci(ci) -> str:
    if ci is None:
        return "n/a"
    return f"[{ci[0]:+.4f}, {ci[1]:+.4f}]"


def screen_table_md(r: dict) -> list:
    g1, g3, g4 = r["gate1_block_ci"], r["gate3_placebo"], r["gate4_joint_separability"]
    L = ["| gate | status | point | interval | detail |", "|---|---|---:|---|---|"]
    if g1.get("status") == "OK":
        L.append(f"| 1. block-CI effect | OK | {g1['raw_point']:+.4f} | "
                 f"Sidak(K={g1['sidak_k']}) {_fmt_ci(g1['ci_sidak'])} | "
                 f"90% unadj. {_fmt_ci(g1['ci_90_unadjusted'])}; credible={g1['credible_sidak']} |")
    else:
        L.append(f"| 1. block-CI effect | {g1.get('status')} | -- | -- | n_group={g1.get('n_group','?')} |")
    L.append(f"| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K={r['idea_factory'].get('batch_k', g1.get('sidak_k','?'))} |")
    status3 = g3.get("status", "?")
    if status3 in ("RED", "GREEN"):
        L.append(f"| 3. shifted placebo | {status3} | -- | -- | real={g3.get('real_effect')}; "
                 f"legs={g3.get('placebo_effects')}; {g3.get('detail','')} |")
    else:
        L.append(f"| 3. shifted placebo | {status3} | -- | -- | {g3.get('detail','')} |")
    if g4.get("status") == "OK":
        L.append(f"| 4. joint separability (T1) | OK | {g4['raw_point']:+.4f} | "
                 f"90% {_fmt_ci(g4['ci_90'])} | vs stack {g4['stack']}; "
                 f"still_credible_after_stack={g4['still_credible_after_stack']} |")
    else:
        L.append(f"| 4. joint separability (T1) | {g4.get('status')} | -- | -- | {g4.get('detail','')} |")
    return L


def write_report(results: list, batch_k: int, cumulative: int) -> None:
    OBSERVATORY_DIR.mkdir(parents=True, exist_ok=True)
    survivors = [r for r in results if r["survived"]]
    reds = [r for r in results if r["gate3_placebo"].get("status") == "RED"]
    L = [f"# Batch screen — {RUN_DATE}", "",
         f"Lever C (research/infrastructure/acceleration-plan-2026-09-14.md), queue item 0-ACCEL. "
         f"Discovery only. No hypothesis ID spent, no scan registered.", "",
         f"**{len(results)} cells screened this run** (batch K = {batch_k} -- this run's own look "
         f"count, not the 143-cell idea-factory sweep and not a cumulative total). "
         f"**{len(survivors)} survivors** (Gate 1 clears the Sidak-adjusted bar at K={batch_k}). "
         f"**{len(reds)} placebo RED flags** (carried forward, not auto-rejected). "
         f"**Cumulative cells screened project-wide: {cumulative} / 143.**", "",
         "Survival = Gate 1 alone (block-CI effect clears Sidak at the batch's own K). "
         "Gates 3 and 4 are diagnostic flags attached to every cell, survivor or not.", "",
         "## Cells screened this run", ""]
    for r in results:
        mark = "SURVIVOR" if r["survived"] else "no edge in this data"
        L += [f"### `{r['state']}` {r['level']} / {r['window']} / {r['outcome']} — {mark}", "",
              f"Idea-factory descriptive: n={r['idea_factory']['n']}, mean={r['idea_factory']['mean']:+.4f}, "
              f"all_mean={r['idea_factory']['all_mean']:+.4f}, z={r['idea_factory']['z']:+.2f}. "
              f"Map anchor: {r['map_anchor']}", ""]
        L += screen_table_md(r)
        L.append("")
    L += ["## Non-survivors: \"no edge in this data\" is a valid result",
          "",
          "Per the acceleration plan: \"If the honest answer is 'no edge in this data', batch "
          "screening gets there sooner too, and that is also worth money.\" Full per-cell detail "
          "above; not repeated in research/idea_inventory.md, which is append-only for survivors.",
          ""]
    REPORT_FILE.write_text("\n".join(L) + "\n")


def next_entry_number() -> int:
    text = INVENTORY_FILE.read_text()
    nums = [int(m) for m in re.findall(r"## ENTRY (\d+)", text)]
    return (max(nums) + 1) if nums else 1


def build_inventory_entry(r: dict, entry_no: int, batch_k: int) -> str:
    g1 = r["gate1_block_ci"]
    state, level, window, outcome = r["state"], r["level"], r["window"], r["outcome"]
    mechanism = ("PROVISIONAL, inherited from the map anchor's own forced-participant story "
                 "cited below; Director/Mechanism stage owed the full written claim before any "
                 "registered scan (per src/idea_factory.py's own discipline: a queue entry is a "
                 "candidate for a mechanism document, not a finding)."
                 if not r["map_anchor"].startswith("TBD") else
                 "NOT YET CLAIMED -- no map anchor identified a forced participant for this state "
                 "(see MAP ANCHOR below); Director/LEARN call before any mechanism doc or registered "
                 "scan can be written for this cell.")
    lines = [
        f"## ENTRY {entry_no} — batch_screen.py cheap-gate survivor: `{state}` {level} / {window} "
        f"-> {outcome} (batch_screen.py, {RUN_DATE}) — SURVIVOR, batch K={batch_k}, DRAWABLE "
        f"(screened only, not scanned)",
        "",
        f"Generation (Lever C, research/infrastructure/acceleration-plan-2026-09-14.md, queue item "
        f"0-ACCEL): drawn from the Idea Factory candidate_queue "
        f"({IDEA_FACTORY_FILE.name}), descriptive n={r['idea_factory']['n']}, "
        f"mean={r['idea_factory']['mean']:+.4f} vs all-days {r['idea_factory']['all_mean']:+.4f}, "
        f"z={r['idea_factory']['z']:+.2f}. Re-tested here with a calendar-time block bootstrap "
        f"(block={BLOCK_SESSIONS}) and a Sidak correction at this batch's own K={batch_k} (NOT the "
        f"143-cell sweep total): raw effect {g1.get('raw_point', float('nan')):+.4f}, Sidak-adjusted "
        f"90%-family interval {_fmt_ci(g1.get('ci_sidak'))}. Gates 3 (shifted-signal placebo) and 4 "
        f"(joint separability vs the vxn_level_vs_trailing / overnight_range_vs_atr / range_vs_atr "
        f"stack, portfolio_hyp162.py's T1 form) are FLAGS carried forward, not additional pass/fail "
        f"bars at this stage -- see the FULL SCREEN TABLE below.",
        "",
        f"1. **STATE VARIABLE**: `{state}` (already implemented in market_state_primitives*.py; "
        f"known at {known_at_label(state)}).",
        f"2. **MECHANISM CLAIM**: {mechanism}",
        f"3. **HORIZON**: {window_label(window)} ({outcome} outcome).",
        f"4. **INTEGRITY GATE RESURRECTION RULING**: NOT YET RULED. This is a cheap-screen survivor, "
        f"not a Director-triaged entry -- Director owes the full resurrection check (ledger by name "
        f"and by what is measured) before any scan is registered against this cell. See MAP ANCHOR "
        f"for any known adjacency/attempt-limit flags on `{state}`.",
        f"5. **MAP ANCHOR**: {r['map_anchor']}",
        "",
        "**FULL SCREEN TABLE** (all four cheap-gate results, batch K carried forward so the "
        f"multiplicity denominator is never lost -- batch K = {batch_k}):",
        "",
    ]
    lines += screen_table_md(r)
    lines += ["", "---", ""]
    return "\n".join(lines)


def append_inventory_entries(survivors: list, batch_k: int) -> list:
    entry_no = next_entry_number()
    text_to_append = []
    numbers = []
    for r in survivors:
        text_to_append.append(build_inventory_entry(r, entry_no, batch_k))
        numbers.append(entry_no)
        entry_no += 1
    assert_writable(INVENTORY_FILE, "idea inventory append")
    with INVENTORY_FILE.open("a") as f:
        f.write("\n" + "\n".join(text_to_append))
    return numbers


def main() -> int:
    both, edges, group_states = IF.build_frame()
    if not IDEA_FACTORY_FILE.exists():
        raise SystemExit(f"pinned idea-factory file missing: {IDEA_FACTORY_FILE}")
    cq = json.loads(IDEA_FACTORY_FILE.read_text())["candidate_queue"]

    state = load_state()
    unscreened = select_unscreened(cq, state["screened"].keys())

    if not unscreened:
        print(f"ALL {len(cq)} candidate cells already screened. Nothing to do this run.")
        return 0

    batch = unscreened[:BATCH_SIZE]
    batch_k = len(batch)
    results = [screen_cell(both, c, batch_k) for c in batch]

    for r in results:
        state["screened"][r["cell_id"]] = {
            "screened_date": RUN_DATE, "batch_k": batch_k, "survived": r["survived"],
            "gate1_credible_sidak": r["gate1_block_ci"].get("credible_sidak", False),
            "placebo_status": r["gate3_placebo"].get("status", "?"),
            "report_file": str(REPORT_FILE.relative_to(ROOT.parent)),
        }
    cumulative = len(state["screened"])
    survivors = [r for r in results if r["survived"]]
    reds = [r for r in results if r["gate3_placebo"].get("status") == "RED"]
    state["history"].append({
        "run_date": RUN_DATE, "report_file": str(REPORT_FILE.relative_to(ROOT.parent)),
        "n_screened": len(results), "batch_k": batch_k, "n_survivors": len(survivors),
        "n_placebo_red": len(reds), "cumulative_screened": cumulative,
    })
    save_state(state)

    write_report(results, batch_k, cumulative)

    entry_numbers = []
    if survivors:
        entry_numbers = append_inventory_entries(survivors, batch_k)

    print(f"batch_screen.py -- {RUN_DATE}")
    print(f"  cells screened this run: {len(results)} (batch K = {batch_k})")
    print(f"  survivors: {len(survivors)}" + (f" -> idea_inventory.md ENTRY {entry_numbers}" if entry_numbers else ""))
    print(f"  placebo RED flags (carried forward, not auto-rejected): {len(reds)}")
    print(f"  cumulative cells screened project-wide: {cumulative} / {len(cq)}")
    print(f"  full output: {REPORT_FILE}")
    if not survivors:
        print("  \"no edge in this data\" for every cell this run -- a valid, logged result, "
              "not a failure to hide (see the report file).")
    return 0


if __name__ == "__main__":
    enable_production()   # NOTE: batch screening is FROZEN (refocus s.3) -- do not run this
    raise SystemExit(main())

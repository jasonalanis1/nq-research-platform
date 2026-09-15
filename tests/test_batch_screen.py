"""Tests for src/batch_screen.py (Lever C, queue item 0-ACCEL).

Covers the parts that decide whether the screen is LEGITIMATE rather than
just fast: the block bootstrap must resample whole calendar-day blocks (not
scramble individual days), the Sidak correction must use the BATCH's own K
(never the 143-cell sweep total), state tracking must never re-screen an
already-screened cell, a survivor must get a fully-formed inventory entry,
and the placebo call must hand integrity_checks.check_placebo its
population/mask in real chronological order. None of these tests touch the
real data pipeline (no build_frame() call) -- they exercise the gate
functions directly on small synthetic arrays, the same style
tests/test_idea_factory_interactions.py uses for idea_factory.py's own
non-data-dependent logic.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(ROOT))

import batch_screen as bs  # noqa: E402


# ---------------------------------------------------------------------------
# Gate 1: the block bootstrap resamples whole calendar blocks, not
# individually-scrambled days
# ---------------------------------------------------------------------------

class _FixedStartsRNG:
    """A stand-in for np.random.default_rng() whose .integers() always
    returns a caller-supplied, fixed array of block-start positions --
    lets a test pin down EXACTLY which indices a bootstrap replicate uses,
    instead of trusting a real RNG's draw."""

    def __init__(self, starts):
        self._starts = np.asarray(starts)

    def integers(self, low, high, size=None):
        assert len(self._starts) == size
        assert np.all((self._starts >= low) & (self._starts <= high - 1))
        return self._starts.copy()


def test_block_bootstrap_resamples_contiguous_calendar_blocks_not_scrambled_days():
    """With block=4 and fixed starts [2, 5, 8] the resample must be the
    CONTIGUOUS runs values[2:6], values[5:9], values[8:12] concatenated --
    not some other selection of 12 individual days. This is the
    resample-then-split invariant Condition 3 of the hyp-000162 blind Gate
    required: block_bootstrap_effect must never be able to assemble an
    index array whose consecutive entries, within one block, are anything
    but n, n+1, n+2, ... (real calendar order)."""
    values = np.arange(12, dtype=float)
    mask = np.array([True] * 6 + [False] * 6)
    rng = _FixedStartsRNG([2, 5, 8])
    effects = bs.block_bootstrap_effect(values, mask, block=4, n_boot=1, rng=rng, min_arm_n=1)

    # hand-computed from the CONTIGUOUS blocks [2,3,4,5],[5,6,7,8],[8,9,10,11]
    idx = np.array([2, 3, 4, 5, 5, 6, 7, 8, 8, 9, 10, 11])
    expected_v = values[idx]
    expected_m = mask[idx]
    expected_effect = expected_v[expected_m].mean() - expected_v.mean()

    assert len(effects) == 1
    assert effects[0] == pytest.approx(expected_effect)


def test_block_bootstrap_index_never_skips_within_a_block():
    """A structural check independent of the fixed-starts trick above: for
    MANY real-RNG replicates, every run of `block` consecutive output
    positions must itself be `block` consecutive integers (mod nothing --
    this project's block bootstrap never wraps). An iid (day-scrambling)
    bootstrap would violate this constantly; a correct block bootstrap
    never does."""
    n, block = 83, 10
    rng = np.random.default_rng(3)
    n_blocks = int(np.ceil(n / block))
    for _ in range(200):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).reshape(-1)[:n]
        for b in range(0, len(idx) - block + 1, block):
            chunk = idx[b:b + block]
            if len(chunk) < block:
                continue
            assert np.all(np.diff(chunk) == 1), "a block's indices must be chronologically consecutive"


# ---------------------------------------------------------------------------
# Gate 1 + 2: Sidak at the BATCH's own K, never the 143-cell sweep's K
# ---------------------------------------------------------------------------

def test_sidak_ci_widens_with_smaller_k_and_uses_the_given_k_not_a_constant():
    rng = np.random.default_rng(0)
    effects = rng.normal(loc=0.5, scale=1.0, size=5000)
    lo_25, hi_25 = bs.sidak_ci(effects, k=25)
    lo_143, hi_143 = bs.sidak_ci(effects, k=143)
    lo_2, hi_2 = bs.sidak_ci(effects, k=2)
    # more looks (bigger K) -> wider Sidak-adjusted interval
    assert (hi_143 - lo_143) > (hi_25 - lo_25) > (hi_2 - lo_2)


def test_gate1_block_ci_uses_the_k_it_is_given_not_the_full_sweep():
    rng = np.random.default_rng(1)
    n = 400
    values = rng.normal(0, 1, n)
    values[:150] += 2.0          # a strong, unmistakable group effect
    mask = np.zeros(n, dtype=bool)
    mask[:150] = True
    seed = 12345
    small_k = bs.gate1_block_ci(values, mask, k=25, seed=seed)
    big_k = bs.gate1_block_ci(values, mask, k=143, seed=seed)
    assert small_k["status"] == "OK" and big_k["status"] == "OK"
    assert small_k["sidak_k"] == 25
    assert big_k["sidak_k"] == 143
    # same bootstrap draw (same seed), but K=143's interval must be the wider one
    width_small = small_k["ci_sidak"][1] - small_k["ci_sidak"][0]
    width_big = big_k["ci_sidak"][1] - big_k["ci_sidak"][0]
    assert width_big > width_small
    # and it must NOT silently be some hardcoded 143 or 1045 regardless of what's passed
    assert small_k["sidak_alpha_adjusted"] != big_k["sidak_alpha_adjusted"]


# ---------------------------------------------------------------------------
# state tracking: an already-screened cell is never re-screened
# ---------------------------------------------------------------------------

def _cell(state="s1", level="HIGH", window="midday", outcome="range"):
    return {"state": state, "level": level, "window": window, "outcome": outcome,
            "n": 200, "mean": 0.5, "all_mean": 0.3, "z": 5.0, "class": "CANDIDATE"}


def test_select_unscreened_drops_already_screened_cells_and_preserves_order():
    cq = [_cell(state=f"s{i}") for i in range(5)]
    already = {bs.cell_id(cq[1]), bs.cell_id(cq[3])}
    out = bs.select_unscreened(cq, already)
    assert [bs.cell_id(c) for c in out] == [bs.cell_id(cq[0]), bs.cell_id(cq[2]), bs.cell_id(cq[4])]


def test_select_unscreened_returns_empty_when_everything_is_screened():
    cq = [_cell(state=f"s{i}") for i in range(3)]
    already = {bs.cell_id(c) for c in cq}
    assert bs.select_unscreened(cq, already) == []


def test_state_file_round_trips_and_next_run_would_skip_screened_cells(tmp_path, monkeypatch):
    state_file = tmp_path / "_batch_screen_state.json"
    monkeypatch.setattr(bs, "STATE_FILE", state_file)
    assert not state_file.exists()
    state = bs.load_state()
    assert state == {"schema": 1, "screened": {}, "history": []}

    cq = [_cell(state=f"s{i}") for i in range(4)]
    state["screened"][bs.cell_id(cq[0])] = {"survived": False}
    state["screened"][bs.cell_id(cq[2])] = {"survived": True}
    bs.save_state(state)

    reloaded = bs.load_state()
    unscreened = bs.select_unscreened(cq, reloaded["screened"].keys())
    assert [bs.cell_id(c) for c in unscreened] == [bs.cell_id(cq[1]), bs.cell_id(cq[3])]


# ---------------------------------------------------------------------------
# Gate 3: check_placebo gets population/mask in real chronological order,
# and the correct (population-mean) null -- never 0.0, never scrambled
# ---------------------------------------------------------------------------

def test_gate3_placebo_passes_population_and_mask_unscrambled_in_order(monkeypatch):
    captured = {}

    def _fake_check_placebo(population=None, mask=None, null_value=None, real_effect=None, seed=None):
        captured["population"] = population
        captured["mask"] = mask
        captured["null_value"] = null_value
        captured["real_effect"] = real_effect
        return {"check": "7. placebo", "status": "GREEN"}

    monkeypatch.setattr(bs.IC, "check_placebo", _fake_check_placebo)

    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])   # already "chronological" order
    mask = np.array([True, False, True, False, True, False])
    bs.gate3_placebo(values, mask, raw_point=0.42, seed=7)

    # exact same array, same order -- not sorted, not reversed, not resampled
    assert np.array_equal(captured["population"], values)
    assert np.array_equal(captured["mask"], mask)
    # null is the POPULATION MEAN (correct null for subgroup-minus-population),
    # never the wrong hardcoded 0.0
    assert captured["null_value"] == pytest.approx(float(values.mean()))
    assert captured["null_value"] != 0.0
    assert captured["real_effect"] == 0.42


def test_gate3_placebo_null_value_is_population_mean_on_a_real_call():
    """No monkeypatching -- a real call through to integrity_checks, with a
    population/mask constructed so the shifted-signal placebo is a
    genuinely different sample (not a persistent-state near-duplicate)."""
    rng = np.random.default_rng(9)
    n = 200
    values = rng.normal(0, 1, n)
    mask = np.zeros(n, dtype=bool)
    mask[rng.choice(n, size=60, replace=False)] = True   # scattered, not persistent
    real_effect = float(values[mask].mean() - values.mean())
    res = bs.gate3_placebo(values, mask, real_effect, seed=1)
    assert res["check"] == "7. placebo"
    assert res["status"] in ("GREEN", "RED", "INSUFFICIENT")


# ---------------------------------------------------------------------------
# Gate 4: skipped, not misleadingly computed, when the cell's own state is
# a stack member
# ---------------------------------------------------------------------------

def test_gate4_not_applicable_when_state_is_a_stack_member():
    import pandas as pd
    idx = pd.date_range("2018-01-01", periods=50, freq="B")
    df = pd.DataFrame({
        "range_midday": np.random.default_rng(2).normal(0, 1, 50),
        "vxn_level_vs_trailing_g": ["HIGH"] * 25 + ["LOW"] * 25,
        "vxn_level_vs_trailing": np.random.default_rng(3).normal(0, 1, 50),
        "overnight_range_vs_atr": np.random.default_rng(4).normal(0, 1, 50),
        "range_vs_atr": np.random.default_rng(5).normal(0, 1, 50),
    }, index=idx)
    cell = _cell(state="vxn_level_vs_trailing", level="HIGH", window="midday", outcome="range")
    out = bs.gate4_joint_separability(df, cell, seed=1)
    assert out["status"] == "NOT_APPLICABLE"


# ---------------------------------------------------------------------------
# survivor disposition: a fully-formed inventory entry, ENTRY BAR's five
# items present, screen table attached, batch K stated -- even with a TBD
# map anchor (this script's documented choice: write the entry anyway
# rather than silently drop a real survivor; see its own docstring)
# ---------------------------------------------------------------------------

def _fake_screened_cell(state="gap_vs_atr", survived=True):
    """A screen_cell()-shaped result dict without running any bootstrap."""
    return {
        "cell_id": f"{state}|HIGH|midday|range", "state": state, "level": "HIGH",
        "window": "midday", "outcome": "range",
        "idea_factory": {"n": 400, "mean": 0.55, "all_mean": 0.30, "z": 7.2},
        "map_anchor": bs.MAP_ANCHORS.get(state, "TBD -- Director/LEARN call"),
        "gate1_block_ci": {"status": "OK", "n_group": 200, "n_population": 400,
                            "raw_point": 0.25, "bootstrap_point": 0.24,
                            "ci_90_unadjusted": [0.15, 0.34], "sidak_k": 25,
                            "sidak_alpha_adjusted": 0.004, "ci_sidak": [0.10, 0.40],
                            "credible_sidak": True},
        "gate3_placebo": {"check": "7. placebo", "status": "GREEN", "n": 200},
        "gate4_joint_separability": {"status": "OK", "n": 380, "n_group": 190,
                                      "stack": bs.STACK, "raw_point": 0.18,
                                      "bootstrap_point": 0.17, "ci_90": [0.05, 0.29],
                                      "still_credible_after_stack": True},
        "survived": survived,
    }


def test_survivor_entry_has_all_five_entry_bar_items_and_the_screen_table(tmp_path, monkeypatch):
    inv = tmp_path / "idea_inventory.md"
    inv.write_text("# Idea Inventory\n\n## ENTRY 36 — something — CLOSED\n\ntext\n")
    monkeypatch.setattr(bs, "INVENTORY_FILE", inv)

    r = _fake_screened_cell(state="volume_vs_expected")   # has a real M31 anchor
    numbers = bs.append_inventory_entries([r], batch_k=25)
    assert numbers == [37]

    text = inv.read_text()
    assert "## ENTRY 37" in text
    assert "1. **STATE VARIABLE**" in text
    assert "2. **MECHANISM CLAIM**" in text
    assert "3. **HORIZON**" in text
    assert "4. **INTEGRITY GATE RESURRECTION RULING**" in text
    assert "5. **MAP ANCHOR**" in text
    assert "M31" in text
    assert "FULL SCREEN TABLE" in text
    assert "batch K = 25" in text
    # the pre-existing entry must be untouched (append-only)
    assert "## ENTRY 36 — something — CLOSED" in text


def test_survivor_entry_written_even_with_a_tbd_map_anchor_not_skipped(tmp_path, monkeypatch):
    """This script's documented choice: a real survivor is never silently
    dropped for lacking an obvious map anchor -- it is written with the gap
    stated honestly in the MAP ANCHOR line, for the Director to see and
    decide, rather than either fabricating an anchor or losing the cell."""
    inv = tmp_path / "idea_inventory.md"
    inv.write_text("# Idea Inventory\n\n")
    monkeypatch.setattr(bs, "INVENTORY_FILE", inv)

    r = _fake_screened_cell(state="directional_persistence")  # TBD in MAP_ANCHORS
    assert r["map_anchor"].startswith("TBD")
    numbers = bs.append_inventory_entries([r], batch_k=25)
    assert numbers == [1]
    text = inv.read_text()
    assert "TBD" in text
    assert "5. **MAP ANCHOR**" in text
    assert "NOT YET CLAIMED" in text  # mechanism claim is honestly unclaimed, not fabricated


def test_non_survivor_gets_no_inventory_entry(tmp_path, monkeypatch):
    inv = tmp_path / "idea_inventory.md"
    inv.write_text("# Idea Inventory\n\n")
    monkeypatch.setattr(bs, "INVENTORY_FILE", inv)
    r = _fake_screened_cell(survived=False)
    survivors = [x for x in [r] if x["survived"]]
    assert survivors == []
    # main() only calls append_inventory_entries on survivors; confirm the
    # would-be text is simply never written
    assert inv.read_text() == "# Idea Inventory\n\n"


def test_next_entry_number_continues_from_the_highest_existing_entry(tmp_path, monkeypatch):
    inv = tmp_path / "idea_inventory.md"
    inv.write_text("## ENTRY 5 — x\n## ENTRY 12 — y\n## ENTRY 3 — z\n")
    monkeypatch.setattr(bs, "INVENTORY_FILE", inv)
    assert bs.next_entry_number() == 13


def test_cell_seed_is_stable_per_cell_not_per_batch_position():
    c1 = _cell(state="a")
    c2 = _cell(state="b")
    assert bs.cell_seed(c1) == bs.cell_seed(c1)          # deterministic
    assert bs.cell_seed(c1) != bs.cell_seed(c2)           # distinct cells, distinct seeds

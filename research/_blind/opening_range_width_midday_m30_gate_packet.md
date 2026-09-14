# BLIND INTEGRITY GATE PACKET

You are the Integrity Gate, in a fresh context. Standing brief: assume this
candidate is wrong; find every reason the PROCEDURE could be fooling us.
Every result figure below is masked on purpose. Rule PASS / VETO / CONDITIONAL
on procedure only: leakage, contamination, post-hoc selection, frozen-before-
test, resurrection, multiplicity accounting, direction pre-registered, cost model
measured not assumed, review point sized (power) before freezing.
If this candidate is a CONDITIONAL STACK (context -> location -> trigger), also rule on:
every layer coded without interpretation; one mechanism per layer plus a stated
interaction claim; no layer added after a null; every layer known strictly before the
trigger fires; the registered spec hash matches the code that ran; and the look-cells
count (how many interaction cells were examined before this spec was written) disclosed.
Output: Finding / Confidence / Novelty / Research Value / Recommendation.

## Family: opening_range_width_midday_range_excursion_nq_m30

## Frozen spec (masked)

# Mechanism — Opening-range width → midday range and excursion, NQ (M30, observatory channel, from the Idea Factory queue)

Written: 2026-09-13, ~7:15 pm CT (7:00 pm test cycle, Sourcing Rule v3). PRE-REGISTERED as a claim;
the descriptive footprint that pointed here is research/observatory/idea-factory-2026-09-13.md
(`opening_range_vs_atr → range/mfe/mae`, strongest family, z ≈ 11 HIGH/midday). Results of any
REGISTERED test: NOT seen. The queue entry is descriptive and is not evidence.
LEARN consulted by name: the state variable `opening_range_vs_atr` has never been the conditioning
variable of a registered scan (Scan 002 used it only as a same-day descriptor, no claim); the
initial-balance breakout family (exp-028/031) tested DIRECTION after the first 30 minutes and closed
null — this is a SIZE claim, not a direction claim, and does not reopen that family.

## 1. The claim
Sessions whose first 30 minutes (09:30–10:00 ET) span a HIGH-tercile range in ATR14 units show a
credibly LARGER midday range (11:30–13:30 ET) and larger maximum excursions from the midday open in
both directions than LOW-tercile sessions. Known at 10:00 ET; outcome starts 11:30 ET (timing rule
satisfied by 90 minutes).

## 2. Who is on the other side
Intraday liquidity providers and the systematic "opening drive" desks. A wide first half-hour means
the open did not find balance: inventory was transferred at a range of prices, dealers are carrying
imbalanced books into the quietest part of the day, and their hedging (and the momentum funds that
key off the opening range) keeps repricing through midday instead of resting. Participant:
market-maker inventory management. Named, observable only through this proxy.

## 3. Why this is not the overfitting trap
One state (already frozen in market_state_primitives), one tercile cut fixed on Discovery, one
outcome window pre-declared (midday), one direction of effect (larger). The Idea Factory's other
windows for this state (morning, afternoon, last hour) are NOT part of this claim; reported only.

## 4. Testable predictions
P1 (GATING). HIGH-tercile opening range → midday range ratio (midday range / trailing-20d mean
   midday range) credibly ABOVE the LOW-tercile ratio; block CI on the HIGH−LOW difference > 0.
P2 (reported). HIGH-tercile → larger midday MFE and MAE from the midday open (both signs) — the
   excursion claim, which is what an exit rule would use.
P3 (reported). The effect survives residualizing on prior-day range tercile (F-048): the opening
   range is not merely yesterday's volatility restated. ≥50% retained.

## 5. What would falsify this
(a) P1 fails → closes; the queue footprint was a Discovery-slice artefact or already captured by
    F-048. (b) P1 passes, P3 fails → duplicate of F-048; closes as duplicate (closure form status
    "duplicate"). (c) Thin-sample: not a concern (~560 days per tercile).

## 6. Information gain and edge potential
Gain: HIGH — a fifth candidate input to the Risk/State Engine that is known at 10:00 ET, i.e. an
INTRADAY update between the pre-open number and the 14:00 afternoon update. Edge: sizing/stop
distance for anything entered after 10:00, including the B3 placeholder entry, whose breakout window
starts exactly then. This is the first queue family that plugs directly into the bot.

## 7. Resurrection ruling
NEW. Not exp-028/031 (direction after the initial balance; closed). Not F-048 (prior-DAY range; P3
tests the distinction). Not M9. Attempt 1 of 2.

## 8. Instrument-choice gate
NQ only; 10:00 ET state; same-session outcome from 11:30; magnitude not direction; NULL = unconditional
midday range ratio. TWO NULLS rule not triggered (no directional or cross-index claim).

## 9. Frozen scope
ONE scan, Discovery slice, daily aggregation (scan_027/030 pattern). Cells: (1) HIGH−LOW midday range
ratio difference, block CI  <== GATING P1; (2) HIGH−LOW midday MFE difference (P2); (3) HIGH−LOW midday
MAE difference (P2); (4) P1 residualized on F-048 tercile (P3); (5) unconditional midday ratio
reference; (6) alignment/coverage disclosure. Block=10, N_BOOT=3000, SEED=20260913, 90% CI.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
DRAWN and SCANNED 2026-09-14 (7:00 am CT catch-up cycle), Scan 036, hyp-000162.
- **P1 (GATING): PASS.** HIGH−LOW midday range-ratio difference [masked], CI90
  ([masked], [masked]), [masked]/556. Credibly positive.
- **P2: both positive.** MFE difference [masked] ATR, [masked], [masked]);
  MAE difference [masked] ATR, [masked], [masked]). Larger excursions in
  both directions, as predicted.
- **P3: PASS.** Stratified on the prior-day range tercile (F-048): [masked] vs
  the raw [masked], **[masked] retained** against a 50% bar. Not a restatement of
  F-048.
- Status: **PROMISING**, Statistical (+POWER) owed, then the BLIND Integrity Gate.

**BLOCKING FINDING FOR THE GATE (U6 mechanical suite, 4 green / 1 RED / 2 not
run — research/integrity/mechanical-scan036-2026-09-14.json).** The PLACEBO
check is red: the shifted-signal (t+1) placebo reaches [masked] against the real
[masked] — **74% of the effect**. Yesterday's opening range predicts today's
midday range nearly as well as today's own does, so the claim's specificity to
the same session is in question; this may be a multi-day volatility-regime
effect rather than an opening-range effect. **P3 does not cover this**: it
residualized on prior-day RANGE (`range_vs_atr`), which is a different variable
from prior-day OPENING range. Disclosed: the shifted leg's overlap with the real
selection is [masked], just under the 50% guard above which that leg stops gating
— roughly 1.5 points from not being raised at all, so the Gate should weigh it
as a near-boundary verdict. The inverted placebo behaves correctly (−[masked],
opposite sign). Per the U6 spec a RED is a blocking finding, **not** an
automatic close, and nothing here is retuned in response to it.


## Mechanism doc (masked)

# Mechanism — Opening-range width → midday range and excursion, NQ (M30, observatory channel, from the Idea Factory queue)

Written: 2026-09-13, ~7:15 pm CT (7:00 pm test cycle, Sourcing Rule v3). PRE-REGISTERED as a claim;
the descriptive footprint that pointed here is research/observatory/idea-factory-2026-09-13.md
(`opening_range_vs_atr → range/mfe/mae`, strongest family, z ≈ 11 HIGH/midday). Results of any
REGISTERED test: NOT seen. The queue entry is descriptive and is not evidence.
LEARN consulted by name: the state variable `opening_range_vs_atr` has never been the conditioning
variable of a registered scan (Scan 002 used it only as a same-day descriptor, no claim); the
initial-balance breakout family (exp-028/031) tested DIRECTION after the first 30 minutes and closed
null — this is a SIZE claim, not a direction claim, and does not reopen that family.

## 1. The claim
Sessions whose first 30 minutes (09:30–10:00 ET) span a HIGH-tercile range in ATR14 units show a
credibly LARGER midday range (11:30–13:30 ET) and larger maximum excursions from the midday open in
both directions than LOW-tercile sessions. Known at 10:00 ET; outcome starts 11:30 ET (timing rule
satisfied by 90 minutes).

## 2. Who is on the other side
Intraday liquidity providers and the systematic "opening drive" desks. A wide first half-hour means
the open did not find balance: inventory was transferred at a range of prices, dealers are carrying
imbalanced books into the quietest part of the day, and their hedging (and the momentum funds that
key off the opening range) keeps repricing through midday instead of resting. Participant:
market-maker inventory management. Named, observable only through this proxy.

## 3. Why this is not the overfitting trap
One state (already frozen in market_state_primitives), one tercile cut fixed on Discovery, one
outcome window pre-declared (midday), one direction of effect (larger). The Idea Factory's other
windows for this state (morning, afternoon, last hour) are NOT part of this claim; reported only.

## 4. Testable predictions
P1 (GATING). HIGH-tercile opening range → midday range ratio (midday range / trailing-20d mean
   midday range) credibly ABOVE the LOW-tercile ratio; block CI on the HIGH−LOW difference > 0.
P2 (reported). HIGH-tercile → larger midday MFE and MAE from the midday open (both signs) — the
   excursion claim, which is what an exit rule would use.
P3 (reported). The effect survives residualizing on prior-day range tercile (F-048): the opening
   range is not merely yesterday's volatility restated. ≥50% retained.

## 5. What would falsify this
(a) P1 fails → closes; the queue footprint was a Discovery-slice artefact or already captured by
    F-048. (b) P1 passes, P3 fails → duplicate of F-048; closes as duplicate (closure form status
    "duplicate"). (c) Thin-sample: not a concern (~560 days per tercile).

## 6. Information gain and edge potential
Gain: HIGH — a fifth candidate input to the Risk/State Engine that is known at 10:00 ET, i.e. an
INTRADAY update between the pre-open number and the 14:00 afternoon update. Edge: sizing/stop
distance for anything entered after 10:00, including the B3 placeholder entry, whose breakout window
starts exactly then. This is the first queue family that plugs directly into the bot.

## 7. Resurrection ruling
NEW. Not exp-028/031 (direction after the initial balance; closed). Not F-048 (prior-DAY range; P3
tests the distinction). Not M9. Attempt 1 of 2.

## 8. Instrument-choice gate
NQ only; 10:00 ET state; same-session outcome from 11:30; magnitude not direction; NULL = unconditional
midday range ratio. TWO NULLS rule not triggered (no directional or cross-index claim).

## 9. Frozen scope
ONE scan, Discovery slice, daily aggregation (scan_027/030 pattern). Cells: (1) HIGH−LOW midday range
ratio difference, block CI  <== GATING P1; (2) HIGH−LOW midday MFE difference (P2); (3) HIGH−LOW midday
MAE difference (P2); (4) P1 residualized on F-048 tercile (P3); (5) unconditional midday ratio
reference; (6) alignment/coverage disclosure. Block=10, N_BOOT=3000, SEED=20260913, 90% CI.
One shot. No new cells, no retuning after seeing results.

## 10. Prediction status
DRAWN and SCANNED 2026-09-14 (7:00 am CT catch-up cycle), Scan 036, hyp-000162.
- **P1 (GATING): PASS.** HIGH−LOW midday range-ratio difference [masked], CI90
  ([masked], [masked]), [masked]/556. Credibly positive.
- **P2: both positive.** MFE difference [masked] ATR, [masked], [masked]);
  MAE difference [masked] ATR, [masked], [masked]). Larger excursions in
  both directions, as predicted.
- **P3: PASS.** Stratified on the prior-day range tercile (F-048): [masked] vs
  the raw [masked], **[masked] retained** against a 50% bar. Not a restatement of
  F-048.
- Status: **PROMISING**, Statistical (+POWER) owed, then the BLIND Integrity Gate.

**BLOCKING FINDING FOR THE GATE (U6 mechanical suite, 4 green / 1 RED / 2 not
run — research/integrity/mechanical-scan036-2026-09-14.json).** The PLACEBO
check is red: the shifted-signal (t+1) placebo reaches [masked] against the real
[masked] — **74% of the effect**. Yesterday's opening range predicts today's
midday range nearly as well as today's own does, so the claim's specificity to
the same session is in question; this may be a multi-day volatility-regime
effect rather than an opening-range effect. **P3 does not cover this**: it
residualized on prior-day RANGE (`range_vs_atr`), which is a different variable
from prior-day OPENING range. Disclosed: the shifted leg's overlap with the real
selection is [masked], just under the 50% guard above which that leg stops gating
— roughly 1.5 points from not being raised at all, so the Gate should weigh it
as a near-boundary verdict. The inverted placebo behaves correctly (−[masked],
opposite sign). Per the U6 spec a RED is a blocking finding, **not** an
automatic close, and nothing here is retuned in response to it.


## Test / scan code (as-is; contains no results)

```python
"""
market_behavior_discovery_scan_036.py
========================================

Scan 036. Draws Entry 34 (map anchor M30): opening-range width -> midday range
and excursion, NQ. Mechanism doc written BEFORE this scan:
research/mechanisms/opening-range-width-midday-excursion-nq-m30.md

WHY THIS ENTRY AND NOT THE OLDEST DRAWABLE (Entry 32/M28): SHELF RULE v2's draw
order is the ranking rule (information gain x edge potential), not age. Stack A
(hyp-000161, a POWERED NULL) established that the Risk/State Engine is a
SIZING and PERMISSION layer, not an entry filter -- so what B2 needs is better
SIZING material. M30 is the only drawable entry that produces exactly that: a
state known at 10:00 ET (an INTRADAY update, between B2's pre-open number and
its 14:00 afternoon update) conditioning a SIZE outcome. Its own doc section 6
says it plainly: "the first queue family that plugs directly into the bot."
Entry 32 (M28, pre-holiday effect) is a calendar effect with no such path.

Frozen scope (doc section 9), Discovery only (2015-01 -> 2021-10-03), daily
aggregation, scan_027/030 pattern. SIX pre-registered cells, 1 gating:
  1. HIGH-LOW midday range-ratio difference, block CI          <== GATING (P1)
  2. HIGH-LOW midday MFE difference, ATR14 units                   (P2, reported)
  3. HIGH-LOW midday MAE difference, ATR14 units                   (P2, reported)
  4. P1 residualized on the prior-day range tercile (F-048):
     stratified HIGH-LOW difference, and the share of cell 1 retained (P3)
  5. unconditional midday range-ratio reference                    (NULL ref)
  6. alignment / coverage disclosure                               (n, skips)

DEFINITIONS, fixed here before any result is seen:
  opening_range_vs_atr  taken from market_state_primitives' frozen state frame
                        (the doc names that variable; re-deriving it here would
                        be a spec deviation). Terciles cut on the Discovery
                        slice, HIGH = top third, LOW = bottom third.
  midday                11:30-13:30 ET, inclusive="left".
  midday range ratio    midday range / trailing-20d mean midday range, the
                        trailing mean SHIFTED BY 1 session (no lookahead).
  midday MFE / MAE      (high - midday open) and (midday open - low), each in
                        ATR14 units -- the same normalisation the Idea Factory
                        footprint that sourced this claim used.
  F-048 stratum         prior-day range tercile (`range_vs_atr`), the validated
                        prior-day-range fact P3 has to survive.

Block bootstrap (block=10) is the CI of record. One shot. No new cells, no
retuning after seeing results.

HOW TO RUN:
    python3 src/market_behavior_discovery_scan_036.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402
from market_state_primitives import build_state_frame  # noqa: E402
from market_state_primitives_v2 import extend_state_frame  # noqa: E402

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BLOCK = 10
N_BOOT = 3000
SEED = 20260913
RANGE_LOOKBACK = 20
SCAN_KEY = "scan_036_2026-09-14"


def _block_boot_means(x: np.ndarray, rng) -> np.ndarray:
    """Moving-block bootstrap of the mean; same construction as
    baseline_relative._block_means, kept local so this scan's CI of record
    cannot drift if that helper is ever changed."""
    n = len(x)
    if n <= BLOCK:
        return rng.choice(x, size=(N_BOOT, n), replace=True).mean(axis=1)
    n_blocks = int(np.ceil(n / BLOCK))
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, n_blocks))
    idx = (starts[:, :, None] + np.arange(BLOCK)[None, None, :]).reshape(N_BOOT, -1)[:, :n]
    return x[idx].mean(axis=1)


def diff_ci(high: np.ndarray, low: np.ndarray, alpha: float = 0.10):
    """90% block-bootstrap CI on mean(HIGH) - mean(LOW). Both arms are daily,
    sequential, and autocorrelated, so BOTH are block-bootstrapped (unlike
    scan_034's block-vs-iid, where the second arm was a pooled hour sample)."""
    high = high[~np.isnan(high)]
    low = low[~np.isnan(low)]
    if len(high) < BLOCK * 3 or len(low) < BLOCK * 3:
        return float("nan"), [float("nan"), float("nan")]
    rng = np.random.default_rng(SEED)
    d = float(high.mean() - low.mean())
    boots = _block_boot_means(high, rng) - _block_boot_means(low, rng)
    return d, [float(np.percentile(boots, 100 * alpha / 2)),
               float(np.percentile(boots, 100 * (1 - alpha / 2)))]


def _cell(label: str, high: np.ndarray, low: np.ndarray) -> dict:
    d, ci = diff_ci(high, low)
    cred = (not np.isnan(ci[0])) and ((ci[0] > 0) or (ci[1] < 0))
    return {"cell": label, "n_high": int(len(high[~np.isnan(high)])), "n_low": int(len(low[~np.isnan(low)])),
            "high_mean": float(np.nanmean(high)) if len(high) else float("nan"),
            "low_mean": float(np.nanmean(low)) if len(low) else float("nan"),
            "diff": d, "ci_90": ci, "credible": bool(cred),
            "direction": "positive" if cred and ci[0] > 0 else ("negative" if cred else "null")}


def main():
    print("=" * 78)
    print("MARKET BEHAVIOR DISCOVERY ENGINE -- Scan 036 (Entry 34 / map M30:")
    print("opening-range width -> midday range and excursion, NQ)")
    print("=" * 78)

    df, synthetic = load_price_data(context="market_behavior_discovery_scan_036.py")
    if synthetic:
        print("ABORT: synthetic data."); return
    disc = get_discovery_data(df)

    states = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(states.index))
    for col in ("opening_range_vs_atr", "range_vs_atr", "atr14"):
        if col not in states.columns:
            print(f"ABORT: state frame has no `{col}`."); return
    opening = pd.Series(states["opening_range_vs_atr"].to_numpy(dtype=float), index=idx)
    prior_rng = pd.Series(states["range_vs_atr"].to_numpy(dtype=float), index=idx)
    atr = pd.Series(states["atr14"].to_numpy(dtype=float), index=idx)

    # ---- midday outcomes, one row per session -----------------------------
    rows, skipped = [], 0
    for day, g in disc.groupby(disc.index.date):
        ts = pd.Timestamp(day)
        mid = g.between_time("11:30", "13:30", inclusive="left")
        if len(mid) < 60:
            skipped += 1
            continue
        o = float(mid["Open"].iloc[0])
        hi, lo = float(mid["High"].max()), float(mid["Low"].min())
        rows.append({"date": ts, "midday_range": hi - lo, "mfe": hi - o, "mae": o - lo})
    daily = pd.DataFrame(rows).set_index("date").sort_index()
    daily["trailing_midday"] = daily["midday_range"].rolling(
        RANGE_LOOKBACK, min_periods=RANGE_LOOKBACK).mean().shift(1)
    daily["ratio"] = daily["midday_range"] / daily["trailing_midday"]
    daily["atr14"] = atr.reindex(daily.index)
    daily["mfe_atr"] = daily["mfe"] / daily["atr14"]
    daily["mae_atr"] = daily["mae"] / daily["atr14"]
    daily["opening"] = opening.reindex(daily.index)
    daily["prior_rng"] = prior_rng.reindex(daily.index)

    usable = daily.dropna(subset=["ratio", "opening", "mfe_atr", "mae_atr"])
    lo_edge, hi_edge = np.nanpercentile(usable["opening"], [100 / 3, 200 / 3])
    usable = usable.assign(
        grp=np.where(usable["opening"] <= lo_edge, "LOW",
                     np.where(usable["opening"] >= hi_edge, "HIGH", "MID")))
    H = usable[usable["grp"] == "HIGH"]
    L = usable[usable["grp"] == "LOW"]
    print(f"\nDiscovery sessions with a usable midday window: {len(daily)} (skipped {skipped});")
    print(f"with all state + trailing inputs present: {len(usable)}  -> HIGH {len(H)}, LOW {len(L)}")
    print(f"opening_range_vs_atr tercile edges (Discovery): LOW <= {lo_edge:.4f}, HIGH >= {hi_edge:.4f}")

    # ---- cells 1-3 --------------------------------------------------------
    c1 = _cell("1_midday_range_ratio_HIGH_minus_LOW_GATING", H["ratio"].to_numpy(), L["ratio"].to_numpy())
    c2 = _cell("2_midday_mfe_atr_HIGH_minus_LOW", H["mfe_atr"].to_numpy(), L["mfe_atr"].to_numpy())
    c3 = _cell("3_midday_mae_atr_HIGH_minus_LOW", H["mae_atr"].to_numpy(), L["mae_atr"].to_numpy())

    # ---- cell 4: residualized on the prior-day range tercile (F-048) ------
    pr = usable["prior_rng"].dropna()
    p_lo, p_hi = np.nanpercentile(pr, [100 / 3, 200 / 3])
    strata, weights, parts = [], [], []
    for name, sel in (("prior_LOW", usable["prior_rng"] <= p_lo),
                      ("prior_MID", (usable["prior_rng"] > p_lo) & (usable["prior_rng"] < p_hi)),
                      ("prior_HIGH", usable["prior_rng"] >= p_hi)):
        sub = usable[sel]
        h = sub[sub["grp"] == "HIGH"]["ratio"].to_numpy()
        l = sub[sub["grp"] == "LOW"]["ratio"].to_numpy()
        h, l = h[~np.isnan(h)], l[~np.isnan(l)]
        if len(h) < BLOCK * 3 or len(l) < BLOCK * 3:
            strata.append({"stratum": name, "n_high": int(len(h)), "n_low": int(len(l)),
                           "diff": None, "note": "below the block floor, excluded from the weighted average"})
            continue
        d = float(h.mean() - l.mean())
        w = len(h) + len(l)
        strata.append({"stratum": name, "n_high": int(len(h)), "n_low": int(len(l)), "diff": round(d, 6)})
        weights.append(w); parts.append(d)
    strat_diff = float(np.average(parts, weights=weights)) if parts else float("nan")
    retained = (strat_diff / c1["diff"]) if c1["diff"] not in (0, None) and np.isfinite(c1["diff"]) else float("nan")
    c4 = {"cell": "4_P1_residualized_on_prior_day_range_tercile_F048",
          "strata": strata, "stratified_diff": strat_diff,
          "raw_diff_cell1": c1["diff"], "share_retained": retained,
          "p3_bar": 0.50, "p3_passes": bool(np.isfinite(retained) and retained >= 0.50),
          "note": "P3: >=50% of cell 1's difference must survive stratification on the prior-day "
                  "range tercile, or the claim is a restatement of F-048 and closes as a duplicate."}

    # ---- cells 5-6 --------------------------------------------------------
    c5 = {"cell": "5_unconditional_midday_ratio_reference",
          "n": int(usable["ratio"].notna().sum()),
          "mean": float(usable["ratio"].mean()),
          "note": "the NULL: a ratio of 1.0 means a session's midday range matches its own "
                  "trailing-20d midday average. The claim is about HIGH vs LOW, not vs 1.0."}
    c6 = {"cell": "6_alignment_and_coverage",
          "sessions_in_discovery": int(len(set(disc.index.date))),
          "sessions_with_midday_window": int(len(daily)), "sessions_skipped_short_midday": int(skipped),
          "sessions_usable_after_state_and_trailing": int(len(usable)),
          "n_high": int(len(H)), "n_low": int(len(L)), "n_mid": int((usable["grp"] == "MID").sum()),
          "tercile_edges": {"low_max": float(lo_edge), "high_min": float(hi_edge)},
          "prior_day_tercile_edges": {"low_max": float(p_lo), "high_min": float(p_hi)}}

    p1_pass = bool(c1["credible"] and c1["ci_90"][0] > 0)
    result = {"scan": SCAN_KEY, "entry": 34, "map_anchor": "M30",
              "mechanism_doc": "research/mechanisms/opening-range-width-midday-excursion-nq-m30.md",
              "slice": "discovery", "block": BLOCK, "n_boot": N_BOOT, "seed": SEED,
              "cells": [c1, c2, c3, c4, c5, c6],
              "p1_gating_passes": p1_pass,
              "p3_passes": c4["p3_passes"],
              "verdict": ("P1 PASS + P3 PASS" if p1_pass and c4["p3_passes"] else
                          "P1 PASS, P3 FAIL -> duplicate of F-048" if p1_pass else
                          "P1 FAIL -> closes"),
              "rule": "One shot, frozen scope (doc section 9). Six cells, one gating. No new cells "
                      "and no retuning after seeing results."}

    out = DATA_DIR / f"{SCAN_KEY}_results.json"
    out.write_text(json.dumps(result, indent=2, default=str))

    print("\n--- CELLS -------------------------------------------------------")
    for c in (c1, c2, c3):
        print(f"{c['cell']}")
        print(f"    HIGH {c['high_mean']:+.4f} (n={c['n_high']})  LOW {c['low_mean']:+.4f} (n={c['n_low']})")
        print(f"    diff {c['diff']:+.4f}  ci_90 ({c['ci_90'][0]:+.4f},{c['ci_90'][1]:+.4f})  -> {c['direction']}")
    print(f"{c4['cell']}")
    for s in c4["strata"]:
        print(f"    {s['stratum']:11s} n_high={s['n_high']:4d} n_low={s['n_low']:4d} "
              f"diff={s['diff'] if s['diff'] is not None else 'excluded'}")
    print(f"    stratified diff {strat_diff:+.4f} vs raw {c1['diff']:+.4f} -> "
          f"{retained:.1%} retained (P3 bar 50%) -> {'PASS' if c4['p3_passes'] else 'FAIL'}")
    print(f"{c5['cell']}: mean {c5['mean']:.4f} (n={c5['n']})")
    print(f"\nP1 (GATING): {'PASS' if p1_pass else 'FAIL'}    VERDICT: {result['verdict']}")
    print(f"\nwritten -> {out}")


if __name__ == "__main__":
    main()

```

## Ledger history for this family (results masked)

```json
[
 {
  "hypothesis_id": "hyp-000162",
  "logged_at": "2026-09-14T12:37:02.280390",
  "strategy_name": "opening_range_width_midday_range_excursion_nq_m30",
  "strategy_origin": "data_discovered",
  "parameters": "{\"map_anchor\": \"M30\", \"shelf_entry\": 34, \"scan\": \"scan_036_2026-09-14\", \"mechanism_doc\": \"research/mechanisms/opening-range-width-midday-excursion-nq-m30.md\", \"state\": \"opening_range_vs_atr (known 10:00 ET), Discovery terciles LOW<=[masked] HIGH>=[masked]\", \"outcome\": \"midday (11:30-13:30 ET) range / trailing-20d mean midday range, shifted 1\", \"gating_P1\": \"HIGH-LOW midday range-ratio difference credibly > 0\", \"P1_result\": \"diff [masked], [masked],[masked]), [masked]/556 -- PASS\", \"P2_mfe\": \"[masked] ATR, [masked],[masked]) -- positive\", \"P2_mae\": \"[masked] ATR, [masked],[masked]) -- positive\", \"P3_residualized_on_F048_prior_day_range_tercile\": \"[masked] retained (bar 50%) -- PASS\", \"unconditional_midday_ratio\": [masked], \"block\": 10, \"n_boot\": 3000, \"seed\": 20260913, \"ci\": 90}",
  "data_slice_used": "discovery",
  "parent_hypothesis_id": null,
  "experiment_doc_id": null,
  "holdout_slot_id": null,
  "search_batch_id": null,
  "trade_count": "[masked]",
  "expectancy_r": "[masked]",
  "profit_factor": "[masked]",
  "max_drawdown_r": "[masked]",
  "strategy_status": "[masked]",
  "notes": "[masked]"
 }
]
```

## Additional procedural disclosures (figures masked), added by the cycle

1. **A mechanical integrity suite (src/integrity_checks.py, 7 checks) was run on
   this scan.** Result: 4 green, 1 RED, 2 not run. The RED is the SHIFTED-SIGNAL
   PLACEBO: the same test re-run using the PREVIOUS session's value of the
   conditioning variable reproduces most of the effect. Procedure of that check:
   the placebo leg re-selects sessions using the t-1 value at the same frozen
   tercile edges, and the check reports the overlap between the placebo leg's
   selected sessions and the real leg's. Disclosed: that overlap is just under
   the suite's own 50% guard, above which the placebo leg stops gating — i.e.
   the red sits near the guard boundary. An INVERTED placebo (sign flipped)
   behaves correctly. Per the suite's spec a RED is a blocking finding for you,
   not an automatic close.
2. **A separability stage has since run** holding four already-validated
   volatility variables fixed one at a time — including the t-1 value of the
   conditioning variable itself — and reports the share of the effect retained
   against a 50% bar. Figures masked. Procedure: strata cut at the candidate's
   own FROZEN Discovery edges, not recut per stratum.
3. **The conditioning variable is known at 10:00 ET; the outcome window opens at
   11:30 ET** (90-minute separation). Trailing normaliser is shifted one session.
4. **Multiplicity:** this scan was drawn from a shelf entry sourced from a
   descriptive Idea Factory sweep. The look-cell count of that sweep is recorded
   in research/observatory/idea-factory-2026-09-13.md. Discovery-stage Sidak N
   for this project is 467 and was applied at the Statistical stage.
5. **The monetization stage rules the claim usable only as a SIZING input**
   (a range forecast has no sign); no directional claim is attached.

**The specific question you are asked to rule on, beyond the general brief:**
does the near-boundary placebo red, taken together with the procedure in (2),
indicate that the PROCEDURE cannot distinguish a same-session opening-range
effect from a multi-day volatility-regime effect — and if so, is that a VETO, a
CONDITIONAL (name the condition), or a PASS with a disclosure?

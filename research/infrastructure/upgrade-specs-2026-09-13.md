# Upgrade specs — U6, U7, U8, U13 (written September 13th, ~5:18 pm CT; freeze lifted, build continuously)

These are the pre-registered specs for the structural items from the six-review
synthesis. Each is a build target for the cycles, in the order listed in NEXT_UP.md
UPGRADE QUEUE v3. Nothing here changes a gate or a bar; U6 and U7 ADD checks.

## U6 — Integrity Gate: structural blindness + mechanical suite

**Blind packet (tighten `src/integrity_blind_packet.py`).** The Gate receives ONLY:
frozen candidate spec (entry/condition/outcome/horizon as registered), raw cell
outputs (n, mean, CI, per-cell), the ledger rows for the family, the benchmark
results (unconditional drift / range reference), and the predefined audit rules. The
Gate does NOT receive: the mechanism doc's narrative sections (§1–§3, §6), the
Discovery report prose, the expected result, or the Director's recommendation.
Implementation: the packet builder strips those sections by header; a test asserts
the packet contains no line from §1–§3/§6 of the mechanism doc.

**Mechanical suite (`src/integrity_checks.py`, ops_checks-style, runs on every
candidate before the Gate, green/red, no judgment):**
1. drift_null — effect re-measured against the instrument's own unconditional
   drift over the same horizon (not zero); red if the sign flips.
2. overnight_intraday_split — effect decomposed into overnight vs RTH legs; red if
   >80% of a "session" effect lives in the overnight leg (or vice versa) and the
   claim did not say so.
3. cost_sensitivity — per-trade effects re-run at COST_STRESS_MULTIPLIER 2.0; red if
   the CI crosses zero under 2x costs.
4. roll_date_contamination — share of observations on CME quarterly roll days /
   missing-RTH days (the M9 defect); red if >5% or if excluding them flips the verdict.
5. subperiod_stability — chronological halves; red if only one half is credible
   AND the halves differ in sign.
6. concentration — share of total effect from the top 5% of observations; red if >50%.
7. placebo (from U7) — shifted-signal (t+1) and inverted-signal versions; red if
   either produces a comparable |effect|.
Output: a JSON block appended to the scan result and a one-line row in the session
report. Any red is a blocking finding for the Gate, not an automatic close.

## U7 — Economic Validity checklist (before Statistical)

Added to the mechanism-doc template as a required Section 8b, and to the scan
result JSON as fields:
- correct_null: which of {zero, unconditional drift, unconditional range ratio,
  matched time-of-day, matched vol state, long/short benchmark} — and why.
- effect_type: directional | relative | conditional | risk-state.
- measurement: which of {raw points, ATR-normalized, R-multiple, vol-adjusted,
  benchmark-relative} and why that one.
- concentration: by year / regime / time-of-day / event / few observations —
  reported, not gated (the mechanical suite gates).
- placebo: shifted / inverted / random-entry — run by the mechanical suite.
- alternative_explanations: trend, volatility, seasonality, drift, liquidity, beta —
  each answered in one line ("ruled out by X" or "not ruled out").
Already in place since the baseline fix: correct null + vol normalization. New:
placebo, concentration, alternative-explanation list.

## U8 — Closure form (every closed hypothesis, retroactive to this week's eleven)

```
Hypothesis ID / family / map anchor:
Closure status: clean null | near miss | data limitation | execution limitation |
                valid-but-non-actionable | invalid premise | duplicate
Primary outcome (as registered) and result:
Sample adequacy (n vs thin-sample threshold):
Closure status: clean null | near miss | data limitation | execution limitation |
  valid-but-non-actionable | invalid premise | duplicate | UNDERPOWERED
  (UNDERPOWERED, added 2026-09-13: the frozen definition yielded fewer occurrences
   than the pre-registered floor. Distinct from `data limitation`, which is about the
   data not existing; underpowered is the format's own failure mode, the definition is
   never loosened to fix it, and it CONSUMES one of the candidate's two attempts.)
Mechanism verdict: falsified | weakened | untested-by-this-result
Robustness / cost / concentration flags:
Data-quality checks passed:
What was learned (one sentence a future sourcing pass can search for):
What must NOT be retested:
Permitted future retest condition (one, or "none"):
Related facts / strategies:
Capacity action: reduce family | hold | increase
```
Location: appended as Section 12 of the mechanism doc at closure, and mirrored as
one line in research/ledger/closures.jsonl (new, append-only). Retroactive pass
owed for: M13, M14, M17, M18, M19, M20, M21, M22, M23(open), M24, M25, M26.

## U13 — Risk/State Engine (the first thing that gets paper-traded; no directional trigger)

**Inputs (all validated, all on disk daily):** prior-day range tercile (hyp-048),
overnight-coil flag (hyp-057), midday-lull → afternoon persistence (hyp-105/141),
VXN level vs trailing (hyp-142/151), and — only if it clears Stage 1 — the
implied-minus-realized gap (M29). Combination by RESIDUAL, not product, per the
hyp-142 Portfolio review (53–66% retained after the other facts).
**Outputs, per session, computed at the prior close and frozen for the day:**
- expected_range_atr: point forecast of the session's RTH range in ATR14 units;
- within_session_shape: expected share of range in first30 / morning / midday /
  afternoon / last hour (from the free-look table, refit only on Discovery);
- stop_distance_atr and target_distance_atr: fractions of expected range
  (default 0.5x / 1.0x, frozen before any paper trade);
- size_multiplier: `position_size_multiplier(expected_range_multiplier)` from
  src/volatility_conditioning.py, unchanged;
- trade_permission: FALSE when expected_range_atr is in the bottom decile, on
  scheduled-event days (NYSE holiday-adjacent + FOMC/CPI/NFP), or when data is stale.
**What it is NOT:** a strategy. It has no entry. It is paper-traded by attaching it to
a dummy signal (U14) purely to measure fills, slippage, latency, and whether the
engine's daily numbers can be produced and acted on in real time.
**Build:** `src/risk_state_engine.py` (pure function of the state frame → a daily
JSON), `tests/test_risk_state_engine.py`, and a daily checker that writes
research/forward_validation/risk_state_engine_log.jsonl. No P&L claim, ever, from
this module alone.

## U16 — Fact registry (seed)

`research/registry/facts.md` — one row per validated fact: ID, definition, instrument,
horizon, mechanism, stage reached, stability note, review date, related facts,
strategies using it. Seeded today with hyp-048, hyp-057, hyp-105/141, hyp-142/151,
M20, M21, M23 (Discovery-pass, Statistical owed), M29 (Stage 0 only).

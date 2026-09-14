# Blind Integrity Gate — hyp-000156 (M23 London-open volatility, 6E) — September 13th, 7:00 pm CT test cycle

Reviewer: fresh subagent, masked packet (research/integrity/packet-hyp156-2026-09-13.md), no access to results. Verbatim report follows; disposition at the end.

**1. Chronological leakage — OK.** Only Discovery data exists on disk; spec frozen before any Validation bars. Residual, unavoidable: the London-open effect is a public stylised fact through 2024, so "novelty" is nil, but that is not leakage.

**2. Selection after seeing results — CONCERN.** Window and ATR14 are literature/template-anchored and the mechanism doc predates Scan 030. But (a) the doc's §4 null is "every hourly window across the full 24-hour session" while the code and spec use six US-RTH bins (09:30–16:00) — the null changed between pre-registration and scan, undocumented; (b) the ledger records `strategy_origin: data_discovered`, contradicting "map channel, pre-registered"; (c) the Statistical stage (incl. Q4 alternate windows) is absent from the packet, so I cannot confirm nothing moved. Q4 is not itself a Validation risk provided the 03:00–04:00 window is unchanged — it is, per spec vs scan parameters.

**3. Multiple testing — CONCERN.** Šidák at "then-current N_validation (20 today)" is floating, not frozen; write it as `max(20, N at run)`. Discovery-level exposure (Scan 030 = ~27 map entries; third draw from the M20/M21/M23 family) is not carried at all. At N=20 the adjusted tail is ≈0.26% — 8 of 3,000 bootstrap draws; N_BOOT must rise (≥20,000) for that CI to be meaningful.

**4. Resurrection — OK (with note).** Different clock time and forcing than M20/M21; not the overnight-coil claim. It is, however, the third "volatility magnitude vs unconditional" template drawn the day after the project declined a third clone — same family, same monetization dead-end (deferred to a future entry).

**5. Construction — CONCERN.** Unconditional pool excludes the London hour (no dilution); ATR14 is prior-day-shifted (no overlap). But: the spec describes a **per-day paired diff** while Scan 030 computes an **unpaired** difference of pooled means with iid resampling of the RTH pool — these are different tests. US-RTH is a defensible (conservative, high-vol) baseline for a 24h FX future but is mislabeled "unconditional". DST: for ~3 weeks/year London opens 04:00 ET, so the window misses the open and the "pre-London" cell contains it. Timestamp zone of the data is stated only as "local"; if the index is CT, every window is off by an hour.

**6. Frozen-ness — BLOCKING (curable).** The Validation script does not exist ("to be written"), cannot be "Scan 030 with loader swapped" because Scan 030 computes neither the paired diff nor a Šidák CI, and ATR warm-up (first 14 Validation days vs Discovery tail), data provenance/roll rule, and timezone handling are unspecified.

**7. Kill check — CONCERN.** Mean|first-minute|/mean|hour| catches a one-print spike but not a spike-and-reverse, and 03:00 ET is not a CME session boundary, so stale-quote is the wrong artifact model. Add: minute-bar density in the window, first-5-minute share of realized variance, and DST-aware window.

**8. Other — CONCERN.** Power quotes the Discovery (winner's-curse) effect. Paying for data to validate a characterization with no product path in this entry is a resource question the Director should answer explicitly.

## Overall verdict: CONDITIONAL
Resolve in writing, before the data pull lands:
1. Reconcile paired vs unpaired construction and the 24h-vs-RTH null; state one test.
2. Write, freeze and hash the Validation script (incl. Šidák CI, N_BOOT ≥ 20,000, `max(20,N)` rule) before data exists.
3. Pin timezone, DST handling, ATR warm-up, vendor/roll parity with Discovery data.
4. Correct or explain `strategy_origin: data_discovered`; attach the masked Statistical-stage output to the packet.
5. Add the density/first-5-minute kill checks as pre-registered, non-gating diagnostics.

## Disposition (Operations, same cycle)
Accepted in full. Two of the five are already answerable: the data index is America/New_York (`timestamp_ny` column, verified), so condition 3's timezone half is closed; condition 4's origin field is a ledger convention (`data_discovered` = surfaced by a scan) and will be explained in the packet, not changed. Conditions 1, 2, 3 (DST/ATR warm-up/provenance) and 5 are real writing work and go to the next cycle as the FIRST research item, ahead of any new sourcing — the Gate found that the Statistical stage and the scan used different constructions (paired per-day vs unpaired pooled), which is exactly the kind of drift it exists to catch. The data pull request to Jason waits until the conditions are resolved, so his money is not asked for before the test is fully frozen. Status: PROMISING with one-shot Validation owed (an earlier note this cycle mislabelled it VALIDATION CANDIDATE, which in this ledger means post-Validation; corrected the same cycle). Ledger note appended.

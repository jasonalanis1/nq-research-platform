# Legacy Leads Classification (CONTINUE / ABANDON / MODIFY)

Required by research/studies/two-layer-methodology.md, per Jason's
2026-09-09 instruction, before any further work touches the four
previously-flagged "unresolved" leads (hyp-000023, hyp-000025,
hyp-000027, hyp-000031).

## Finding that changed the classification question

Before classifying, each lead's actual ledger history was checked (not
just its own top-level status). All four are still logged with a
top-level status of PROMISING -- but all four already have a child
hypothesis in the ledger that ran their one pre-registered prospective
test on the Validation slice, and all four of those tests came back
non-clearing:

| Lead | Top-level status (stale) | Prospective test | Result |
|---|---|---|---|
| hyp-000023 (weekly trend, low-vol split) | PROMISING | hyp-000024 (exp-054) | INCONCLUSIVE / underpowered (n=8) |
| hyp-000025 (collective evidence, trend family) | PROMISING | hyp-000026 (exp-056) | REJECTED, CI crosses zero |
| hyp-000027 (collective evidence, intraday) | PROMISING | hyp-000028 (exp-058) | REJECTED, CI crosses zero |
| hyp-000031 (ZN bond lead, standalone) | PROMISING | hyp-000035 (exp-062), hyp-000034 (exp-065, alt framing) | Both REJECTED |

This is the same class of ledger-hygiene gap found and fixed earlier in
this project's history for hyp-063/079/044/050/052 -- a hypothesis's own
later, definitive result was never propagated back to correct its
top-level status. Corrective entries have been appended to
research/ledger/hypotheses.jsonl (hyp-000097 through hyp-000100),
each marked REJECTED with the actual reason.

## Classification

**hyp-000023 (nq_weekly_trend_volatility_regime_split_exploratory) -- ABANDON.**
Already received its one pre-registered prospective test (hyp-000024)
and did not clear it (inconclusive/underpowered). Per the no-retuning-
after-a-null-result commitment, continuing this specific line would
violate the project's own discipline. If the underlying question
(does trend-following differ in low-vol regimes) still seems worth
asking, it re-enters as a brand-new Layer-1 Observatory candidate with
its own Behavioral Finding -- not a resumption of this thread.

**hyp-000025 (collective_evidence_pilot_trend_family) -- ABANDON.**
Already received its one pre-registered prospective test (hyp-000026)
and failed it cleanly (CI crosses zero). Also a legacy strategy-first-
flavored derivative test (post-hoc filter search on an existing signal)
that predates the current behavior-first default -- doubly appropriate
to abandon rather than modify. The collective-evidence aggregation
machinery itself (week-level dedup, multiple-comparisons accounting)
worked correctly and is a reusable capability for future work; the
specific candidate finding from this pilot is closed.

**hyp-000027 (intraday_collective_evidence_pilot) -- ABANDON.**
Same reasoning as hyp-000025: already prospectively tested (hyp-000028)
and failed cleanly. Aggregation machinery validated as reusable;
specific finding closed.

**hyp-000031 (zn_bond_lead_standalone_signal) -- ABANDON.**
Already prospectively tested (hyp-000035) and failed cleanly, with a
second independent framing (hyp-000034, multi-day cumulative) also
failing. The most conclusively closed of the four. Per the 2026-09-07
Advisor consult already on record, the free/owned cross-market data
well (ZN, 6E, CL, same-day and multi-day framings) is exhausted for
standalone signals -- a genuinely new cross-market candidate would need
new data, and should in any case now originate as a Layer-1 Observatory
candidate rather than a hand-picked instrument test.

## Net effect

All four legacy leads classified ABANDON. None require further work
under the current no-retuning discipline. This closes out the "four
unresolved leads" thread entirely -- it was resolved earlier than
realized; the gap was in the ledger's top-level status bookkeeping, not
in unfinished research. No MODIFY or CONTINUE candidates in this batch.

Per the now-canonical methodology, future research generation defaults
to Layer 1 (Observatory) rather than resuming or reframing legacy
strategy-first threads.

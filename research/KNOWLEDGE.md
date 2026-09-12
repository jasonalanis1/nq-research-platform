# KNOWLEDGE — what Tony knows, what it has learned, what is open
Maintained by every cycle at close (LEARN update step). One page a future reader can start from. First version September 12th, 2026, ~10:50 am CT. Older detail lives in research/studies/, research/mechanisms/, research/sessions/, the ledger, and git history — nothing is deleted, this is the index.

## 1. What is TRUE (validated, kept)
Three volatility-persistence facts, each passed a pre-registered out-of-sample test. None is a directional edge; all are STATE variables and belong to the risk/execution product track.
- Range contraction/expansion cycle (hyp-046/048): unusually narrow days are followed by relatively narrow days; wide by wide.
- Overnight coil (hyp-056/057): an overnight range in the bottom 20% of its own trailing distribution predicts a compressed regular session.
- Midday-lull persistence (hyp-105/106/141, HOLDOUT PASSED): a quiet 12:00-13:00 predicts a quieter afternoon, ratio ~0.74. Cleanest result in the project. 82.5% separable from the overnight coil.
Integrated in src/volatility_conditioning.py as sizing/context tools. OPEN QUESTION (largest loose end): these have never been turned into a product — a volatility-conditioned sizing overlay on a simple base strategy.

## 2. What FAILED, and why (the failure-mode taxonomy, with examples)
137 distinct hypotheses logged; 0 have ever cleared a correctly-specified promotion bar.
1. Cost-dominance — real gross effect, wiped by round-trip costs (many intraday fades).
2. Thin-sample overconfidence — credible CI on too few events (calendar studies at n=50-80: pre-FOMC, post-FOMC, month-end).
3. Correlated-lens double-counting — several "different" signals measuring one latent state (caught repeatedly; hyp-000140 |gap| vs overnight coil).
4. Direction ambiguity in pooled measurements — pooled event reactions with no consistent sign (CPI/NFP).
5. Marginal Discovery passes don't replicate — 0-for-several at Validation (H93, COT positioning, H116, H117).
6. Exit-design mismatch — a real drift effect destroyed by a stop/target that races it (H87/H89, H93, H114/115).
7. Baseline confusion (named September 12th) — a long-only effect measured against ZERO on a trending asset. H118 passed three stages this way; against NQ's own drift it is nothing. The two-nulls rule now prevents it.
Idea-source hit rates for finding SOMETHING real: pattern-guess 0%; intuition ~1 in 8; behavior-first Observatory ~1 in 3; forced-participant map: 11 entries, 0 survivors (9 clean nulls, 1 near-miss, 1 untestable). Literature / practitioner / observatory channels: being measured from September 12th.
Closed families (never resurrect without a genuinely different claim): candlestick/bar patterns; opening-range/IB breakout; VWAP and reference-level fades; gap fades (3 variants); weekly/multi-day trend following (7 variants); VXN level/ROC as direction; ZN lead-lag (daily); turn-of-month; closing-pressure reversal; CPI/NFP reaction; pre-NFP drift; pre-FOMC drift (2 attempts); post-FOMC continuation; month-end NQ-vs-ZN; NQ-ZN correlation breakdown (near-miss); basket correlation convergence (clean null, no gradient); days-to-opex; overnight_range_vs_atr drift; vwap_dist LOW drift (H118, baseline confusion).
Structural conclusion (September 12th, four independent reads agree): scheduled, public flows are the most competed in NQ and nine nulls there is the expected outcome; the participants who leave money on the table (dealers hedging gamma, basis arbs, intraday liquidity takers) are not visible in 1-minute OHLCV. Widening the search without new data produces lottery tickets with nicer stories.

## 3. What is PARKED, and why
- Data ceiling (Jason, September 12th): 1-minute OHLCV for NQ, ZN, 6E, CL; no purchases. Quotes on file: ES $14.69, RTY $10.77, YM $14.31 (src/quote_data_pulls.py runs from Jason's own Terminal; sandboxed shells cannot reach the Databento API).
- Entries parked at the ceiling: M9 Nasdaq rebalance (continuous-contract roll-day gap; outright months would fix it), M13 LETF close rebalance (needs RTY/ES), M14 gamma regime (needs ES), cash-open NQ/ES residual (needs ES + SPY/QQQ), curve rotation (needs ZT).
- VXN -> next-session range (hyp-000142/144): passed Validation, gated at Holdout, HELD by Jason ("wait for a cleaner story"). 3 of 5 Holdout Gen-2 slots remain.
- Execution clock (signal engine, Tradovate/IBKR ~$60-115/mo, pre-approved): PARKED explicitly — it was unblocked for H118 and H118 is gone. Resumes only when a candidate reaches execution qualification.
- Options / tick data: only if a price-only result earns it (M14 was designed as that gate).

## 4. What is OPEN (live work)
- Shelf (SHELF RULE v2): counts DRAWABLE entries only; sourcing every cycle from every channel; below floor = more sourcing, never a draw. Currently 2/3 drawable (Entry 19 M15 overnight-vs-intraday split; Entry 20 M16 intraday momentum), 3 pending at the data ceiling.
- Written and drawable (September 12th, 11 am cycle): M15 overnight-vs-intraday split (Lou/Polk/Skouras 2019) and M16 intraday momentum (Gao et al. 2018), mechanism docs first, one pre-registered scan each. Practitioner stream opened (research/sourcing/practitioner.md; three claims ruled, none entered).
- 3 pm cycle (queue item 4, Observatory): closed the last unchecked pairwise separability gap among the 3 validated volatility facts -- prior-day range regime vs. overnight coil (82.8% retained) and vs. midday-lull (66.1% retained), both SEPARABLE. Started the NQ/ZN/6E/CL information-transmission map (v1, 15-min RTH): no lead-lag structure detected in any pair at this resolution, only contemporaneous co-movement (ZN -0.32, CL +0.16, 6E ~0) -- a third independent lens agreeing with the M11/M12 cross-asset nulls. Next: overnight session, other resolutions, shock-conditioned view; then event reaction shape.
- Forward logs: EXP047 weekly trend (3/260 weeks); H118 forward log for information only.
- CHECKPOINT September 19th (Jason): one page — what survived, what it is worth, one recommendation. If nothing reached Validation, the decision is data vs. product (sizing overlay on a simple base).
- CHANGE FREEZE on structure until September 19th: observations go into the weekly review, not into live fixes.

## 5. How the system works (one paragraph)
Sourcing (map / literature / practitioner / observatory) -> template with instrument-choice gate, kill rule, two nulls, decay, resurrection ruling -> shelf (drawable only) -> mechanism doc BEFORE scan -> one pre-registered Discovery scan (Discovery slice 2015-Oct 2021) -> Statistical (4 questions, Sidak, power) -> blind Integrity Gate -> one-shot Validation (Oct 2021-Jan 2024) -> Monetization -> blind Gate -> Holdout (Jason only, 2024+) -> Portfolio. Two attempts per family. Every scan cell counted project-wide. Cycles every 2 hours: lock, budget clock, sweep, checkers, sourcing, draw if drawable, tests, ops checks, console, report, git push, reschedule. Jason is looped in for: Holdout slots, purchases, a real signal, capital protection, integrity problems with promoted work. Governance docs: research/infrastructure/agent-governance-structure.md (v2 + AMENDMENT v2.5), back-half-production-integrity-v3.md (+ v3.2), research/studies/two-layer-methodology.md (+ two-nulls amendment). NEXT_UP.md is the handoff baton; this file is the memory.

## 6. Decision log (structural changes, dated, with the reason)
- 2026-09-09: Discovery/Validation/Holdout chronological splits; two-attempt limit; LEARN layer; Market Behavior Discovery Engine (state-first) replaces strategy-first search; Research Director + mandatory Integrity Gate. Reason: 120 hypotheses rejected, pipeline was a filter with no generator.
- 2026-09-10: Back-half v3 + v3.1 (forward test != paper trading != live; anti-optimization rule; two clocks); execution infrastructure pre-approved.
- 2026-09-11: Outside review adopted — market structure map, mechanism BEFORE scan, blind gates, power check, 2-hour self-scheduling cycles with lock/budget/checkpoint; console simplified to one state document; UPGRADE brief ($1k/mo goal, $20/mo data, $300 risk budget).
- 2026-09-12 (overnight): map exhausted (M1-M11 closed or parked); M9 untestable on a roll-day data gap; M12 cross-asset clean null; approval-card stall root-caused (a path outside the workspace); create_trigger vs send_later slip fixed.
- 2026-09-12 (11 am cycle): first unattended cycle under SHELF RULE v2 ran as designed -- sourced two literature entries and ruled three practitioner claims instead of drawing thin; shelf 2/3. Open question for the Sept 19 review: is a #1-ranked, on-disk entry drawable below the floor.
- 2026-09-12 (morning): scope opened beyond NQ; three outside AIs polled; sourcing stage + template + ranking by information gain x edge potential; TWO NULLS rule (failure mode #7); H118 baseline diagnostic -> H118 REJECTED; SHELF RULE v2 (drawable-only count, sourcing every cycle, no invented scopes, shelf-starving alert); data decision: no purchase; per-entry scan hold lifted (cycles scan autonomously); CHANGE FREEZE + CHECKPOINT September 19th; weekly review instituted; this file created.

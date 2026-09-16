# KNOWLEDGE — what Tony knows, what it has learned, what is open
Maintained by every cycle at close (LEARN update step). One page a future reader can start from. First version September 12th, 2026, ~10:50 am CT. Older detail lives in research/studies/, research/mechanisms/, research/sessions/, the ledger, and git history — nothing is deleted, this is the index.

## 1. What is TRUE (validated, kept)
Six volatility/magnitude facts characterized (four range-persistence facts out-of-sample confirmed through Validation, three of those all the way through Holdout; two more -- CL's EIA-report-hour volatility and 6E's ECB-decision-hour volatility -- passed Discovery but have no strategy to attach to yet, see below). None is a directional edge; all are STATE variables and belong to the risk/execution product track.
- Range contraction/expansion cycle (hyp-046/048): unusually narrow days are followed by relatively narrow days; wide by wide.
- Overnight coil (hyp-056/057): an overnight range in the bottom 20% of its own trailing distribution predicts a compressed regular session.
- Midday-lull persistence (hyp-105/106/141, HOLDOUT PASSED): a quiet 12:00-13:00 predicts a quieter afternoon, ratio ~0.74. Cleanest result in the project. 82.5% separable from the overnight coil.
- VXN level vs. trailing average (hyp-142/144/151, HOLDOUT PASSED September 12th, ~9:45 pm CT, Jason's sign-off, slot 3 of 5): elevated implied volatility (VXN above its own trailing-20d average) predicts an elevated next-session RTH range. Effect ran 1.305 (Discovery) -> 1.120 (Validation) -> 1.239 (Holdout) -- strengthened at the last stage, unusual, disclosed not just banked. THIRD hypothesis in project history to clear all three stages. Only 53-66% separable from the existing conditioning facts (residualized) -- the most overlapping of the four range-persistence survivors; must combine by RESIDUAL, not product, if ever integrated (research/studies/portfolio-hyp142-separability-2026-09-13.md).
- EIA weekly report hour, CL (hyp-000148, Discovery PASS September 12th): post-release-hour realized range ~2x the unconditional hourly baseline (0.367 vs 0.186 ATR). NOT promoted -- Monetization found no credible path (zero CL strategies exist to attach a sizing overlay to). Disclosed near-kill: ~half the effect is the release-print minute itself. First pass under the open scope (signal+trade outside NQ) and the first magnitude-only design (built to dodge the CPI/NFP direction-ambiguity failure mode). Held for future use if a CL strategy is ever built.
- ECB decision hour, 6E (hyp-000150, Discovery PASS September 13th): decision-hour realized range ~4x the unconditional hourly baseline (0.713 vs 0.179 ATR, diff +0.534) -- the largest magnitude effect found in either open-scope family. NOT promoted -- Monetization found no credible path (zero 6E strategies exist; every 6E-touching script uses it only as a cross-asset predictor for NQ). Statement-print share 37.9%, disclosed but below the kill threshold. Second open-scope Discovery pass, cross-confirms the scheduled-macro-event volatility pattern alongside M20. Held for future use if a 6E strategy is ever built.
Integrated in src/volatility_conditioning.py as sizing/context tools (the 3 range-persistence facts). OPEN QUESTION (largest loose end, sharpened September 13th): these have never been turned into a product — a volatility-conditioned sizing overlay on a simple base strategy. This now applies to FIVE facts, not three: M20/CL and M21/6E are both confirmed volatility facts sitting unused because no base strategy exists in either instrument to size. Sourcing considered a third scheduled-event-magnitude clone (FOMC or NFP magnitude in 6E or CL) this cycle and declined it: the class ("scheduled public event -> volatility jump") is now confirmed twice and a third instance would restate it, not extend it, and would face the identical Monetization dead end regardless of the result. The higher-value move is building ONE simple base strategy in CL or 6E so the two banked volatility facts have something to attach to -- worth raising at the September 19th checkpoint.

## 2. What FAILED, and why (the failure-mode taxonomy, with examples)
137 distinct hypotheses logged; 0 have ever cleared a correctly-specified promotion bar.
1. Cost-dominance — real gross effect, wiped by round-trip costs (many intraday fades).
2. Thin-sample overconfidence — credible CI on too few events (calendar studies at n=50-80: pre-FOMC, post-FOMC, month-end).
3. Correlated-lens double-counting — several "different" signals measuring one latent state (caught repeatedly; hyp-000140 |gap| vs overnight coil).
4. Direction ambiguity in pooled measurements — pooled event reactions with no consistent sign (CPI/NFP).
5. Marginal Discovery passes don't replicate — 0-for-several at Validation (H93, COT positioning, H116, H117).
6. Exit-design mismatch — a real drift effect destroyed by a stop/target that races it (H87/H89, H93, H114/115).
8. Cost basis mismatch (named September 15th, S001) — every pre-directive study charged the full-size NQ round trip (0.75 pts at $20/pt); the paper book trades the MICRO, where the same $2.50/side commission is 2.5 pts. S001's +2.6-pt gross edge a trade (131 Discovery trades) is real in-sample and smaller than a micro's assumed $6.00 round trip. Cost-fragile (avg R < 0.10 after assumed costs, directive s.11) is the DEFAULT state of an ~11-pt-risk intraday NQ trade at this assumption; B4b's measured number is the most valuable missing input.
7. Baseline confusion (named September 12th) — a long-only effect measured against ZERO on a trending asset. H118 passed three stages this way; against NQ's own drift it is nothing. The two-nulls rule now prevents it.
Idea-source hit rates for finding SOMETHING real: pattern-guess 0%; intuition ~1 in 8; behavior-first Observatory ~1 in 3; forced-participant map: 11 entries, 0 survivors (9 clean nulls, 1 near-miss, 1 untestable). Literature / practitioner / observatory channels: being measured from September 12th -- literature so far 0 for 2 scanned (M15, M16), both clean nulls on decayed 2018/2019 results; practitioner 0 entries from 3 claims; observatory characterized 3 questions, 0 candidates.
Closed families (never resurrect without a genuinely different claim): Treasury 10-year auction concession/rebound (M19, ZN, n=40 events, both gating legs null, kill check clears -- a real absence, not underpowered noise masquerading as a kill); overnight-vs-intraday split (M15, night = 55% of drift, not 'all'; do not slice to weekday-only); market intraday momentum first-30 -> last-30 (M16, null in every cell); candlestick/bar patterns; opening-range/IB breakout; VWAP and reference-level fades; gap fades (3 variants); weekly/multi-day trend following (7 variants); VXN level/ROC as direction; ZN lead-lag (daily); turn-of-month; closing-pressure reversal; CPI/NFP reaction; pre-NFP drift; pre-FOMC drift (2 attempts); post-FOMC continuation; month-end NQ-vs-ZN; NQ-ZN correlation breakdown (near-miss); basket correlation convergence (clean null, no gradient); days-to-opex; overnight_range_vs_atr drift; vwap_dist LOW drift (H118, baseline confusion).
Structural conclusion (September 12th, four independent reads agree): scheduled, public flows are the most competed in NQ and nine nulls there is the expected outcome; the participants who leave money on the table (dealers hedging gamma, basis arbs, intraday liquidity takers) are not visible in 1-minute OHLCV. Widening the search without new data produces lottery tickets with nicer stories.

## 3. What is PARKED, and why
- Data ceiling (Jason, September 12th): 1-minute OHLCV for NQ, ZN, 6E, CL; no purchases. Quotes on file: ES $14.69, RTY $10.77, YM $14.31 (src/quote_data_pulls.py runs from Jason's own Terminal; sandboxed shells cannot reach the Databento API).
- Entries parked at the ceiling: M9 Nasdaq rebalance (continuous-contract roll-day gap; outright months would fix it), M13 LETF close rebalance (needs RTY/ES), M14 gamma regime (needs ES), cash-open NQ/ES residual (needs ES + SPY/QQQ), curve rotation (needs ZT).
- Execution clock (signal engine, Tradovate/IBKR ~$60-115/mo, pre-approved): PARKED explicitly — it was unblocked for H118 and H118 is gone. Resumes only when a candidate reaches execution qualification.
- Options / tick data: only if a price-only result earns it (M14 was designed as that gate).

## 4. What is OPEN (live work)
- Shelf (SHELF RULE v2): counts DRAWABLE entries only; sourcing every cycle from every channel; below floor = more sourcing, never a draw. Currently 2/3 drawable (Entry 27 M23 London-open 6E volatility burst, sourced 1am cycle 2026-09-13, no scan run yet; Entry 28 M24 month-end payment-cycle reversal NQ, sourced 3am cycle 2026-09-13, no scan run yet); pending on data/Jason: Entries 15, 17, 18 (data-ceiling). M18 (Entry 22) CLOSED 1am cycle: Scan 026 P1_PASS_P2_FAIL, hyp-000152 REJECTED. M22 (Entry 26) CLOSED 3am cycle: Scan 027 P1_FAIL (n=82, thin-sample), hyp-000153 REJECTED. M19/ZN and M21/6E both CLOSED (Scan 024 clean null hyp-000149; Scan 025 Discovery PASS -> Monetization NO CREDIBLE PATH hyp-000150). SOURCING OWED again -- one more genuinely novel entry needed to reach the floor.
- Written and drawable (September 12th, 11 am cycle): M15 overnight-vs-intraday split (Lou/Polk/Skouras 2019) and M16 intraday momentum (Gao et al. 2018), mechanism docs first, one pre-registered scan each. Practitioner stream opened (research/sourcing/practitioner.md; three claims ruled, none entered).
- 3 pm cycle (queue item 4, Observatory): closed the last unchecked pairwise separability gap among the 3 validated volatility facts -- prior-day range regime vs. overnight coil (82.8% retained) and vs. midday-lull (66.1% retained), both SEPARABLE. Started the NQ/ZN/6E/CL information-transmission map (v1, 15-min RTH): no lead-lag structure detected in any pair at this resolution, only contemporaneous co-movement (ZN -0.32, CL +0.16, 6E ~0) -- a third independent lens agreeing with the M11/M12 cross-asset nulls. 4:15 pm TEST cycle (new budget-use rule) finished item 4: lead-lag v2 (both sessions, 5/15/30/60-min, shock-conditioned) -- transmission complete within one bar everywhere, one of 192 cells clears zero at +0.04 sd (multiplicity-consistent null); fixed state classifier -- variance persistence is two-sided (wide overnight -> +29% RTH range, wide prior day -> +22%; the validated facts read from the other tail), NQ-ZN rate configuration conditions nothing (range 1.04 vs 1.03; direction +0.065 vs drift +0.036, not separable; adjacent to closed ZN lead-lag family). ITEM 4 CLOSED at the data ceiling. Then, with budget open: sourced M17 (same-slot next-day periodicity, Heston et al. 2010) -> shelf 3/3 -> DREW Entry 19 (M15): Scan 020 clean null (night 55% of drift). Run 1 of that scan had a sample bug (Monday night legs dropped) that showed a marginal pass; caught by the drop count, fixed to spec, run 2 of record. Sourced M18 (volume-conditioned reversal, CGW 1993) -> 3/3 -> DREW Entry 20 (M16): Scan 021 clean null. Shelf now 2/3 (Entries 21, 22). Design fact from Scan 020: NQ's intraday session has POSITIVE drift (+0.03 ATR/session) -- intraday directional claims face a positive NULL 1, not zero.
- Forward logs: EXP047 weekly trend (3/260 weeks); H118 forward log for information only.
- CHECKPOINT: held September 13th (pulled forward). Verdict: CONTINUE, target moves from direction to structure -- Risk/State Engine paper-traded first, Observatory free-look + question families for generation, execution measurement now, data ceiling kept with a written trigger. See research/weekly/2026-09-13.md.
- CHANGE FREEZE fully lifted September 13th (~4:55 pm CT): checkpoint held today (research/weekly/2026-09-13.md); UPGRADE QUEUE v3 (U1-U22) is the approved work; the September 19th review is cancelled, routine weekly reviews resume September 26th.

- 2026-09-13 ~5:25 pm CT (interactive test cycle): shelf 3/3 (Entry 31 M27, 32 M28, 33 M29 implied-minus-realized vol gap). M26/Entry 30 CLOSED (Scan 033 P1_FAIL, hyp-000159) -- first sanctioned conditional retest, answer for this pattern+condition: no. Sidak diagnosis on file (research/studies/sidak-stacking-diagnosis-2026-09-13.md): no cross-stage double-counting; Discovery-stage N=451 and rising -- policy decision open for Jason. UPGRADE QUEUE v3: U1, U3(M26), U4 done; U2 next.

- 2026-09-13 ~7:35 pm CT (7:00 pm test cycle): BOT B0-B3 DONE (B2 risk_state_engine built; B3 placeholder entry spec'd + coded); B4 order path is next and needs Jason's broker paper account. M23/hyp-000156 Statistical PASS x4 (Sidak N=451 survives) -> PROMISING, Validation owed, blind Gate CONDITIONAL (5 conditions), Validation BLOCKED on 6E data (Discovery slice only on disk). M27/Entry 31 CLOSED (Scan 034: Tokyo hour credibly quieter; London burst is London-specific). Sourced M30/Entry 34, M31/Entry 35 from the Idea Factory queue. Shelf 4/3 (32, 33, 34, 35). 12 closure forms filed.

- 2026-09-13/14 ~11:00 pm CT (scheduled cycle): B4 SPLIT and B4a BUILT -- Jason's IBKR paper account exists but futures permission is in a 30-day cooldown, so B4a (order path against a simulated broker, no account needed) proceeded on its own: src/broker_interface.py (contract), src/simulated_broker.py (deterministic seeded reject/partial-fill/disconnect/late-ack), src/order_path.py (capital-protection gate first, journal-before-submit, fill/reconciliation, crash recovery). B6 kill switches now WIRED, not just present. Also built the same cycle: src/bot_forward_log.py (B4a/B7-EARLY, the free statistical forward test, two clocks rule kept explicit) and src/execution_measurement.py (B5 first cut, the 14 checks, honest INSUFFICIENT SAMPLE reporting at N=0). 34 new tests, full suite 358/358. Spec: research/infrastructure/b4a-order-path-spec.md.

- 2026-09-14 ~1:00-7:00 am CT (scheduled cycle): B7 BUILT, TESTED, RUN -- src/bot_stack_paper_run.py wires base_entry_b3's signal + risk_state_engine's decision + order_path's real order machinery into one loop, one row per session to research/forward_validation/bot_stack_paper_log.jsonl (kept visibly separate from bot_stack_forward_log.jsonl -- two clocks rule). Own execution anchor (2026-09-08), separate from the statistical log's forward-only anchor, with the reasoning written into the file itself. First real run (1 session, 2026-09-08): a real signal, real risk_state_engine permission, and a real capital_protection BLOCK (stop too wide for the $50-150 swing band) -- B6 proven fail-closed on real data for the first time, not just in tests. 14 new tests, full suite 372/372. Also fixed: docs/BOT_ROADMAP.md's table, which the 11:00 pm cycle's own close-out had claimed to update but never did.

- 2026-09-14 ~7:09-7:25 am CT (3:00 am cycle, run as catch-up): U28 DONE -- src/idea_factory.py --interactions, the pairwise state x state look table, with the timing rule on BOTH layers and context/trigger ordering by known-at time. 13 tests. FIRST RESULT: of K=14,740 interaction cells on the Discovery slice, ZERO clear the multiplicity yardstick (|z| ~ 4.64 at that K); the strongest, after main effects are removed, is 4.4. At the project's current resolution the market states on disk do not visibly modify one another beyond their own separate effects -- descriptive, not a test, but it means the look table does not have a better conditional-stack pair waiting in it than Stack A was. Also fixed the approval-prompt bug that stalled the 1:00 am cycle (Artifact write_db must be given a path inside the session workspace, never the staged upload path; and the scheduled task's prompt must never be rewritten, only its fire time moved). Console v88. 385 tests.

- 2026-09-14 ~7:25-7:45 am CT (5:00 am cycle, run as catch-up): U6 DONE -- src/integrity_checks.py, the Integrity Gate's seven-check mechanical suite, 24 tests. First runs: Stack A (hyp-000161) 3 green / 2 RED (era-dependent, and its top 5% of observations carry 188% of a small net effect -- neither was why it was closed); hyp-000142 5 GREEN / 0 red, the first independent structural audit of a promoted fact in this project, and it holds up. Three FALSE verdicts were caught on the suite's own first runs and fixed with regression tests: the roll check flagged ordinary calendar exposure (12.7% base rate vs a 5% threshold), cost_sensitivity greened an effect that had inverted under 2x costs, and the shifted placebo redded hyp-000142 because a VXN tercile persists (P(HIGH tomorrow|HIGH today)=0.79, 78.8% sample overlap) so t+1 is not an independent placebo. 409 tests.

- 2026-09-14 ~7:45-8:05 am CT (7:00 am cycle, run as catch-up): SHELF DRAW Entry 34 (M30) -> Scan 036 -> hyp-000162, PROMISING. A wide first half-hour (opening_range_vs_atr HIGH tercile, known 10:00 ET) predicts a midday (11:30-13:30) range about half a trailing-average wider than a narrow one, with larger excursions in BOTH directions: P1 gating +0.5193 ci_90 (+0.4475,+0.5975) n=555/556; MFE +0.0886 ATR; MAE +0.1108 ATR; and it survives residualizing on the prior-day range tercile (F-048) at 83.6% against a 50% bar, so it is NOT that fact restated. First Discovery survivor since hyp-000151 and the first ever sourced from the Idea Factory queue. BUT the U6 mechanical suite -- built one cycle earlier -- is RED on the placebo: yesterday's opening range does ~74% of the same work (shifted t+1 0.2040 vs real 0.2741), so what is actually known is 'sessions in a wide-range REGIME have wider middays, and the opening half-hour is one readable marker of that regime, not necessarily its cause'. P3 does not cover this (prior-day RANGE is a different variable from prior-day OPENING range). Near-boundary: shifted-leg overlap 48.56% vs the 50% gating guard. Statistical (+POWER) owed, then the blind Gate, which inherits that specific question.

- 2026-09-14 11:00-11:35 am CT (11:00 am cycle): DIRECTOR RE-EVALUATION hyp-000162 = ADVANCE, and the U6 placebo red is EXPLAINED rather than dismissed. Residualised against every validated volatility fact plus its own lagged self: VXN level 79.8% retained, overnight coil 75.3%, prior-day range 83.6% (reproduces scan_036's P3 exactly -- method control), and opening range AT T-1 87.2%, all against a 50% bar. A LAGGED PREDICTOR CAN BE INDIVIDUALLY INFORMATIVE AND STILL LEAVE MOST OF THE CURRENT PREDICTOR'S INFORMATION INTACT -- the two share a persistent driver without being substitutes. So the placebo was detecting persistence in the VARIABLE, not redundancy in the CANDIDATE. Consequence: B2's inputs are four distinct things, not one volatility regime wearing four hats, and the sizing-queue pause is lifted. Also carried forward: the effect is largest in the HIGH tercile of every stratum tested -- it scales with volatility, so its magnitude is conditional.

- 2026-09-14 9:00-9:55 am CT (9:00 am cycle): STATISTICAL STAGE hyp-000162 = PASS. n=555/556, diff +0.5193 ci_90 (+0.4475,+0.5975); stable across chronological halves; credible in BOTH volatility regimes (low +0.4560 / high +0.6082); survives the BINDING Sidak correction at 467 project-wide Discovery trials with the whole adjusted interval (+0.3511,+0.6875) above zero; insensitive to the midday window boundary within +/-0.04 across four variants. Validation would be well powered: 0.815 even at HALF the Discovery effect. So the doubt about this candidate is NOT statistical -- the association is real, stable and correction-proof. What is unknown is what it is an association WITH, and the U6 placebo red (yesterday's opening range does ~74% of the work) is carried to the blind Gate unchanged rather than absorbed here. Also sourced Entry 36 / M32 (location_in_range -> last-hour range, known 09:30) with the shifted-signal placebo pre-registered as a GATING control.

## 5. How the system works (one paragraph)
Sourcing (map / literature / practitioner / observatory) -> template with instrument-choice gate, kill rule, two nulls, decay, resurrection ruling -> shelf (drawable only) -> mechanism doc BEFORE scan -> one pre-registered Discovery scan (Discovery slice 2015-Oct 2021) -> Statistical (4 questions, Sidak, power) -> blind Integrity Gate -> one-shot Validation (Oct 2021-Jan 2024) -> Monetization -> blind Gate -> Holdout (Jason only, 2024+) -> Portfolio. Two attempts per family. Every scan cell counted project-wide. Cycles every 2 hours: lock, budget clock, sweep, checkers, sourcing, draw if drawable, tests, ops checks, console, report, git push, reschedule. Jason is looped in for: Holdout slots, purchases, a real signal, capital protection, integrity problems with promoted work. Governance docs: research/infrastructure/agent-governance-structure.md (v2 + AMENDMENT v2.5), back-half-production-integrity-v3.md (+ v3.2), research/studies/two-layer-methodology.md (+ two-nulls amendment). NEXT_UP.md is the handoff baton; this file is the memory.

## 6. Decision log (structural changes, dated, with the reason)

- 2026-09-13 (7:00 am CT scheduled cycle): sourcing search only, no new entry. Investigated a quarterly-witching-day closing-volatility/reversal candidate for NQ (options/futures expiration forces a mechanical unwind in the final 30 minutes of quad-witching Fridays) -- distinct in principle from M1/M13/M14/M9 and not requiring any new data. RULED OUT before writing a mechanism doc: re-verified the data-integrity finding already on record from Entry 2/Scan 007 -- the continuous NQ 1-minute series has ZERO usable RTH bars on quarterly witching Fridays (checked directly: 2021-06-18 and 2021-09-17 both return 0 RTH bars; the continuous-contract roll splices exactly on those dates). The exact days needed to test this candidate are unusable in the data actually on disk, so it cannot be drawn without a non-continuous or roll-adjusted NQ series (new data, not currently available). Not pursued further; not re-checked again without a data-source change. No other genuinely novel, adequately-powered candidate cleared the LEARN/resurrection bar. Shelf stays 2/3 (Entry 27/M23, Entry 28/M24); sourcing owed again next cycle.

- 2026-09-13 (9:00 am CT scheduled cycle): discovered Jason had run the RTY and ES Databento fetch scripts himself on his own Mac (per the standing guidance that these fetches must run outside the sandboxed/bridged shells) -- both files were already on disk, silently unblocking Entry 17/M13 and Entry 18/M14 without any message from Jason in this session. Also found and fixed a real bug in data_fetch_databento.py's log_cost_entry(): it hardcoded the module's own NQ symbol/dataset/schema globals regardless of the caller, so the RTY cost-log entry had been mislabeled "NQ.c.0"; corrected the entry and added the ES purchase's missing entry (its own script never logs, by design, since it skips the live re-quote). Discovered RTY's CME history only goes back to 2017-07-09 (Russell 2000 moved ICE->CME in 2017) -- Entry 17/M13's 3-instrument scan restricted to the common 2017-07-09->2021-10-03 window across RTY, ES, and NQ for comparability, disclosed rather than absorbed. Shelf jumped from 2/3 to 4/3 DRAWABLE (Entries 17, 18, 27, 28). Drew Entry 17/M13 (LETF close-rebalance flow): Scan 028, 15 cells, P1 gate (TOP-tercile sign-adjusted close-window return vs each instrument's own NULL1) FAILED for RTY, ES, and NQ alike (diffs -0.0050/+0.0082/+0.0060, none credible). hyp-000154 REJECTED, entry CLOSED. Cross-instrument P2 ordering never reached since no instrument cleared the gate.
 Budget remained open (started 14:00:48 UTC, ~87 min left), so proceeded to also draw Entry 18/M14 (option-dealer gamma regime, NQ and ES, ES-derived autocorrelation proxy) per the budget-use rule's precedent for drawing multiple shelf items in one cycle: Scan 029, 8 cells, P1 gate (TOP-minus-BOTTOM regime difference, sign-adjusted close-window return, credibly positive) FAILED for both instruments -- NQ diff=-0.0221 ci_90=(-0.0427,+0.0007), ES diff=-0.0162 ci_90=(-0.0382,+0.0104), both wrong-signed vs the mechanism's prediction though neither credible. hyp-000155 REJECTED, entry CLOSED. Overlap discipline observed: M14's regime-difference test never double-counted against M13's own level test (both independently failed). Shelf back to 2/3 (Entry 27/M23, Entry 28/M24) after both draws; sourcing owed next cycle.
Sourced Entry 29/M25 (monthly options-expiration week delta-hedge unwind, NQ, literature: Stivers and Sun SSRN, distinct from the declined quarterly witching-day candidate and from M14 despite thematic overlap) restoring shelf to 3/3 floor. Deliberately did NOT draw M25 this cycle (budget-use judgment call, not a blocker) -- reserved remaining budget for a careful close-out of an already cycle-heavy session (2 full scans, a real bug fix, extensive doc updates). Shelf ends this cycle at 3/3 DRAWABLE (Entry 27, 28, 29), next draw M23 (oldest).

- 2026-09-13 (5:00 am CT scheduled cycle): sourcing search only, no new entry. Practitioner queue fully ruled (no new claims to evaluate). Literature search considered and declined the daylight-saving-time stock-return anomaly (Kamstra-Kramer-Levi 2000 AER, sleep-disruption-driven risk aversion around the two annual clock changes): declined because (a) it is a contested finding with a published "Fact or Fiction" rebuttal already in the literature disputing out-of-sample replication, and (b) only ~2 events/year gives ~13 events across the whole Discovery window, thinner than even M19's n=40 or M22's n=82 -- not enough power to be worth a shelf slot even under the thin-sample disclosure convention. No other genuinely differentiated, adequately-powered candidate cleared the LEARN/resurrection bar this cycle. Shelf stays 2/3 (Entry 27/M23, Entry 28/M24); sourcing owed again next cycle.

- 2026-09-13 (3:00 am CT scheduled cycle): sourced Entry 28/M24 (month-end payment-cycle reversal, NQ, literature: Graziani 2024 EFMA working paper -- pension/cash-management forced selling into month-end depresses price, reverses over the following month) restoring shelf to 3/3, authorizing a draw within the same cycle per SHELF RULE v2. Drew and scanned Entry 26/M22 (month-end ZN duration-extension flow; Scan 027, ZN, block=5, Discovery only). RESULT: GATING cell (last-2-session ZN return net of unconditional 2-session drift) n=82 mean=+0.1022 ci_90=(-0.1210,+0.2630) -- not credibly positive; not killed (final-minute share 0.096); issuance-direction split omitted (no issuance-size data on disk, only 10Y auction dates from M19's file -- not fabricated). CLOSED per falsifier, THIN-SAMPLE caveat (n=82, same discipline as M19's n=40). Logged hyp-000153 (REJECTED). Shelf back to 2/3 (Entry 27/M23, Entry 28/M24), sourcing owed again next cycle.

- 2026-09-13 (1:00 am CT scheduled cycle): sourced Entry 27/M23 (London FX session-open volatility burst, 6E, structural session-boundary mechanism, distinct from M20/M21's scheduled-news mechanism) restoring shelf to 3/3, which per SHELF RULE v2 authorized drawing within the same cycle. Drew and scanned Entry 22/M18 (volume-conditioned daily reversal, NQ, Campbell-Grossman-Wang 1993; Scan 026, 10 cells/1 gating, Discovery only). RESULT: P1 gating cell passed (HIGH-volume sign-adjusted next-day mean credibly negative, ci_90=(-0.1523,-0.0463)) but P2 failed (HIGH not credibly below LOW, diff ci_90=(-0.1253,+0.0054)) -- reversal present but not volume-graded; NQ's own daily mean reversion, not a size effect from volume. Not killed (first-min share 0.036). CLOSED per falsifier (b). Logged hyp-000152 (REJECTED). Closes the volume-gradient-on-reversal channel for good, alongside hyp-000043's prior closure of volume level alone. Shelf back to 2/3 (Entry 26, 27), sourcing owed again next cycle.

- 2026-09-13 (interactive, Jason: "Push through the option through the holdout"): spent Holdout Generation 2 slot 3 of 5 on hyp-000142/144 (VXN level vs. trailing average -> next-session RTH range). Holdout script written verbatim from the Validation script (only the holdout_gen2 loader and stage label swapped, diff-checked line-by-line before running, per the frozen spec). RESULT: HOLDOUT PASSED (hyp-000151) -- HIGH n=208 ratio 1.2389 ci_90 [1.170,1.313], Sidak-adjusted [1.154,1.324] > 1.0, floor cleared at 0.24 (largest margin of the three stages). Effect strengthened Validation->Holdout (1.120->1.239), unusual and disclosed, not just banked. THIRD hypothesis in project history to clear all three stages (after H118, later reclassified REJECTED, and midday-lull/afternoon-expansion, KNOWN TRUE). Portfolio incremental-information review run immediately after (research/studies/portfolio-hyp142-separability-2026-09-13.md): SEPARABLE, 53-66% retained residualized on the existing conditioning facts -- most-overlapping of the four range-persistence survivors, must combine by RESIDUAL not product if ever integrated into volatility_conditioning.py. That integration itself is deferred to the September 19th product-build decision, not done tonight (structure freeze). 2 of 5 Holdout Gen-2 slots now remain.

- 2026-09-13 (9:00 pm CT cycle): sourced M22, month-end index duration-extension flow in ZN (open scope, map channel) -- bond index funds forced to extend duration at month-end via Treasury futures, distinct participant/calendar from M19 (auction concession) and M5 (NQ-vs-ZN relative performance, CLOSED). Entry 26, DRAWABLE, mechanism doc written before any scan. Shelf 2/3. Searched for a second new candidate to reach the floor of 3 and declined to invent one -- every option considered was either a scheduled-event-magnitude clone (already declined last cycle for the same reasoning) or blocked on data not on disk. Sourcing remains owed.
- 2026-09-09: Discovery/Validation/Holdout chronological splits; two-attempt limit; LEARN layer; Market Behavior Discovery Engine (state-first) replaces strategy-first search; Research Director + mandatory Integrity Gate. Reason: 120 hypotheses rejected, pipeline was a filter with no generator.
- 2026-09-10: Back-half v3 + v3.1 (forward test != paper trading != live; anti-optimization rule; two clocks); execution infrastructure pre-approved.
- 2026-09-11: Outside review adopted — market structure map, mechanism BEFORE scan, blind gates, power check, 2-hour self-scheduling cycles with lock/budget/checkpoint; console simplified to one state document; UPGRADE brief ($1k/mo goal, $20/mo data, $300 risk budget).
- 2026-09-12 (overnight): map exhausted (M1-M11 closed or parked); M9 untestable on a roll-day data gap; M12 cross-asset clean null; approval-card stall root-caused (a path outside the workspace); create_trigger vs send_later slip fixed.
- 2026-09-12 (4:15-5:25 pm CT, TEST cycle under the budget-use rule): one cycle did what four used to -- closed Observatory item 4, sourced 2 entries, drew and scanned 2 (both clean nulls), 2 ledger rows. Two defects caught and fixed: session reports missing the Agents/new-information sections (ops_checks now flags), and Scan 020 run 1 silently dropping Monday night legs (Globex-only calendar days broke the prior-close chain) -- would have advanced a false marginal pass. Lesson written into every scan going forward: a calendar day with only Globex bars is not a session and does not break the chain; always print the dropped-session count.
- 2026-09-12 (4:10 pm CT, staff meeting, Jason-called): budget is a ceiling not a target, but a cycle should work through an item's own remaining honest sub-steps if budget is open, not stop at the first clean deliverable and hand the rest to the next cycle. Never used to invent work or re-touch a stage. research/staff-meeting-cycle-scoping-2026-09-12.md.
- 2026-09-12 (11 am cycle): first unattended cycle under SHELF RULE v2 ran as designed -- sourced two literature entries and ruled three practitioner claims instead of drawing thin; shelf 2/3. Open question for the Sept 19 review: is a #1-ranked, on-disk entry drawable below the floor.
- 2026-09-13 (~12:20-12:45 am UTC, 7:00 pm CT cycle): drew Entry 25/M21 (ECB decision volatility, 6E) after a fresh WebFetch found a usable historical source (the Jarocinski-Karadi academic dataset, not the ECB's own JS-heavy pages that failed last cycle). Scan 025: Discovery PASS, decision-hour diff +0.534 ATR (largest effect in the M20/M21 family), Statistical PASS, Director CONTINUE, Monetization NO CREDIBLE PATH (no 6E strategy to size). hyp-000150 REJECTED as a valid characterization, filed KNOWN TRUE. This closes all three open-scope entries sourced on September 12th (M19 ZN, M20 CL, M21 6E) -- one Discovery pass with no strategy (M20), one clean Discovery null (M19), one Discovery pass with no strategy (M21).
- 2026-09-12 (~7:10 pm CT, interactive): Jason supplied the TreasuryDirect 10-year auction-date CSV he had asked what was needed of him for. Drew Entry 23/M19 (Treasury auction concession, ZN): Scan 024, both gating legs null vs ZN's unconditional 3-session drift (n=40 events), kill check clears cleanly (8.8%, not a print artifact -- a real absence). hyp-000149 REJECTED, entry CLOSED, attempt 1 of 2 spent. Caught and fixed a kill-share denominator bug in the scan itself before treating the result as final (used the signed post-leg mean instead of the mean of per-event |post-leg|, inflating the share past 1300%).
- 2026-09-12 (5:00 pm CT cycle, survived a mid-cycle cloud-container reset with no work lost -- the connected project folder, not the ephemeral container, is where the working tree lives): sourced M19/ZN (Treasury auction concession, WAITING on TreasuryDirect data), M20/CL (EIA report volatility), M21/6E (ECB decision volatility) -- 2nd and 3rd open-scope entries. Drew and closed Entry 21/M17 (clean null, hyp-000147). Drew Entry 24/M20 through the full pipeline: first open-scope Discovery PASS in the project, honest near-kill disclosure, Monetization verdict NO CREDIBLE PATH (hyp-000148, valid characterization, no CL strategy to size with yet). Entry 25/M21 blocked honestly on a missing verified historical ECB date list (web-tool session limit hit) rather than scanned on guessed dates -- filed WAITING. Shelf 1/3, sourcing owed into the next cycle.
- 2026-09-12 (morning): scope opened beyond NQ; three outside AIs polled; sourcing stage + template + ranking by information gain x edge potential; TWO NULLS rule (failure mode #7); H118 baseline diagnostic -> H118 REJECTED; SHELF RULE v2 (drawable-only count, sourcing every cycle, no invented scopes, shelf-starving alert); data decision: no purchase; per-entry scan hold lifted (cycles scan autonomously); CHANGE FREEZE + CHECKPOINT September 19th; weekly review instituted; this file created.

- 2026-09-13/14 (~11:00 pm CT scheduled cycle): B4 split honored in code, not just in the roadmap doc -- B4a (order path against a simulated broker) needs no broker account and was built, tested, and wired to the kill switches this cycle; B4b (the real IBKR adapter) stays blocked on the futures-permission cooldown (~Oct 13th) without slowing B4a. Reason this is a decision-log entry, not just a session note: it is the project's first concrete instance of "the deliberate-failure broker exists on purpose" -- SimulatedBroker is built to reject, partially fill, disconnect mid-order, and return late acks on command, specifically so the order path's failure modes are exercised before any real money or even a real broker account is involved. B6 (capital_protection.pre_order_check) is now actually called before every order, closing the "CODE EXISTS, NOT WIRED" gap noted at B6's original build. See research/infrastructure/b4a-order-path-spec.md.

- 2026-09-14 (~1:00 am CT scheduled cycle): B7's own execution anchor is a separate decision from bot_forward_log.py's statistical forward anchor, made explicit rather than assumed. B7 is not a statistical claim (it measures whether the order-path machinery runs correctly, not whether the strategy is any good), so gating it on the same forward-only boundary that protects the statistical log from re-litigating already-searched data would have been importing a rule from the wrong clock. B7 gets its own anchor -- the latest session on disk the first time it runs -- written to disk so a later cycle can't silently move it. Reason this is a decision-log entry: it is the first time the two-clocks rule had to be extended from "don't compare the two logs' numbers" to "don't even reuse the same eligibility boundary between them" -- a subtler form of the same discipline. See src/bot_stack_paper_run.py's own header for the full reasoning, including four other scope choices made explicit the same way (broker lifetime, which stop/target gets ordered, bookkeeping-exit reimplementation, gross vs. costed P&L).

- 2026-09-14 (3:00 am catch-up cycle): ranking a cross-tab by distance from either MARGINAL mean re-discovers the main effects you already validated; only the ADDITIVE contrast isolates an interaction. Caught on the interaction table's own first run: ranked by distance from the trigger-alone mean, the top of the table was `vxn_level_vs_trailing HIGH x <anything> -> range` at |z| up to 8.5, which is the validated "volatile days have bigger ranges" fact with a second state along for the ride -- the context's own main effect was still inside the contrast. Now ranked by z_vs_additive = (cell - (context_alone + trigger_alone - all_mean)) / se. Reason this is a decision-log entry and not just a bug note: the project already had the rule that the idea-factory queue is DESCRIPTIVE and never a result. This is the discovery that the queue can also be descriptively WRONG -- pointing confidently at restatements -- if the contrast is chosen carelessly. "Not a result" was never sufficient protection on its own. The second consequence is substantive: with the contrast fixed, zero of 14,740 cells stand out, so the conditional-stack format has no sourced material visibly better than the pair that already produced a powered null, and one null remains before the format closes.

- 2026-09-14 (5:00 am catch-up cycle): A STRUCTURAL CHECK NEEDS ITS OWN BASE RATE BEFORE ITS THRESHOLD MEANS ANYTHING, AND THE BASE RATE MUST BE COMPUTED, NOT ASSUMED. Three for three now, in two cycles: U28's interaction table ranked main effects as interactions until it was measured against the additive prediction; U6's roll check redded ordinary calendar exposure until it was measured against the calendar base rate (an 8-day quarterly window is 12.7% of sessions, so a 5% threshold reds everything); U6's shifted placebo redded a Holdout-passed fact until it was measured against the signal's own persistence (a VXN tercile re-selects 79% of itself at t+1, so the "placebo" is the same signal). Each check was individually reasonable and each was wrong on first contact with real data, in the same direction: firing on something normal. A false RED costs the Gate exactly as much attention as a false green costs it safety, and a suite that cries wolf gets ignored, which is the worse failure. Every threshold in src/integrity_checks.py now either computes its own base rate or reports the quantity that makes it readable. SECOND, PROCEDURAL CONSEQUENCE: run the mechanical suite on a conditional stack's occurrence file BEFORE registering the stack. Stack A's two reds (era dependence, 188% concentration) were visible in its own occurrence data and would have been known before the format spent one of its two attempts on it.

- 2026-09-14 (7:00 am catch-up cycle): INFRASTRUCTURE THAT PAYS OFF ONE CYCLE LATER IS NOT BUSY WORK -- BUT THE ALERT SHOULD KEEP FIRING ANYWAY. ops_checks' busy-work guardrail went to FAIL after three straight cycles (B7, U28, U6) moved no ledger row, scan, doc or inventory entry. It was right by its own definition and was reported to Jason rather than argued with. The corrective cycle drew from the shelf and produced hyp-000162, the first Discovery survivor since hyp-000151 -- and the tool built in one of those three 'busy work' cycles (U6's mechanical suite) is what immediately found the blocking finding on it, one cycle after being written. The lesson is NOT to soften the alert: the project had no way to know that infrastructure would pay off until it did, and a guardrail that only fires when you already agree with it is not a guardrail. Keep it firing on schedule; answer it by moving the pipeline, not by relaxing it. SECOND, from the same run: a candidate can pass every one of its own registered predictions and still carry a defect none of them were shaped to catch. hyp-000162 passed P1, P2 and P3 -- including a control on prior-day RANGE -- while the mechanical suite showed prior-day OPENING range does 74% of the work, a variable the registered scope never mentioned. Pre-registration protects against moving the goalposts; it does not protect against asking too few questions. That is exactly the gap a mechanical suite that runs on EVERY candidate is for.

- 2026-09-14 (9:00 am cycle): A CANDIDATE CAN BE STATISTICALLY UNIMPEACHABLE AND STILL NOT BE UNDERSTOOD, AND THE PROJECT NOW HAS A PLACE TO PUT THAT DISTINCTION. hyp-000162 passed every gating question of the Statistical stage, survived a binding multiplicity correction at N=467 with room, and would enter Validation at 82% power against half its own effect -- while the mechanical suite's placebo check says yesterday's value of the conditioning variable does 74% of the same work. Those two facts are not in tension: one is about whether the association exists, the other is about what the association is WITH. The Statistical stage deliberately did NOT absorb the second question, because answering it needs a conditioning variable that was never in the registered scope (prior-day OPENING range, as distinct from prior-day RANGE which P3 already controlled), and quietly widening a frozen spec to resolve an inconvenient finding is precisely the failure the freeze exists to prevent. It goes to the blind Gate as a specific question instead. SECOND, THE LEARNING LOOP CLOSED INSIDE ONE DAY: M32, sourced the same cycle, carries a GATING pre-registered shifted-signal placebo control that exists only because hyp-000162 tripped one hours earlier. The cost was one candidate's ambiguity; the payment is that the next candidate cannot reach the Gate with that question still open.

- 2026-09-14 (11:00 am cycle): A HIGH PLACEBO SCORE IS A REASON TO RUN THE RESIDUALISED TEST, NOT A VERDICT ON ITS OWN. The mechanical suite said yesterday's opening range does 74% of hyp-000162's work, which reads as redundancy. The Director test held yesterday's value FIXED and found 87.2% of the effect still there. Both numbers are correct and they are not in conflict: a lagged predictor and a current one can share a persistent driver without being substitutes. Read alone the placebo number would have killed a genuinely new candidate; read alone the separability number would have missed that the underlying variable persists strongly enough to matter for sizing. The suite should KEEP flagging high placebo scores -- the flag did its job by forcing the analysis -- but the DISPOSITION belongs to the stage that can hold the suspect fixed, not to the flag. This is the counterpart to the same morning's lesson that a structural check needs its own base rate: a check can be correct, informative, and still not be a verdict.

## 2026-09-16 (1:00 pm CT scheduled cycle) — the pre-correction KILLS rechecked against the corrected cost: S001 flips, S007 does not

Jason's Amendment 2 corrected the round-trip cost (research/infrastructure/cost-model-2026-09-16.md; src/cost_model.py:
MNQ market $2.60 = 1.300 pt, not the old $6.00 = 3.000 pt). S007 and S008 were rescreened against it in the
cost-correction cycle. **S001 never was**, and it was the other verdict the wrong number could have produced. This cycle
grepped every SCREEN row in research/ledger/strategies.jsonl and recomputed each against cost_model. There are exactly
two verdicts of KILL-at-SCREEN in the project's history, S001 and S007, and only S001's gross per trade exceeded the
corrected cost.

- **S001 (Level Sweep Reversal on compressed prior days, M26 via Salvage) FLIPS, in all four combinations.** The frozen
  spec and module were not edited (s.13): both sha256 were re-verified byte-identical to the FREEZE row before the
  module was re-run. Same Discovery slice (2,101 sessions), same 131 trades, same gross +$669.62 = **+2.5552 pt/trade**.
  At the old, wrong $6.00 the assumed costs were $786.00 and the net was **-$116.38** -> KILL. At the corrected cost the
  assumed costs are $340.60 and the net is **+$328.87 MNQ market (+1.2552 pt/tr, avg -0.0182R)**; MNQ limit (OPTIMISTIC)
  +$394.37 (+1.5052 pt/tr, +0.0044R); NQ market +$4,742.85 (+1.8102 pt/tr, +0.0319R); NQ limit (OPTIMISTIC) +$5,397.85
  (+2.0602 pt/tr, +0.0544R). **Reopened as an INPUT-ERROR CORRECTION, exactly as S008 was — not a salvage, not a second
  attempt, not a FIX ONCE.** The 2026-09-15 KILL/SALVAGE/LEARN rows stand as the record of what was decided on the wrong
  number, and S001's one salvage stays spent (S001a remains in PAPER on its own record). Nothing was adjusted to make it
  pass; only the erroneous input was corrected. SLOW by Amendment 1 from its own screen rate: 131/2101 = 0.0624/session
  x 126 = **7.86 projected trades in six months**, far under 40 — background paper, no queue slot, judged at 40 trades
  however long that takes. Flagged as S008 is: dollar-positive on a slightly negative average R on the MNQ market
  decision basis, so SCREEN (a dollars question) passes while s.6's KEEP (avg R > 0) is not yet answered.
- **S007 does not flip** and was not re-run: its gross is +0.1726 pt/trade, below even the cheapest of the four costs
  (0.495 pt, NQ limit, itself optimistic). MNQ market -$3,438.67, MNQ limit -$2,676.17, NQ market -$17,459.20, NQ limit
  -$9,833.73. **The KILL stands**, its salvage stays spent, and it is not registered in the paper book.

THE LESSON, and it is the one that matters more than either verdict: **when a shared input turns out to be wrong, the
re-check is owed to EVERY decision that input produced, not just to the most recent one.** The cost-correction cycle
rescreened the two candidates that were in front of it (S007, S008) and stopped there; S001 sat killed for a day on a
number the project had already disowned. The cheap systematic sweep — every SCREEN row in the registry, recomputed
against the corrected constant — takes minutes and is the only way to know the list is exhausted. It is now exhausted:
two kills existed, both have been rechecked, one flipped. A correction is not finished when the thing that exposed it
has been fixed.

## 2026-09-16 (11:00 am CT scheduled cycle) — S008: the cost budget run BEFORE the freeze, and the candidate refused on it

**The 9:00 am lesson ("ask for per-trade edge first, fire rate second") was applied as
a GATE this cycle rather than as a post-mortem, and it stopped a candidate at SPECIFY
for one third of S007's cost.**

S008 (late-day constant-leverage rebalance continuation) was sourced from market
mechanics with a genuinely forced counterparty: constant-leverage ETFs, variable-
annuity hedges and risk-parity programmes must rebalance in the direction of the day's
move into the 16:00 ET NAV clock, price-insensitively, with notional roughly
proportional to the day's return. Whole trade written: entry at the 15:00 ET next-bar
open when |Close(15:00) − Open(09:30)| ≥ 0.5 × the trailing-20 median 09:30–15:00
range, direction sign(M), stop 0.50 × that range, target 1.5R, flat 15:55 ET, 1 micro.
**Fire rate 0.4390/session → 55.3 trades in 126 sessions: NOT SLOW.** The frequency
half of Amendment 1's preference worked on the second try as it did on the first.

**The budget, written into the spec before any outcome was looked at:** $6.00 ASSUMED
per micro round trip ÷ $2.00 per MNQ point = **3.00 index points**, so a candidate
must earn a gross expectancy of **≥ 9.0 points per trade** (3× cost). **The specified
cell earned +2.55 gross points (n=708, t=2.11) — −0.45 points NET, 3.5× short.**
Monetization ruled NO CREDIBLE PATH, which directive s.4 sends to LEARN *without a
screen*. No spec hashed, no module written, no SCREEN row spent.

1. **THE INTRADAY DIRECTIONAL DRIFT AVAILABLE ON NQ IS 1–6 POINTS, AND THE ROUND TRIP
   IS 3.** Thirty-six continuation cells across six decision times (10:00–15:30 ET)
   and four move thresholds all land between −0.9 and +5.5 gross points. The RTH VWAP
   2σ-band reversion — `detect_vwap_reversion.py`'s shape moved off its 08:30
   pre-market open to the 09:30 RTH open, with a real 1:1 stop and a VWAP target —
   fires on **92.7% of sessions** at **gross +0.043R** on a median 17.6-point risk,
   i.e. −1.55 points net, with a FLAT edge across distance buckets (+0.098/+0.038/
   −0.014/+0.012/+0.082). This band is now the project's reference number: an intraday
   candidate has to explain why it sits outside a range nothing tested has left.
2. **THE SINGLE BEST CELL OF A GRID IS NOT A CANDIDATE.** T=13:30, z≥0.5 came back
   +5.54 gross points at t=2.93 — still short of the budget, and the maximum of 36
   cells. Taking it would have been the same ex-post selection S001's and S007's
   salvages each refused. Refused again, in a third context: at SOURCE, before a
   freeze, where refusing is cheapest.
3. **THE VALIDATED MAGNITUDE FACTS SIZE A TRADE; THEY DO NOT CREATE ONE — AND ONE OF
   THEM POINTS THE WRONG WAY FOR A FIXED COST.** The quiet-midday → expanded-afternoon
   fact selects days whose afternoon range is *smaller in absolute points* (median
   27.4 vs 38.2): expansion measured against a compressed midday is not expansion in
   the units a $6.00 cost is paid in, so conditioning on it makes the cost problem
   worse. The wide-opening-range fact (hyp-000162 / M30) splits 48.3% of sessions and
   leaves the morning continuation at +3.1/−0.8/+0.7/+1.1 points (t = 1.05/−0.30/
   0.27/0.43). A bigger expected range widens the stop; it does not supply the edge
   that stop protects. Same answer Stack A (hyp-000161) gave about the expected-range
   regime as an entry filter, reached this time from the cost side.
4. **THE FIRE RATE AND THE PER-TRADE EDGE PULL AGAINST EACH OTHER IN THIS BOOK.** The
   only two candidates that clear 40 trades in six months (S007 at 91.5, S008 at 55.3)
   are exactly the two whose edge cannot pay $6.00; the only strategy with a real
   per-trade edge (S003, +$379/trade, +0.396R) projects 1.3 trades in six months. That
   is an observation for LEARN and nothing more — Amendment 1 stands as Jason wrote it
   and the SLOW label already handles the clock. Its only operational consequence is
   sourcing ORDER: ask the budget question first and accept whatever fire rate the
   surviving structure has.
5. **WHAT WOULD CHANGE THE ANSWER IS THE COST, NOT A FILTER.** No knowable condition
   in S007's menu found an edge and this study found the family-level reason why. The
   levers left are a MEASURED cost basis from B4b (the 3.00 points is an assumption
   and could be materially smaller), a longer hold in which forced flow accumulates,
   or a mechanism whose forced participant moves tens of points. The S008 mechanism is
   not refuted; what is refuted is that it is worth $6.00 a trade.

Detail: `research/studies/S008-cost-budget-2026-09-16.md`,
`research/infrastructure/strategy-specs/S008-late-day-rebalance-continuation.md`,
`src/study_s008_intraday_cost_budget.py`, `data/study_S008_cost_budget.json`, registry
rows SOURCE/SPECIFY/LEARN in `research/ledger/strategies.jsonl`.

## 2026-09-16 (9:00 am CT scheduled cycle) — S007, the first Amendment 1 intraday candidate: KILLED at SCREEN, salvage spent, nothing spawned

**The sourcing preference worked. The strategy did not, and it failed for the one
reason a daily-firing strategy fails.**

S007 (opening-range break continuation, opening-range-scaled stop) was the first
candidate sourced under Jason's Amendment 1 preference for intraday strategies that
trade most days. It took the one event this project already knew fires almost every
session — the break of the 09:30–10:00 ET opening range, which `src/base_entry_b3.py`
fires on 74.7% of sessions as *plumbing with no claimed edge* — and put a real trade
around it: a 0.10 × width decisiveness requirement, a stop scaled to the opening range
(0.50 × width) from the project's own validated magnitude fact hyp-000162 / M30 rather
than B3's unconditioned far-side stop, a 1.5R target justified by that fact's symmetric
excursion result, a 10:00–13:00 ET window covering the midday session the fact
describes, and a mechanism paragraph naming the counterparty: the short-term liquidity
provider who faded the open, whose inventory is underwater on a decisive break and is
covered mechanically in the direction of the break.

**Screen (Discovery, 2,101 sessions): 1,525 trades, net -$8,623.67 at 1 micro, 39.6%
wins, avg -0.2459R. Rate 0.7258/session → 91.5 trades in six months, NOT SLOW.**

1. **THE FREQUENCY PREFERENCE IS DOING ITS JOB — ON THE FIRST TRY.** Every other
   strategy in the book projects 1.3 to 21.8 trades in six months against the 40 the
   verdict needs. S007 projects 91.5. Amendment 1 asked for a candidate whose clock can
   actually run and the first attempt under it produced one. That is worth separating
   from the result, because the result was bad.
2. **FREQUENCY AND EDGE TRADE AGAINST EACH OTHER, AND COSTS ARE WHERE THE TRADE IS
   SETTLED.** Gross was **+$526.33** — positive. Assumed costs were **$9,150.00**. The
   gross edge is **+$0.35 per trade** against a **$6.00** assumed round trip:
   seventeen times the edge. A strategy that fires most days must clear roughly **0.10R
   of cost every single day**, and this is now the project's reference number for what
   an intraday candidate has to beat before it is worth specifying. The cost bar is not
   a detail that gets applied at the end; for a daily-firing trade it *is* the bar.
   Sourcing under the new preference should ask for the per-trade edge first and the
   fire rate second.
3. **AN EX-POST SALVAGE CONDITION IS A TAUTOLOGY, AND THE KNOWABLE HALF IS THE TEST.**
   The salvage menu's condition 2 came back strongly positive on TREND days (n=658,
   +$6,469.93, +0.178R, 54.9% wins) — but that label is the day's *own* range, not
   known at the 10:00–13:00 ET entry. Spawning on it would have meant "this breakout
   strategy works on days that broke out." S001's salvage made this identical ruling on
   this identical condition, so the precedent already existed and was followed. What is
   new here is the *second step*: the knowable half of the same menu condition —
   prior-day range against its own trailing-20 average, known before the open — was
   split as well, and **both sides lose** (PRIOR_EXPANDED -$5,043.69 / -0.266R;
   PRIOR_CONTRACTED -$3,345.74 / -0.221R). That converts "we refused to use an ex-post
   label" into a finding: **range expansion is not forecastable from the prior session
   for this trade.** When a salvage condition is ex-post, split its knowable half rather
   than only declining the ex-post one — the refusal then produces knowledge instead of
   just withholding a spawn.
4. **DOLLARS-POSITIVE ON NEGATIVE R IS NOT A CONDITION.** The AFTERNOON side was
   +$52.28 across 55 trades at -0.072R. S001's pre-09:30 side was +$24 at -0.300R and
   was refused. Same shape, same answer. A handful of dollars on a losing per-trade
   expectation is noise wearing a filter's clothes.

Menu 1 (VXN), menu 4 (news) and the spec-named direction split lose on both sides;
the spec-named narrow-opening-range and gap-open conditions are subsumed by menus 1
and 2. **No condition taken, one salvage spent, nothing spawned, S007 stays KILLED.**
The mechanism is not refuted — what is refuted is that it is worth $6.00 a day.
Anything revisiting it has to start from a larger per-trade edge, because no knowable
filter in the menu found one.

Detail: `research/studies/S007-screen-and-salvage-2026-09-16.md`, `data/screen_S007.json`,
`data/salvage_S007_2026-09-16.json`, registry rows SOURCE/SPECIFY/FREEZE/SCREEN/KILL/
SALVAGE/LEARN in `research/ledger/strategies.jsonl`.

## 2026-09-15 (11:00 pm CT scheduled cycle) — S003 (M24 month-end reversal) SPECIFY -> FREEZE -> SCREEN -> PAPER

A closed statistical effect can still be a profitable trade, and this is the first
clean demonstration of it under the standing directive's revamp premise (s.9).
M24 / hyp-000157 was closed 2026-09-13 P1_FAIL: LOW-tercile next-month return net of
NQ's own drift +0.0112, block CI (-0.0005, +0.0224), n=27 -- a near miss by the old
academic bar, with MONETIZATION never run. Built as a whole trade (long the 15:59
open of a heavily-sold month's final RTH session, flat at the 15:59 open of the next
month's final RTH session, stop entry - 4.0 x ATR20 as a disaster cap, 1 micro,
ASSUMED $6.00/RT), it screened at **+$8,339.07 net over 22 Discovery trades, 77.3%
wins, +0.3956 avg R net**. S003 entered PAPER the same cycle.

What is and is not new here:
- The +0.396 R is NOT a bigger effect than +0.0112. It is the SAME effect denominated
  in a 4.0xATR20 stop instead of in a month of drift. Anyone comparing the two numbers
  without that conversion will overstate what changed.
- What genuinely changed is the question. Scan 031 asked whether the monthly mean
  clears a CI; the screen asks whether the trade makes money after costs. The directive
  retired the first as a gate for exactly this reason.
- S003 is the FIRST candidate in the paper book that is not cost-fragile: average risk
  467.7 pts ($935 at 1 micro), costs $132 against $8,471 gross = 1.6%. S001a and S002
  are both cost-fragile. So S003's paper record will test the effect, not the cost
  assumption -- the most informative paper slot the book has held.
- The 4.0xATR20 disaster cap fired on 5 of 22 holds, more often than the spec expected
  a "should almost never be the exit" cap to fire. Recorded as a fact about the spec's
  own expectation, not adjusted (s.13: a change is a FIX ONCE, never an edit).
- Frequency remains the structural problem: ~1 trade a month at most, ~1 month in 3 on
  the condition. The 6-week judgment point will arrive under the 15-trade floor, which
  is a KILL as unjudgeable (s.6) -- the same fate S001a faces. The screen, not the
  paper clock, is where a monthly-frequency strategy carries its information. This is
  now true of two of the three candidates in the book and is worth Jason knowing:
  the 40-trades-or-6-weeks rule cannot judge a strategy that fires monthly.
- Method note carried forward: a statistical cell's frozen boundary (Scan 031's
  Discovery-wide tercile) is inadmissible in a strategy, because a trader at a month
  end cannot know it. Replaced with the same split measured over a trailing 24
  month-end window -- knowable at decision time, untuned, and it is what any future
  revamp of a tercile-conditioned effect should do.

## 2026-09-13 (interactive, off-cycle) — perspective scoping for Sept 19 checkpoint
Jason asked whether the project's search perspective needs to shift: (1)
incorporating scheduled-event/"chatter" data, and (2) reading order
flow/market depth more like a discretionary trader, rather than only
backward-testing documented mechanisms. He then asked to have this ready
to think about ahead of the Sept 19 checkpoint.
Scoping note written: research/infrastructure/perspective-scoping-2026-09-13.md.
Key findings: (1) event-calendar data is already in use (FOMC/NFP/CPI
tested on free public dates); a related idea is already queued for
LEARN/Mechanism/Director review. (2) Order-flow/depth data at ~$54k/yr
was priced Sept 3rd and explicitly rejected by Jason Sept 7th ("drop it
entirely") — he is knowingly revisiting that closure now, told him so
directly along with a correction (I had inaccurately told him I'd priced
it "earlier tonight" — that was wrong, it was Sept 3rd/7th). Found a
materially cheaper, previously-unpriced alternative: Databento Standard
at $199/mo, no annual commitment, forward-collection only (1-month
rolling window, no deep history) — ~$2,400/yr vs ~$54k/yr, different
proposition (build forward, not buy history). (3) The "read like a
trader" angle is already scoped and mostly run: 5 candidate intraday
behaviors from the Sept 8th pivot were all tested, one (range-contraction)
survived Validation — the project's first-ever Validation survivor. That
surfaced a real open fork (pair the 3 surviving volatility facts with a
new directional signal, vs. treat them as pure characterization) that has
been sitting undecided since Sept 9th and needs no new data — flagged as
probably the highest-leverage decision available for the 19th.

- 2026-09-13 (11:00 am CT scheduled cycle): drew Entry 27/M23 (London-open
  volatility burst, 6E). Scan 030 (4 cells): GATING P1_PASS -- London-open
  hour |return|/ATR14 credibly exceeds the unconditional hourly baseline
  (diff +0.0400 ATR, ci_90=[+0.0279,+0.0550], n=891 days, largest-n
  open-scope entry so far); pre-London hour secondary cell does NOT show
  the same elevation (specificity confirmed -- effect concentrated at the
  session boundary, not broader overnight elevation); not a first-minute
  print artifact (share 0.194). A real, clean, well-powered structural
  finding, first genuine (non-ambiguous) P1_PASS in the M20/M21/M23
  open-scope-volatility family. Director: CONTINUE. Monetization: per
  the mechanism doc's own Section 9, 6E has zero base strategies to size
  and this fires daily (unlike M20/M21's rare events) -- credible path
  via a standalone opening-range breakout/fade strategy, but designing
  one is new work outside this hypothesis's registered scope, so deferred
  to a fresh sourced entry rather than invented mid-cycle. hyp-000156
  logged PROMISING (real characterization, live monetization path, not
  yet a tested strategy). Filed KNOWN TRUE alongside M20/M21.
  Sourced Entry 30/M26 to restore the shelf floor: Level Sweep Reversal
  (close_min_distance variant), conditioned on prior_day_narrow (the
  project's own already-validated range-contraction state fact), rather
  than the bare unconditional pattern (six variants, all closed,
  non-credible). Origin: this cycle's earlier interactive conversation --
  Jason asked directly whether a pattern that failed on average could
  still work under specific conditions. This is the first concrete test
  of that question, and it directly serves the September 19th
  hypothesis-generation-methodology deep dive he asked to prioritize.
  Mechanism doc explicit on why this is not the overfitting trap the
  question could easily become: the conditioning variable was chosen and
  validated for an unrelated purpose before this hypothesis existed, not
  searched-for after seeing Level Sweep Reversal's own results. NOT
  drawn this cycle -- budget-use deferral (a full Discovery scan plus its
  disposition already ran); first in line next cycle. Shelf 3/3
  restored (Entry 28, 29, 30).

## 2026-09-13 (1:00 pm CT scheduled cycle) — M24/Entry 28 closed (P1_FAIL), M27/Entry 31 sourced

Drew Entry 28 (map M24, month-end payment-cycle reversal, NQ): Scan 031,
10 cells, 1 gating, thin-sample family (80 usable calendar months, ~27
per tercile, block=3). GATING P1 (LOW-tercile next-month return net of
NQ's own unconditional next-month drift) came back close but not
credible: mean=+0.0112, ci_90=(-0.0005,+0.0224) -- lower bound sits just
barely on the negative side of zero. P2 (LOW-minus-HIGH asymmetry) also
not credible. Not confounded with the closed M6/hyp-000108 turn-of-month
effect (first-3-session share 0.452, below the 0.5 kill threshold).
Director concurred with closure despite the near-miss CI -- this
project's own discipline treats a near-miss the same as a clean miss;
no re-test authorized without new information (a longer data history or
a materially different instrument). Logged hyp-000157 (REJECTED). Entry
closes; dropped the shelf to 2/3.
Sourced M27/Entry 31 (Tokyo FX session open, 6E) to restore the shelf
floor: a direct companion to M23 (same day's earlier P1_PASS, London-
open volatility), applying the identical pre-existing methodology
(unconditional-hourly-baseline comparison, specificity check, kill
check) to a distinct, non-overlapping session boundary (19:00-20:00 ET
Tokyo open vs. M23's 03:00-04:00 ET London open) with its own
participant story (Japanese exporter/importer flow, Asian real-money
accounts, Tokyo bank desks). Mechanism doc written before any scan, per
standard discipline; not drawn this cycle (budget-use deferral). Shelf
3/3 restored (Entry 29, 30, 31).

## 2026-09-13 (3:00 pm CT scheduled cycle) — M25/Entry 29 closed (P1_FAIL), M28/Entry 32 sourced

Drew Entry 29 (map M25, monthly options-expiration week delta-hedge
unwind, NQ): Scan 032, 10 cells, 1 gating, calendar-week partition
(80 expiration weeks vs. 269 non-expiration weeks). GATING P1
(expiration-week return, ATR14-normalized, net of NQ's own unconditional
weekly drift) came back not credible: mean=+0.1872, ci_90=(-0.0291,
+0.3950) -- wide CI spanning both signs, a clean non-credible result
(unlike M24's near-miss). P2 (expiration minus non-expiration) also not
credible. Individual day-of-week cumulative cells (Tue/Wed/Thu/Fri) were
credibly positive but non-gating, descriptive only -- does not override
the failed gate, same discipline this project applies elsewhere.
Director concurred with closure. Logged hyp-000158 (REJECTED). Entry
closes; dropped the shelf to 2/3.
Sourced M28/Entry 32 (pre-holiday effect, NQ) to restore the shelf
floor: a well-replicated, multi-decade equity-market anomaly
(Lakonishok-Smidt 1988, Ariel 1990) never before tested against NQ in
this project -- flagged honestly as carrying a weaker named-participant
mechanism story than this project's usual standard, included because
the empirical regularity itself is unusually well-replicated. Mechanism
doc written before any scan; not drawn this cycle (budget-use
deferral). Shelf 3/3 restored (Entry 30, 31, 32).

## 2026-09-13 (interactive, ~3:00-4:40 pm CT) -- Checkpoint pulled forward; six outside reviews; freeze lifted for a named list
- Jason added "swing trading with a particular exit strategy" to the checkpoint agenda (Topic 6 in the deliberation file), then pulled the September 19th conversation forward to today and gathered six outside reviews of Tony. All six consolidated, nothing dropped, in research/infrastructure/outside-review-synthesis-2026-09-13.md (v2): consensus matrix, each review in full, conflicts, candid observations, 17 decisions, build sequence, glossary.
- Unanimous verdict across the six: CONTINUE, no pivot; validation machinery is the asset; idea generation is the bottleneck; the validated volatility facts are state variables to build a risk/sizing layer from, not consolation prizes; look at the data first (Observatory), then write the mechanism; conditional retests only via one pre-registered condition; exit rules frozen before results; no data purchase yet.
- DECISIONS (Jason): freeze LIFTED for the named list (D2-D17 except D12); paper-trade the Risk/State Engine alone first (no directional trigger); un-park execution-clock measurement; Sidak stacking diagnosed read-only before any bar change; Integrity Gate gets both blind-packet tightening and a mechanical test suite; Observatory free-look rule adopted; sourcing emphasis shifts to map/structure with a higher bar for literature (no hard quotas); conditional-retest protocol adopted (8 conditions); M20/M21 reclassified into the scheduled-event volatility family with M23 (micro contracts exist); VXN-minus-realized-range sourced as a new state variable; registries/forms in cheapness order; yield metrics replace "hypotheses closed"; Data Acquisition Trigger written.
- D11 swing strategy: Jason has not named an exit rule -- he asked Tony to PROPOSE THE QUESTION (what a swing strategy looks like in Tony's terms and how it fits the current pipeline) so he can get outside feedback: research/infrastructure/swing-strategy-question-2026-09-13.md. Nothing built until he returns with an answer.
- D12 goal/capital fit ($1,000/mo vs $300 budget vs $600-900/day per micro, raised only by review A): DEFERRED by Jason until paper trading is actually running.
- DATA ACQUISITION TRIGGER (D17, from review B), now the standing rule replacing "we aren't buying": purchase data only when ALL of (1) an existing price-based discovery establishes a credible mechanism; (2) the missing variable is specifically required to test it; (3) expected information gain is high; (4) the candidate cannot be adequately falsified with current data; (5) the likely edge justifies the cost; (6) the purchase resolves a defined decision. The $20/month cap and the $5+ sign-off rule are unchanged.
- The September 19th trigger stays as the weekly review; its checkpoint questions are now largely answered and it becomes a progress review on U1-U10 plus the swing-question feedback.
- 2026-09-13 ~4:55 pm CT (Jason): "We're no longer doing the 19th weekly review. We're doing all of it right now." Checkpoint held today: research/weekly/2026-09-13.md. Sept 19th trigger deleted. Freeze fully lifted -- UPGRADE QUEUE v3 is the approved work, nothing else remains frozen. Routine Saturday weekly reviews resume September 26th (cycle-written, no trigger).
- 2026-09-13 ~5:40 pm CT (Jason: "I don't think we made enough change towards developing more opportunities to finding and discovering more strategies" -- correct, and acted on): built src/idea_factory.py, the generation engine. 11 market states x 8 session windows x 5 outcomes (move, range, MFE, MAE, time-to-extreme) on the Discovery slice, descriptive, no ID spent, no scan registered. Emits a RANKED CANDIDATE QUEUE, not a table. SOURCING RULE v3 adopted: cycles now source FROM the queue instead of inventing one idea each. TIMING RULE adopted and binding: a state may only be crossed with a window starting at or after the moment the state is known -- added because run 1 ranked vwap_dist_vs_atr (known at the close) against the same session's move at z=-20.4, a definition restated as a discovery; 315 cells dropped on that rule in run 2. RESULT of run 2: 1045 cells ranked, 143 candidates in 19 families, and ZERO direction families -- at far higher resolution and with a full outcome battery, the "direction is noise in this data" finding holds. Every candidate is about SIZE of movement or EXCURSION (how far a move runs for and against before it ends) -- the first feeds the Risk/State Engine, the second is exactly what exit rules are designed from.
- 2026-09-13 ~6:00 pm CT (Jason, strategic correction): "A very important distinction should be this is an end goal trading bot, we should keep that envision bc our overall goal should be working to that not being the best research tool." Adopted as the project's ordering principle. docs/BOT_ROADMAP.md written and now OUTRANKS research/NEXT_UP.md: nine bot milestones B0-B9, current status B0 done / B1 partial / B2 spec'd / B3-B9 missing. Key reframe: a trading bot does not need an edge to exist (signal -> size -> order -> fill -> monitor -> kill); Tony has validated material for SIZE and nothing for SIGNAL, so B3 is a deliberately ordinary frozen placeholder entry, labelled validation_status="placeholder" end to end, never claimed as an edge and never reported as one. Stated plainly in the roadmap: such a bot is expected to roughly break even minus costs -- its purpose is to make the machine real, measure what execution actually costs, and test whether the volatility layer improves a base strategy's risk-adjusted behaviour. Real capital still waits for evidence; B8 remains Jason's alone. BINDING ORDERING RULE: every cycle advances the lowest-numbered incomplete bot milestone it can before working any research item. Research is now a FEEDER with exactly two jobs -- replace B3 with a real edge (what the Idea Factory queue is for), and improve B2 with better state variables.
- 2026-09-13 7:00 pm CT scheduled cycle (designated full-pipeline test; all ten roles exercised): BOT MILESTONES B1/B2/B3 DONE in one cycle -- src/risk_state_engine.py (frozen params on Discovery, residual VXN combination, no P&L claim, daily log), research/infrastructure/base-entry-b3-spec.md + src/base_entry_b3.py (ORB 09:30-10:00 / window 10:00-11:30 / entry next-bar open / placeholder label, 2,717 signals over 3,638 sessions, 0 lookahead). Two defects found by the test: (1) the bot layer inherited the research Holdout boundary from the default loader -- its "latest session" was April 6th; fixed with apply_holdout=False, documented; (2) both legacy detectors (detect_setups.py ORB, detect_ib_breakout.py) open their window at 08:30 in NY-stamped data -- pre-market, not the RTH open; neither reused, noted in the B3 spec. RESEARCH: hyp-000156 (M23) Statistical PASS on all four questions including Sidak at N_discovery=451 (raw [0.043,0.067] -> adjusted [0.026,0.081]) -> VALIDATION CANDIDATE; first fresh-subagent BLIND GATE of the day returned CONDITIONAL with five conditions (paired-vs-unpaired construction drift between scan and stat stage; freeze/hash the Validation script with Sidak CI and N_BOOT>=20000; DST/ATR-warm-up/provenance; explain strategy_origin convention; density + first-5-min kill diagnostics) -- accepted, resolved next cycle BEFORE asking Jason for the 6E Validation-slice data pull (6E on disk covers only 2015-01-01..2021-10-03). M27 closed (Scan 034, hyp-000160): the Tokyo-open hour is credibly QUIETER than the US-session baseline -- the London burst is specific to London. SOURCING RULE v3 used for the first time: M30 (opening-range width -> midday range/excursion) and M31 (prior-day volume -> first-30 range) written from the queue with LEARN consulted by name. U8 retroactive closure forms filed for 12 closures. Portfolio pass on the fact registry written. Platform: git lock files handled by src/git_unlock.sh before every git command.
- 2026-09-13 ~9:00 pm CT (staff meeting, Jason present; record research/infrastructure/staff-meeting-conditional-stack-2026-09-13.md): CONDITIONAL STACK hypothesis format ADOPTED, disposition MODIFY. A stack = context -> location -> trigger, evaluated in fixed order, pre-registered as ONE hypothesis = ONE trial (paired family = two), frozen as a whole, spec HASHED into SCAN_REGISTRY before any look. Binding rules: (1) 2-layer ceiling until one result; (2) first test PAIRED, claim is the difference; (3) both formats run, one stack in flight at a time; (4) floor default 100 occurrences + MDE pre-registered by Statistical, UNDERPOWERED closes it and consumes an attempt, definition never loosened; (5) one mechanism per layer + explicit interaction claim, "filters losers" rejected at Mechanism; (6) each layer's known-at precedes the trigger, context before location; (7) K look-cells from the free-look interaction table recorded with the hash and attached to the blind packet; (8) `stacks_attempted` counter; (9) a stack of individually-closed variables is a resurrection unless the interaction is the stated novel claim; (10) format kill = two powered nulls. Stack A first (B3 breakout alone vs inside HIGH expected-range context -- the bot's own B2-vs-B3 question); Stack B (ICC pullback, deterministic) second only if A closes. Build ~3 cycles (U25-U30), no data purchase, no rule weakened, bot milestones still outrank it. ICC videos are the source of the SHAPE, not a candidate.
- 2026-09-13 ~9:55 pm CT (scheduled cycle, first under the conditional-stack format): STACK A -- the first conditional stack -- ran and closed as a POWERED NULL (hyp-000161, scan_035, spec hash 4df7b408). Gating difference (B3 opening-range break INSIDE the top-tercile expected-range context minus OUTSIDE it) = +0.0247R, CI90 (-0.0496,+0.0976), Sidak at Discovery N=460 (-0.1401,+0.1896), n=566 vs 977 against a floor of 100. NEGATIVE KNOWLEDGE, stated plainly: the expected-range regime known at the prior close does NOT change the forward outcome of an opening-range breakout on NQ; the interval excludes any effect above +0.19R while the mechanism implied ~0.23R. The individual layers are untouched -- this falsifies the INTERACTION only. Consequence for the bot: the Risk/State Engine (B2) is a sizing and permission layer and is NOT an entry filter; the BASE vs BASE+B2 paper comparison keeps that as its stated prior and measures distribution, not expectancy. Do not retest expected-range tercile x opening-range break in any variant of edges, windows or targets -- same question. Format accounting: 1 of the 2 powered nulls that would close the conditional-stack format; the 2-layer ceiling lifts to 3 now that one result exists. Also this cycle: hyp-000156's five blind-Gate conditions resolved IN WRITING before any Validation data exists (one test = paired per-day diff against a baseline named honestly as US-RTH hourly; src/validate_hyp156.py written and hashed e679fba6; Sidak as the rule max(20,N); DST handled by non-gating diagnostics rather than a changed window; ATR warm-up from the Discovery tail; provenance/roll parity asserted) -- the 6E Validation-slice data pull is now Jason's $5+ call. And U24: the ledger refuses VALIDATION CANDIDATE (or later) without a validation-slice row, so the September 13th mislabel cannot recur.

## 2026-09-15 (Day One of the STANDING OPERATING DIRECTIVE, ~5:30-8:30 pm CT)
- STRUCTURAL: Jason's standing operating directive (research/infrastructure/standing-directive-2026-09-15.md, verbatim, md5 aa496b87...) replaces the CI/holdout promotion bar with the paper record as the evidence for a strategy: SOURCE -> SPECIFY -> FREEZE -> SCREEN -> PAPER -> JUDGE (40 trades / 6 weeks) -> KEEP / FIX ONCE / KILL -> SALVAGE (menu only) -> LEARN. Retired in code: the shelf floor, the draw-thin rule, the 20-trial directional cap (research/ledger/directional_lane.json marked retired, five null trials kept), the old busy-work definition (src/cycle_budget.py movement() now = registry stage change / candidate paper trade / verdict / salvage check). Built: src/strategy_registry.py + research/ledger/strategies.jsonl (the single record of every candidate), src/paper_book.py (per-strategy record net of ASSUMED costs, 1/5/10 micros, worst streak, survivable daily limit, cost-fragile), the PAPER BOOK section in src/session_report.py, the paper-book line in src/cycle_preflight.py, src/screen_strategy.py (one number, paper-loop bookkeeping), src/salvage_check.py (the s.7 menu), src/revamp_list.py -> research/ledger/revamp_list.json (137 closed hypotheses: 27 top, 2 middle, 108 bottom). The execution dummy and B3 stay PLUMBING (Jason's decision): shown as one line each, never judged.
- LEARN (S001, first candidate through the loop): the Level Sweep Reversal on compressed prior days LOST MONEY at the screen on the micro cost basis (131 trades, -$116.38 at 1 micro, +0.099R gross / -0.172R net). Salvage by the menu: the edge, where it exists, is at PRIOR-DAY levels (40 trades, +$353.70, +0.080R, 57.5% wins); PRE-MARKET levels are noise (91 trades, -$470.08). VXN-LOW days are dollar-positive but avg-R negative (a few large-risk winners); shorts lose (-0.321R) as the spec predicted; news days lose. S001a (prior-day levels only) spawned at SPECIFY; the Level Sweep Reversal family's one salvage is spent. Detail: research/studies/S001-screen-and-salvage-2026-09-15.md.
- LEARN (the 72% placebo-RED rate, explained once per directive s.9): an arithmetic property of the placebo legs on magnitude cells -- the inverted leg is the complement and sits at exactly 50% of the effect by construction (11 of 18 REDs, ratio pinned at -0.50, the GREEN twins at 0.4995), and the shifted leg re-selects 51-88% of the same days for persistent states (7 of 18). Not evidence about the 25 effects. Entries 37-61: 24 marked SIZING-INPUT CANDIDATE (M29/M30/M31 families), Entry 60 CLOSED. research/integrity/placebo-red-explanation-2026-09-15.md. batch_screen.py is never run again.


## 2026-09-15 (7:00 pm CT scheduled cycle, first ordinary cycle under the directive)
- S001a (Level Sweep Reversal, compressed prior day, PRIOR-DAY levels only) is the FIRST STRATEGY IN PAPER: specified + frozen (e509b59), screened on Discovery (40 trades, +$353.70 net at 1 micro, 57.5% wins, +0.080R net -- cost-fragile; reproduces S001's salvage cell by construction), entered PAPER via `bot_stack_paper_run.py --strategy s001a` (4 sessions since the B7 anchor scored, all no_signal). Expectation stated in its spec: ~0-1 trades per 6 weeks at the historical rate -> likely KILL on the s.6 15-trade floor; no salvage of its own. The paper record decides (research/studies/S001a-screen-2026-09-15.md).
- LEARN (S002 SOURCE -> SPECIFY, the M15 night leg through the s.7 menu, src/study_s002_night_leg_menu.py): the raw close-to-open carry on NQ is NQ's drift minus a 3-point cost drag -- +3.55 pts gross a night against 3.0 pts of ASSUMED micro costs, +$1,784.50 over 1,631 Discovery nights with a -$6,434 drawdown and 3 losing years of 7. Every menu side is dollar-positive because the drift is; the net is CONCENTRATED: prior_day_narrow nights (22% of sessions) carry 91% of it at +5.2 pts a night with a -$735 drawdown; scheduled-news nights (12%) carry 97% at +7.4 pts (the 08:30 CPI/NFP releases sit inside the leg); the weekend leg loses -$3,401 (not a menu condition, not filtered). Design lesson: a carry trade on a micro lives or dies on B4b's measured cost; at 3 pts assumed, only the concentrated regime is worth a paper slot. S002 specified (NOT frozen) as the night leg on compressed prior days, with a cross-session exit in the paper loop named as the FREEZE prerequisite.


## 2026-09-15 (9:00 pm CT scheduled cycle)
- PLATFORM (the paper loop can now hold a position overnight): `_resolve_fill_outcome` scanned a single calendar-day frame, which is why S002 could not be frozen. Choice 7 in src/bot_stack_paper_run.py: a strategy declares an ABSOLUTE `market_context["exit_ts"]`, the bookkeeping walks the whole frame across the boundary (stop/target first touch, stop wins a tie) and the time exit books the first bar at or after that timestamp at its OPEN. The design decision worth keeping: the session-completeness guard was extended to the EXIT session rather than inventing an "open trade" row. A trade whose exit session is absent or in progress DEFERS its entry session whole -- nothing is written, nothing is force-closed, `session_end_fallback` is refused across a boundary -- so the append-only paper log never has to be revised, which is what the never-re-score rule (directive s.13) would otherwise have collided with. Same-session behaviour is unchanged by construction and proved so against a verbatim copy of the pre-change function (tests/test_cross_session_exit.py).
- S002 (overnight carry on compressed prior days) FROZEN, SCREENED and IN PAPER: 364 Discovery trades, +$1,446.10 net at 1 micro after ASSUMED costs, 53.6% wins, **+0.006R average** -- profitable in dollars and almost entirely eaten by costs. The general lesson, now twice observed (S001a +0.080R, S002 +0.006R): on a micro, a strategy sourced from a drift-bearing leg screens positive on dollars long before it has any edge per unit of risk, and avg R is the only number that separates them. B4b's MEASURED cost decides whether S002 exists at all.
- S002's first two paper trades are the spec's own "where this should fail" list arriving early: +0.9519R on a clean clock exit (2026-09-10 -> 09-11 09:30) and -1.0R stopped out on the Sunday 18:00 reopen (2026-09-11 -> 09-13), i.e. the weekend leg hyp-000145 ruled out filtering. Recorded per trade, not filtered, so LEARN can see it at judgment.

## 2026-09-16 (cost-correction cycle, Jason's Amendment 2) — the cost wall was inflated 2–3×, and what survives of it

**Jason caught a material error. The assumed cost constant, $6.00 per micro round trip =
3.00 index points, applied `src/integrity_checks.py`'s `COMMISSION_PER_SIDE_USD = 2.50` —
a FULL-SIZE E-mini (NQ) figure — to the MICRO (MNQ) contract the paper book trades. That is
roughly 3–10× too high on the commission leg and about 2.3× too high on the round trip.**
The corrected, sourced schedule now lives in `src/cost_model.py` and nowhere else
(write-up `research/infrastructure/cost-model-2026-09-16.md`; directive Amendment 2):

| | commission/side | fees/side | slippage/side | round trip | in POINTS |
|---|---|---|---|---|---|
| MNQ market entry+exit *(decision basis)* | $0.25 | $0.55 | $0.50 | **$2.60** | **1.300 pt** |
| MNQ limit entry *(OPTIMISTIC)* | $0.25 | $0.55 | $0.50 exit only | $2.10 | 1.050 pt |
| NQ market entry+exit | $0.85 | $1.60 | $5.00 | $14.90 | **0.745 pt** |
| NQ limit entry *(OPTIMISTIC)* | $0.85 | $1.60 | $5.00 exit only | $9.90 | 0.495 pt |

### 1. What survives of the "cost wall" conclusion, and what does not

**SURVIVES — the measurement.** The gross numbers were never wrong. The intraday directional
drift available on NQ really is a **1–6 point** band: 36 continuation cells land between −0.9
and +5.5 gross points, and the RTH VWAP 2σ reversion really does fire on 92.7% of sessions at
gross +0.043R on a 17.6-point median risk. Nothing in the correction touches a gross figure,
a fill, an exit or a t-statistic.

**SURVIVES — the shape of the problem.** Short-horizon intraday trades are still the most
cost-sensitive thing this project can run, and a fixed cost still eats a per-trade edge that
is measured in single points. The wall is real. It is just **half to a third as tall as Tony
said it was**, and the band it has to be compared against is 1.30 points on MNQ, not 3.00.

**DOES NOT SURVIVE — "a 2–5 point intraday drift cannot pay for a round trip."** It can. A
gross edge of 2.55 points per trade is **+1.25 points net** on MNQ at market and **+1.81 net**
on NQ at market. The S008 spec's closing line — "what is refuted is that $6.00 a trade is
affordable out of a 2–5 point intraday drift" — was refuting the wrong number.

**DOES NOT SURVIVE — the reference band as a kill line.** The VWAP 2σ reversion was recorded
as −1.55 points net per trade. At the corrected cost the same unchanged measurement is −0.54
net on MNQ market, −0.29 on MNQ limit, **+0.01 on NQ market and +0.26 on NQ limit** — i.e. it
crosses from "clearly dead" to roughly break-even on the full-size contract. That is a
descriptive study, not a screen, and nothing is being revived on it; it is recorded so the
number in the ledger is the right one.

**DOES NOT SURVIVE — the "3× cost" pre-screen.** It was Tony's invention. The standing
directive never contained it, and it was used to refuse S008 **without a screen**. Jason's
replacement rule: *at SPECIFY, reject only if the expected per-trade edge is below the
corrected per-trade cost itself; otherwise screen it* (`cost_model.specify_gate()`).

### 2. THE NEW STRUCTURAL FACT: IN POINTS, THE FULL-SIZE NQ COSTS HALF WHAT THE MICRO COSTS

0.745 pt against 1.300 pt at market; 0.495 against 1.050 on an optimistic limit entry. In
dollars the NQ round trip is 5.7× the micro's, but a point is worth 10× as much, so the fixed
commission-and-fee component spreads over ten times the notional while the tick of slippage
stays the same size in points. **A strategy whose per-trade edge lands between about 0.5 and
1.3 points is profitable on NQ and unprofitable on MNQ.** "The cost wall killed it" is
therefore, for that whole band, a statement about the CONTRACT and not about the pattern.
Every screen and the paper book now print all four combinations side by side so the two can
never again be confused. (The size question is separate and stays Jason's: NQ is 10× the risk
per trade at the same stop distance.)

### 3. EVERY LIMIT-ENTRY FIGURE IS AN OPTIMISTIC UPPER BOUND, AND IS LABELLED SO

A limit entry genuinely avoids paying the spread on the way in. What no historical screen can
model is that **a resting limit order does not always fill, and fills preferentially when the
market is about to trade through it** — adverse selection, which shows up not as a cost but as
a worse mix of trades. The screen fills every limit order by construction, so the limit column
is a **ceiling on what a limit entry could achieve, never an estimate of it**. `cost_model.py`
carries `optimistic: true`, the `(OPTIMISTIC)` label and the note on every limit row so no
printer can quietly drop it.

### 4. THE RECORD WAS RE-COSTED, NOT RE-SCORED — AND THE INTEGRITY GATE CAN SEE IT

Directive s.13: *the paper record is never adjusted, deleted, or re-scored.* **No paper fill
was touched.** Every entry, exit, exit reason and gross `pnl_usd` in
`research/forward_validation/bot_stack_paper_log.jsonl` is exactly what it was before this
cycle. What changed is the **cost overlay** `src/paper_book.py` subtracts from that unchanged
gross — and it now shows four overlays side by side on the same one record
(`paper_book.four_combination_overlay()`, `cost_model.overlay()`), with identical gross in
every row, which is the visible proof that the record itself was left alone. Frozen specs and
modules (S002, S003, S007) still quote the old $6.00 in their own text and were **not edited**;
the corrected cost is applied *to* them from `cost_model.py`.

### 5. WHAT THE RESCREENS SAID

- **S007 (opening-range break continuation): THE KILL STANDS.** Same frozen spec and module,
  same 2,101-session Discovery slice: 1,525 trades, gross +$526.33 = **+0.1726 points per
  trade**. MNQ market net −$3,438.62 (−1.1274 pt/trade, avg −0.1139R); MNQ limit −$2,676.12;
  NQ market −$17,458.73 (−0.5724 pt/trade); NQ limit −$9,833.73 (−0.3224 pt/trade). The gross
  edge is **2.9× below even the cheapest of the four costs**, so neither contract nor entry
  style rescues it. The correction changed the size of the loss, not the verdict. S007 stays
  closed, its salvage stays spent, nothing revived.
- **S008 (late-day rebalance continuation): REOPENED AS AN INPUT-ERROR CORRECTION, AND IT
  PASSES.** It had been sent to LEARN *without a screen* on two erroneous inputs — the wrong
  cost and the invented 3× budget. It was **rejected on an erroneous input, not on evidence**,
  so reopening it is neither a Salvage (none spent; S008 has never had one) nor a FIX ONCE (no
  rule of the trade changed). Specified in full, FROZEN in its own commit before any outcome
  data was read, then screened for the first time: 704 trades over 2,101 Discovery sessions,
  gross **+2.6851 points per trade**, and it **makes money in all four combinations** —
  MNQ market +$1,950.18 (+1.3851 pt/trade), MNQ limit +$2,302.18, NQ market +$27,316.22
  (+1.9401 pt/trade), NQ limit +$30,836.22. It is in PAPER, and at 0.3351 trades/session ×
  126 = **42.2 projected trades in six months it is NOT SLOW** — the first strategy in the
  book whose six-week clock can actually run.

### 6. THE FLAG ON S008, STATED BEFORE ANYONE IS SURPRISED BY IT

S008's screen is **dollar-positive on a slightly negative average R** (−0.0116R on MNQ market,
+0.0027R on NQ market): its winners carry larger risk than its losers, so the two measures
disagree. The SCREEN's question is the dollar one (directive s.2) and it passes it. But s.6's
KEEP criterion is **average R above zero**, so on this screen's shape S008 would not yet clear
a KEEP. That is for the paper record to settle at 40 trades, not to pre-judge here — recorded
now so the disagreement is on the table from the start rather than discovered at the verdict.
It is the same shape the S007 salvage refused ("dollars-positive on a losing expectation"), and
the difference is that there it was one ex-post slice of a losing strategy and here it is the
whole frozen strategy's own screen.

### 7. THE LESSON, WHICH IS ABOUT INPUTS, NOT ABOUT COSTS

**A number that every stage reads and no stage owns will be wrong for a long time before
anyone notices.** `COMMISSION_PER_SIDE_USD = 2.50` sat in a file called `integrity_checks.py`
— the file whose entire job is to assume the candidate is wrong — with a comment describing it
as a placeholder, and it was imported by the paper book and applied to a different contract
than the one it was written for. Nothing in the project's machinery could catch that, because
every check downstream was consistent with it: the screen, the salvage, the paper book and the
spec all agreed, and all agreed on the wrong number. Two things follow, and both are now in
place. First, **one owner per constant**: `cost_model.py` is the only place a cost is defined,
its components are named separately (commission / fees / slippage), and its sources are cited
in the file. Second, and larger: **Tony invented a gate the directive did not authorize and
then killed a candidate with it.** The cost error was an accident; the 3× budget was not. A
rule that is convenient — it ends candidates cheaply — and unaccountable, because no one wrote
it down as Jason's, is the more dangerous of the two failures. The directive says Tony does not
make rules; this is what it costs when he does.

---

## S009 — afternoon VWAP-completion continuation: the right sign, two-thirds of the size
*September 16th 2026, 3:00 pm CT cycle. SOURCE → SPECIFY → FREEZE → SCREEN → SALVAGE → KILL, one cycle.*
*Spec `research/infrastructure/strategy-specs/S009-afternoon-vwap-completion-continuation.md`; screen
`data/screen_S009.json`; salvage `data/salvage_S009_2026-09-16.json`.*

The candidate: at 13:30 ET, if price sits more than 0.30 × the 09:30–13:30 range away from that
window's VWAP, trade in the direction of the gap with a 0.50 × RNG stop, a 1.5R target and a 15:55
flat. The forced counterparty is agency execution — VWAP/POV algos with a fixed parent quantity, a
clock deadline and a back-loaded volume curve, which must work whatever is stranded on the wrong
side of the benchmark into the remaining hours regardless of price.

**The result, on 585 Discovery trades: gross +0.7113 index points per trade.** Not noise, and in the
direction the mechanism predicts — that gross edge is an implied ~40.9% hit rate against the 40.0%
breakeven a 1.5R/1R trade needs. But the pre-freeze gate (Amendment 2, the cost itself and no
multiple of it) needed **41.6%**, and the screen came in below it:

| combination | net/trade | verdict |
|---|---|---|
| MNQ market — **decision basis** | −0.5887 pt | loses |
| MNQ limit (OPTIMISTIC) | −0.3387 pt | loses |
| NQ market | **−0.0337 pt** | loses, by 3 hundredths of a point |
| NQ limit (OPTIMISTIC) | +0.2163 pt | the only positive column, and it is an upper bound |

**Three things worth keeping.**

**1. This is the first candidate where the corrected cost was genuinely the binding constraint and
the honest answer was still no.** S008 and S001 flipped from negative to positive when the cost was
fixed. S009 does not: at the corrected 1.300 pt it misses by 0.59 pt, and even at the full-size NQ's
0.745 pt it misses by 0.034 pt. Jason's reason for printing all four side by side was exactly this
question — cost wall or pattern? — and here the answer is *both, and neither is enough*: the pattern
is real and small, the micro's cost is nearly twice it, and the full-size contract closes almost the
whole gap without closing it. A strategy that needs the cheaper contract to break even has no margin
left for the slippage the broker will actually measure.

**2. The pre-freeze edge-vs-cost check did its job for the first time.** The gate was written as a
hit rate — "fails only if p ≤ 0.4155" — before any outcome was read, and the outcome landed at
p ≈ 0.409. That is the first time a specify-stage number has been precise enough to be *wrong by a
stated amount* rather than vindicated after the fact. Stating the gate in the units the screen will
report it in is worth doing every time.

**3. The biggest number on the salvage page was refused, and the reason is reusable.** Menu
condition 2's TREND side was +$2,615 at +0.137R on 301 trades — by far the best cell in the check —
and it is **ex-post-only**: the condition is the day's *full* RTH range, and the trade is decided at
13:30, so the 13:30–16:00 bars the trade's own outcome lives in are inside the variable that selects
it. A salvage condition has to be evaluable at the moment of the decision or it is not a filter, it
is a description of the trades that worked. The known-at-13:30 substitute is a different variable,
and it had already been measured and rejected at SPECIFY for making the strategy SLOW; swapping it in
would have been a re-specification wearing a salvage's clothes. Two more sides were refused: a
`direction = long` cell (+$1,397) because the mechanism is symmetric by construction and a long-only
version of it is a long-NQ result on a rising sample, and a LOW-VXN cell (+$502) because the spec had
*pre-named low volatility as where this should fail* — a slice that pays exactly where the mechanism
said it should not is a found slice, not a confirmation.

**What was taken:** menu condition 4, QUIET (no FOMC / CPI / NFP). It is a menu condition, it is also
the spec's own pre-named failure condition written before any outcome was read, it is known in
advance from a calendar, and its losing side is coherent — on a release day the morning VWAP is one
print and the afternoon is news, not execution schedules, with FOMC's 14:00 statement sitting inside
the holding window. n=518, +$333.28 at 1 micro. That spawns **S009a**, which enters at SPECIFY and
will be SLOW (0.2465/session → 31.1 projected six-month trades). S009 stays KILLED and its one
salvage is spent.

## 2026-09-16 (5:00 pm CT scheduled cycle) — S010: the falsifier fired again, and a queue item was stopped by its own calendar

**Two things were learned, and neither is about the cost model.**

### 1. A candidate can be blocked by the data its rule needs, and that is found at SPECIFY or not at all

S009a was next in the queue and was **not advanced**, for a reason discovered while writing its spec.
S009a's single added rule is "the session is not a scheduled FOMC / CPI / NFP release day". The
project's only sourced release calendar is `src/study_fomc_volatility.py`'s `FOMC_SET`
(2015-01-28 → 2021-09-22) and `src/study_economic_calendar.py`'s `CPI_SET` / `NFP_SET`
(2015-01-16 → 2023-12-12). The **Discovery slice is covered**, so the screen would have been sound —
but **the paper loop scores 2026 sessions**, which are past the end of every one of those lists.
That leaves two implementations and both are unacceptable:

- **fail-open** (a date not in the list is QUIET) makes every 2026 session quiet, so S009a's paper
  record would be **S009's record under a different name** — precisely the "strategy quietly swapped
  for a tweaked one" the Integrity Gate exists to catch (directive s.4, s.13);
- **fail-closed** (no coverage, no trade) puts a strategy into PAPER that can **never record a trade**.

Neither is a record, so S009a stays at SOURCE with its queue position and the blocker written on its
registry row. The remedy is a **data task, not a research one**: extend the three lists to the paper
dates with the sourcing discipline they were compiled under (federalreserve.gov press-release
archive; bls.gov year-by-year Schedule of Releases, cross-validated on day-of-week) — **never from
memory**. The generalisable rule: **a strategy's rule needs its input to exist over the window the
strategy will be JUDGED on, not just the window it is screened on, and that is a SPECIFY-stage
question.** S010a's spawn row carries the same check against `data/VXNCLS_MAX.csv` (ends 2026-09-02,
days stale rather than years, and it must still fail closed).

### 2. S010 — the second pre-freeze falsifier stated in the screen's own units, and it fired

S010 (thin-participation afternoon completion continuation) was sourced instead, under Amendment 1's
top preference: **NOT SLOW** (48.0 projected six-month trades), because S008 is the only strategy on
a live six-week clock. Mechanism: the same benchmark- and close-referenced execution S008 and S009
name, but selected on the **denominator** — market impact scales with size *relative to available
volume*, so a session whose 09:30–14:00 volume is below its trailing-20 median has to push an
unchanged completion residual through a thinner book.

**It lost in all four cost combinations** (MNQ market −$1,774.70 / −1.1078 pt per trade; MNQ limit
OPTIMISTIC −$1,374.20; NQ market −$8,855.93 / −0.5528 pt; NQ limit OPTIMISTIC −$4,850.93 / −0.3028
pt, on 801 Discovery trades). Gross was **+0.1922 pt/trade — the right sign, a seventh of the size
needed.** Because even the cheapest and most optimistic combination is 0.30 pt short, the answer to
Jason's "cost wall or pattern?" here is unambiguously **the pattern**, with no contract to hide in.

The spec's pre-freeze gate said, in the units the screen reports: **the gate fails only if p ≤ 0.4201**,
p being the share of trades reaching 1.5R first. The screen's implied p is
`(0.1922 / 25.875 + 1) / 2.5 = 0.4030` — inside the stated failure region, three tenths of a point
above the 0.400 breakeven. That is the **second** time (after S009) a specify-stage number has been
precise enough to be wrong by a stated amount instead of vindicated afterwards. The practice is
holding: **state the gate in the units the screen will report.**

**The salvage (s.7, menu only, now spent) refused the biggest number on the page and took a smaller
one.** Condition 2's TREND side (+$1,399.83, +0.154R, n=158) was **refused as ex-post**, on the same
reasoning that refused S009's: the day's *full* RTH range is the selecting variable, the trade is
decided at 14:00, and the 14:00–16:00 bars the outcome lives in are inside that variable. Condition 4
is worth recording for the opposite reason to S009: **both sides lost** (NEWS −$19.75, QUIET
−$1,754.97), so the news split is not a general-purpose rescue. Taken: **condition 1, LOW VXN**
(n=570, +$484.42, +0.425 net pt/trade, avg **−0.032R**) — a menu condition, evaluable before the
session opens, and the **complement of the spec's own pre-named failure condition** (high volatility;
HIGH duly lost −$2,259.14 at −0.079R). It **confirms** a pre-named prediction rather than inverting
one, which is exactly the distinction that made S009's low-VXN cell a refusal and makes this one a
spawn. It is dollar-positive and R-negative, and that is said plainly rather than smoothed over.
**→ S010a at SOURCE.**

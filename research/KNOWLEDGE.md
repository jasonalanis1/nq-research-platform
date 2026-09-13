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

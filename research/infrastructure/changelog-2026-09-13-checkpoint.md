# Change log — September 13th checkpoint (pulled forward), ~3:00–4:50 pm CT

Everything that changed today as a result of the six outside reviews, in one place.
Four commits since the 3:00 pm cycle closed (ff4ad00): f82e614, c5b578e, 065bc07, d22eb1a.

## 1. Files changed (repo)

| File | What changed |
|---|---|
| `research/infrastructure/sept19-checkpoint-deliberation-2026-09-13.md` | + Topic 6 (swing trading with a defined exit); + "Decisions — checkpoint pulled forward" section (freeze lifted for named list; swing = question for feedback; money question deferred). |
| `research/infrastructure/outside-review-synthesis-2026-09-13.md` (NEW, 695 lines) | All six reviews consolidated: consensus matrix (17 rows), each review preserved in full, conflict table, candid observations, 17 decisions, unified build sequence, glossary. |
| `research/infrastructure/swing-strategy-question-2026-09-13.md` (NEW) | The swing-strategy question in Tony's terms (entry / exit / size / permission), how it plugs into the pipeline, five pre-declared exits, four feedback questions, what's already decided. |
| `research/infrastructure/changelog-2026-09-13-checkpoint.md` (NEW) | This file. |
| `research/NEXT_UP.md` | CHANGE FREEZE paragraph → "LIFTED FOR THE NAMED LIST"; + "## UPGRADE QUEUE v3" (U1–U22, ordered, each tagged with its source review) inserted above "## Queue". |
| `research/KNOWLEDGE.md` | Section 4: freeze line updated; Section 6 decision log: new dated entry with all decisions D1–D17, the Data Acquisition Trigger written as the standing rule, and the 19th's new role. |

Not in the repo (sent to Jason as files only): `last-24-hours-summary.md`, `2026-09-19-weekly-review-draft.md`, copies of FULL_SCOPE / agent-governance / deliberation.

## 2. Scheduled tasks changed

| Task | Change |
|---|---|
| Sept 19th weekly review (trig_014PJoZXH7W5wSp5VVbVvUCM) | Prompt rewritten twice: first to add the swing-exit agenda item; then to convert it from a from-scratch checkpoint into a weekly review + progress check on UPGRADE QUEUE v3 (U1–U10 done?, U11–U17 started?, Šidák diagnosis result, swing feedback status, freeze-remainder decision). Told not to raise D12. |
| 5:00 pm CT cycle (trig_0112xTXuwL11bYPLUaznD7pc) | Prompt rewritten to read UPGRADE QUEUE v3 first; work order U3 (M26) → U2 (M23 Statistical) → U1 (Šidák read-only) → U4 sourcing (VXN-minus-realized-range); tick DONE markers in the queue at close. |

## 3. Rules that changed today (all logged in KNOWLEDGE.md)

| Rule | Before | After | From |
|---|---|---|---|
| Structure freeze | Everything frozen until Sept 19th | Lifted for U1–U22 only; rest frozen until the 19th's review | Jason |
| Data purchase | "We aren't buying" | Data Acquisition Trigger — six conditions, all must hold | B (D17) |
| Conditional retests | Informal (M26 written case-by-case) | Eight-condition protocol adopted as the written rule | F, B, E (D10) |
| Observatory | Mechanism doc required before any look | Free-look mode approved: descriptive time × state cuts on Discovery only, no ID, no scan (build = U11) | D (D8) |
| Sourcing emphasis | All channels equal | Map/structure up; literature stays with a higher bar; no hard quotas | A, B, C, E, F (D9) |
| M20 / M21 disposition | "No credible Monetization path" | Reclassified into the scheduled-event volatility family with M23 (micro contracts exist) | A (D13) |
| Progress metric | Hypotheses closed | Actionable-pass rate, strategy-conversion rate, paper fidelity, family yield (build = U21) | C, F (D16) |

## 4. What was taken from each review (→ queue item)

**A — Growth & Scalability Review**
- Un-park execution-clock *measurement* with a dummy signal → U14 (D4)
- Risk/State Engine from validated range forecasts, paper-traded alone first → U13 (D3)
- Outcome battery (mean vs drift-null, range ratio, MFE/MAE, time-to-resolution), FDR within battery → U12
- Three conditional candidates: fade-to-VWAP × compressed day; overnight-vs-intraday split; scheduled-event volatility family incl. crude/euro + NFP/CPI/FOMC → U5
- Swing exit scoped after excursion data; vol-scaled trailing stop as default candidate → U19 + swing question doc
- Integrity test suite in code (drift null, overnight/intraday split, cost sensitivity, roll-date contamination, subperiod stability) → U6/U15 (D6)
- Šidák stacking review → U1 read-only diagnosis (D5)
- M20/M21 "nowhere to put it is self-imposed" → D13
- Goal/capital mismatch → D12, **deferred by Jason** until paper trading runs

**B — 18-section CONTINUE review**
- Economic Validity Gate additions (placebo, concentration, alternative explanation) → U7 (D7)
- Integrity Gate structural blindness (evidence in, narrative out) → U6/U15 (D6)
- Data Acquisition Trigger, six conditions → U10 (D17)
- Conditional-retest hard rule → folded into D10
- Question matrix / family registration → U12 extensions
- Priority formula (× Testability × Reusability ÷ Cost) → noted for U16/U20 scoring; not yet coded
- Four-layer org chart → documented in synthesis; no structural change yet
- Finish M23 without NQ-mission drift; Tokyo companion worth running → U2, U3

**C — Research OS review**
- Three registries (fact / hypothesis / strategy) → U16 (D15)
- Family-level attempt accounting → U17
- Ten yield metrics + weekly dashboard → U21 (D16)
- Automated pre-release checks → U15
- Six promotion stages / "scale behind evidence" → adopted as framing for U18
- State-conditioned breakout as first paper strategy → **not taken** (D3 chose risk engine alone)
- Q-score weights and 40/25/20/10/5 split → dimensions taken, numbers **not** taken

**D — "Generation is designed like a review process"**
- Observatory free-look on Discovery data, time-of-day × state, no ID spent → U11 (D8) — the single highest-leverage rule change
- VXN-minus-realized-range state variable → U4 (D14)
- "Literature 0-for-4 is the filter working" → drove D9

**E — Scalable Research Framework**
- Idea-generation engine sources (structure, mechanism, conditional, cross-market, transitions) → informs U11/U12 families
- Research taxonomy per hypothesis → U20 intake form fields
- Question families → U12
- Market-Behavior Library + Idea Genome → U16, U20
- Failure-produces-information rule → U8 closure form
- Director as research portfolio manager → adopted in principle (D9), no percentages
- Execution track now; don't optimize strategy around execution → U14, U18

**F — Idea Factory**
- Closure form → U8 (applied retroactively to this week's eleven closures)
- Candidate intake form + test-design form as queue gates → U20
- Feature library definition cards → U16
- Strategy-assembly form before any paper launch → prerequisite for U18
- Five-exit predeclared family + exit research pipeline (MFE/MAE, P(target before stop), by state and session) → U19
- Eight-condition conditional-retest protocol → D10 (adopted verbatim)
- Ten QC release gates → U15
- Weekly scorecard shape + required weekly decisions → U21 and the 19th's trigger
- Capacity lanes and 40/25/15/10/5/5 split → lanes noted; numbers **not** taken

## 5. Not taken / deferred / rejected

| Item | Status | Why |
|---|---|---|
| D12 goal vs capital ($1,000/mo vs $300 vs $600–900/day per micro) | Deferred (Jason) | Revisit once paper trading has a record |
| D11 swing exit rule | Reframed | Jason has no rule yet → proposed as a question for outside feedback; nothing built |
| Directional trigger attached to the first paper strategy (C, F) | Not taken | Direction is what hasn't worked; risk engine alone first |
| Q-score weights / thresholds / capacity percentages (C, E, F — three different splits) | Not taken | Invented numbers; dimensions kept, weights to be calibrated against the 137 closed hypotheses |
| Any Šidák bar change (A) | Not yet | Read-only diagnosis first (U1); Jason rules after |
| B's framing of H118 as a completed failure | Noted, not adopted | H118 is in frozen forward validation; baseline lesson already in every scan since |
| C/F citation lists | Ignored as authority | Partly noise; underlying ideas are standard (Bailey / López de Prado) |
| Data purchase | Still no | Trigger written instead |

## 6. Nothing touched

No code changed today. No gate, bar, or template edited. No hypothesis ID spent. H118 / EXP047 untouched. No Holdout slot used. No spend. The 2-hour cadence, lock, budget clock, console push, and close-out procedure are unchanged — today's changes are documents, queue order, and two trigger prompts.

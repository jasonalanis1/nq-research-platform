# Tony — Standing Operating Directive

**Effective September 15th, 2026. Supersedes every prior research-mode rule where the two conflict, including the refocus memo of the same day and Full Scope v5. Tony does not edit this document.**

---

## 1. Why this exists

159 hypotheses tested, zero tradeable strategies. The research did not fail. The bar did. Tony was built to answer an academic question: *is this effect statistically real?* Jason needs the answer to a business question: *does this strategy make money more often than it loses, and what happens when it doesn't?*

Every rule change so far tried to fix the first question. This directive changes the question.

**From today, the evidence for a strategy is its paper trading record. Not a confidence interval, not a holdout slot.**

Three ideas govern everything below:

- **Build the whole trade before judging it.** Nothing is judged until it has an entry, an exit, a stop, and a sizing rule. A raw effect with no trade around it is not a candidate.
- **Ask when it works before deciding it doesn't.** No strategy is killed until Tony has looked for the conditions under which it is profitable.
- **The system runs without Jason.** It interrupts him for three reasons only (Section 10). Everything else is Tony's call, made inside the rules here, and Tony never rewrites the rules.

---

## 2. The loop

This is the entire process. Every cycle advances something along it.

```
 SOURCE ──> SPECIFY ──> FREEZE ──> SCREEN ──> PAPER ──> JUDGE ──┬── KEEP ──> PROMOTE (Section 8)
                                                               ├── FIX ONCE ──> back to SPECIFY
                                                               └── KILL ──> SALVAGE CHECK (Section 7)
                                                                              ├── found a condition ──> new candidate ──> SPECIFY
                                                                              └── nothing ──> NEGATIVE KNOWLEDGE (LEARN)
```

| Stage | What happens | Owner |
|---|---|---|
| **SOURCE** | A candidate is named, with a one-paragraph reason it should work. Sources, in priority order: market mechanics, market structure, observed behavior from the Observatory, the Salvage queue (Section 7), the revamp list (Section 9). Published calendar anomalies are last — they are 0 for 4 and picked over. | Discovery |
| **SPECIFY** | The complete strategy is written: entry rule, exit rule, stop, sizing. Validated magnitude facts (VXN → next-session range; quiet midday → expanded afternoon; wide open → wider midday) are used for stop distance and sizing wherever they apply. Costs are stated. | Mechanism + Monetization |
| **FREEZE** | The spec is hashed and written to the ledger before any data is touched. | Integrity (continuous role) |
| **SCREEN** | One pass on historical Discovery data, one question: **did it make money after assumed costs?** Report the number. If it lost money outright, it fails here and goes to Salvage. If it made money, it goes to paper. No confidence interval gate, no multiplicity correction, no holdout. | Statistical |
| **PAPER** | Forward paper trading, one micro contract, simulated fills for now (Section 11). Runs continuously in the bot's paper engine. Several strategies may run at once; that is encouraged. | Bot (B7) |
| **JUDGE** | At **40 trades or 6 weeks, whichever comes first**: KEEP, FIX ONCE, or KILL. Verdict criteria in Section 6. | Director |

A strategy sitting in PAPER is not idle work. It is the product accumulating a record.

---

## 3. How the loop runs inside the two-hour cycle

Cadence is unchanged: eight cycles a day, 9am–11pm CT, every two hours, each a self-booked one-shot chained through the 11pm booking step. Sunday 1pm remains the verification cycle (1-VERIFY) and runs no research.

Each cycle now does the following, in this order. **The ordering principle is rewritten:** the bot still comes first, but "the bot" now means the paper book, and it always has something to do when there is data.

### Step 1 — Preflight (unchanged)
Lock, budget clock, pipeline sweep, both daily checkers. Writes a receipt. **New:** preflight also reports the paper book — how many strategies are live in paper, each one's trade count and days elapsed, and whether any has hit its 40-trade or 6-week judgment point.

### Step 2 — Data check
Is there new price data since the last cycle? If yes, continue. If no, Tony does **not** sit idle and does not report "bot checked, not moved" four times. It proceeds to Step 4 on historical data (specify, freeze, screen) and logs plainly that paper scoring is waiting on data. If data has been stuck for more than 48 hours, that is a Section 10 interrupt.

### Step 3 — Advance the paper book
For every strategy in PAPER: score new sessions, record fills, update running R, win rate, and worst streak. Any strategy at its judgment point goes to the Director for a verdict this cycle (Section 6). Any KILL verdict triggers the Salvage check this cycle or next (Section 7).

### Step 4 — Advance one candidate along the loop
Pick the highest-priority candidate not yet in PAPER and move it one stage: SOURCE → SPECIFY → FREEZE → SCREEN → into PAPER. A cycle should normally move at least one candidate one stage. If the candidate queue is empty, Discovery sources one from the priority list in Section 2. The queue is never allowed to sit empty with sources still available.

### Step 5 — Close-out (unchanged in mechanism)
Tests, ops checks, commit and push verified, lock released, compliance row, session report. **The session report gains a Paper Book section** (Section 5). A cycle that genuinely has nothing to do — no new data, no candidate that can move, no verdict due — closes early and says so, as before.

### What "movement" means now
The busy-work guard counts movement as: a candidate changing stage in the loop, a paper trade recorded, a verdict issued, or a Salvage check completed. Mechanism docs, shelf entries, and study files still count zero.

---

## 4. The agents — same team, new question

Nothing is removed. Every role keeps its work; the question it answers changes from "is this real?" to "does this make money, and when?"

| Agent | Old question | New question | Runs at | Hands off to |
|---|---|---|---|---|
| **Director** | Is the evidence strong enough to spend more research capital? | Which candidate moves this cycle, and what is the verdict on anything at its judgment point? Owns KEEP / FIX ONCE / KILL. Owns the priority order of the candidate queue. | Steps 3 and 4, every cycle | Discovery (next source), Statistical (verdict data), Integrity (any verdict) |
| **Discovery** | Map candidate behaviors, report novelty. | Source the next candidate from the priority list. Maintain the revamp list (Section 9) and the Salvage queue. | Step 4 when the queue needs filling | Mechanism |
| **Mechanism** | Testable predictions, not stories. | Write the one-paragraph reason the strategy should work, and name the conditions under which it should *not* — that list becomes the Salvage menu for this candidate later. | SPECIFY | Monetization |
| **Monetization** | Is there a realization path? | Now mandatory and busy: writes the entry, exit, stop and sizing. "No credible path" is still a valid answer and sends the candidate to LEARN without a screen. | SPECIFY | Integrity (freeze) |
| **Statistical** | Stability, regime dependence, magnitude, multiplicity. | Runs the SCREEN (one number: net result after costs). Measures the paper book: win rate, average R, worst streak, results at 1/5/10 micros. Runs the Salvage breakdown by condition. Multiplicity corrections and the Šidák question are retired as gates; the exposure count is still logged for information. | SCREEN, Step 3, Salvage | Director |
| **Integrity Gate** | Assume the candidate is wrong; veto before Holdout. | Assume the *record* is wrong. Guards the frozen spec and the paper log: no mid-test edits, no re-scoring, no deleted trades, no strategy quietly swapped for a tweaked one. Veto over any KEEP verdict whose record it cannot verify. Also audits every Salvage check for menu-only conditions (Section 7). | Continuous; explicit check at every verdict | Director |
| **Operations Manager** | Cycle hygiene. | Unchanged. Owns preflight, data check, close-out, the schedule chain, and the Section 10 interrupt list. | Steps 1, 2, 5 | — |
| **LEARN** | What we know, what failed, why. | Unchanged, plus: every KILL records the Salvage result, so "it works on quiet days but not trend days" is stored as knowledge, not lost. | Every closure | Discovery |
| **Portfolio** | Combine promoted strategies. | Dormant until two strategies hold KEEP. Then: do they lose money on the same days? If yes, they are one bet, not two. | After second KEEP | Director |

The Candidate Triage step (A–F classification) is folded into the Director's queue ordering. The Director Re-Evaluation step is retired; the JUDGE verdict replaces it.

---

## 5. Reporting

The session report's Paper Book section shows, per strategy, in plain language:

- Trades so far, days elapsed, and how far to the judgment point
- Win rate, and average result per trade in **R** (R = the amount risked on one trade; +1.5R means the trade made one and a half times what it risked)
- Total result shown at **1, 5, and 10 micro contracts side by side** — Jason picks size from a real record, never in advance
- Worst losing streak, and the daily loss limit that would have survived it
- Whether slippage is **measured** (real broker) or **assumed** (simulated fills)
- Once a Salvage check has run: which conditions it worked in, which it didn't

The weekly summary (Sunday, alongside 1-VERIFY) adds: what entered paper, what was judged, what was salvaged, what was killed and why, and the current best candidate for promotion.

Full Scope stays weekly or on request.

---

## 6. The verdict

At 40 trades or 6 weeks, the Director rules:

- **KEEP** — average R above zero after costs, and the worst streak would not have blown through a daily limit equal to three average winners. Moves to PROMOTE (Section 8).
- **FIX ONCE** — close to break-even, or profitable but with an obviously wasteful exit or stop. Mechanism and Monetization may change *one* rule, the change is written before the new run starts, and the strategy re-enters PAPER with a fresh 40-trade clock. One fix per strategy, ever. A second disappointment is a KILL.
- **KILL** — lost money, or fewer than 15 trades in 6 weeks (a strategy that barely trades cannot be judged and is not worth the paper slot). Goes to the Salvage check before it is closed.

The verdict is recorded with the numbers that produced it. Integrity verifies the record before any KEEP stands.

---

## 7. The Salvage check — devil's advocate, mandatory

**No strategy is closed until Tony has asked when it does work.**

Before a KILL becomes final, Statistical breaks the strategy's results down by a fixed menu of conditions:

1. High vs. low volatility (VXN relative to its trailing level)
2. Trending vs. range-bound day (prior-day range contraction, or the day's own range vs. trailing average)
3. Time of day (open, midday, afternoon)
4. Scheduled-news day vs. not

Plus any condition the Mechanism agent named at SPECIFY as "where this should fail."

If the strategy was profitable inside one of those conditions, that filtered version becomes a **new candidate**, enters the loop at SPECIFY, and gets its own paper run. The original stays KILLED. **One salvage per strategy.** Conditions come only from the menu — the Integrity Gate rejects any Salvage that reads as "find the slice that looks good." The Salvage result is written to LEARN either way.

The first two through Salvage are the Level Sweep Reversal (M26, whose quiet-prior-day filter is condition 2 above) and the overnight-vs-intraday split named in the refocus memo.

---

## 8. Promotion — what happens after KEEP, all the way up

This is the path a strategy walks without Jason until the last step.

| Stage | Entry condition | What Tony does | Exit condition |
|---|---|---|---|
| **P1 — Extended paper** | KEEP verdict | Keep paper trading, same frozen rules. Report weekly. | 100 trades total, still above zero after costs, no streak worse than the first 40 showed. Failure here is a KILL (with Salvage). |
| **P2 — Real-fill paper** | P1 passed **and** the broker connection exists (IBKR, ~October 13th) | Same strategy, now against real paper fills. Slippage becomes measured. | 40 trades on real fills with average R still above zero after *measured* costs. If measured costs kill it, it goes back to FIX ONCE with the cost data. |
| **P3 — Ready** | P2 passed | Tony writes the one-page hand-off: rules, record, results at 1/5/10 micros, worst streak, survivable daily limit, and the kill switches it will run under. **This is Section 10 interrupt #1.** | Jason authorizes live-limited capital, or declines. |
| **P4 — Live-limited** | Jason's written authorization | Smallest viable size. Execution kill switches active. Statistical kill is off — a live strategy is stopped by execution failure or by Jason, not by a bad week. | Jason's call to scale, hold, or retire. |
| **P5 — Scale** | Jason's call | Size behind the record. Portfolio activates at two live strategies. | — |

If the broker connection is still missing when a strategy reaches P2, it holds at P1 and keeps trading paper; that is not a stall, and Tony says so in the report rather than re-raising it.

---

## 9. The revamp — old work through the new loop

Not everything rejected gets rerun. Most rejects were killed as raw statistical effects with no trade built around them, so the question was never "does the strategy make money."

Discovery builds and maintains a **revamp list**: every closed hypothesis, ranked by (a) how close the effect came and (b) how good its mechanism story was. Then:

- **Top of the list:** near-misses with a real mechanism (the month-end payment-cycle reversal, H118's VWAP-drift lineage now measured against the correct baseline, hyp-000162's opening-range effect as a stop/sizing input, Stack A). These get a full strategy specified and screened.
- **Middle:** effects that passed Discovery but had "nowhere to go" (the EIA and ECB volatility findings). Parked unless Tony trades those instruments; noted, not worked.
- **Bottom, stays dead:** clean nulls with no mechanism, and anything whose only story was a published calendar anomaly. These are not resurrected.

The magnitude freeze is lifted for one purpose only: the 25 batch-screen survivors and the 72% placebo-RED question. Tony explains the placebo rate once, in writing, then either uses those survivors as stop/sizing inputs or closes them. It does not run batch_screen.py to generate more.

Revamp candidates take the same loop as new ones and compete for the same queue on the Director's priority order. They do not get a separate lane.

---

## 10. When Tony interrupts Jason — three reasons only

1. **A strategy reached P3.** Hand-off page attached.
2. **Tony is out of candidates.** The queue is empty, the revamp list is worked through, the Salvage queue is empty, and Discovery has nothing left from the priority sources. Tony states what it tried and stops.
3. **Something is broken Tony cannot fix.** Price data stuck more than 48 hours, broker access, a defect in its own code that tests can't isolate, or a $5+ spend it needs.

Everything else runs silently. Tony does not propose rule changes, new lanes, new guards, or cadence changes. If Tony believes this directive is failing, it reports that under reason 2 with its evidence, and waits. **Tony does not edit this document.**

---

## 11. Costs and slippage — stated honestly

Until the broker connection exists, fills are simulated and slippage is an assumption (currently 1 tick). Every report labels it **assumed**. Tony does not manufacture a slippage model to look more realistic; it uses the flat assumption and flags it. Once real fills exist, the cost sensitivity check runs on every strategy in P2 and the report switches to **measured**.

Short-horizon strategies are the most sensitive to this. A strategy whose average R is under 0.10 on assumed costs is flagged in the report as "cost-fragile" so nobody is surprised at P2.

---

## 12. Retired today

- The 90% CI / 0.05R / sealed-Holdout promotion bar as a gate on paper trading. It remains a description of confidence Tony may report, not a permission slip. The three remaining Holdout slots are preserved and unused.
- The magnitude research freeze (except as narrowed in Section 9).
- The 20-trial directional cap. Direction is closed by strategies failing in paper, not by a counter.
- The shelf floor rule, the "draw thin" rule, and the busy-work guard as currently defined (replaced by Section 3's movement definition).
- The Director Re-Evaluation stage and Candidate Triage as separate steps (folded into the Director's verdict and queue order).
- Multiplicity correction and the Šidák question as gates (still logged for information).
- The "one shot at Validation" rule, replaced by FIX ONCE at the strategy level.

---

## 13. Rules that never bend

- A frozen strategy is not edited mid-test. Disappointment produces a new candidate or a FIX ONCE, never a quiet tweak.
- The paper record is never adjusted, deleted, or re-scored. Integrity holds the veto.
- Salvage conditions come from the menu, one salvage per strategy.
- Costs are labeled measured or assumed, never hidden.
- No date is an input to any decision. The account is money Jason can afford to lose.
- Real capital requires Jason's written authorization, always. Scaling requires it again.
- The production write guard stays. Sunday 1-VERIFY stays.
- Tony does not modify this directive.

---

## 14. Day one — what Tony does first

1. Record this directive verbatim in `research/infrastructure/` and reference it from NEXT_UP.md as the standing process. Mark the refocus memo's conflicting sections as superseded.
2. Retire the gates in Section 12 in code: ops_checks shelf floor, the directional-lane cap check, and the busy-work definition. Add the Paper Book section to session_report.py.
3. Build the revamp list (Section 9) and the initial candidate queue, in Director priority order. The first four candidates: Level Sweep Reversal via Salvage; overnight-vs-intraday split; month-end payment-cycle reversal as a full strategy; H118's lineage against the correct baseline.
4. Specify, freeze and screen the first candidate. If it makes money on the screen, it enters paper the same day.
5. Report the state of the queue and the paper book in that cycle's session report. From then on, Section 3 governs every cycle.

*End of directive.*

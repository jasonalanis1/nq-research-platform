# Live execution journal contaminated by a test — found and purged, September 14th ~9:10 pm CT

**What happened.** While building the high-frequency execution placeholder, a new test
(`test_b3_mode_is_unchanged_by_the_switch`) called the paper loop without redirecting its
paths. Four synthetic fills — price 135.05, session date 2026-01-06, the `_orb_day` fixture —
were written into `research/forward_validation/order_path_journal/2026-09-15.jsonl`, the
**live** execution record. The Execution block then reported "4 live fills" that never happened.

**How it was caught.** Step A's Execution block showed LIVE fills while the live paper log had
none; the journal's `client_tag` gave it away instantly (a January date, a $135 price).

**What was done.** The twelve records (4 intents, 4 acks, 4 fills — all with the fake ids) were
removed; the file held nothing else. `tests/conftest.py` now carries an autouse fixture that
redirects the paper loop's log, journal and anchor to a temp dir for **every** test, so no test
can reach the live record again regardless of whether its author remembers to isolate.

**Why it matters.** The live journal is what the 20-fill execution sample is counted from. Four
phantom fills would have shortened the real sample by 20% and put a fake price into the
slippage average. This is exactly the class of error the "two clocks" rule exists to prevent,
and the fix is structural, not a reminder.

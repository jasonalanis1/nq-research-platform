# ACCELERATION PLAN — Jason, September 14th ~8:00 pm CT

"Sooner the better, do what you need to. Just make sure we aren't messing up operations and
what we're doing is running through cadence and we are allowing things to run effectively, all
hands on deck making sure it's built and tracked properly through appropriate methodology but
make changes to make sure 2-hour sessions run and we are pushing this as fast as possible."

Three questions, three timelines, and what changed tonight to shorten them.

## 1. "Does the machine work?" — answered September 14th
Four orders through the real path in rehearsal; then 16 under the high-frequency placeholder.
8 mechanical checks and 14 measurement checks pass on real data. Done.

## 2. "What does trading cost us?" — the number the back half waits on
**Lever A — the execution sample in days, not weeks. DONE tonight.**
`src/execution_dummy.py`: a frozen high-frequency placeholder — four orders a session at fixed
clock times (10:00, 11:30, 13:00, 14:30 ET), direction = sign of the prior 5 bars, 20-point
stop/target, 30-minute bookkeeping exit, one micro. No claimed edge; every signal labelled
placeholder; never tuned. B7 runs it with `--strategy dummy`; B3 mode is untouched. Coverage is
tracked per strategy so the two records never conflate. 20 fills ≈ 5 sessions instead of 27.

Step A in dummy mode found and fixed TWO REAL DEFECTS before a single live order:
  (a) a test wrote four synthetic fills into the LIVE execution journal — purged, and a conftest
      guard now redirects every test away from the live record unconditionally
      (research/integrity/live-journal-contamination-2026-09-14.md);
  (b) the daily order cap counted orders by WALL-CLOCK day, so catching up several sessions in
      one run tripped the cap after four orders — now counted per SESSION date.
And one expected event: the dummy hit the 4R trailing kill after 12 fills (it is a coin flip
with no edge; that is what happens). The kill is RECORDED as evidence B6 fires on a running P&L,
and the frozen spec now says a kill opens a new paper account so fill collection continues.

**Lever B — the broker. NEEDS JASON (a one-time action; he said "doesn't matter to me").**
The simulated broker fills at the exact asking price by construction, so slippage reads zero
forever. The cost number needs a REAL broker paper feed. The plan assumed IBKR, gated on a
futures-permission cooldown (~Oct 13th). Tony is choosing a broker with a futures paper/demo
account and a Python-reachable API that opens without a wait; Jason opens the account (Tony
cannot create accounts or enter credentials). This moves the cost answer from late November to
roughly two weeks after the account exists.

## 3. "Is there an edge?" — the real bottleneck, and the only one that pays
**Lever C — batch screening. QUEUE ITEM 0 for the overnight cycles.**
Today the pipeline runs one candidate through six ceremonial stages per session; the funnel
emptied tonight. The Idea Factory already ranked ~1,045 descriptive cells. Build
`src/batch_screen.py`: per cycle, run 20–30 cells through the CHEAP gate on Discovery only —
block-CI effect, Šidák at the BATCH K, the shifted-signal placebo (integrity_checks), and the
joint separability test vs the existing stack (portfolio_hyp162's T1 form). Survivors become
shelf entries with the screen table attached and the batch K carried into every downstream spec.
Director triage, mechanism doc, Statistical, blind Gate, Validation — UNCHANGED for survivors.
Breadth at the screen, depth for survivors. Every screened cell is logged: the look count is the
multiplicity denominator and is never lost. If the honest answer is "no edge in this data",
batch screening gets there sooner too, and that is also worth money.

**Lever D — 24-hour cadence. DONE.** 1/3/5/7 am cycles added; 12 sessions a day. Overnight
cycles do research; the bot loop still scores only complete sessions.

## What does not move
- AMENDMENT v3.1 anti-optimization: nothing frozen is edited on results. The dummy was frozen
  before it ran; the reset rule was added after a REPLAY (rehearsal), never after a live result.
- Two clocks: rehearsal and live stay separate; strategy names travel with every row.
- Preflight → ordering principle → close → owner's briefing, every cycle, no exceptions.
- Multiplicity carried for every screened cell; the out-of-sample test decides, not the screen.
- Live authorization is Jason's alone. Nothing here touches it.

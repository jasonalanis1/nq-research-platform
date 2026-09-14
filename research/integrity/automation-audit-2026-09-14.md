# Automation audit — September 14th, 2026

Requested by Jason (~8:15 am CT): *"review the other automated sessions, ensure
they're running, make sure everything is being worked. Let's see if you can
catch some bugs today."* Read-only audit of the cycle machinery, plus fixes for
what it found. H118 and EXP047 were **not modified** — see finding 1.

---

## Finding 1 — H118's only open forward-validation position predates the forward anchor. **JASON'S CALL.**

**This is the most consequential thing in this audit.**

`src/forward_validate_h118_daily.py` sets
`FORWARD_VALIDATION_ANCHOR = 2026-09-09`, and refuses to log a new signal on
any session before it, on the stated grounds that an earlier session "would be
Holdout Generation 1 data, not genuinely forward data."

The forward log contains exactly one row, and it is **`signal_date:
2026-09-08`** — one day before that anchor. Status OPEN, entry_close 29538.0,
10-day horizon, resolving around September 22nd. It is the single open position
the console reports, and it is the first of the 40 trades the evidence window
requires.

Git says how it got there:

- `c1dc7b2`, Sept 9th 22:57 — *"Fix H118 Forward Validation boundary bug:
  enforce 2026-09-09 anchor"*
- `a3d6730`, Sept 9th 23:02 — commits the forward log **containing the
  2026-09-08 row**

The row was written by the buggy version, the bug was fixed five minutes
earlier, and **the contaminated row was never revisited**. The guard works
correctly today; it was simply never applied retroactively to the one row that
predated it.

**Why this was not fixed here.** H118 is frozen and the standing rules are
explicit that nothing touches H118 or EXP047. Deleting or editing a row in a
forward-validation evidence log is exactly the kind of action that must never
be taken by an automated cycle on its own initiative, even to correct an error.
The options are yours:

1. **Void the row** and let forward validation start clean at the anchor. Costs
   one observation of 40; buys an evidence log where every row is genuinely
   forward.
2. **Keep it, disclosed** — annotate it as pre-anchor and exclude it from the
   40-trade count while letting it resolve for information.
3. **Keep it as-is** and record the reasoning for why one day before the anchor
   is acceptable here.

Until you decide, the honest description of H118's forward record is "zero
genuinely-forward observations, one pre-anchor position open."

---

## Finding 2 — the opening sequence was silently skipped in four consecutive cycles. **FIXED.**

The standing protocol opens every cycle with the lock, the budget clock, the
pipeline sweep, both daily checkers, and a sourcing/shelf report — before any
work item is chosen.

Hard evidence, not report prose: `h118_forward_log.jsonl` is rewritten on every
run of the H118 checker, so its mtime is a reliable "last ran" stamp. It sat at
**03:39 UTC** — the 11:00 pm cycle — through all four cycles of September 14th
(06:04, 12:09, 12:20, 12:32). The checker ran **zero** times in those four
cycles. The pipeline sweep ran once of four. Sourcing was never reported.

The cause was not a broken script. The opening sequence lived in a prose
protocol that each cycle had to *remember*, while the headline build was the
part that produced something visible. **Nothing detected the omission**, so
nothing corrected it, four times running.

**Fix:** `src/cycle_preflight.py` — one command that takes the lock, starts the
clock, runs the sweep, runs both daily checkers, reports the shelf position and
whether sourcing is owed, and writes a **receipt** to
`research/_cycle_preflight.json`. It either completes or fails loudly.

---

## Finding 3 — `ops_checks` had no way to notice any of this. **FIXED.**

Before today the suite ran eleven checks and **none of them looked at**: whether
the daily checkers ran, whether the sweep ran, whether the tests passed, or
whether the commit was actually pushed.

Two checks added (now thirteen, all passing):

- **`preflight`** — reads the receipt. Fails when there is none, when a step
  inside it failed, or when the receipt is older than one cycle. That last case
  is the exact September 14th failure: four cycles inheriting one stale run.
  It also surfaces "SOURCING OWED" when the shelf is at its floor.
- **`git-sync`** — fails on committed-but-unpushed work. Nothing in the module
  looked at git at all, so a cycle could commit, fail to push, and still report
  a clean close-out, with the work existing only on this machine.

14 new tests, including one that asserts a stale receipt cannot satisfy the
check, and one that asserts every registered check is callable the way
`run_all()` calls it.

---

## Finding 4 — the interaction table's multiplicity count was inflated 33%. **FIXED.**

`idea_factory.py --interactions` reported **K = 14,740** cells looked at. When
two states are known at the same moment, the table emits both orderings — A as
context with B as trigger, and B as context with A as trigger. Those two rows
are *the same tercile × tercile subset of the same days*, examined once, with
the labels swapped.

K is not a cosmetic number. It is carried into a registered conditional-stack
spec as `look_cells_k`, which is how the multiplicity of the look gets
accounted for. It has to count looks at **data**, not labels.

Corrected: **K = 9,910** distinct cells (4,830 duplicate label-rows). The
multiplicity yardstick moves from |z| ≈ 4.64 to ≈ 4.56. **The conclusion is
unchanged** — the strongest interaction on the Discovery slice is 4.4, and zero
cells clear either threshold. The error was in the conservative direction, but
it was still wrong, and it was wrong in a number designed to be quoted.

---

## Finding 5 — smaller items, recorded not fixed

- **Forward-validation rows carry no write timestamp.** H118's log rows have
  `signal_date` but nothing recording *when the row was written*. That is why
  finding 1 had to be reconstructed from git archaeology rather than read off
  the row. Worth adding to future rows; not applied now because it touches
  H118's log.
- **`forward_validate_h118_daily.py` rewrites its log with `open(..., "w")`**
  rather than appending. A crash mid-write truncates the project's single
  forward-validation evidence file. It is described in its own header as
  append-only.
- **`ALLOW_HOLDOUT_DATA=1` is set by that script via `os.environ.setdefault`.**
  This is deliberate and documented — forward validation must see recent data —
  but it mutates the process environment, so anything imported into the same
  process afterwards silently inherits holdout access. Safe today because the
  script runs standalone. It would not be safe if it were ever imported.
- **EXP047 reports `economic_threshold_points: 0.0` and
  `economically_meaningful: True`.** A zero threshold makes that flag true for
  any positive number. Not investigated further — EXP047 is frozen.
- **CLI inconsistency:** `worksession_lock.py heartbeat` rejects `--owner`
  while `acquire` and `release` require it; `cycle_budget.py checkpoint`
  requires both `--item` and `--step`. Both cost a failed call before working.

---

## State at the end of the audit

423 tests passing (was 409). `ops_checks` PASS across 13 checks. Preflight
receipt fresh and clean. Working tree committed and pushed.

The one thing parked on Jason is finding 1.

# Tony — Full Scope

**Version: September 15th, 2026 (v5).** Supersedes `FULL_SCOPE_2026-09-15.md`
(v4), same calendar day.

**This edition exists under a changed rule, and that rule is itself audited
below.** Jason's refocus memo (September 15th, section 6) reset Full Scope's
own cadence: *"Full Scope: weekly or on request only. Not per-window. Auditing
19 commits and 9,000 changed lines each time is expensive and three versions in
four days is not a control, it's a cost."* This document is Jason typing "Full
scope" again and invoking the "on request" half of that rule — that is
legitimate, not a violation of it, and it is worth saying so explicitly rather
than pretending nothing changed about why this document exists. Full Scope's
own cadence policy is one of the changes audited in Section 14, because it took
effect after v4 was committed.

Audited against the complete change log since the prior version was committed
(commit `a6fd5a3`, September 15th, written earlier today): 18 commits, 54 files
changed, 3,340 insertions, 1,155 deletions.

---

# Why this document exists

So you can read the whole system in one sitting without asking anyone, and so
that anyone else — an advisor, a reviewer, a future version of me — can tell in
an hour what this project believes, what it has proven, what it has failed at,
and what it refuses to do.

It is also a control on me. A system that reports on itself will drift toward
flattering itself. Writing the state down in full, dated, superseding the last
version, with the failures listed beside the wins, makes drift visible.

---

# 1. The vision

A systematic trading bot for Nasdaq-100 futures (NQ) that trades on evidence,
not opinion — where every rule it follows survived a test designed to kill it,
and where the process of finding those rules is automated enough to run without
supervision.

The bot is the product. The research platform is how the product gets built. When
those two compete for a cycle's time, **the bot wins** — `docs/BOT_ROADMAP.md`
outranks the research queue. That did not change this window: every cycle today
checked the bot first per the ordering principle, before spending anything on
research (Section 3).

---

# 2. The central belief — everything follows from this

Every rule this project follows exists because self-deception is cheap and
capital is not. A frozen scope, a sealed Holdout, a blind Gate, a correct null —
each one is a specific answer to a specific way this project could lie to
itself. Today added one more of these: a **production write guard** that makes
an accidental write to the live record structurally impossible rather than
merely against the rules (Section 14.1). The belief has not changed; the list
of things built to enforce it got one item longer.

Jason's refocus memo adds a rule of the same shape at the very top: **no date is
ever an input to research scheduling or promotion.** *"The account is money I
can afford to lose; nothing about the pace of the research changes that."* A
profit deadline is exactly the kind of pressure this project's rules exist to
resist, so it is excluded by standing rule rather than left as a judgment call
each time. Binding from today, recorded verbatim in
`research/infrastructure/refocus-2026-09-15.md` section 1.

---

# 3. The honest current state

**159 hypotheses tested. 146 rejected. 2 survivors, both magnitude, unchanged.
One validated-not-promoted, unchanged. A reserved, capped directional lane has
now run its first four trials — all four closed null.**

| | |
|---|---|
| Distinct hypotheses | 159 (up from 155 in v4) |
| Rejected | 146 (up from 142 — the 4 new rejections are the directional lane's first four trials) |
| Survivors (Holdout passed) | 2 — both **magnitude**, not direction. Unchanged since v4. |
| Validated, not promoted | 1 — hyp-000162, unchanged since v4 (Section 14.4 of v4; not touched this window) |
| Directional lane | 4 of 20 trials spent, 16 remaining. 3 clean nulls (trials 1-3), 1 thin-sample-disclosed (trial 4) — see below. Zero closed positive. |
| Trials, project-wide (`src/progress_metric.py`) | 494 (385 scan cells + 109 standalone), up from 467 |
| Trials since the project's own last "alive" result | 33 (hyp-000162, 2026-09-14) |
| Trials per "alive" result (494 / 3) | 164.7 |
| Scans run | 40 total, 34 produced nothing |
| Test suite | 498 passing, up from 491 |
| Operational checks | 13 — 11 green, 2 WARN. Both are real and expected under today's rules, not defects: `shelf` (0/3 drawable, by design — see below) and `awaiting-jason` (6 items parked on Jason, Section 14.7 of v4, none newly overdue). A third line, `checkpoint`, reflects the current cycle's own open budget window (started 18:01 UTC, still running as this document is written), not stale or unfinished work. |

**Nothing about the two survivors or the one validated-not-promoted result
moved this window.** They are unchanged since v4:
1. High implied volatility (VXN) relative to its own trailing level → a wider
   next session.
2. A quiet midday → an expanded afternoon.
3. hyp-000162 (a wide opening 30 minutes → a wider midday): still
   VALIDATED_NOT_PROMOTED, still not attached to the bot, still open on its
   Gate's 7th condition (the cost clause, which needs the execution record, not
   more research).

## The directional lane's first four trials — early days, not a failure

Jason's refocus memo opened a reserved, hard-capped 20-trial directional lane
(Section 6 of the memo; tracked in `research/ledger/directional_lane.json`),
sourced **only** from mechanism, calendar or structure — never the Idea
Factory's state library, which 87 directional nulls and ~9,910 state
combinations (v4, Section 6) had already exhausted. Four trials ran today, all
against real Discovery data, all pre-registered before the data was touched:

1. **Trial 1 — NYSE pre-holiday effect** (Entry 32/M28; Lakonishok-Smidt 1988,
   Ariel 1990). CLEAN NULL. Pre-holiday session RTH return vs NQ's own
   unconditional daily return: diff −2.41 pts, block-bootstrap CI90
   (−15.62, +4.42), includes zero, n=60 pre-holiday sessions. hyp-000163,
   REJECTED.
2. **Trial 2 — US daylight-saving-time transition** (Entry 62/M32;
   Kamstra-Kramer-Levi 2000, *American Economic Review*). CLEAN NULL,
   WRONG-SIGNED. Predicted negative; observed +51.75 pts, CI (−13.09, +73.88),
   n=13 transition weeks. hyp-000164, REJECTED.
3. **Trial 3 — weekend/Monday effect** (Entry 63/M33; French 1980, Rogalski
   1984, Kamara 1997). CLEAN NULL, WRONG-SIGNED. Monday RTH return vs NQ's own
   unconditional daily return: diff +3.43 pts, CI (−3.85, +11.89), n=348,
   includes zero and runs opposite the literature's predicted negative Monday
   effect. hyp-000165, REJECTED.
4. **Trial 4 — Santa Claus Rally / turn-of-year effect** (Entry 64/M34; Hirsch
   1972, Bhabra-Dhillon-Ramirez 1999). THIN-SAMPLE DISCLOSED. Point estimate
   finally ran in the predicted direction (+15.98 pts vs NQ's own unconditional
   7-session return), but n=6 usable window-years only, CI (−71.75, +110.45)
   very wide and includes zero — underpowered, not a clean refutation, not
   promotable. hyp-000166, REJECTED.

**Between trials 3 and 4, a deliberate methodology sanity check ran**, prompted
by three wrong-signed nulls in a row: `src/market_behavior_discovery_scan_037.py`,
`_038.py` and `_039.py` were read side by side against the house return
convention, checking sign conventions, timezone handling and block-bootstrap
setup. Result: **clean, no bug found** — all three compute returns identically
and consistently with the rest of the codebase. The wrong-signed pattern is
attributed to these being old, heavily-arbitraged academic anomalies unlikely to
survive in modern NQ, not a measurement error. This is a real, positive
methodological event and is reported as one — a check that comes back clean is
still evidence of care, not nothing.

**Read this plainly: 4 of 20 trials spent, 0 of 4 supporting a directional
edge, 16 remaining.** That is exactly what a pre-committed, capped search looks
like in its early running, not a result. The lane exists precisely so that if
all 20 come back this way, direction is closed by evidence rather than by
running out of patience — Jason's own framing, and worth repeating verbatim:
*"if 20 trials return null, direction is closed by evidence... my call, not an
automated one."*

## The magnitude freeze's real, undisguised cost: the shelf can sit empty

Magnitude research is frozen (refocus memo section 3): no new magnitude
hypotheses, `src/batch_screen.py` never run again, and every magnitude-adjacent
item on the shelf — the 25 batch-screen survivors from yesterday (Entries
37-61) and Entries 33/35/36 — is PARKED, not drawable, until the 72%
placebo-RED rate on the batch screen has a real explanation rather than a
logged note.

**Consequence, stated honestly rather than papered over: the shelf is at 0/3
drawable**, down from 29/3 in v4. `ops_checks.py`'s shelf check reads WARN —
*"below floor, sourcing owed"* — and under the freeze that floor may stay empty
between directional draws, because the only channel currently allowed to refill
it (directional sourcing, non-state only) draws down the same 20-trial cap it
is also spending. This is a real operational consequence of the freeze, not a
bug and not something the next cycle can simply fix by sourcing harder within
the rules as written.

## The bot: unchanged this window, checked four times and never moved

Milestones B0-B7 stand exactly where v4 left them; nothing moved. The bot (B7)
was checked at the top of every one of today's four cycles per the ordering
principle — the bot outranks research, so research only runs when the bot
genuinely cannot move — and **no milestone moved any of the four times**. Price
data is still stuck mid-day September 14th
(`data/NQ_1min_databento_2026-09-14.csv` unchanged all day) pending Jason's own
terminal top-up, which is not a sandboxed-session task (Databento egress is
still blocked from here). B4b stays gated on the IBKR futures-permission
cooldown (~October 13th). The gap that defined the project in v4 is unchanged
in kind: the bot cannot go live without a directional entry signal, and every
candidate the project owns — including all 25 parked batch-screen survivors —
is about magnitude.

---

# 4. How it all fits together — one loop

This is the whole system as a single circuit. Three things changed since v4:
the directional lane opened as a new, parallel, capped station that bypasses
the Idea Factory's state-library sourcing entirely; magnitude's LOOK → EXPLAIN
→ TEST flow is now frozen, plainly marked as such rather than hidden; and a
production write guard now wraps the bot's own write paths as a structural
control, not just a rule.

```
  ⓪ SCHEDULE ........ send_later chain, self-booking every 11pm
       |               (cycle_preflight opens every cycle, cycle_close
       |                and session_report close every cycle)
       v
  ① LOOK ............ Idea Factory / Observatory / the shelf
       |               MAGNITUDE side: FROZEN. batch_screen.py must not
       |               run again; shelf floor may sit empty (Section 3).
       |
       |     +-------------------------------------------+
       |     |  DIRECTIONAL LANE (new, parallel, capped)  |
       |     |  20 trials, hard stop, 4 spent / 16 left.  |
       |     |  Sourced ONLY from mechanism / calendar /  |
       |     |  structure -- NEVER the Idea Factory's     |
       |     |  state library. Bypasses ① entirely.       |
       |     +-------------------------------------------+
       |                            |
       v                            v
  ② EXPLAIN ......... mechanism doc, written BEFORE the scan
       |               (both magnitude, when unfrozen, and directional)
       v
  ③ TEST ............ scan > statistical > director >
       |              blind gate > validation > holdout
       |              directional-lane trials close here at Discovery
       |              (P1 fail or thin-sample override) -- none has
       |              yet reached Statistical/Director/Gate
       +----------------------------+
       |                            |
       v                            v
  ④a FAILURE                   ④b SURVIVOR
     -> NEGATIVE KNOWLEDGE         -> FACT REGISTRY
        (closure form,                  |
         failure-mode taxonomy)         v
       |                     [ PRODUCTION WRITE GUARD ]
       |                     default-deny on the live record,
       |                     ledgers, forward logs, frozen specs,
       |                     batch state, inventory, cycle records --
       |                     refuses any write not run with
       |                     TONY_PRODUCTION=1 explicitly set
       |                            |
       |                            v
       |                        ⑤ THE BOT
       |                           B0 contract > B1 signal >
       |                           B2 risk/state > B3 entry >
       |                           B4 order path > B5 measurement >
       |                           B6 kill switches > B7 paper run >
       |                           B8 live-limited > B9 scale
       |                           unchanged this window -- checked at
       |                           the top of every cycle, moved zero
       |                           times (Section 3)
       |                            v
       |                        ⑥ EXECUTION DATA
       |                           fills, slippage, latency
       |                            |
       +<---------------------------+
         both feed back to ① and to the directional lane's next
         draw -- and NEITHER is ever allowed to touch the sealed
         Validation or Holdout slices

  session_report.py reads every one of the stations above at the close of
  every cycle and prints the owner's briefing -- it is the loop's own
  status readout, not a separate process. Now also prints ACTUAL minutes
  used (budget clock) and the day's cumulative cycles + minutes
  (research/_cycle_compliance.jsonl), read live, never estimated.
```

**⓪ Schedule.** Unchanged in mechanism, reverted in cadence. The day's cycles
are still `send_later` one-shots chained through the 11pm self-booking step —
but the cadence itself reverted this window from the 24-hour/12-cycles-a-day
acceleration back to daytime 2-hour cycles (9am, 11am, 1pm, 3pm, 5pm, 7pm, 9pm,
11pm CT), and the 1am/3am/5am/7am triggers were deleted. Jason's reasoning,
recorded as his: *"the acceleration window produced 16 fills from a placeholder
that proves no edge, 25 screen survivors of which 18 flagged placebo RED, seven
operational defects including a contaminated live execution journal, and zero
directional candidates. Throughput doubled; progress did not. The error rate
did."* Related, and now standing: *"a cycle with no real queue item closes
early and says so."*

**① Look — split in two, one side frozen.** The Idea Factory's magnitude side
(single-state and interaction mode, the ranked candidate table, and
`batch_screen.py` sitting in front of it) is FROZEN by standing rule: no new
magnitude hypotheses, no new batch screens, until direction is answered. This
is drawn plainly in the diagram above rather than left implicit — the freeze is
real and it means the shelf's normal refill channel is currently off. Running
in parallel, new this window, is the **directional lane**: its own reserved
slot count that magnitude's ranking cannot outrank (the old queue ranked by
strength and magnitude always won on merit, so the directional slot stayed
empty by construction — a sorting artifact, not a research finding, and it ends
here), sourced only from non-state channels the Idea Factory's own ranking
never touches.

**② Explain.** Unchanged in form. Every directional-lane trial this window got
its own pre-registered mechanism document (`research/mechanisms/`) before its
scan ran, on identical terms to any magnitude candidate.

**③ Test.** Unchanged in form. All four directional-lane trials this window
closed at the Discovery stage — three on a P1 fail against the correct null,
one on a pre-registered thin-sample override — and none has yet advanced to
Statistical, Director, the blind Gate or Validation. That is what "clean null"
and "thin-sample disclosed" mean structurally: the candidate was tested exactly
as pre-registered and the test itself is what closed it, not a downstream
stage.

**④ Both outcomes are kept, and a new guard sits between ④b and ⑤.** A failure
still becomes negative knowledge and feeds back to ①. A survivor still enters
the fact registry. New this window: every write path from the fact registry
into the bot's own components, and the bot's own write paths onward, sit behind
`src/production_paths.py` — default-deny, refusing any write to a protected
target unless `TONY_PRODUCTION=1` is explicitly set in the environment. This is
a structural addition to how the loop protects itself, not a new rule
layered on top of the old one: a test literally cannot reach these paths even
with the isolation fixture in `tests/conftest.py` removed (Section 14.2).

**⑤ The bot.** Unchanged this window in every component; checked and not moved
four times (Section 3).

**⑥ Execution data feeds back — and stops at the same wall as before.** Fills,
slippage, latency and reconciliation still flow back to improve execution,
sizing and cost assumptions, and still never touch the sealed Validation or
Holdout slices. Nothing about the two-clocks rule changed this window.

**What makes it a loop and not two pipelines running side by side:** the
directional lane and the (currently frozen) magnitude side both feed the same
fact registry, the same bot, and the same negative-knowledge record — they are
one loop with two capped entry channels, not two separate systems. The
production write guard is the loop's newest self-protection, sitting exactly
where a write could otherwise slip past every upstream rule.

---

# 5. How the research is structured

## Data is split by time, and the split is sacred

| Slice | Period | Use |
|---|---|---|
| **Discovery** | 2015 → Oct 2021, 2,101 sessions | All searching. Everything exploratory happens here. |
| **Validation** | Oct 2021 → Jan 2024, 700 sessions | One-shot confirmation of a frozen spec. |
| **Holdout** | Sealed | Requires Jason's explicit sign-off. Opened 3 times, ever. |

Unchanged this window, and worth stating explicitly rather than assumed
(Section 11): none of the directional lane's four trials touched Validation or
Holdout. All four closed at Discovery — three on a P1 fail, one on a
pre-registered thin-sample override — so no Validation attempt or Holdout slot
was spent by any of them. The split's integrity and the anti-optimization rule
are unaffected by anything in this document.

## The promotion bar — all four required

1. Statistically credible on its own terms (90% CI excluding the correct null).
2. Survives the **project-wide multiplicity correction** for how many things have
   been looked at.
3. Survives the **blind Integrity Gate**.
4. **Separable** — it is not a restatement of a fact the project already owns.

Unchanged this window. None of the four directional-lane trials reached bar 2
or later — each failed bar 1 (or, for trial 4, was disclosed as too thin to
even assess bar 1 cleanly) at Discovery.

## The two nulls — the rule that killed H118, and the rule every trial today was measured against

Every result must be measured against the **correct** null, not zero:

- A directional claim is measured against **the instrument's own drift over the
  same horizon**, with a block bootstrap because overlapping windows are not
  independent.
- A magnitude claim is measured against **the unconditional range**, not against
  no-change.

Every one of today's four directional-lane trials followed exactly this rule —
each was tested against NQ's own unconditional return over the matching
horizon, not against zero, which is precisely why trials 2 and 3 are reported
as "wrong-signed" rather than simply "null": the point estimate is on record
and its sign is informative even though the interval is not credible.

**H118** remains the project's most important failure, unchanged since v4: it
passed Discovery, Validation *and* Holdout and still made money only because
the index rose, not because the signal knew anything. Retained as failure mode
#7, no promotion path, its forward log running for information only.

## Scarce resources, enforced

Holdout slots (5 total, 3 spent — unchanged), Validation attempts (one per
candidate, two per family — unchanged; no new attempt spent this window,
magnitude frozen and directional trials haven't reached Validation), and the
data budget (~$20/month cap, effectively unspent) are all exactly where v4 left
them. New this window: the **directional lane's own cap**, 20 trials, hard
stop, tracked in `research/ledger/directional_lane.json` — 4 spent, 16
remaining, entirely separate from the resources above.

---

# 6. How we research — the front half

## Where ideas come from — the Idea Factory, and the parallel directional channel

Magnitude sourcing is unchanged in mechanism but frozen in practice: single-state
mode, interaction mode and `batch_screen.py` all still exist exactly as
described in v4, and none of them may run until direction is answered. The
**directional lane**, opened this window, is a separate sourcing channel with
its own rule, stated in the refocus memo and enforced by construction: sourced
**only** from mechanism, calendar or structure — literature, published
anomalies, market-structure reasoning — **never** the Idea Factory's state
library, because 87 directional nulls (v4) already exhausted that space for
direction specifically. All four of today's trials came from the literature
channel: pre-holiday effect, DST transition, weekend/Monday effect, and the
Santa Claus Rally, each citing its academic source in its mechanism doc and its
ledger row.

## Two hypothesis formats

Unchanged this window. No new conditional-stack trial ran; Stack A remains the
format's only result to date (v4, Section 6).

## The shelf — why we don't draw thin, and why it is allowed to sit empty right now

Unchanged in mechanism, changed sharply in state. **Shelf position: 0/3
drawable**, down from 29/3 in v4 — every batch-screen survivor (Entries 37-61)
and every other magnitude-adjacent sourced entry (33, 35, 36) is PARKED under
the freeze. The rule that the owed action below the floor is "more sourcing,
never a thin draw" still holds, but under the freeze the only sourcing channel
open is the directional lane, which is itself capped and separately accounted
for. This is stated in Section 3 as a real operational consequence, not
resolved here.

## What we've concluded about where the edge isn't

87 directional nulls stood at v4. **Three more joined the list today** (trials
1-3 of the directional lane — trial 4 is disclosed thin-sample, not counted as
a clean addition to this figure): pre-holiday, DST transition, and
weekend/Monday, none of which transfer to NQ futures at this data ceiling, two
of them running opposite the literature's predicted sign. That brings
literature-sourced directional nulls specifically tested this window to 3 clean
+ 1 thin-sample-disclosed, on top of the 87 already on record from the old
Idea-Factory-sourced directional search. **All null so far.** That remains the
strongest single thing the project can hand an outside advisor, and the
directional lane exists specifically to keep adding to — or, eventually,
closing — this list with a pre-committed budget rather than an open-ended one.

---

# 7. The bot — the product roadmap

| # | Component | Status |
|---|---|---|
| B0 | Signal contract | **DONE** — unchanged |
| B1 | Signal engine | **DONE** for B3 — unchanged |
| B2 | Risk/State Engine | **BUILT** — unchanged |
| B3 | Base entry, frozen | **DONE**, acknowledged placeholder — unchanged |
| B4a | Order path (simulated) | **DONE** — unchanged |
| B4b | Order path (real broker) | **BLOCKED ON JASON** — IBKR futures permission, ~Oct 13th cooldown, unchanged, not re-raised |
| B5 | Execution measurement | **FIRST CUT DONE**, still scoring the same 16/20-fill sample — unchanged this window, no new fills landed (price data stuck at Sept 14th, Section 3) |
| B6 | Kill switches | **WIRED** — unchanged |
| B7 | Continuous paper run | **LIVE** — unchanged; checked at the top of all four cycles today, never advanced, per the ordering principle (Section 3) |
| B8 | Live-Limited | **MISSING** — Jason's authorization alone, non-delegable |
| B9 | Scale behind evidence | **MISSING** |

**Nothing under B0-B9 moved this window.** The bot was checked first every
cycle, exactly as the ordering rule requires, and every check landed the same
way: no new session data on disk to score, so no new fill, no new milestone.
This is the ordering rule working as designed, not a stall — the alternative
would have been spending a cycle on magnitude research it is not permitted to
do, or forcing a bot action with nothing new to act on.

---

# 8. How we prove we can execute it — the back half

Unchanged this window: the fourteen frozen execution checks, the two-clocks
rule, and the honest INSUFFICIENT SAMPLE reporting below 20 fills all stand
exactly as in v4. New this window: every write those checks and that execution
record depend on — the paper log, the order-path journal, the forward logs —
now sits behind the production write guard (Section 14.1), so the
live-journal-contamination failure mode that v4 reported as fixed by a test
fixture alone is now also fixed at the write-path level, independent of any
test remembering to isolate itself.

---

# 9. The agents — how the work is done and reviewed

Unchanged this window. Ten roles, the Director's separability question, the
blind Integrity Gate — all exactly as described in v4. None of today's four
directional-lane trials reached the Director, Monetization or the Gate; all
four closed at Discovery.

---

# 10. How we learn — and how we guard against fake work

Every closed hypothesis still gets a closure form with a classified failure
mode. The **busy-work guard was redefined this window**, directly from an
honest finding in v4's own operational review: the old guard fired after three
cycles with no ledger movement, but yesterday's batch-screen run moved 25 rows
while discovering almost nothing, and the guard passed during exactly the
failure it exists to catch. `src/cycle_budget.py`'s `done()` and
`ops_checks.py`'s `value` check now count movement only as: a hypothesis
changing stage in the ledger (a status-or-slice change, or a hypothesis's first
appearance), a scan being registered, or a bot milestone flipping in
`docs/BOT_ROADMAP.md`. **Shelf, inventory, study and mechanism-doc additions
count zero** — under today's rules, a fully-parked shelf and zero new
mechanism docs is not by itself evidence of busy work, and a shelf that fills
up with unworked entries no longer registers as progress. This closes the exact
gap the acceleration window's batch screen exposed.

Every other guard from v4 — hashed frozen scopes, the Director's separability
stage, the Idea Factory's descriptive-only status — is unchanged.

---

# 11. Rules that never bend

- Never fabricate data. Ever.
- The Holdout is sealed. Only Jason opens it.
- A frozen strategy is never retuned. Disappointing behaviour permits retain,
  restrict, suspend or retire — never a live edit.
- The placeholder entry is never a strategy, never an edge, and its P&L is never
  evidence. Unchanged; applies identically to any future placeholder.
- The Idea Factory queue is descriptive and never a result. The directional
  lane inherits this exactly — a lane trial that closes null is a result about
  the claim, not a claim about the lane itself.
- One stack = one trial; a paired family = two.
- Below the shelf floor, source more — never draw thin. Now explicitly tested
  by the freeze: the floor is allowed to sit unmet rather than draw a parked
  magnitude entry to fill it (Section 3, Section 6).
- **B8 live authorization is Jason's alone and is non-delegable.**
- No statistical result authorizes capital by itself.
- Nothing touches H118 or EXP047 without Jason.
- An automated cycle never edits a forward-validation evidence log on its own
  initiative — not even to correct a known error.
- **New this window:** a date is never an input to research scheduling or
  promotion decisions (refocus memo section 1, Section 2 above).

**Verified against this window's actual work, not assumed:** the Discovery /
Validation / Holdout split's integrity and the anti-optimization rule are
unaffected by anything in this window's change log. Checked explicitly, not
assumed: none of the four directional-lane trials touched Validation or
Holdout (Section 5); the production write guard changes what can write where,
never what a frozen spec means; the busy-work redefinition changes how movement
is *counted*, never what movement *is permitted*; and the cadence reversion is
a scheduling change, not a change to any promotion bar. Nothing above was
touched.

---

# 12. Autonomy — what runs without me and what doesn't

Cycles run every two hours, daytime only, 9am-11pm CT (**reverted this window**
from the 24-hour/12-cycles-a-day acceleration — Section 4, Section 14.3 of v4
for what the acceleration was), still pre-booked as independent one-shots
chained through the same self-booking 11pm step. Each cycle:

1. **Preflight** — lock, budget clock, pipeline sweep, both daily checkers,
   shelf/sourcing position. Writes a receipt.
2. **Ordering principle** — advance the lowest incomplete bot milestone that can
   actually move; if none can, say which is blocked and why, then fall through to
   research. Unchanged; this is why B0-B9 show "checked, not moved" rather than
   "not checked" in Section 7.
3. **The work item** — today, four directional-lane trials plus the sanity
   check, per the freeze's rules on what research is permitted at all.
4. **Close-out** — tests, operational checks, commit and push verified, lock
   released, compliance row written, then the owner's briefing
   (`session_report.py`), which now also prints **actual minutes used** from
   the budget clock and the day's cumulative cycles and minutes from
   `research/_cycle_compliance.jsonl` — read, never estimated, per Jason's
   explicit request in refocus section 6.

**Runs unattended:** everything through Validation, exactly as in v4. None of
today's directional-lane work required Jason's sign-off to close — each trial's
mechanism doc pre-registered its own falsifier, and a P1 fail or a
pre-registered thin-sample override closes the trial without a Holdout
decision.

**Requires Jason:** unchanged — opening the Holdout, authorizing live capital,
buying data, any decision about frozen evidence, and now, explicitly, reversing
the no-profit-deadline rule (Section 2) or the Full Scope cadence rule this
document is itself operating under.

---

# 13. What I want critiqued

1. Four directional-lane trials, all sourced from well-known, heavily-studied
   literature anomalies, all null (three clean, one thin-sample). Is that
   informative evidence that direction is genuinely hard to find in NQ RTH
   returns, or is four trials — all from the same "literature" channel, none
   yet from "mechanism" or "structure" — too narrow a sample of the lane's own
   sourcing rule to say anything about the lane as a whole yet?
2. Two of the four trials ran opposite the literature's predicted sign
   (positive where DST and weekend-effect research predicts negative). Is that
   just old, arbitraged-away anomalies behaving as expected in a modern,
   futures, 24-hour-traded instrument — the sanity-check's own conclusion — or
   is there a real possibility the house return convention itself has a subtle
   issue the same-code sanity check wasn't built to catch (it compared the
   three scripts to each other and to house convention, not to an independent
   from-scratch reimplementation)?
3. The magnitude freeze means the shelf can now sit at 0/3 indefinitely between
   directional draws. Is 16 remaining directional trials, spent at roughly one
   every two hours when the queue has something, actually going to resolve the
   direction question on a timescale that avoids the shelf sitting empty for
   weeks, or does the lane's pace of literature-sourcing (one new mechanism doc
   per candidate, written fresh each time) become the real bottleneck long
   before the 20-trial cap does?
4. The busy-work guard now counts zero for shelf, inventory, study and
   mechanism-doc growth. Is there a failure mode on the *other* side of this
   fix — a cycle that writes a real mechanism doc and sources a real
   directional candidate but the candidate doesn't reach a ledger stage change
   in that same cycle, and so reads as "no movement" when real, uncounted work
   happened?
5. The production write guard is default-deny, explicit-allow via
   `TONY_PRODUCTION=1`. Section 14.1 documents 13 files, 2 trees and 1 glob as
   protected, ~150 writers left deliberately unguarded as scratch/regenerable.
   Is that boundary drawn in the right place, or does "deliberately
   unprotected because it's regenerable" quietly assume no scratch output ever
   becomes load-bearing later the way `_console_state.json` once was treated as
   authoritative before it was retired?
6. Everything from v4's own critique list (magnitude vs. direction, the
   promotion bar's conservatism, the 72% batch-screen placebo-RED rate,
   measuring execution quality with placeholder-only fills, the search rate
   and multiplicity penalty, what an honest business built on magnitude alone
   looks like) is unresolved and unchanged. None of it moved this window
   because magnitude research is frozen and the bot didn't move. Should any of
   those six questions be re-ranked given today's four null trials, or do they
   stand exactly as asked in v4?
7. What is the single biggest way this project could still be fooling itself
   — including about the refocus itself, which this document was written to
   justify as much as to audit?

---

# 14. Everything that changed since v4 (September 15th, written earlier today)

Audited against 18 commits, 54 files changed, 3,340 insertions, 1,155
deletions (`a6fd5a3..HEAD`).

## 14.1 New tools and files

| Tool / file | What it is |
|---|---|
| `src/production_paths.py` | Default-deny write guard: `TONY_PRODUCTION=1` must be set for a write to reach a protected target. 13 files + 2 trees + 1 glob protected via 18 call sites in 13 scripts. |
| `tests/test_production_paths.py` | 8 tests proving the real ledger, execution log and journal are refused at their real paths with the conftest redirect undone, and are byte-for-byte unchanged afterward. |
| `research/integrity/write-path-audit-2026-09-15.md` | The audit itself: every writer under `src/`, classified PROTECTED or NOT-PROTECTED-BY-DESIGN with a stated reason (Section 14.1 table above summarizes it; the file has the full per-writer breakdown). |
| `research/infrastructure/weekly-verification-checklist.md` | Six-part checklist for the new queue item **1-VERIFY**: doc numbers vs code constants, registry counts vs actual files, booked triggers vs the standing schedule, the write guard vs test isolation, GitHub sync, and a written report citing `path:line` on every discrepancy. |
| `research/ledger/directional_lane.json` | The directional lane's own ledger: cap 20, one object per trial (n, hypothesis_id, entry, source_channel, claim, result, closed_at). Used 4/20 as of this document. |
| `research/mechanisms/dst-anomaly-nq-m32.md`, `weekend-effect-nq-m33.md`, `santa-claus-rally-nq-m34.md` | Pre-registered mechanism docs for directional-lane trials 2-4 (trial 1's is dated in yesterday's window). |
| `src/market_behavior_discovery_scan_037.py` / `_038.py` / `_039.py` / `_040.py` | The four directional-lane scan scripts (pre-holiday, DST, weekend/Monday, Santa Claus Rally). |
| `research/infrastructure/refocus-2026-09-15.md` | Jason's standing direction, recorded verbatim (Section 6 above, Section 14.3 below). |

## 14.2 Retired tools — git rm, nothing rebuilt

- `src/generate_console_state.py`, `research/_console_state.json`,
  `tests/test_generate_console_state.py`, and the push sequence that
  maintained them. Jason: *"It is overhead that nothing depends on, and the
  session report already carries every number it showed. Do not maintain it,
  do not port it, do not rebuild a replacement."* The session report
  (`session_report.py`) is the sole owner's briefing going forward.

## 14.3 New rules, forms and registries — the refocus, in full

All of the following comes from one source, `research/infrastructure/refocus-2026-09-15.md`,
recorded verbatim and copied into `research/NEXT_UP.md`'s REFOCUS section. It
supersedes the September 14th acceleration plan's Levers C and D and the "push
this as fast as possible" direction; Levers A and B (execution sample, broker)
stand as facts and are untouched.

- **No profit deadline, standing rule.** *"Any date by which I need trading
  income is not an input to research scheduling, promotion decisions, or the
  bot roadmap. If I ever state one, treat it as a flag that I am under
  pressure, not as a constraint to plan around, and say so... The account is
  money I can afford to lose; nothing about the pace of the research changes
  that."* His to set, his alone to reverse, in writing.
- **Cadence reverted.** 24-hour/12-cycles-a-day acceleration reverted to
  daytime 2-hour cycles (9am-11pm CT, 8/day); the 1am/3am/5am/7am triggers
  deleted. Reason, his: the acceleration window produced 16 fills from a
  placeholder proving no edge, 25 screen survivors (18 flagged placebo RED),
  seven operational defects including a contaminated live execution journal,
  and zero directional candidates. *"A cycle with no real queue item closes
  early and says so."*
- **Magnitude research frozen.** No new magnitude hypotheses, `batch_screen.py`
  never run again, the 25 batch-screen survivors (Entries 37-61) and Entries
  33/35/36 PARKED, not drawable until the 72% placebo-RED rate has a real
  explanation. Existing validated facts stay in use by the Risk/State Engine.
- **Directional lane opened.** Queue item 0-DIR, 20-trial hard stop, tracked in
  `research/ledger/directional_lane.json`, sourced only from non-state ideas.
  First candidate suggested by the memo (the overnight-vs-intraday split) was
  not what actually ran first — the four trials that ran are documented in
  Section 3.
- **Console retired.** Section 14.2 above.
- **Busy-work alarm redefined.** Section 10 above; code in `src/cycle_budget.py`
  and `src/ops_checks.py`.
- **Session report prints actual usage.** `src/session_report.py`'s OPERATIONS
  section now reads this cycle's minutes from the budget clock and the day's
  cumulative cycles + minutes from `research/_cycle_compliance.jsonl`, never
  estimated.
- **Production write guard built.** Section 14.1 above.
- **1-VERIFY weekly verification cycle queued.** Checklist in Section 14.1
  above, booked for Sunday 1pm CT. Its only job is checking Tony against
  itself; no research runs in it.
- **No-profit-deadline recorded as standing** (repeated here because it is also
  a new rule under Section 11, not only a fact about this window).
- **Full Scope's own cadence changed to weekly/on-request** — this document is
  the first edition produced under that rule, and its own opening section
  audits the change.

## 14.4 Results produced

- **Directional lane trials 1-4.** Full detail in Section 3. Summary: 3 clean
  nulls (trials 1-3, two of them wrong-signed against the literature's
  prediction), 1 thin-sample-disclosed (trial 4, point estimate in the
  predicted direction but n=6 and not credible). hyp-000163 through
  hyp-000166, all REJECTED. Directional lane: 4/20 spent, 16 remaining.
- **Methodology sanity check, clean.** `market_behavior_discovery_scan_037.py`,
  `_038.py` and `_039.py` read side by side against house return convention
  after three wrong-signed nulls in a row. No bug found; sign conventions,
  timezone handling and block-bootstrap setup are consistent across all three
  and with the rest of the codebase. Reported as a positive methodological
  event, not a null result.
- **Busy-work guard redefinition landed and is live.** `src/cycle_budget.py`'s
  `done()` now computes movement from `stage_changes`, `scans_registered` and
  `bot_milestones_flipped` only; shelf/inventory/study/mechanism-doc counts are
  still recorded for information but no longer decide `moved`. 7 tests added
  (`tests/test_cycle_budget_and_value.py`, `tests/test_session_report.py`).
- **Production write guard landed and is verified.** `python3 -m pytest -q`
  green with the guard in place (498 passing, this document's own count);
  `python3 src/bot_stack_paper_run.py --strategy dummy` ran normally through
  its `__main__` with no guard error; `tests/test_production_paths.py` proves
  the real ledger, execution log and journal are refused at their real paths
  with the conftest redirect undone. Full detail:
  `research/integrity/write-path-audit-2026-09-15.md`.

## 14.5 Errors found and corrected — the honest column

Nothing new joined this list this window beyond what is already reported as a
genuinely positive finding in Section 3 and 14.4 above: the scan_037/038/039
sanity check ran specifically because three wrong-signed nulls in a row raised
suspicion of a bug, and it came back clean. No live-record contamination, no
scheduling duplicate, and no reporting bug were found or fixed this window —
worth stating plainly since v4's own equivalent section (14.5) found five
separate errors; today's shorter, narrower cycle set (four directional trials
plus close-out) simply had less surface area for this kind of error to hide
in, and the production write guard now makes one whole class of them (an
accidental live-record write) structurally harder to reintroduce regardless.

## 14.6 Methodological lessons added to KNOWLEDGE

1. **A guard that measures activity instead of discovery will pass during the
   exact failure it exists to catch.** Yesterday's batch-screen run moved 25
   ledger-adjacent rows while discovering almost nothing, and the old busy-work
   alarm passed. The fix (Section 10) is now live and was itself the direct
   subject of this window's work, not a retrospective addition.
2. **A capped, pre-registered search on well-known literature anomalies is
   worth running even when — especially when — the expected outcome is null.**
   Four clean-to-thin nulls in one afternoon is exactly what "direction is
   closed by evidence, not by running out of patience" is supposed to produce
   evidence toward, on a pre-committed budget that cannot silently grow past
   its own cap.
3. **A sanity check that finds nothing is still worth reporting as a finding.**
   Three wrong-signed results in a row is the kind of pattern that would
   otherwise sit unexamined until it accumulated further; checking it
   immediately and reporting the clean result honestly (rather than only
   reporting checks that find bugs) keeps the record from silently selecting
   for negative findings.
4. **Freezing one side of a loop makes the other side's capacity constraint
   visible immediately.** The shelf sitting at 0/3 is not a new problem this
   window created; it is the magnitude freeze's real cost becoming visible the
   first day it was in effect, exactly as the rule that produced it intended.

## 14.7 Parked on Jason — carried forward from v4, unchanged, plus one addition

All of v4's Section 14.7 items are unchanged and not touched this window:
B4b/IBKR futures permission (~Oct 13th), B8 live authorization, hyp-000162's
cost clause, hyp-000162's joint-separability re-check, H118's open position
predating the forward anchor, the Šidák method, the undefined PAPER VERIFIED
review threshold, and the D11 swing strategy (await Jason, do not build). One
addition:

| Item | Status |
|---|---|
| **18/25 batch-screen placebo-RED cells** | Still not a decision item — flagged to Director/LEARN, unresolved. Now also gating: the freeze means none of the 25 survivors (or Entries 33/35/36) can be drawn until this has a real explanation, so this is now also blocking shelf capacity, not only a standalone open question. |

---

*End of Full Scope v5. Full Scope is now weekly-or-on-request
(research/infrastructure/refocus-2026-09-15.md, section 6) — the next version
runs whenever a week has passed or Jason asks again, and must audit against the
change log since this commit.*

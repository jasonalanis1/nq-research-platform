# Staff meeting — "What to do" (September 14th, ~9:40 am CT)

Convened at Jason's request. Present: Director, Statistical, Mechanism, LEARN,
Integrity Gate, Operations, Portfolio. Standing rule applied: a plan is judged
the way a hypothesis is — would we have adopted it before seeing the data, and
will being wrong about it teach us something.

Input: the ledger (468 trials), `research/_cycle_history.jsonl`, the Idea
Factory queue of 2026-09-14, `docs/BOT_ROADMAP.md`, `src/capital_protection.py`.

---

## The finding that reframes the question

The project has **one directional, Holdout-passed edge: H118** (vwap_dist LOW
tercile → 10-day drift). It is real, it survived all three stages, and it is in
forward validation now.

**The bot cannot trade it.** H118 is a *10-day swing* position. The bot being
built (B0–B9) is an *intraday* bot: B3, its entry slot, is a same-session
opening-range breakout. And `src/capital_protection.py` does not merely fail to
accommodate H118 — it **excludes it by name** (`excluded_strategies = ("H118",)`)
because its per-trade swing of roughly $1,000–1,400 sits far outside the
$50–150 band the funded budget is reserved for.

So the two halves of the project are pointed at different markets:

| | what it is | status |
|---|---|---|
| The one directional edge found | 10-day swing, ~$1,000–1,400 per trade | Holdout passed, forward validating |
| The bot being built | intraday, $50–150 per trade, placeholder entry | B0–B6 done, B7 live, B8 unreachable |

The bot's entry slot is still `base_entry_b3`, which its own spec says is **not
an edge and whose P&L is never evidence**. B8 (live capital) can never be
authorized on a placeholder. So on the current path the bot is complete,
correct, well-tested — and structurally unable to ever go live.

## The second finding: the generation engine cannot fix this

`docs/BOT_ROADMAP.md` gives research two jobs: **(1) replace B3 with a real
edge**, and **(2) improve B2 with better state variables**.

Of the 19 candidate families in today's Idea Factory queue, **17 are size
outcomes (range/mfe/mae) and 0 are direction.** Every candidate sourced in the
last week — M29, M30, M31, M32 — is a sizing input. Job (2) has a pipeline. Job
(1) has nothing in it at all.

This is not a sourcing oversight. The queue ranks by |z|, and volatility is
autocorrelated and therefore predictable while direction is not, so size
outcomes win every ranking on merit. The engine is doing exactly what it was
built to do and will keep returning sizing material indefinitely.

## Positions

**Statistical.** 468 trials, 234 per survivor, 159 since the last one. Of the
three things that cleared Holdout, one is directional and two are size. That
ratio is what the literature would predict and is not evidence of failure — but
it does mean the expected cost of finding a *second* directional edge is on the
order of another 200+ trials. At the current rate that is weeks of cycles for a
coin-flip. Also flags: two of the three survivors are volatility facts, and
hyp-000162's placebo red raises the live possibility that the sizing facts are
several readings of one underlying regime rather than independent inputs.

**Mechanism.** Every mechanism doc written in the last week tells a volatility
or flow story. Nobody has written a mechanism for why price should go one
*direction*, because the honest ones are hard and the project's own discipline
rejects "it filters out losers." Six directional entry detectors exist in `src/`
(fade-the-gap, FVG, initial-balance breakout, level sweep, ORB, VWAP reversion)
and none produced a live survivor. That is real negative knowledge about
intraday direction at this resolution.

**LEARN.** The closed backlog is dense with directional intraday attempts. The
project has already run this experiment many times. Trying a 21st variant
without a new *kind* of reason is the pattern the shelf rules were written to
prevent.

**Integrity Gate.** Notes the live example: hyp-000162 passed every registered
prediction and then failed the placebo. If the sizing facts are all proxies for
one volatility regime, then B2 has *one* input dressed as four, and the Risk/
State Engine is less informative than its documentation claims. This should be
settled before more sizing inputs are added on top.

**Operations.** Price data ends 2026-09-08. B7 has executed exactly **one**
session in its life, and that one was correctly gate-blocked — so the execution
layer has **zero fills, ever**. Every downstream milestone depends on a sample
that cannot begin to accumulate. Historical pulls cost $4.74 (RTY) and $8.35
(ES) for *seven years* of 1-minute data against an untouched $20/month cap;
keeping NQ current is pennies. Also: 5 of the last 12 cycles moved nothing.

**Portfolio.** With no entry, there is nothing to allocate. Portfolio has no
work until job (1) is answered one way or the other.

## Disposition: **MODIFY** — stop adding sizing inputs, force the direction
## question into the open, and unblock the execution sample

Four binding items.

**1. The sizing queue is paused at four inputs.** B2 already has prior-day
range, coiled overnight, VXN level, and (pending) M30. No further sizing
candidate is drawn until the Integrity Gate answers hyp-000162's regime
question, because that answer decides whether B2 currently has four inputs or
one. Adding a fifth reading of the same regime is not progress, and the queue
will keep offering them.

**2. The Idea Factory must report its queue split by JOB.** Direction
candidates and sizing candidates are listed separately, with the direction count
stated even when it is zero. The bias is currently invisible: a ranked list where
size always wins looks like a healthy queue right up until someone asks what is
feeding the entry slot. Making the zero visible every cycle is the cheap fix.

**3. Data currency is an operating cost, not a research purchase — Jason's
call.** The standing NO PURCHASE decision was made about buying *new
instruments*. Keeping the existing NQ series current is a different thing, costs
cents, and is the single blocker on B7 accumulating any execution sample at all.
Recommend approving a small standing spend. Without it the entire back half of
the roadmap is frozen no matter how much code gets written.

**4. The strategic fork goes to Jason, because it is a goal question, not a
research one.** Three honest options:

- **(a) Build the bot around the edge we actually found.** H118 is validated,
  directional, and forward-testing. It is a swing strategy — which is D11,
  currently parked with "awaits Jason — do not build." This path means the
  intraday bot becomes an execution testbed and the *live* bot is a swing bot,
  with a capital model rebuilt around $1,000–1,400 swings instead of $50–150.
- **(b) Keep the intraday bot and fund a real hunt for an intraday directional
  edge** — accepting, on Statistical's numbers, that this is likely 200+ more
  trials with no guarantee, and that the generation engine must be rebuilt to
  even produce candidates for it.
- **(c) Keep both as they are**: the intraday bot stays a paper-only execution
  laboratory indefinitely, H118 forward-validates on its own track, and the
  project stops describing B8 as reachable on the current path.

The staff's recommendation is **(a)**, with one caveat stated plainly: it means
accepting that the intraday bot — which is most of the engineering done to date —
becomes infrastructure for a strategy it was not designed around, and the
capital-protection model needs rewriting from its band upward. That is a real
cost. It is smaller than the cost of (b), which is the one path where the
project can work correctly for months and still have nothing to trade.

**What none of the options change:** the ordering principle stands, the freeze
rules stand, nothing touches H118 or EXP047 without Jason, and B8 remains his
authorization alone.

## What this meeting did not decide
Whether hyp-000162 is a distinct fact or a regime proxy — that is the blind
Gate's, and item 1 waits on it. Whether to spend the conditional-stack format's
last powered null — U28's look table found nothing that stands out, so the
answer stays "not yet" until material exists.

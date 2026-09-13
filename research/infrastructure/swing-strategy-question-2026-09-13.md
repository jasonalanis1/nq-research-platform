# Swing strategy — the question to take out for feedback (September 13th, ~4:45 pm CT)

Jason asked (Topic 6) for "swing trading with a particular exit strategy" to be on
the docket, and then said he doesn't have the exit rule yet — he wants Tony to
propose what the question looks like and how it would plug into what's already
running, so he can get outside feedback before anything is built. This is that
proposal. Nothing here is a hypothesis, a scan, or a rule change; it is the
question, in Tony's own terms, with the parts already decided marked as such.

## Plain-language framing

"Swing trading" here means holding a position for hours to a few days instead of
minutes — the same window the project already prefers because it resolves fast.
The thing that makes it a *strategy* rather than an idea is that all four parts
are written down and frozen before results are seen: what gets you in, what gets
you out, how big the position is, and when you're not allowed to trade at all.
Tony has proven facts for "how big" and "when not to"; it has nothing proven for
"what gets you in"; and "what gets you out" has never been researched as its own
question. That is the gap the outside reviews all pointed at.

## The question, as Tony would register it

> Given the market states Tony has already validated (prior-day range contraction,
> overnight coil, midday-lull → afternoon expansion, VXN level → next-day range),
> is there a **multi-day directional behavior that begins inside one of those
> states**, and if so, which **pre-declared exit** captures it after costs without
> being stopped out by ordinary noise?

Broken into the four frozen parts:

| Part | Status in Tony today | What the swing question asks |
|---|---|---|
| **Entry** (what starts a trade) | Nothing validated. Every directional idea has failed on average. | Does a directional move that *starts inside a validated volatility state* behave differently from the same move on an ordinary day? Candidates already queued: fade-to-VWAP on compressed days; overnight-vs-intraday split; the scheduled-event volatility family. Each is one pre-registered condition. |
| **Exit** (what ends it) | Never researched as its own family. | Which of five pre-declared exits preserves the entry's edge: (1) fixed stop + fixed target; (2) fixed stop + time exit; (3) fixed stop + volatility-scaled trailing stop; (4) fixed stop + session-end exit; (5) one exit conditioned on a validated state (e.g., exit when the expected-range forecast collapses). Chosen from excursion data — how far trades ran for and against before closing — never by trying dozens of thresholds. |
| **Size** (how much) | Solved in principle: the Risk/State Engine (U13) turns expected range into stop distance and position size. | Feeds the exit distances directly; a swing trade's stop is set from expected range, not fixed points. |
| **Permission** (when not to trade) | Solved in principle: the same engine flags compressed / event / illiquid sessions. | Adds one swing-specific rule: no new swing entries into a scheduled event the position would have to hold through. |

## How it plugs into what's running now

1. It is **not** a new pipeline. It is one research family ("swing horizon") that
   goes through the existing sequence: mechanism doc → registered family with a
   fixed outcome battery → one Discovery scan → Statistical → Director → Monetization
   → blind Gate → Validation → Holdout (Jason) → Risk/State Engine → paper trading.
2. The **exit research** piece is the only genuinely new machinery, and it only
   starts once the Discovery Engine v2 outcome battery (U12) is producing
   max-favorable / max-adverse excursion numbers — that is the data an exit is
   designed from. Until then the question is registered, not run.
3. The **entry candidates** are the three already on the upgrade queue (U5). If any
   passes, it becomes the first swing entry; if none does, the swing family closes
   honestly and the exit research still has value for any future directional
   candidate.
4. **Sizing and permission** come from the Risk/State Engine (U13), which is being
   built regardless.

## What feedback would actually help

- Is "a directional move that begins inside a validated volatility state" the right
  definition of a swing entry for this project, or is there a better starting point
  that doesn't require Tony to first find direction?
- Of the five exits, which one (or two) should be the *default* to test first, and
  is there a sixth worth pre-registering? The reviews' consensus candidate is (3),
  a volatility-scaled trailing stop fed by the Risk Engine.
- Should a swing position ever hold through a scheduled release, or is "flat into
  events" a hard rule?
- Is hours-to-a-few-days the right window, or does swing here mean multi-week (which
  would collide with the project's fast-resolution constraint and needs to be said
  out loud if so)?

## What is already decided (not up for feedback)

- Exit rules are frozen before any result is interpreted (all six reviews).
- Exit research is its own family, never a tuning step on a failed entry.
- Position size and stop distance come from expected range, not fixed points.
- Swing does not become a loophole around the hours-to-days focus.
- No capital until execution qualification passes; live authorization is Jason's alone.

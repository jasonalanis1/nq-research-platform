# Scoping note — search perspective ahead of Sept 19 checkpoint

Written: 2026-09-13, interactive session (off-cycle, at Jason's request)
Purpose: prep material for the Sept 19 "how to be more effective at
pinpointing strategies" agenda item. Not a decision document — lays out
what's true today so the 19th conversation starts from facts, not memory.

## Where this came from

Jason raised two related but separate questions: (1) is scheduled-event
data ("chatter," calendar events) part of the search, and (2) should the
project read order flow / market depth in something closer to how a
discretionary trader reads a screen (who's "in," who's "out," Level 2/3),
rather than only backward-testing documented statistical mechanisms.

## 1. Scheduled-event data — already in the platform

FOMC, NFP, and CPI release-day/pre-release drift have all been tested
already, using only the public dates of those events (no purchased
calendar data needed — the dates are free and public). Results: pre-FOMC
drift was not credible; pre-NFP drift was credible but wrong-signed
against two monetization attempts. A separate, more specific idea —
conditioning the "Opening-Hour Reference-Level Fade" finding (a real,
already-measured conditional-return behavior) on proximity to a scheduled
catalyst window — was carved out from an event-gap-analysis doc Jason
supplied 2026-09-11 and is sitting in LEARN/Mechanism/Director review
(`research/studies/event-conditioned-reference-level-fade-h81-recut-draft.md`).
This is a live, in-progress thread, not something to start from scratch.
Net: this half of Jason's question doesn't need new data or new
infrastructure — it needs the review it's already queued for to finish.

## 2. Order-flow / market-depth data — the honest history

This exact category was priced on Sept 3rd and Jason explicitly, firmly
rejected it on Sept 7th ("drop it entirely, don't keep bringing it up"),
filed under Backlog's "Rejected" heading specifically so it would stop
resurfacing. That closure is being revisited now at Jason's own
initiative — worth being upfront about that at the 19th, not pretending
it's a fresh question.

**What it actually costs, broken into what was and wasn't priced before:**
The ~$54k/yr figure that got rejected is Databento's Unlimited plan
($4,500/mo, annual contract) — full order-book depth (L0-L3: trades,
book-by-order, book-by-price) across 16+ years of history. That is the
expensive way to get this data: buying a decade-plus of tick-level book
reconstruction up front.

There's a materially cheaper, structurally different option that was not
priced before: Databento's Standard plan is $199/mo with no annual
commitment, and gives full L2/L3 depth — but only a rolling 1-month
history window. That doesn't support backtesting years of history, but it
does support starting a forward-collection process today: subscribe,
start capturing NQ's real order book going forward, and after some months
you have your own growing depth dataset built at ~$2,400/yr instead of
$54k/yr. The tradeoff is time — you'd be building a real dataset, not
buying one, and it would take months to have anything to backtest on.
Exact current pricing should be confirmed directly (Databento's own
`metadata.get_cost()` / `list_unit_prices()` API is free to query, no
purchase needed — this requires a request from a machine that can reach
databento.com, which this session's sandboxed shells cannot; the RTY/ES
purchase pattern from this week is precedent for doing this from your own
Terminal if we want an exact number before the 19th).

**What this doesn't resolve:** the project's own standing principle
(logged back in the September 8th pivot) says define exactly what
information or behavior is being sought using the 1-min data already on
hand, before buying anything new. That's the more useful thing to do
next, independent of the pricing question — see below.

## 3. Reading the chart "like a trader" using data already on disk

This has already been scoped and partially run — not a new idea. Back on
Sept 8th, five candidate behaviors were drawn up as ways to approximate
intraday, trader-style pattern recognition using only the 1-min OHLCV
already on disk (no order book needed): opening-range structure, VWAP
reversion vs. trend persistence, volume-profile shape across the session,
momentum-burst bars, and overnight-gap fill dynamics. All five have been
tested. One survived — a volatility-conditioning fact about range
contraction predicting what happens next — the first finding in this
project's history to survive the Validation stage.

That success immediately hit a real, unresolved fork: this project now
has three of these volatility/conditioning facts that survived Validation
(range-contraction, overnight-coil, release-day-magnitude) and zero
directional signals left alive to attach them to — every existing
directional signal is dead, so there's nothing to condition. Trying to
graft these facts onto already-dead signals has been tried three times
and, unsurprisingly, found nothing. The two real paths forward were
identified back then but never decided:
(a) design a brand-new directional entry built specifically to pair with
    one of these volatility facts (e.g., a breakout-style entry sized and
    timed around post-coil or release-day expansion — opposite structure
    from a mean-reversion entry, which is what's been tried and killed
    repeatedly), or
(b) treat these three facts as pure characterization — real, interesting,
    but not something to force into a tradeable signal — and look for the
    next directional idea independently.

This is, in plain terms, the closest thing this project already has to
"read the chart like a trader": recognizing a state (compressed range,
overnight coil) the way a discretionary trader would glance at a chart
and say "this is coiled, it's going to move" — except measured
statistically instead of by eye. It's sitting exactly where Jason's
question points, and it's been waiting on a decision since early
September rather than a new data purchase.

## Recommendation for the 19th

Two separate decisions, not one:
1. The order-flow/depth data question is really "cheap forward-collection
   starting now" vs. "stay out entirely" — not a re-litigation of the
   $54k full-history purchase, which stays a bad idea either way. Decide
   whether a ~$200/mo forward collection is worth starting now so there's
   something to test in a few months, understanding it buys nothing
   immediately.
2. The fork above (pair volatility facts with a new directional signal,
   or stop trying) is the more immediately actionable "search perspective"
   decision, needs no new data or spend, and has been open since
   September 9th. Resolving it is probably the highest-leverage single
   decision available for the 19th.

Nothing from this project's history has been lost — the market structure
map and idea inventory track every tested idea (closed or open) with its
reasoning, and this note draws entirely from that record plus the backlog
log, not from anything reconstructed or guessed.

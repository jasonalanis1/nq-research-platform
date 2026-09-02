# VWAP Mean Reversion (2σ / 3σ Bands)

**Status: frozen definition, not yet tested** — drafted 2026-09-02, at
Claude's own initiative as research lead, directly in response to
Jason's request for deep research into widely-used day-trading
techniques as a source for the next hypothesis, rather than continuing
to invent or condition on already-tested ideas.

## Where this came from

Jason asked, after Fade the Gap's rejection, for research into how real
day traders actually operate and which techniques are widely used —
looking for a legitimately different, well-grounded idea rather than
another self-generated variation. This document is the result of that
research (web search across futures-specific trading education sites,
prop-firm content, and academic/SSRN sources on VWAP execution — see
citations at the end) plus an explicit filtering pass against everything
this project has already tested.

**What research surfaced, and why most of it was set aside:**

- **ICT-style concepts (liquidity sweeps, order blocks, the "Judas
  swing")** — currently one of the most-discussed retail futures
  trading frameworks. Set aside: stripped of its branding, the core
  claim ("price sweeps a liquidity level, then reverses") is the exact
  thesis this project already tested six ways as Level Sweep Reversal
  and its variants, all rejected, one (the FVG entry trigger) decisively.
  Retesting it under ICT's vocabulary would be exactly the kind of
  "keep varying one idea until something looks positive" search
  `docs/RESEARCH_INTEGRITY_PROTOCOL.md` exists to catch.
- **Volume Profile / Value Area (POC, VAH, VAL) reversion** — also
  widely used, and a legitimately different LEVEL CONSTRUCTION (a
  volume-distribution statistic rather than a swing point or a session
  open/close). But the underlying behavioral claim — "price reverts off
  a specific, precomputed static level" — is philosophically the same
  shape as the already-six-times-rejected reversal thesis and Fade the
  Gap's prior-close target. Not chosen as the next test for that reason,
  though it remains a candidate worth naming for the record.
- **Classic floor-trader pivot points (PP/R1-R3/S1-S3 from the prior
  day's H/L/C)** — extremely widely used, especially in futures, but
  the same "static level precomputed from a prior period" shape as
  Fade the Gap and the volume-profile idea above. Also set aside for
  that reason, also worth naming for the record.
- **Opening Range Breakout variants** — this project has already tested
  this thesis twice (the original ORB placeholder, exp-013, and
  Initial Balance Breakout, exp-028), both rejected. Not revisited
  without a specific new reason to expect a different definition would
  behave differently.

**Why VWAP mean reversion is the one actually chosen:** it is the only
widely-used technique surfaced that is mechanically distinct from
everything above. Every setup this project has tested reverts to or
breaks from a STATIC level fixed at one point in time — a swing high/low,
the Initial Balance range, the prior session's close. VWAP (volume-
weighted average price, recomputed cumulatively bar by bar through the
session) is a DYNAMIC level that price interacts with continuously all
day, and its grounding is different in kind, not just in degree: VWAP is
the standard institutional execution benchmark (asset managers and
brokers routinely measure and are measured against how their fills
compare to session VWAP), a real, well-documented piece of market
microstructure with academic literature behind it (e.g. Frei &
Westray's "Optimal Execution of a VWAP Order," and later work on VWAP
execution algorithms and their market impact — see citations), not a
purely technical-analysis "the market remembers this price" claim like
every reversal-family setup tested so far. Large VWAP-benchmarked
execution flow creates genuine, mechanically-motivated buying/selling
pressure back toward the running average as the session progresses —
this is a different causal story from "traders remember a swept level,"
which is the honest reason it's worth a fresh test rather than a
retest.

**An explicit skepticism flag on the research itself:** the retail
trading-education sites surveyed (see citations) claimed VWAP strategy
win rates of 65-85%. Those figures are not backed by any visible
methodology, sample size, cost model, or out-of-sample check — exactly
the kind of unverified marketing claim this project's own
`docs/RESEARCH_INTEGRITY_PROTOCOL.md` exists to be skeptical of. Nothing
about those specific numbers is used here; only the STRUCTURE of the
technique (standard-deviation bands around VWAP, entry at the 2nd band,
stop beyond the 3rd, target back at VWAP) is borrowed, because that
structure is a genuine, independently-documented convention (analogous
to Bollinger Bands' standard 2σ default), not because the claimed win
rates are trusted.

## Definition

### 1. Session VWAP and bands — computed causally, bar by bar

Starting from the same 8:30 AM ET session-open convention every other
setup in this project uses (`detect_ib_breakout.py`'s
`OPEN_HOUR`/`OPEN_MINUTE`, not redefined here), VWAP is the running,
volume-weighted average of price from the session open through the
current bar:

    VWAP[t] = sum(typical_price[i] * Volume[i] for i in session bars 0..t) / sum(Volume[i] for i in session bars 0..t)

using each bar's typical price `(High + Low + Close) / 3` (the standard
VWAP convention). The band width at each bar is the volume-weighted
standard deviation of price around VWAP over the same cumulative window:

    variance[t] = sum(Volume[i] * (typical_price[i] - VWAP[t])**2 for i in 0..t) / sum(Volume[i] for i in 0..t)
    sigma[t] = sqrt(variance[t])

Both are recomputed at every bar using only that bar and everything
before it in the same session — no look-ahead, and VWAP/bands reset to
zero at the start of every session (this is a SESSION VWAP, not a
multi-day running average).

### 2. Warm-up period — bands are meaningless on too little data

For the first `WARMUP_MINUTES` (30, matching the Initial Balance window
already used elsewhere in this project) after the open, sigma is
computed from too few, too-similar bars to mean anything (it can be
near zero, producing absurdly tight "bands"). No signal is considered
during this warm-up window — the first bar eligible for a signal is the
first bar at or after 9:00 AM ET.

### 3. Signal — first close beyond the 2σ band

Starting after the warm-up window, watch for the first 1-minute bar
whose Close closes beyond `VWAP[t] + 2*sigma[t]` (upper band) or
`VWAP[t] - 2*sigma[t]` (lower band). The first such bar in either
direction is the signal for the day — no flip-flopping if the other
band is also touched later, same discipline as every other setup here.

### 4. Direction — fade it, back toward VWAP

- Close beyond the **upper** band: go **short**, betting on reversion
  down toward VWAP.
- Close beyond the **lower** band: go **long**, betting on reversion up
  toward VWAP.

### 5. Entry, stop, and target — a 2:1-or-better structure from the bands themselves, not tuned

- **Entry:** the signal bar's Close. Note this can land somewhat past
  the 2σ trigger line, not always right at it (a fast 1-minute move can
  close well beyond where it first crossed the band) — this matters for
  the stop definition below.
- **Stop:** exactly **1σ from ENTRY** (`entry + sigma[t]` for a short,
  `entry - sigma[t]` for a long) — betting the move is exhausted, not
  that it can never reach one more standard deviation.
- **Target:** `VWAP[t]` itself, at the signal bar — literally the level
  being reverted to, the same honesty-flagged departure from this
  project's usual 1.35R-multiple target that Fade the Gap used, for the
  same reason (the entire premise is reversion to a specific level, not
  a risk-multiple).

Because risk is always exactly 1σ from entry and reward is at least 2σ
(entry is at or past the 2σ line, target is at 0σ), this gives a **2:1
R:R or better by construction of the band convention itself** — not
picked or tuned to make this setup's math look better than Fade the
Gap's forced 1:1.

**A real bug found and fixed during implementation/testing, documented
here because it changed the frozen definition:** the first version of
this document (and the code built from it) defined the stop as a FIXED
`VWAP[t] + 3*sigma[t]` band level, assuming entry always sits close to
the 2σ line. Testing against the real Discovery slice found this was
wrong often enough to matter (~17% of signals): a fast 1-minute move can
close well past 2σ — sometimes even past where the fixed 3σ level would
have been — which put that fixed stop on the WRONG SIDE of entry
(already in-the-money before the trade even started), producing wildly
unstable R-multiples that were a bookkeeping artifact of the stop
definition, not a real result. Anchoring the stop to ENTRY instead
(always exactly 1σ away, same direction as the excursion) fixes this
by construction — the stop can never land behind entry, regardless of
how far past the 2σ trigger the actual close happened to land. See
`src/detect_vwap_reversion.py`'s docstring and
`tests/test_detect_vwap_reversion.py`'s
`test_stop_stays_on_adverse_side_even_for_a_large_overshoot` for the
full detail.

### 6. Resolution — no artificial time cutoff, unlike Fade the Gap

Unlike Fade the Gap (which was bounded at noon to match the specific
window its underlying characterization study measured), VWAP mean
reversion has no natural session-fraction anchor — the claim is simply
"an overextended move relative to the day's own volume-weighted average
tends to revert," which could just as easily trigger and resolve at
10am or 2pm. The trade is held using this project's standard
open-ended `backtest.simulate_trade()` (stop or target, whichever comes
first; unresolved if neither is hit before the day's data ends) —
reused completely unmodified, not a new bespoke resolution rule.

### 7. First signal only per day

Only the first qualifying 2σ-band touch each day is tradeable, matching
every other setup in this project's "no flip-flopping" discipline. A
more sophisticated version could allow multiple reversion trades per
day (VWAP reversion isn't inherently a one-shot event the way a
breakout or a gap is) — noted here as a real simplification and a
possible follow-up, not silently assumed away.

### 8. No look-ahead

VWAP and sigma at the signal bar are computed only from that bar and
everything before it in the same session; the entry itself is that same
bar's Close. Nothing used to define direction/entry/stop/target depends
on data that hadn't occurred yet at the moment of the signal.

## Honesty flags — our own choices, not derived from any single source

- **Typical price `(H+L+C)/3`** for the VWAP calculation is one common
  convention among several (Close-only VWAP is also widely used) —
  chosen because it's the more standard definition in the sources
  reviewed, not because it was tested against the alternative.
- **30-minute warm-up window** — borrowed from this project's own
  Initial Balance convention for consistency, not derived from any
  claim about how long VWAP bands specifically take to stabilize. A
  shorter or longer warm-up is a legitimately different, untested
  choice.
- **2σ entry / 3σ stop / VWAP target** — a real, independently
  documented convention (see citations), but still one convention among
  possible variations (e.g. 1.5σ/2.5σ, or a partial-reversion target
  short of VWAP itself). Not chosen after looking at how this project's
  own data responds to alternatives — chosen from the outside literature
  first, per this project's standing discipline against fitting the
  definition to this data.
- **First signal per day only** — a real simplification, flagged in
  Definition #7 above.
- **The claimed 65-85% win rates from the retail sources researched are
  explicitly NOT relied on anywhere in this definition or expected to
  hold** — see "Where this came from" above. Only the band STRUCTURE is
  borrowed.

## Multiple-testing context

This is the tenth strategy hypothesis tested in this project (after six
reversal variants, Initial Balance Breakout, and Fade the Gap), and the
first sourced from external technique research rather than a market-
structure concept applied fresh or a direct mechanical translation of
this project's own characterization finding. `purgedcv` remains
unavailable for the formal DSR/PBO correction — flagged consistently on
every experiment in this project to date.

## Status

Frozen definition only — not yet tested against real data. Will be
tested against the Discovery slice per this project's standard pipeline
(detection code, unit tests, verified performance-optimized backtest
run, honest write-up as `research/experiments/exp-034-vwap-mean-reversion.md`,
ledger entry regardless of outcome).

## History

- 2026-09-02: this document written, at Claude's own initiative as
  research lead, following Jason's explicit request for research into
  widely-used day-trading techniques as a source for the next
  hypothesis.

## Citations (from the research pass — see "Where this came from")

- NinjaTrader (futures platform vendor), "VWAP Strategies for New
  Futures Traders" — trend-following and mean-reversion VWAP framework,
  standard deviation bands as fade/exit zones.
- futureshive.com, "VWAP Trading Strategy: Complete 2026 Guide for
  ES/NQ Futures" — the specific 1σ/2σ/3σ band structure and
  entry/stop/target shape this definition borrows (win-rate claims in
  this source explicitly NOT relied upon, see Honesty flags).
- SSRN: Frei & Westray and related work on optimal/mean-variance VWAP
  execution, and academic literature on VWAP algorithm market impact —
  cited as evidence VWAP is a real, mechanically-grounded institutional
  benchmark, not a purely technical-analysis construct.
- Cross-referenced against this project's own history
  (`research/experiments/_index.md`) to rule out ICT liquidity-sweep
  concepts, volume-profile/value-area reversion, floor-trader pivot
  points, and further ORB variants as not-genuinely-new — see "Where
  this came from" above for the reasoning on each.

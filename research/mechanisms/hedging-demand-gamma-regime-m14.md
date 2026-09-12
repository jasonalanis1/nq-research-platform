# Mechanism — Option-dealer gamma regime and late-day continuation (M14)

Written: September 12th, ~9:32 am CT  ·  Pre-registered  ·  Sourcing entry, queue v2 item 2b (TEST cycle)
Results seen before writing: no. No scan exists. Scan waits for ES data and Jason's go.

## 1. The claim
Baltussen, Da, Lammers and Martens (2021, Journal of Financial Economics,
"Hedging demand and market intraday momentum") show that the late-day
continuation of the day's move (the Gao et al. 2018 intraday-momentum
effect) is driven by hedging demand from two constrained participants:
leveraged-ETF sponsors (our M13) and option dealers. When dealers are net
SHORT gamma, their delta hedging must chase the market -- buy after it
rises, sell after it falls -- so the day's move is amplified into the
close. When they are net LONG gamma, hedging leans against the move and
dampens it. The gamma sign is not a view; it is set by what the public has
bought and sold, and the hedge is mandatory.

M14's claim is therefore NOT "late-day continuation exists" (that is M13
and 2e). It is: late-day continuation is STRONGER in negative-gamma regimes
than in positive-gamma regimes. The regime is the conditioning variable;
the level is not the test.

## 2. Who is on the other side
Liquidity providers and any participant willing to fade a hedging-driven
push, compensated by the partial next-session reversal once the hedge is
complete. Dealers cannot decline to hedge.

## 3. The proxy, and why it is the weak part (stated plainly)
Dealer gamma is not visible in price. Two proxies, in order:
- PRICE-ONLY (what can run now, once ES is on disk): the trailing 20-day
  first-order autocorrelation of ES 30-minute intraday returns. Negative
  gamma should produce POSITIVE intraday autocorrelation (hedgers chase);
  positive gamma NEGATIVE. Computed on ES because SPX options are the
  gamma pool and the regime transmits to NQ through correlation (outside-
  AI response A). Terciles frozen on Discovery. This proxy is coarse and
  can be contaminated by any other source of autocorrelation; that is why
  this entry's information value is mostly as a GATE (Section 6).
- OPTIONS-DATA (if Jason lifts the ceiling): end-of-day SPX/NDX/QQQ open
  interest by strike and expiry, dealer gamma estimated with a stated,
  reproducible convention (customers long calls / short puts assumption),
  never a vendor "GEX" number. This is the version the paper actually
  tests.

## 4. Testable predictions
P1 (GATING). Sign-adjusted 15:30-16:00 return / ATR14 (sign = day-so-far
   9:30-15:30 return) is credibly LARGER in the top tercile of the proxy
   (most positive ES intraday autocorrelation = most negative gamma) than
   in the bottom tercile. The test is the DIFFERENCE between regimes, with
   its own bootstrap CI; NULL 1 applies to each cell as well.
P2 (reported). The regime effect exists within NQ and within ES with the
   same sign; it does NOT order by instrument the way M13 does. Next-
   session reversal is larger after negative-gamma-regime closes.

## 5. What would falsify this
(a) No credible difference between regimes (the level may still be
    positive -- that belongs to M13 / 2e, not here).
(b) The regime effect disappears after controlling for realized-volatility
    tercile: then the proxy was just measuring volatility.
(c) Kill rule: if the regime difference lives only in the 15:59-16:00 bar.

## 6. Information gain and edge potential (the ranking fields)
Information gain: HIGHEST in the queue regardless of outcome. A credible
price-only regime effect is the specific, pre-registered reason to buy
options data (the paper's real test); a null price-only result keeps the
data ceiling where it is. Either way the ceiling decision stops being a
guess.
Edge potential if real: regime-dependent behavior every day, not event-
bound -- it sets direction and size of late-day trades and the choice
between continuation and fade. Product track: risk-execution first,
directional second.

## 7. Resurrection ruling (LEARN + Integrity)
- M7 / hyp-000029, 030 (VXN level and rate-of-change as directional
  signals, CLOSED): VXN measures expected variance, not the sign of dealer
  hedging. Different variable, different mechanism. Not a resurrection.
- M13 (LETF): the same paper's OTHER channel. Overlap is real and is
  handled by design: M13 tests level and instrument ordering; M14 tests
  regime difference within instrument. A cycle must never count a shared
  late-day-continuation level as evidence for both.
- 2e intraday momentum (Gao): the base effect; M14 conditions it.
RULING: NEW. Attempt 1 of 2. Decay: base intraday momentum documented on
1993-2013 SPY, published 2018; the hedging-demand explanation published
2021. Discovery 2015-2021 is post-publication for the base effect; a null
may be decay.

## 8. Instrument-choice gate
1. Leads: ES carries the SIGNAL (SPX options are the pool); NQ and ES both
   express it. 2. Minutes not milliseconds: dealer hedging is executed
   through the closing window, on a schedule. 3. NQ is a fine vehicle; MES
   too. 4. Directional within the day's sign, regime-conditioned. 5. NULL 1
   applies per cell; the regime DIFFERENCE is baseline-free.

## 9. Frozen scope
Instruments NQ and ES. Regime = terciles of trailing 20-day lag-1
autocorrelation of ES 30-minute intraday returns, frozen on Discovery,
lagged one day (no lookahead). Outcome as in M13. Cells: 2 instruments x
3 regimes = 6, plus the 2 gating differences = 8 to register. Data: ES
1-minute NOT on disk (queue item 3). Do not scan NQ-with-NQ-proxy first.

## 10. Prediction status
P1 -- untested. P2 -- untested. Waiting on ES data and Jason's go.

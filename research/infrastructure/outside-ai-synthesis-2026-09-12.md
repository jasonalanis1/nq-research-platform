# Outside-AI synthesis — hypothesis sourcing (three responses + staff meeting)
Filed September 12th, ~9:10 am CT. Jason polled three outside AIs with the shared brief plus the open-scope clarification. This reconciles them with the staff-meeting disposition and sets the working queue.

## Four-way consensus (all three responses + staff meeting)
- Baseline check on H118 first; never test a long-only directional claim against zero again.
- The three validated volatility facts are STATE variables that switch other relationships on/off, not signals. They are "risk/execution alpha" (a real product track), not consolation prizes.
- Add ES, RTY, YM 1-minute bars (cheap, same tier). Contract-specific bars where possible — the continuous-series roll gap that killed M9 must not recur.
- Defer options/tick data until a price-only result says there is something to sharpen. When it happens, compute the gamma regime from ES/SPX, not NQ.
- Never restart: candlesticks, ORB variants, VWAP/level fades, gap rules, rejected calendar effects, daily lagged cross-asset regressions, correlation-regime screens, multi-asset 1-5 day trend, ML feature matrices, opaque "GEX"/"smart money" products.
- Cap the active slate at ~5 families. The danger now is hypothesis count, not weak testing.

## The one real conflict, adjudicated
A: cross-index spread mean reversion has no forced participant and is competed by stat arb — skip.
B and C: NQ-vs-ES beta-adjusted residual repricing is the centerpiece.
C's own caveat resolves it: a 1-minute lead-lag can be real and still too fast to trade (order-flow impulse responses dissipate within a second — arXiv 2508.06788). RULING: pure 1-minute cross-index lead/lag is NOT a trade family. Relative-value claims enter only (a) at 5-30 minute horizons or session transitions where a participant plausibly adjusts slowly (the cash-open acceptance/rejection test is the best-shaped version), (b) with the residual r_NQ - beta*r_ES as the outcome, beta estimated from prior data and frozen within each OOS stage, and (c) with a pre-registered kill rule: if the response is concentrated in the first 1-minute bar, the family terminates — no re-tuning toward slower variants. B's broader lead/lag and state-vector ideas become an OBSERVATORY characterization program (our designed home for "describe before you claim"), not hypothesis families.

## Best single new entry (A only, adopted at the top)
Leveraged-ETF close rebalancing. Leveraged/inverse funds MUST trade into the close in the direction of the day's return; size is computable from public AUM (sum of (L^2 - L) * AUM * r per family). Built-in mechanism test: the flow is a small share of NQ's close and a large share of RTY's, so run one pre-registered scan with instrument as a factor (RTY, ES, NQ) and expect it in RTY first. Not a resurrection of M1/hyp-000110 (those were reversal claims about the close move itself; this is continuation driven by the day's return, a different participant). Caveat: widely known since ~2010 and traded against in big indices — which is exactly why the RTY leg matters. Needs RTY data + LETF AUM (free, manual).

## Adopted from C
- Two nulls, stated project-wide: directional claims vs the unconditional drift; cross-index claims vs the beta-implied move.
- Instrument-choice gate before any cross-market test: which contract should lead under the mechanism, why at minutes not milliseconds, is NQ the right vehicle, directional or relative, does it survive a beta-neutral benchmark.
- Three product tracks: directional alpha / relative-value alpha / risk-execution alpha.
- Curve-conditioned rotation (front-end vs long-end rate shocks change NQ's relative response) — fixes the identification problem in our old ZN test; needs a front-end rates future (ZT or SR3).
- Cash-open acceptance/rejection of the pre-open NQ/ES residual.
- Rebalance/roll mechanics need contract-specific data — same as A's outright-contract fix for M9.

## Adopted from B
- Semivariance (upside vs downside realized variance) as a state variable — free, from data on disk; cited evidence is commodities, may not transfer.
- Event reaction SHAPE (shock -> retrace -> continue/reverse) as a new claim family distinct from the closed event-direction families; low priority, small n.
- The reframe: an intraday information-discovery program whose execution target is NQ.

## Data plan, in order (all under Jason's cap; $5+ rule applies per purchase)
1. ES, RTY, YM 1-min OHLCV, contract-specific/outright where the feed allows (A: ~$8-15 each; verify with get_cost).
2. NQ outright contract months for the ~46 witching weeks only — revives M9.
3. SPY, QQQ, IWM, DIA 1-min bars (equities feed; needed for the cash-open test and futures-vs-ETF confirmation).
4. ZT (2-year) or SR3 for the curve test.
5. Free: VIX and VXN futures settlements (CBOE) for term-structure slope; LETF AUM/shares outstanding (issuer files).
6. Only after a price-only result: targeted tick/BBO sample around selected hours; EOD options chains for the hedging-demand refinement.

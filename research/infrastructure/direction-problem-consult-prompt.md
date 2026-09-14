# Consult prompt — the direction problem

*Paste this whole thing into a strong reasoning model (a fresh one, not the one
that has been working on the project), or hand it to a quant who has traded
index futures. It is written to be self-contained.*

---

## The ask

I run a systematic research program on Nasdaq-100 futures (NQ). Over ~155
pre-registered hypotheses I can now predict **how much** the market will move
with results that survive rigorous validation, but I have never once predicted
**which way** it will move. I need an outside read on whether I am looking in the
wrong place, whether my process is killing real effects, or whether I should stop
looking for directional edge entirely and build the business around what I can
actually predict.

Please push back hard. I would rather be told the premise is wrong than be
encouraged.

## What the program is

A single-person systematic research operation on NQ futures, running automated
research cycles every two hours. The goal is a live trading bot. Everything is
pre-registered and logged; the process was deliberately built to make
self-deception expensive.

**Method, in brief:**
- Data is split three ways: **Discovery** (2015 → Oct 2021, 2,101 sessions) for
  all searching, **Validation** (Oct 2021 → Jan 2024, 700 sessions) for one-shot
  confirmation, and a sealed **Holdout** that requires my explicit sign-off to
  touch and has been opened 3 times total.
- Every hypothesis needs a written **mechanism document before the scan runs** —
  who is on the other side of the trade and why they are there. "It filters out
  losers" is rejected as curve-fitting.
- Scope is **frozen before data is touched** and hashed. One shot per candidate.
  No retuning after seeing results.
- A **blind integrity gate**: a fresh reviewer sees the frozen spec and the raw
  cell outputs but not the narrative, the expected result, or my recommendation.
- **Multiplicity is tracked project-wide** — currently Šidák-corrected at
  N = 467 Discovery trials, and a result must survive that correction.
- Confidence intervals use a **moving-block bootstrap** where observations
  overlap in time.
- Failed hypotheses are closed with a written failure-mode classification, never
  quietly abandoned.

## The results

**155 distinct hypotheses. 141 rejected. 2 survivors.**

Both survivors are **magnitude** facts, not direction:
1. High VXN (implied vol) relative to its own trailing level → wider next-session
   range. Holdout passed.
2. A quiet midday → an expanded afternoon range. Holdout passed.

A third, recently added and still early: a wide opening 30 minutes → a wider
midday. It passed its statistical stage cleanly, including the multiplicity
correction — but a placebo test showed *yesterday's* opening range predicts
today's midday almost as well, so it may just be reading a multi-day volatility
regime rather than anything about the opening.

**Zero directional survivors.** Not one, in 155 attempts.

## What I have already tried and killed

87 of the 141 rejected hypotheses were directional. This is roughly the entire
classical intraday playbook, and I would ask you not to suggest these:

| Family | Variants tested |
|---|---|
| Gap fades | gap fade, gap-down fade, overnight-down wide-open fade, overnight-high wide-open fade, swing-high wide-open fade, narrow-open fade — 9+ variants |
| Opening-range / initial-balance breakout | base + volatility-conditioned, stop-width-conditioned, high-vol-excluded variants |
| Level-sweep reversal (liquidity grabs) | 5+ variants incl. protected-liquidity filters, FVG entry, volatility-regime overlays |
| VWAP | mean reversion, distance-from-VWAP conditioned drift |
| Momentum / continuation | 15-min burst continuation, three-bar sequence, failed-breakout continuation, rejection wick, volume vacuum (both directions) |
| Trend following | weekly trend following, volatility-regime splits, multi-timeframe alignment (and its fade), 20MA pullback continuation |
| Cross-asset lead-lag | bonds (ZN) ×4, oil, currencies, cross-asset short-term reversal |
| Event drift | pre-FOMC, pre-NFP, CPI reversal, pooled CPI/NFP |
| Reference levels | opening-hour level fade, midmorning level fade, round-number continuation |
| Multi-day drift conditioned on a state | overnight-range-mid, location-in-range, VWAP-distance — all 10-day horizon |

**The most instructive failure.** One multi-day candidate (buy after price closes
far below its session VWAP, hold 10 days) passed Discovery, Validation *and*
Holdout. It looked like the program's first real edge. A late baseline diagnostic
then asked the obvious question nobody had asked: does it beat **NQ's own 10-day
drift over the same period**? It does not. The signal minus all-days is +0.12
with a block-bootstrap CI of (−0.26, +0.49) on Discovery, and +0.05 with
(−0.59, +0.66) on Validation. Neither clears zero. It made money in backtest
because the index rose over 10-day windows, not because the signal knew anything.
It was rejected. Every long-horizon directional result is now required to be
measured against the instrument's own drift.

## What I have to work with

- **1-minute OHLCV bars only** (Databento GLBX.MDP3), NQ 2015–present, ~3,600
  sessions. Also ES, RTY, ZN, CL, partial 6E. Daily VXN.
- **No order book, no tick data, no order flow, no options flow, no positioning
  data** beyond weekly COT.
- Data budget is about **$20/month**. Seven years of 1-minute history for one
  instrument costs roughly $5–15 as a one-off.
- One person plus automation. No colocation, no low-latency infrastructure.
  Execution would be retail through a standard futures broker.

## The questions

1. **Is "magnitude is predictable, direction is not" the correct conclusion from
   this evidence, or the signature of looking in the wrong feature space?** My
   features are all derived from OHLCV bars. My suspicion is that whatever
   genuine intraday directional information exists in a market this liquid lives
   in order flow and microstructure that 1-minute bars cannot see. Is that right,
   or is it a comfortable excuse?

2. **Is my process killing real effects?** Pre-registration, one-shot validation,
   a sealed holdout, Šidák correction at N=467, and block bootstraps on
   overlapping windows are collectively very conservative. A real but modest edge
   — say 0.05R per trade — might not survive this gauntlet even if it is
   genuinely there. How would I tell the difference between "no edge exists" and
   "my filter is too strict"? Is there a principled way to loosen without
   reopening the door to self-deception?

3. **If direction genuinely is not available to me, what is the honest business
   built on magnitude prediction alone?** Options structures (straddles,
   strangles) are the obvious answer and are direction-neutral by construction,
   but that is a different instrument, different skill set and different risk
   profile. Are there futures-only strategies where a reliable volatility
   forecast is the edge rather than an input? Or is the honest answer that a
   directional futures bot is simply the wrong goal for the data I have?

4. **What would you test next, specifically?** Given everything above is closed,
   what class of directional hypothesis would you spend the next 20 trials on,
   and what is the mechanism — who is on the other side and why do they keep
   being there?

5. **What am I not asking that I should be?**

## What would be most useful

Concrete and specific over encouraging. If the answer is "stop looking for
direction," say so plainly and explain what the evidence would have to look like
for that to be wrong. If it is "your features are the problem," name the feature
class. If it is "your statistics are too strict," show me where the bar is set
wrong and what a defensible looser bar would be.

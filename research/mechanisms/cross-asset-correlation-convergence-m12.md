# Mechanism — Cross-asset correlation convergence forces risk-parity delevering (M12)

Written: September 12th, 1:42 am CT (2026-09-12 06:42 UTC)  ·  Pre-registered
Results seen before writing: no — this doc precedes Scan 019, which has not been written or run.

## 1. The claim
Portfolio variance is a mechanical function of the correlation matrix:
for a book with weights w and volatilities sigma, variance is the sum of
w_i * w_j * sigma_i * sigma_j * rho_ij over all pairs. So when average
pairwise correlation across a multi-asset book RISES, the book's measured
volatility rises even if every single position and every single asset's
own volatility is unchanged. A vol-targeting or risk-parity mandate is
defined by holding measured portfolio volatility at a target, so that
manager MUST cut gross exposure — not because anyone formed a view, but
because the arithmetic of the mandate says the book is now too big.

Equities are the largest gross leg in essentially all of these books, so
NQ absorbs the largest single share of that forced selling. The
delevering is not instantaneous: these are large books executed over
sessions, not minutes. The claim is therefore that a sharp basket-wide
correlation rise is followed by negative NQ drift over the next 1-3 days.

Signed, not absolute, correlation is the correct measure here, and this
is a substantive choice rather than a convention: a strongly NEGATIVE
correlation between two legs also diversifies and LOWERS portfolio
variance. Using absolute correlation would treat a diversifying
relationship as if it were a risk-concentrating one and would measure
something the mechanism does not claim.

## 2. Who is on the other side
Counterparty: discretionary managers and liquidity providers who are
willing to absorb supply that carries no information. The forced seller
is selling because of a covenant in their own mandate, not because they
learned anything about Nasdaq earnings. Whoever takes the other side is
compensated by the price recovering once the mandate-driven supply
clears. If this effect is real, the counterparty's edge is patience.

## 3. Testable predictions
P1 (GATING, single pre-registered cell). In the HIGH tercile of the
five-day change in basket average correlation — the sharpest correlation
rises — mean NQ forward 3-day return, in ATR units, is credibly NEGATIVE
(90% bootstrap CI entirely below zero).

P2 (reported, not gating). The LOW tercile — correlations falling, which
mechanically permits RE-levering — should not show the same negative
drift, and under a symmetric reading of the mechanism should lean
positive. Horizons 1 and 2 days are reported for all three terciles to
show whether the effect has the gradual shape that a multi-session
execution would produce, rather than appearing only at one arbitrary
horizon.

## 4. What would falsify this
Any of the following closes the claim:
(a) The HIGH tercile 3-day mean is not credibly negative.
(b) The effect is credible but survives only because of the confound in
    Section 5 — i.e. it disappears once trailing NQ direction is
    controlled for. In that case what has been measured is the already-
    closed momentum/continuation family wearing a new label, and it does
    NOT count as a finding.
(c) The effect appears with no gradient across terciles and no shape
    across horizons — a single isolated credible cell among nine, with
    nothing monotonic around it, is what multiplicity noise looks like.

## 5. The confound, pre-registered and binding
Correlation spikes cluster inside selloffs. Everything falls together in
a risk-off move, so "average correlation just rose sharply" is partly
just "NQ has recently gone down." This project has already closed the
momentum/continuation family, so an uncontrolled negative-forward-return
result here would be indistinguishable from rediscovering it.

Two disclosures are therefore REQUIRED in the scan output, not optional
and not to be added after seeing the headline number:
1. Mean trailing 5-day NQ return, by tercile. This makes the size of the
   confound visible rather than assumed away.
2. The gating cell split by the SIGN of that trailing 5-day NQ return.
   If the negative forward drift lives only in the already-falling
   subset, the entry closes under falsifier (b).

The mechanism makes a specific prediction that separates it from
momentum: forced delevering should show up after correlation rises
whether or not NQ itself has already fallen, because the trigger is the
correlation matrix, not the equity drawdown. If the effect is present in
BOTH trailing-sign subsets, that is genuine support for this mechanism
over the momentum explanation.

## 6. Frozen scope (Scan 019)
- Daily log returns for NQ, ZN, 6E, CL from each instrument's reference
  close (study_volatility_regime.compute_daily_ref_closes and
  compute_daily_log_returns, both reused unmodified).
- avg_corr[t] = mean of the six pairwise Pearson correlations over the
  20 trading days ending at t (inclusive of t; this is information
  available at t's close).
- delta_corr[t] = avg_corr[t] - avg_corr[t-5], on the common trading-day
  calendar shared by all four instruments.
- Terciles of delta_corr computed ONCE on the full Discovery slice and
  never refit.
- Outcome: (NQ reference close at t+h minus NQ reference close at t)
  divided by ATR14 at t, where ATR14 is the trailing 14-day mean RTH
  range through t-1 (no lookahead), h in {1, 2, 3}.
- 9 cells measured (3 terciles x 3 horizons). GATING = HIGH tercile at
  h=3. Everything else is reported.
- scan_019_2026-09-12 (9 cells) registered in
  src/project_wide_multiplicity.py BEFORE the scan runs.
- ONE pre-registered shot. No retuning of window lengths, tercile
  definitions or horizons after seeing any result.

## 7. Prediction status
P1 (GATING) -- REFUTED. HIGH tercile, h=3: n=553, mean +0.1897 ATR,
ci_90 [+0.0804, +0.3020]. The claim was a credibly NEGATIVE mean. The
measured value is credibly POSITIVE -- not merely absent, but opposite in
sign to the prediction.
P2 (reported) -- the LOW tercile does lean positive as the symmetric
reading would suggest (h=3: +0.1988 ATR, ci_90 [+0.0921, +0.3032]), but
this is meaningless as support, because see Section 8: EVERY tercile is
positive by the same amount.

## 8. Verdict
REFUTED, and cleanly. n=1659 usable observations, 553 per tercile -- the
best-powered scope this Discovery Engine has run. Falsifier (a) fired.

The important result is not the sign, it is the ABSENCE OF ANY GRADIENT.
NQ forward 3-day return by tercile of the correlation-change state
variable:
    LOW  +0.1988 ATR   ci_90 [+0.0921, +0.3032]
    MID  +0.1815 ATR   ci_90 [+0.0703, +0.2901]
    HIGH +0.1897 ATR   ci_90 [+0.0804, +0.3020]
Three buckets, spread of 0.017 ATR between the highest and lowest, every
confidence interval sitting on top of the others. The state variable
carries no discriminating information whatsoever. Eight of the nine cells
read "credibly positive" and that is not nine-tenths of a finding -- it is
one fact (NQ drifted up over 2015-2021) showing through every bucket
equally because the conditioning variable does nothing.

So the mechanism is not merely unsupported; the specific observable it
predicted does not exist at a sample size where it would have been easy to
see. A 0.06-0.08 ATR effect was detectable here and the between-tercile
spread is 0.017 ATR. Risk-parity delevering may well be real as a market
event -- this says that if it is, it leaves no footprint in NQ daily
returns conditioned on basket correlation change, which is the only way
1-minute OHLCV can see it.

Attempt 1 of 2 on M12. A second attempt would need a genuinely different
forced-flow proxy, not a different window length or bucket count -- and
per the standing note in market_structure_map.md, the honest read is that
this axis is now also exhausted at the current data ceiling.

## 9. Disclosed post-hoc observation -- NOT a lead, NOT pursued
Confound check 2 split the (failed) gating cell by the sign of the
trailing 5-day NQ return and produced a large positive number in one
subset: HIGH tercile with trailing 5-day return NEGATIVE, n=198, mean
+0.5074 ATR, ci_90 [+0.3107, +0.7099]; the trailing-POSITIVE subset was
null (+0.0126, ci_90 [-0.1185, +0.1436]).

This is recorded because hiding it would be dishonest, and it is NOT being
pursued, for three reasons stated together so the reasoning is auditable:
(1) it is a post-hoc subset of a gating cell that already FAILED -- the
pre-registered claim was negative drift, and this is positive drift in a
subset, which is not "the hypothesis in different clothes," it is a
different hypothesis found by looking; (2) "NQ fell over the last week and
then bounced" is the mean-reversion/short-term-reversal family, which this
project has already tested and closed (hyp-000022 cross-asset short-term
reversal among others) -- the correlation tercile is doing little work
here beyond selecting volatile periods; (3) the trailing-5-day-negative
condition alone, with no correlation conditioning at all, is the obvious
control and has not been run, so the correlation variable's marginal
contribution is unknown and presumed near zero given Section 8.
If this is ever revisited it must enter as a NEW map-anchored entry with
its own mechanism doc and its own resurrection ruling against the closed
reversal family -- not as attempt 2 of M12, and not as a continuation of
this scan.

## 10. Methodological finding (LEARN) -- the baseline problem
The unconditional NQ forward 3-day return across the whole Discovery slice
is roughly +0.18 to +0.20 ATR. Sanity-checked against reality rather than
taken on faith: at NQ's Discovery-period levels that works out to roughly
15-16% annualized, against the Nasdaq-100's actual ~20% annualized total
return over 2015-2021. The magnitude is the real equity risk premium
showing through, not a normalization error.

That has a consequence beyond this entry. This project's promotion bar for
a directional claim is "90% CI entirely above zero." For a LONG-ONLY claim
on an asset with a strong secular uptrend, zero is the wrong null -- the
right comparison is against the UNCONDITIONAL drift over the same slice.
A long-only signal that produces +0.19 ATR over 3 days has found nothing;
it has rediscovered buy-and-hold and dressed it as a conditional edge.

Sign-adjusted, ratio-based and range-based results in this project are NOT
affected (overnight coil, range contraction, midday lull are all range or
sign-adjusted measures, where the baseline is 1.0 or symmetric). The
exposure is specifically to long-only directional drift claims. H118
(vwap_dist LOW tercile -> positive 10-day drift, long only) is the one
candidate on record in that shape. This does not overturn H118 -- it
passed on Validation and Holdout slices that include the 2022 drawdown,
which a pure bull-market artifact would likely have failed -- but the
correct test for it was always "LOW tercile drift vs. all-days drift,"
not "vs. zero," and that comparison has never been run.
RECOMMENDED, not yet done, flagged for Jason: (a) adopt baseline-relative
testing as the convention for any future long-only directional claim, and
(b) run the all-days-baseline comparison for H118 as a diagnostic. Neither
touches H118's frozen forward-validation spec, and (b) is a new
calculation on already-used Discovery/Validation data, not a new attempt.

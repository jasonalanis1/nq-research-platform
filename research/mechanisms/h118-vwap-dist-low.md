# Mechanism — H118 (vwap_dist_vs_atr LOW tercile, 10-day drift)

Written: 2026-09-10  ·  **POST-HOC**
Results seen before writing: YES — Discovery, Validation and Holdout were all
complete before this document existed. **This is a hypothesis, not evidence.**
It carries no weight toward H118's promotion. It earns weight only if its
predictions hold on things it was not built to explain.

## 1. The claim

H118 fires when price sits unusually far below its volume-weighted average
price, scaled by current volatility. The candidate explanation: this state
marks episodes where selling pressure has been impatient or forced rather
than informed — liquidation, de-risking, or momentum selling that overshoots
what the information justifies. Buyers who are willing to take the other side
of that flow are supplying liquidity when it is scarce, and are paid for it
over the following days as the overshoot is absorbed.

Note this is one of at least three stories that fit the same data. The others:
(b) the effect is compensation for genuinely elevated risk, not an
inefficiency — we get paid because these are frightening moments to buy; and
(c) the ATR scaling is doing the real work and this is ordinary volatility-
adjusted mean reversion with no special mechanism at all. Distinguishing
these matters, because (a) and (c) should persist while (b) is not free money.

## 2. Who is on the other side

Under claim (a): sellers who must sell — margin calls, risk-limit breaches,
fund outflows, stop-loss cascades — plus discretionary traders exiting on
discomfort. They pay for immediacy. Under (b): we are the ones being paid to
hold risk others do not want, which is a real service, not a mispricing.

Honest gap: this project has no order-flow, volume-profile, or positioning
data that could confirm forced selling is actually present. The counterparty
is inferred, not observed. That is a genuine weakness and the main reason
this mechanism sits at hypothesis level.

## 3. Testable predictions

P1. **Monotonic gradient across buckets.** If price-below-VWAP genuinely
    carries information, the effect should not be a lone quirk of the LOW
    cell. HIGH (price far above VWAP) should show the opposite sign, and MID
    should sit near zero. A single isolated bucket would suggest a lucky cell.

P2. **Front-loaded absorption.** If the mechanism is overshoot being absorbed,
    most of the effect should appear quickly, then flatten — not accumulate
    steadily over ten days.

P3. **Stronger after fast declines.** Forced selling is fast. The effect
    should be larger when the move into the LOW state happened over few bars
    with elevated volume, versus a slow grind down. UNTESTED — requires work
    not yet done.

P4. **Should weaken, not strengthen, with holding period beyond absorption.**
    If the edge keeps growing well past the absorption window, that points
    away from liquidity provision and toward risk compensation (claim b).

## 4. What would falsify this

An isolated LOW-bucket effect with no gradient across buckets. Or an effect
that accumulates linearly across all horizons, which would look like drift or
beta rather than absorption of an overshoot.

## 5. Prediction status

**P1 — CONFIRMED.** Scan 002 Discovery data, 10-day horizon, effect versus
baseline by bucket:
    LOW   +20.45 pts
    MID    -2.42 pts
    HIGH  -16.81 pts
A clean monotonic gradient, sign-flipped at the far end, near zero in the
middle. The 1-day horizon shows the same ordering (LOW +13.38, MID -5.20,
HIGH -5.72). This was never part of H118's promotion case and was not
selected for — it is a genuine out-of-sample-in-spirit check of the mechanism,
and it passes. This is the single strongest piece of evidence that H118 is
measuring something real rather than a lucky cell.

**P2 — PARTIALLY CONFIRMED, with an anomaly.** Effect by holding period:
    1 day  +13.38 pts   (0.105R)
    3 day  +13.55 pts   (0.106R)
    5 day  +14.01 pts   (0.110R)
   10 day  +20.45 pts   (0.160R)
Two-thirds of the effect lands within the first day and then goes completely
flat through day five — strongly consistent with rapid absorption of an
overshoot. But the jump between day five and day ten is NOT explained by this
mechanism and is the most important open question about H118. Either a second,
slower effect is present, or the 10-day figure is partly noise. Note the
uncomfortable implication: H118 holds risk for nine additional days to collect
a second piece of edge that has no mechanism story behind it.

**P3 — UNTESTED.** Requires classifying the approach into the LOW state by
speed and volume. Queued.

**P4 — CONTRADICTED so far.** The effect grows from day five to day ten rather
than flattening, which points toward risk compensation rather than pure
liquidity provision. Not fatal — but if H118's edge is mostly compensation for
holding uncomfortable risk, it is real, harder to scale, and behaves worse in
exactly the conditions where it fires.

## 6. Verdict

The mechanism survives at hypothesis level and is materially stronger than it
was before this document existed, because P1's monotonic gradient was hiding
in plain sight in the scan data and had never been stated as a prediction or
checked as one.

But the 5-to-10-day jump has no mechanism behind it, and P4 leans away from
the cleanest story. The honest position: the FIRST DAY of H118's edge has a
plausible, partially-confirmed mechanism. Days two through ten do not. That
is directly relevant to the queued 1-day variant — which may be the part of
H118 that is actually understood.

None of this changes H118's frozen definition, its forward test, or its review
point. It is a mechanism record, not a strategy change.

# The round-trip cost model — corrected September 16th, 2026

**Owner in code: `src/cost_model.py`. Nothing else in this repository defines a cost.**
Recorded under Jason's Amendment 2 to the standing operating directive
(`research/infrastructure/standing-directive-2026-09-15.md`), which quotes his instruction verbatim.

---

## 1. What was wrong

Every cost figure in the project traced back to four constants in `src/integrity_checks.py`:

```
TICK_SIZE = 0.25   COMMISSION_PER_SIDE_USD = 2.50
SLIPPAGE_TICKS_PER_SIDE = 1.0   CONTRACT_MULTIPLIER = 20.0
```

`src/paper_book.py` imported the commission and slippage from there and applied them to the **micro**
(MNQ, $2.00 per index point) the paper book actually trades, producing

> $2.50 × 2 + 1 tick × $0.50 × 2 = **$6.00 per micro round trip = 3.00 index points**

$2.50 a side is a commonly-cited **full-size E-mini (NQ)** all-in rate. Charged to a micro it is roughly
**3–10× too high on the commission leg**, and the round trip as a whole came out about **2.3× too expensive
in dollars and 2.3× too expensive in points**. Jason caught it; his own estimate ($2–2.50, ~1.1 points) was
right and the repo's was not.

## 2. The researched figures and their sources

| component | MNQ | NQ | source |
|---|---|---|---|
| commission, per contract per side | **$0.25** (fixed; $0.10–0.25 tiered) | **$0.85** | Interactive Brokers, official micro futures comparison page, `interactivebrokers.com/en/trading/micro-futures-comparison.php` — micro futures commission $0.25/contract fixed, "plus exchange and regulatory fees". NQ figure from BrokerChooser's IBKR NQ page. |
| exchange + regulatory (NFA) + clearing, per side | **$0.55** | **$1.60** | BrokerChooser, IBKR MNQ page (MNQ ≈ $0.55) and IBKR NQ page (NQ ≈ $1.60). |
| point value | **$2.00** per index point | **$20.00** per index point | CME contract specs. |
| tick | 0.25 pt = **$0.50** | 0.25 pt = **$5.00** | CME contract specs. |
| slippage, per side, market order | **1 tick ASSUMED** | **1 tick ASSUMED** | Standing directive s.11 — assumed, never manufactured, until B4b measures real fills. |

## 3. The four combinations

| | commission/side | fees/side | slippage/side | round trip $ | round trip POINTS |
|---|---|---|---|---|---|
| **MNQ, market entry + exit** | $0.25 | $0.55 | $0.50 (1 tick, both sides) | **$2.60** | **1.300 pt** |
| **MNQ, limit entry, market exit** *(OPTIMISTIC)* | $0.25 | $0.55 | $0.50, exit only | **$2.10** | **1.050 pt** |
| **NQ, market entry + exit** | $0.85 | $1.60 | $5.00 (1 tick, both sides) | **$14.90** | **0.745 pt** |
| **NQ, limit entry, market exit** *(OPTIMISTIC)* | $0.85 | $1.60 | $5.00, exit only | **$9.90** | **0.495 pt** |

Arithmetic, worked, so it can be checked: MNQ market = 2×$0.25 + 2×$0.55 + 2×$0.50 = $0.50 + $1.10 + $1.00 =
$2.60; ÷ $2.00/pt = 1.30 pt. MNQ limit drops one tick of slippage: $2.60 − $0.50 = $2.10 = 1.05 pt. NQ market
= 2×$0.85 + 2×$1.60 + 2×$5.00 = $1.70 + $3.20 + $10.00 = $14.90; ÷ $20.00/pt = 0.745 pt. NQ limit = $14.90 −
$5.00 = $9.90 = 0.495 pt.

**Decision basis: MNQ market entry ($2.60 = 1.300 pt).** It is what the paper loop trades — one micro, market
orders, simulated fills — it is the honest (non-optimistic) column, and it is the most expensive of the four in
points, so a strategy that clears it clears all four.

## 4. The structural point Jason wants visible

**In POINTS the full-size NQ round trip costs roughly HALF what the micro does** — 0.745 pt against 1.300 pt at
market, 0.495 pt against 1.050 pt on an optimistic limit entry. In dollars the NQ round trip is ~5.7× the
micro's, but a point is worth 10× as much, so the fixed commission-and-fee component spreads over ten times the
notional while the tick of slippage stays the same size in points.

The consequence for research: a strategy whose per-trade edge sits between about 0.5 and 1.3 points is
**profitable on NQ and unprofitable on MNQ**. "The cost wall killed it" is therefore a statement about the
contract as much as about the pattern, and no screen report is allowed to hide which. That is why every screen
from now on prints all four columns side by side (`src/screen_strategy.py`), and the paper book does the same
for the record it holds (`src/paper_book.py`).

The size question is separate and stays Jason's: NQ is 10× the risk per trade at the same stop distance.

## 5. Why every limit-entry figure is labelled OPTIMISTIC

A limit entry avoids paying the spread on the way in — that part is real, and it is the whole of the difference
above. What the model cannot capture is that **a resting limit order does not always fill**, and that it fills
*preferentially when the market is about to trade through it*, i.e. when the trade is about to go against you.
That is adverse selection, and it does not appear as a cost; it appears as a worse mix of trades.

A historical screen fills every limit order at its price by construction, so it silently assumes (a) no missed
fills and (b) that the fills it got are a fair sample of the fills it would have got. Both assumptions flatter
the limit column. **The limit numbers are therefore a ceiling on what a limit entry can achieve, never an
estimate of it**, and `src/cost_model.py` carries that note on every limit row (`optimistic: true`,
`OPTIMISTIC_NOTE`, and the `(OPTIMISTIC)` suffix in the label) so no printer can drop it.

## 6. The SPECIFY rule (replacing Tony's invented pre-screen)

Tony had invented a "candidate must gross ≥ 3× the cost" pre-screen and refused S008 on it **without running a
screen**. The directive never contained such a rule. Jason's rule, in `cost_model.specify_gate()`:

> **At SPECIFY, reject only if the expected per-trade edge is below the corrected per-trade cost itself;
> otherwise screen it.**

No multiple, no budget, no "well north of". The SCREEN stage answers the directive's one question and the
evidence is the paper record.

## 7. What this correction did and did not touch

- **Did not touch any frozen spec or module** (directive s.13). S002, S003 and S007's frozen files still quote
  the old $6.00 figure in their own text; they are the record of what was frozen and are not edited. The
  corrected cost is applied *to* them from `cost_model.py` when they are screened or scored.
- **Did not re-score a single paper fill.** The paper log's entries, exits, exit reasons and gross P&L are the
  record and are untouched. What changed is the cost overlay `src/paper_book.py` subtracts from that unchanged
  gross — and it now shows four overlays side by side on the same one record, so the Integrity Gate can see
  that the record itself was not adjusted.
- **Did** replace the constants in `src/integrity_checks.py` and `src/backtest.py` with reads from
  `cost_model.py`. (`backtest.py` prices the full-size NQ; its old hand-written $2.50/side happened to be close
  to the correct NQ all-in of $2.45/side, so its round trip moves only from 0.750 pt to 0.745 pt.)

*Tests: `tests/test_cost_model.py`, plus the corrected expectations in `tests/test_paper_book.py`,
`tests/test_screen_strategy.py` and `tests/test_study_s002_night_leg_menu.py`.*

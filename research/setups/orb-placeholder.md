# Opening Range Breakout (placeholder)

**Status: PLACEHOLDER.** This is not Jason's actual setup — it's a
standard, well-documented pattern used as a default so the pipeline had
something concrete to detect, backtest, and score while Jason's real
setup was still undecided. Replace or heavily edit this file once his
actual setup is defined.

## Definition (as currently coded in `src/detect_setups.py`)

1. **Range:** the high and low of price during the first 15 minutes
   after the 8:30 AM NY open (8:30-8:45).
2. **Signal:** the first bar, within the following 60 minutes
   (8:45-9:45), whose close breaks above the range high (long) or below
   the range low (short).
3. **Stop:** the opposite side of the range.
4. **Target:** entry price plus (long) or minus (short) one range-width.

## Known limitations of this definition

- Parameters (15 / 60 / 1x) are arbitrary reasonable defaults, not tuned
  or validated against anything.
- Doesn't account for volume, prior day's range, news events, or any
  other context — pure price-range logic only.
- Target/stop are symmetric-ish by construction; real setups often have
  asymmetric risk/reward on purpose.

## History

- 2026-08-15: created as the Stage 2 placeholder, first (and so far only)
  tested in `../experiments/exp-001-orb-synthetic-baseline.md`.

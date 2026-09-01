"""
detect_ib_breakout.py
=======================

Implements the "Initial Balance Breakout (Continuation)" setup frozen in
`research/setups/initial-balance-breakout.md`. First CONTINUATION-thesis
setup in this project -- every prior setup (Level Sweep Reversal's three
variants, the FVG entry trigger, the trend-structure liquidity filter)
tested a REVERSAL thesis (a level sweeps, price reverses) and all six
failed to clear the promotion bar. This tests the opposite bet: a range
breaks, price continues.

WHICH SETUP THIS IMPLEMENTS:

    1. The Initial Balance (IB): the high/low of price during the first
       IB_MINUTES (30) after the 8:30 AM NY open (8:30-9:00).
    2. From the end of the IB window through BREAKOUT_END_HOUR (12:00
       PM), watch for the first 1-minute bar whose CLOSE breaks beyond
       either side of the IB range.
    3. The first breakout in either direction is the signal -- no
       flip-flopping if the other side also breaks later.
    4. Entry: the close of the breakout bar.
       Stop: the opposite side of the IB range.
       Target: entry +/- TARGET_R_MULTIPLE * risk (the same 1.35 constant
       every other setup in this project uses, imported from
       detect_level_sweep.py rather than redefined, so it can never
       silently drift out of sync).
    5. A zero-width IB range (IB high == IB low) produces no trade for
       that day -- degenerate case, not a real signal. Same reasoning as
       the zero-risk-signal fix made to detect_fvg_entry.py for exp-025.

Related to, but NOT a retest of, the existing "ORB placeholder"
(detect_setups.py) -- see research/setups/initial-balance-breakout.md's
"Relationship to the existing ORB placeholder" section for the full
comparison (different window length, different breakout window, tested
under the current Discovery-slice protocol for the first time, standard
1.35R target instead of the placeholder's ad hoc range-width target).

NO LOOK-AHEAD: the IB range is fully known and frozen the moment the
9:00 AM window closes; the breakout scan only ever looks forward from
that point using data that has already occurred. No confirmation-lag
mechanism is needed (unlike trend_structure.py's swing points).

HOW TO RUN:
    python3 src/detect_ib_breakout.py
"""

import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from detect_level_sweep import TARGET_R_MULTIPLE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# ---------------------------------------------------------------------------
# SETTINGS -- see research/setups/initial-balance-breakout.md for the
# reasoning behind each of these.
# ---------------------------------------------------------------------------
OPEN_HOUR, OPEN_MINUTE = 8, 30          # the 8:30 AM NY open
IB_MINUTES = 30                          # Initial Balance window length (8:30-9:00)
BREAKOUT_END_HOUR, BREAKOUT_END_MINUTE = 12, 0   # watch for a breakout through noon ET


def detect_ib_breakout_for_day(day_df: pd.DataFrame, day) -> dict | None:
    """
    Looks at one day's worth of bars and returns a signal dict if a clean
    Initial Balance breakout happened, or None if the day didn't produce
    one (no breakout by noon, a degenerate zero-width IB range, or not
    enough data to define the IB window at all).
    """
    tz = day_df.index.tz
    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    ib_end_ts = open_ts + pd.Timedelta(minutes=IB_MINUTES)
    breakout_end_ts = pd.Timestamp(day, tz=tz).replace(hour=BREAKOUT_END_HOUR, minute=BREAKOUT_END_MINUTE)

    ib_bars = day_df[(day_df.index >= open_ts) & (day_df.index < ib_end_ts)]
    if ib_bars.empty:
        return None  # not enough data to define an IB range for this day

    ib_high = ib_bars["High"].max()
    ib_low = ib_bars["Low"].min()
    ib_range = ib_high - ib_low

    if ib_range <= 0:
        return None  # degenerate/zero-width IB range -- not a real signal, see module docstring

    # Volume context (added 2026-09-01 for research/setups/volume-confirmed-
    # ib-breakout.md) -- NOT used by the detection/entry logic above, which
    # is completely unchanged. ib_avg_volume is this day's own IB-window
    # average, so any later "was the breakout bar's volume unusual"
    # comparison is self-normalizing against that same day (avoids both the
    # multi-year drift in NQ's overall traded volume and any lookahead --
    # the IB window is fully known before the breakout window even starts).
    ib_avg_volume = ib_bars["Volume"].mean()

    watch_bars = day_df[(day_df.index >= ib_end_ts) & (day_df.index < breakout_end_ts)]

    for ts, bar in watch_bars.iterrows():
        if bar["Close"] > ib_high:
            entry = bar["Close"]
            stop = ib_low
            risk = entry - stop
            return {
                "date": day,
                "direction": "long",
                "ib_high": round(ib_high, 2),
                "ib_low": round(ib_low, 2),
                "breakout_time": ts,
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target": round(entry + TARGET_R_MULTIPLE * risk, 2),
                "ib_avg_volume": round(float(ib_avg_volume), 2),
                "breakout_volume": float(bar["Volume"]),
            }
        if bar["Close"] < ib_low:
            entry = bar["Close"]
            stop = ib_high
            risk = stop - entry
            return {
                "date": day,
                "direction": "short",
                "ib_high": round(ib_high, 2),
                "ib_low": round(ib_low, 2),
                "breakout_time": ts,
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target": round(entry - TARGET_R_MULTIPLE * risk, 2),
                "ib_avg_volume": round(float(ib_avg_volume), 2),
                "breakout_volume": float(bar["Volume"]),
            }

    return None  # price stayed inside the IB range through noon -- no signal today


def scan_all_days(df: pd.DataFrame) -> tuple[list[dict], dict]:
    """Walks every day in df and returns (raw signal dicts, stats). Same
    shape/convention as every other detector's scan_all_days()."""
    all_days = sorted(set(df.index.date))
    signals = []
    no_signal_days = 0
    degenerate_or_missing_ib_days = 0

    for day in all_days:
        day_df = df[df.index.date == day]
        signal = detect_ib_breakout_for_day(day_df, day)
        if signal is not None:
            signals.append(signal)
        else:
            tz = day_df.index.tz if len(day_df) else None
            if tz is not None:
                open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
                ib_end_ts = open_ts + pd.Timedelta(minutes=IB_MINUTES)
                ib_bars = day_df[(day_df.index >= open_ts) & (day_df.index < ib_end_ts)]
                if ib_bars.empty or (ib_bars["High"].max() - ib_bars["Low"].min()) <= 0:
                    degenerate_or_missing_ib_days += 1
                    continue
            no_signal_days += 1

    stats = {
        "total_days": len(all_days),
        "no_signal_days": no_signal_days,
        "degenerate_or_missing_ib_days": degenerate_or_missing_ib_days,
    }
    return signals, stats


STRATEGY_NAME = "initial_balance_breakout"
STRATEGY_VERSION = "1.0"


def generate_signals(df: pd.DataFrame, validation_status: str = "research") -> list:
    """Signal-contract adapter (docs/AUTOMATION_ARCHITECTURE.md's approved
    Signal schema) around the unchanged scan_all_days() logic above,
    same pattern as every other detector in this project."""
    from strategy_contract import Signal, risk_multiple as _risk_multiple

    raw_signals, _stats = scan_all_days(df)
    out = []
    for s in raw_signals:
        out.append(Signal(
            strategy_name=STRATEGY_NAME,
            strategy_version=STRATEGY_VERSION,
            timestamp=s["breakout_time"],
            instrument="NQ",
            timeframe="1m",
            direction=s["direction"],
            entry=s["entry"],
            stop=s["stop"],
            target=s["target"],
            risk_multiple=_risk_multiple(s["entry"], s["stop"], s["target"]),
            validation_status=validation_status,
            market_context={
                "ib_high": s["ib_high"], "ib_low": s["ib_low"], "date": str(s["date"]),
                "ib_avg_volume": s["ib_avg_volume"], "breakout_volume": s["breakout_volume"],
            },
        ))
    return out


def main():
    df, is_synthetic = load_price_data(context="detect_ib_breakout.py")
    if is_synthetic:
        print("NOTE: using SYNTHETIC data -- signal counts below are for testing the pipeline only.")

    signals, stats = scan_all_days(df)

    signals_df = pd.DataFrame(signals)
    out_path = DATA_DIR / "setups_ib_breakout.csv"
    signals_df.to_csv(out_path, index=False)

    print(f"\nScanned {stats['total_days']} days.")
    print(f"  Signals found: {len(signals_df)}")
    if not signals_df.empty:
        print(f"    Long:  {(signals_df['direction'] == 'long').sum()}")
        print(f"    Short: {(signals_df['direction'] == 'short').sum()}")
    print(f"  Days with no breakout by noon: {stats['no_signal_days']}")
    print(f"  Days with a degenerate/missing IB range: {stats['degenerate_or_missing_ib_days']}")
    print(f"\nSaved signal log to: {out_path}")
    if not signals_df.empty:
        print("\nFirst few signals:")
        print(signals_df.head())


if __name__ == "__main__":
    main()

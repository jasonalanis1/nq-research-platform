"""
detect_fvg_entry.py
=====================

Implements the "Fair Value Gap (FVG) Entry Trigger" variant frozen in
`research/setups/fvg-entry-trigger.md` -- same base setup as Level Sweep
Reversal (level selection + sweep/rejection confirmation), but with a
different entry trigger layered on top once rejection is confirmed.

NOTHING FROM detect_level_sweep.py IS REIMPLEMENTED HERE. This file
imports and reuses, unchanged:
  - compute_levels()          -- SUPPORT/RESISTANCE level selection
  - scan_for_signal()          -- the sweep + rejection-confirmation walk,
                                   for whichever CONFIRMATION_MODE is
                                   requested (close_any / close_min_distance
                                   / full_bar_range)
  - CONFIRMATION_MODES, WATCH_MINUTES, TARGET_R_MULTIPLE

scan_for_signal()'s existing output already gives us everything the base
setup is supposed to provide: direction, the rejection-confirming
candle's timestamp (signal_time), and stop (the sweep extreme). This
file only adds what fvg-entry-trigger.md actually changes: what counts
as the ENTRY once rejection has fired, replacing "close back beyond the
level" with a 3-candle Fair Value Gap.

ONE THING THE FROZEN DOC DOES NOT SPECIFY, RESOLVED HERE (flag this
before trusting any backtest of this variant): fvg-entry-trigger.md says
to reuse "the existing sweep/rejection logic" but doesn't say which of
the three CONFIRMATION_MODES marks "rejection confirmed" for the purpose
of starting the FVG search. This file exposes confirmation_mode as a
parameter/CLI argument, same as detect_level_sweep.py, defaulting to
"close_any" to match that file's own default -- NOT a decision Jason
made explicitly for this variant. Worth resolving deliberately (probably
by testing more than one, the same way the three confirmation modes
themselves were compared instead of guessed) before results from this
file are trusted.

BAR-ADJACENCY NOTE (also not explicit in the frozen doc): "3 consecutive
candles" here means 3 consecutive ROWS in the day's 1-minute bar data,
not necessarily 3 minutes with zero gaps in wall-clock time (this
project's minute bars can have small gaps during illiquid stretches).
This matches how FVGs are read on a chart (the next three candles that
actually printed), not a strict wall-clock definition.

STATUS AS OF 2026-08-24: detection logic only, written directly from
fvg-entry-trigger.md's frozen definition. NOT yet run against any real
or synthetic data -- no backtest, no experiment logged. Per
docs/RESEARCH_INTEGRITY_PROTOCOL.md, any future test of this variant
goes through the Discovery slice first, same as everything else.
"""

import sys
import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from detect_level_sweep import (
    compute_levels,
    scan_for_signal,
    CONFIRMATION_MODES,
    TARGET_R_MULTIPLE,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Bars in this project's data are indexed by each candle's OPEN
# timestamp (1-minute OHLCV bars) -- so a candle's CLOSE time is its
# index timestamp + one bar. Needed because fvg-entry-trigger.md defines
# the window relative to the rejection-confirming candle's CLOSE time,
# not its open/index time.
BAR_DURATION = pd.Timedelta(minutes=1)

FVG_WINDOW_MINUTES = 30  # per fvg-entry-trigger.md -- an arbitrary illustrative choice, not derived from the source video


def find_fvg_after_rejection(day_df: pd.DataFrame, rejection: dict) -> dict | None:
    """
    Given a day's bars and the rejection signal scan_for_signal() already
    found (unchanged sweep/rejection logic), looks for the first
    qualifying 3-candle Fair Value Gap per fvg-entry-trigger.md's timing
    rule:

      - candle 1 can never be the rejection-confirming candle itself --
        it must be the first candle whose OPEN time is at or after the
        rejection-confirming candle's CLOSE time.
      - candle 1's open time must fall in the half-open window
        [window_start, window_start + FVG_WINDOW_MINUTES), where
        window_start = the rejection-confirming candle's close time.
      - once a qualifying candle 1 begins inside that window, candles 2
        and 3 are free to complete the pattern even past the window --
        the window only gates the START of the sequence.
      - the FIRST qualifying sequence wins; later ones in the same day
        are ignored.

    Returns None if no qualifying FVG is found before the day's bars run
    out (this is a legitimate outcome -- fvg-entry-trigger.md says a
    rejection with no FVG in time is simply a no-trade day, not a
    fallback to any other entry rule).
    """
    direction = rejection["direction"]
    window_start = rejection["signal_time"] + BAR_DURATION
    window_end_exclusive = window_start + pd.Timedelta(minutes=FVG_WINDOW_MINUTES)

    candidates = day_df[day_df.index >= window_start]
    n = len(candidates)

    for i in range(n - 2):
        candle1_ts = candidates.index[i]
        if candle1_ts >= window_end_exclusive:
            break  # candidates are time-ordered -- no later candle1 can qualify either

        candle1 = candidates.iloc[i]
        candle3 = candidates.iloc[i + 2]

        if direction == "long":
            is_gap = candle1["High"] < candle3["Low"]
        else:  # short
            is_gap = candle1["Low"] > candle3["High"]

        if is_gap:
            candle3_ts = candidates.index[i + 2]
            return {
                "fvg_candle1_time": candle1_ts,
                "fvg_candle3_time": candle3_ts,
                "entry_bar_close": candle3["Close"],
            }

    return None


def scan_day_for_fvg_entry(df: pd.DataFrame, day, prior_day, confirmation_mode: str) -> dict | None:
    """
    One day's full pipeline for this variant: unchanged level selection,
    unchanged sweep/rejection confirmation (via scan_for_signal), then
    this file's FVG-based entry search on top. Returns None if levels
    can't be computed, no rejection ever confirms, or no FVG forms in
    time -- all three are legitimate no-trade outcomes, not errors.
    """
    levels = compute_levels(df, day, prior_day)
    if levels is None:
        return None

    day_df = df[df.index.date == day]
    rejection = scan_for_signal(day_df, levels, confirmation_mode)
    if rejection is None:
        return None

    fvg = find_fvg_after_rejection(day_df, rejection)
    if fvg is None:
        return None

    entry = fvg["entry_bar_close"]
    stop = rejection["stop"]  # unchanged: the sweep extreme, reused as-is
    if rejection["direction"] == "long":
        risk = entry - stop
        target = entry + TARGET_R_MULTIPLE * risk
    else:
        risk = stop - entry
        target = entry - TARGET_R_MULTIPLE * risk

    return {
        "date": day,
        "direction": rejection["direction"],
        "level_source": rejection["level_source"],
        "level_swept": rejection["level_swept"],
        "sweep_extreme": rejection["sweep_extreme"],
        "rejection_time": rejection["signal_time"],
        "fvg_candle1_time": fvg["fvg_candle1_time"],
        "signal_time": fvg["fvg_candle3_time"],  # entry moment, matching the signal_time column name other detectors use
        "entry": entry,
        "stop": stop,
        "target": target,
    }


def scan_all_days(df: pd.DataFrame, confirmation_mode: str = "close_any") -> tuple[list[dict], dict]:
    """
    Same day-iteration shape as detect_level_sweep.py's scan_all_days(),
    so this file plugs into the rest of the pipeline the same way --
    but with three no-trade outcomes tracked separately (skipped for
    missing levels, no rejection at all, rejection but no FVG in time)
    instead of two, since this variant has an extra way for a day to
    produce no trade.
    """
    all_days = sorted(set(df.index.date))
    signals = []
    skipped_no_levels = 0
    no_rejection_days = 0
    no_fvg_days = 0

    for i, day in enumerate(all_days):
        if i == 0:
            continue  # first day in the dataset has no "prior day"
        prior_day = all_days[i - 1]

        levels = compute_levels(df, day, prior_day)
        if levels is None:
            skipped_no_levels += 1
            continue

        day_df = df[df.index.date == day]
        rejection = scan_for_signal(day_df, levels, confirmation_mode)
        if rejection is None:
            no_rejection_days += 1
            continue

        fvg = find_fvg_after_rejection(day_df, rejection)
        if fvg is None:
            no_fvg_days += 1
            continue

        entry = fvg["entry_bar_close"]
        stop = rejection["stop"]
        if rejection["direction"] == "long":
            risk = entry - stop
            target = entry + TARGET_R_MULTIPLE * risk
        else:
            risk = stop - entry
            target = entry - TARGET_R_MULTIPLE * risk

        signals.append({
            "date": day,
            "direction": rejection["direction"],
            "level_source": rejection["level_source"],
            "level_swept": rejection["level_swept"],
            "sweep_extreme": rejection["sweep_extreme"],
            "rejection_time": rejection["signal_time"],
            "fvg_candle1_time": fvg["fvg_candle1_time"],
            "signal_time": fvg["fvg_candle3_time"],
            "entry": entry,
            "stop": stop,
            "target": target,
        })

    stats = {
        "total_days": len(all_days) - 1,
        "skipped_no_levels": skipped_no_levels,
        "no_rejection_days": no_rejection_days,
        "no_fvg_days": no_fvg_days,
    }
    return signals, stats


STRATEGY_NAME = "level_sweep_reversal_fvg_entry"
STRATEGY_VERSION = "1.0"


def generate_signals(df: pd.DataFrame, confirmation_mode: str = "close_any",
                      validation_status: str = "research") -> list:
    """
    Signal-contract adapter (docs/AUTOMATION_ARCHITECTURE.md's approved
    Signal schema), matching the pattern detect_level_sweep.py and
    detect_setups.py already use -- built on top of this file's own
    unchanged scan_all_days(), not a separate implementation.
    """
    from strategy_contract import Signal, risk_multiple as _risk_multiple

    raw_signals, _stats = scan_all_days(df, confirmation_mode)
    out = []
    for s in raw_signals:
        out.append(Signal(
            strategy_name=STRATEGY_NAME,
            strategy_version=f"{STRATEGY_VERSION}-{confirmation_mode}",
            timestamp=s["signal_time"],
            instrument="NQ",
            timeframe="1m",
            direction=s["direction"],
            entry=s["entry"],
            stop=s["stop"],
            target=s["target"],
            risk_multiple=_risk_multiple(s["entry"], s["stop"], s["target"]),
            validation_status=validation_status,
            market_context={
                "level_source": s["level_source"],
                "date": str(s["date"]),
                "rejection_time": str(s["rejection_time"]),
                "fvg_candle1_time": str(s["fvg_candle1_time"]),
            },
        ))
    return out


def main():
    confirmation_mode = sys.argv[1] if len(sys.argv) > 1 else "close_any"
    if confirmation_mode not in CONFIRMATION_MODES:
        print(f"Unknown confirmation mode '{confirmation_mode}'. Choose one of: {CONFIRMATION_MODES}")
        return

    df, is_synthetic = load_price_data(context="detect_fvg_entry.py")
    if is_synthetic:
        print("NOTE: using SYNTHETIC data -- signal counts below are for testing the pipeline only.")
    print(f"Confirmation mode (base rejection rule): {confirmation_mode}")

    signals, stats = scan_all_days(df, confirmation_mode)

    signals_df = pd.DataFrame(signals)
    if not signals_df.empty:
        signals_df = signals_df[["date", "direction", "level_source", "level_swept", "sweep_extreme",
                                  "rejection_time", "fvg_candle1_time", "signal_time", "entry", "stop", "target"]]
        for col in ["level_swept", "sweep_extreme", "entry", "stop", "target"]:
            signals_df[col] = signals_df[col].round(2)

    out_path = DATA_DIR / f"setups_fvg_entry_{confirmation_mode}.csv"
    signals_df.to_csv(out_path, index=False)

    print(f"\nScanned {stats['total_days']} days (excluding the first, which has no prior day).")
    print(f"  Signals found: {len(signals_df)}")
    if not signals_df.empty:
        print(f"    Long:  {(signals_df['direction'] == 'long').sum()}")
        print(f"    Short: {(signals_df['direction'] == 'short').sum()}")
    print(f"  Days skipped (missing prior-day or pre-market data): {stats['skipped_no_levels']}")
    print(f"  Days with no sweep+rejection in the watch window: {stats['no_rejection_days']}")
    print(f"  Days with rejection but no FVG within {FVG_WINDOW_MINUTES} min: {stats['no_fvg_days']}")
    print(f"\nSaved signal log to: {out_path}")
    if not signals_df.empty:
        print("\nFirst few signals:")
        print(signals_df.head())


if __name__ == "__main__":
    main()

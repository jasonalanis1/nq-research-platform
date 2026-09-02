"""
detect_fade_the_gap.py
=========================

Implements the "Fade the Gap" setup frozen in
`research/setups/fade-the-gap.md`. Directly triggered by
`research/studies/overnight-gap-behavior.md`'s own Step 3 rule
(exp-032): that characterization study found a gap-fill rate
significantly above 50% in both directions and a significant negative
correlation between gap size and the +90-minute forward return, both
pointing the same way -- gaps tend to partially close, not extend. This
setup is the most direct mechanical translation of that finding: bet on
the gap closing, at the open.

WHICH SETUP THIS IMPLEMENTS:

    1. `prior_close`: the last available bar's Close at or before 4:00
       PM ET the prior day (reuses study_overnight_gap.py's own
       get_reference_close(), not reimplemented).
    2. `today_open`: the Open of the first bar at or after 8:30 AM ET
       (reuses detect_ib_breakout.py's OPEN_HOUR/OPEN_MINUTE).
    3. `gap = today_open - prior_close`. Zero gap -> no signal (nothing
       to fade).
    4. Direction: gap up -> SHORT (fade it down); gap down -> LONG
       (fade it up).
    5. Entry: today_open itself, no confirmation wait.
       Target: prior_close, literally -- the gap-fill level, NOT a
       risk-multiple like every other setup in this project.
       Stop: the same distance on the opposite side of entry as the
       target (a deliberate 1:1 R:R, forced by the target being a fixed
       price level rather than a multiple -- see the setup doc's
       honesty flags for what win rate this actually requires).
    6. Exit window: bounded at noon ET, matching the study's own
       gap-fill watch window -- NOT open-ended like every other setup's
       backtest. If neither stop nor target is hit by noon, the trade
       is closed at the last available bar's price before that cutoff.

NO LOOK-AHEAD: prior_close is fully known and frozen at 4:00 PM ET the
day before; entry is the very first bar of the watched window, so
nothing used to define entry/stop/target/direction happens after the
moment of entry.

HOW TO RUN:
    python3 src/detect_fade_the_gap.py
"""

import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE
from study_overnight_gap import get_reference_close, GAP_FILL_WATCH_END_HOUR, GAP_FILL_WATCH_END_MINUTE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Exit window is bounded at the same noon ET cutoff the underlying study
# measured gap-fill against -- see research/setups/fade-the-gap.md #6.
WATCH_END_HOUR, WATCH_END_MINUTE = GAP_FILL_WATCH_END_HOUR, GAP_FILL_WATCH_END_MINUTE


def detect_fade_the_gap_for_day(prior_day_df: pd.DataFrame, day_df: pd.DataFrame,
                                 day, prior_day) -> dict | None:
    """
    Looks at one (prior_day, day) pair and returns a signal dict if there
    was a nonzero gap to fade, or None if either reference point is
    missing or the gap is exactly zero (nothing to fade).
    """
    tz = day_df.index.tz
    prior_close = get_reference_close(prior_day_df, prior_day, tz)
    if prior_close is None:
        return None

    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    open_bars = day_df[day_df.index >= open_ts]
    if open_bars.empty:
        return None

    entry_ts = open_bars.index[0]
    today_open = float(open_bars.iloc[0]["Open"])
    gap = today_open - prior_close

    if gap == 0:
        return None  # nothing to fade -- degenerate case, not a real signal

    watch_end_ts = pd.Timestamp(day, tz=tz).replace(hour=WATCH_END_HOUR, minute=WATCH_END_MINUTE)

    if entry_ts >= watch_end_ts:
        # Real-data edge case (a sparse/gappy morning session where the
        # earliest available bar at/after 8:30 already falls at or past
        # noon) -- there is no watch window left to hold this trade in at
        # all, so it isn't a real signal, not just a "quickly resolved"
        # one. Caught by the real Discovery-slice run, not anticipated by
        # the unit tests' clean synthetic data.
        return None

    if gap > 0:
        direction = "short"
        entry = today_open
        target = prior_close
        risk = entry - target
        stop = entry + risk
    else:
        direction = "long"
        entry = today_open
        target = prior_close
        risk = target - entry
        stop = entry - risk

    return {
        "date": day,
        "prior_day": prior_day,
        "direction": direction,
        "prior_close": round(prior_close, 2),
        "today_open": round(today_open, 2),
        "gap": round(gap, 2),
        "entry_time": entry_ts,
        "entry": round(entry, 2),
        "stop": round(stop, 2),
        "target": round(target, 2),
        "watch_end_time": watch_end_ts,
    }


def simulate_fade_the_gap_trade(day_df: pd.DataFrame, signal: pd.Series) -> dict:
    """Backtest.py's simulate_trade(), but with the day's bars truncated
    to before this setup's noon ET watch-end cutoff first (see setup
    doc #6) -- reuses that unmodified function rather than duplicating
    its stop/target-touch logic. If neither level is hit before the
    cutoff, simulate_trade()'s own "ran out of data" outcome is
    relabeled from "unresolved_end_of_data" to "unresolved_noon_cutoff"
    so it isn't misread as a real end-of-session/end-of-data case like
    every other setup's unresolved trades are."""
    import backtest as bt

    truncated = day_df[day_df.index < signal["watch_end_time"]]
    outcome = bt.simulate_trade(truncated, signal, "entry_time")
    if outcome["exit_reason"] == "unresolved_end_of_data":
        outcome["exit_reason"] = "unresolved_noon_cutoff"
    return outcome


def scan_all_days(df: pd.DataFrame) -> tuple[list[dict], dict]:
    """Walks every consecutive (prior_day, day) pair in df and returns
    (raw signal dicts, stats). Same shape/convention as every other
    detector's scan_all_days()."""
    all_days = sorted(set(df.index.date))
    signals = []
    no_gap_days = 0
    missing_reference_days = 0
    entry_after_watch_window_days = 0

    for i in range(1, len(all_days)):
        prior_day, day = all_days[i - 1], all_days[i]
        prior_day_df = df[df.index.date == prior_day]
        day_df = df[df.index.date == day]
        signal = detect_fade_the_gap_for_day(prior_day_df, day_df, day, prior_day)
        if signal is not None:
            signals.append(signal)
        else:
            tz = day_df.index.tz if len(day_df) else None
            if tz is None:
                no_gap_days += 1
                continue
            if get_reference_close(prior_day_df, prior_day, tz) is None:
                missing_reference_days += 1
                continue
            open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
            open_bars = day_df[day_df.index >= open_ts]
            watch_end_ts = pd.Timestamp(day, tz=tz).replace(hour=WATCH_END_HOUR, minute=WATCH_END_MINUTE)
            if not open_bars.empty and open_bars.index[0] >= watch_end_ts:
                entry_after_watch_window_days += 1
            else:
                no_gap_days += 1

    stats = {
        "total_day_pairs": len(all_days) - 1,
        "no_gap_days": no_gap_days,
        "missing_reference_days": missing_reference_days,
        "entry_after_watch_window_days": entry_after_watch_window_days,
    }
    return signals, stats


STRATEGY_NAME = "fade_the_gap"
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
            timestamp=s["entry_time"],
            instrument="NQ",
            timeframe="1m",
            direction=s["direction"],
            entry=s["entry"],
            stop=s["stop"],
            target=s["target"],
            risk_multiple=_risk_multiple(s["entry"], s["stop"], s["target"]),
            validation_status=validation_status,
            market_context={
                "date": str(s["date"]), "prior_day": str(s["prior_day"]),
                "prior_close": s["prior_close"], "today_open": s["today_open"],
                "gap": s["gap"], "watch_end_time": str(s["watch_end_time"]),
            },
        ))
    return out


def main():
    df, is_synthetic = load_price_data(context="detect_fade_the_gap.py")
    if is_synthetic:
        print("NOTE: using SYNTHETIC data -- signal counts below are for testing the pipeline only.")

    signals, stats = scan_all_days(df)

    signals_df = pd.DataFrame(signals)
    out_path = DATA_DIR / "setups_fade_the_gap.csv"
    signals_df.to_csv(out_path, index=False)

    print(f"\nScanned {stats['total_day_pairs']} consecutive day pairs.")
    print(f"  Signals found: {len(signals_df)}")
    if not signals_df.empty:
        print(f"    Long:  {(signals_df['direction'] == 'long').sum()}")
        print(f"    Short: {(signals_df['direction'] == 'short').sum()}")
    print(f"  Days with no gap to fade: {stats['no_gap_days']}")
    print(f"  Days with missing reference close: {stats['missing_reference_days']}")
    print(f"\nSaved signal log to: {out_path}")
    if not signals_df.empty:
        print("\nFirst few signals:")
        print(signals_df.head())


if __name__ == "__main__":
    main()

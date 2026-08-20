"""
detect_setups.py
==================

WHAT THIS FILE DOES:
This is Stage 2 of the roadmap: turning a specific trading idea into code
that scans historical bars and flags "this looks like the setup."

WHICH SETUP THIS IMPLEMENTS (a starting default, not necessarily YOUR
setup -- swap this out once you tell me what you actually watch for):

    "Opening Range Breakout" (ORB), one of the most common and
    well-documented setups traders use around a session open. The idea:

    1. Watch the first RANGE_MINUTES after the 8:30 open (default: 15
       minutes, so 8:30-8:45). Whatever the highest and lowest price was
       during that window is "the opening range."
    2. After that window closes, watch for price to break above the
       range's high (a "long" / buy signal) or below the range's low (a
       "short" / sell signal), within the next BREAKOUT_WINDOW_MINUTES
       (default: 60 minutes, so by 9:45).
    3. The first bar that closes outside the range in either direction is
       the signal. Its entry price, a stop (the opposite side of the
       range), and a target (one "range-width" beyond entry, a simple
       starting rule) all get recorded.

    Some days won't break out at all in either direction within the
    window -- that's a normal, valid outcome, not a bug. Not every day
    has a clean setup.

THIS SCRIPT ONLY DETECTS AND RECORDS SIGNALS. It does NOT check whether
they would have won or lost -- that's Stage 3 (the backtest engine),
which is next.

HOW TO RUN:
    python3 src/detect_setups.py
"""

import pandas as pd
from pathlib import Path
from data_loader import load_price_data

# ---------------------------------------------------------------------------
# SETTINGS -- the "knobs" for this specific setup definition. Change these
# to try a tighter or wider opening range, or a longer/shorter breakout
# window, without touching the logic below.
# ---------------------------------------------------------------------------
OPEN_HOUR, OPEN_MINUTE = 8, 30          # the 8:30 AM NY open
RANGE_MINUTES = 15                       # how long the "opening range" window is
BREAKOUT_WINDOW_MINUTES = 60             # how long after the range to watch for a breakout

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def detect_orb_for_day(day_df: pd.DataFrame, day) -> dict | None:
    """
    Looks at one day's worth of bars and returns a signal dict if a clean
    opening-range breakout happened, or None if the day didn't produce one
    (e.g. price never broke out, or there wasn't enough data for that day).
    """
    tz = day_df.index.tz
    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    range_end_ts = open_ts + pd.Timedelta(minutes=RANGE_MINUTES)
    breakout_end_ts = range_end_ts + pd.Timedelta(minutes=BREAKOUT_WINDOW_MINUTES)

    range_bars = day_df[(day_df.index >= open_ts) & (day_df.index < range_end_ts)]
    if range_bars.empty:
        return None  # not enough data to define a range for this day

    range_high = range_bars["High"].max()
    range_low = range_bars["Low"].min()
    range_size = range_high - range_low

    watch_bars = day_df[(day_df.index >= range_end_ts) & (day_df.index < breakout_end_ts)]

    for ts, bar in watch_bars.iterrows():
        if bar["Close"] > range_high:
            return {
                "date": day,
                "direction": "long",
                "range_high": round(range_high, 2),
                "range_low": round(range_low, 2),
                "breakout_time": ts,
                "entry": round(bar["Close"], 2),
                "stop": round(range_low, 2),
                "target": round(bar["Close"] + range_size, 2),
            }
        if bar["Close"] < range_low:
            return {
                "date": day,
                "direction": "short",
                "range_high": round(range_high, 2),
                "range_low": round(range_low, 2),
                "breakout_time": ts,
                "entry": round(bar["Close"], 2),
                "stop": round(range_high, 2),
                "target": round(bar["Close"] - range_size, 2),
            }

    return None  # price stayed inside the range the whole watch window -- no signal today


def scan_all_days(df: pd.DataFrame) -> tuple[list[dict], dict]:
    """
    Walks every day in df and returns (raw signal dicts, stats). This is
    the exact day-by-day loop main() used to run inline -- extracted
    2026-08-20 so main() and generate_signals() (the Signal-contract
    adapter, below) share one implementation instead of two copies that
    could silently drift apart. detect_orb_for_day() itself is untouched.
    """
    all_days = sorted(set(df.index.date))
    signals = []
    no_signal_days = 0

    for day in all_days:
        day_df = df[df.index.date == day]
        signal = detect_orb_for_day(day_df, day)
        if signal is not None:
            signals.append(signal)
        else:
            no_signal_days += 1

    stats = {"total_days": len(all_days), "no_signal_days": no_signal_days}
    return signals, stats


STRATEGY_NAME = "orb_placeholder"
STRATEGY_VERSION = "1.0"


def generate_signals(df: pd.DataFrame, validation_status: str = "research") -> list:
    """
    Signal-contract adapter (docs/AUTOMATION_ARCHITECTURE.md's approved
    Signal schema) around the existing, unchanged scan_all_days() logic.
    Returns a list of strategy_contract.Signal objects instead of the
    raw dicts scan_all_days() produces internally.
    """
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
            market_context={"range_high": s["range_high"], "range_low": s["range_low"], "date": str(s["date"])},
        ))
    return out


def main():
    df, is_synthetic = load_price_data(context="detect_setups.py")
    if is_synthetic:
        print("NOTE: using SYNTHETIC data -- signal counts below are for testing the pipeline only.")

    signals, stats = scan_all_days(df)

    signals_df = pd.DataFrame(signals)
    out_path = DATA_DIR / "setups_orb.csv"
    signals_df.to_csv(out_path, index=False)

    print(f"\nScanned {stats['total_days']} days.")
    print(f"  Signals found: {len(signals_df)}")
    if not signals_df.empty:
        print(f"    Long:  {(signals_df['direction'] == 'long').sum()}")
        print(f"    Short: {(signals_df['direction'] == 'short').sum()}")
    print(f"  Days with no breakout in the watch window: {stats['no_signal_days']}")
    print(f"\nSaved signal log to: {out_path}")
    if not signals_df.empty:
        print("\nFirst few signals:")
        print(signals_df.head())


if __name__ == "__main__":
    main()

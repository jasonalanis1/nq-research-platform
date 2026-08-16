"""
detect_level_sweep.py
=======================

A second Stage 2 setup, alongside the Opening Range Breakout placeholder
in detect_setups.py -- this one built from reviewing screenshots Jason
sent of a chart showing a real reversal trade at the open.

WHICH SETUP THIS IMPLEMENTS -- "Level Sweep Reversal":

    Instead of watching an arbitrary 15-minute range like the ORB
    placeholder, this watches PRICE LEVELS THAT ACTUALLY MATTER --
    yesterday's high/low, and the high/low of today's pre-market session
    (before the 8:30 open). These are widely-watched reference points:
    other traders and algorithms tend to react around them, which is a
    more defensible reason to expect a reaction than an arbitrary window.

    1. Each day, compute two levels:
       - SUPPORT: the lower of {yesterday's low, today's pre-market low}
       - RESISTANCE: the higher of {yesterday's high, today's pre-market high}
    2. Watch the period from the 8:30 open through WATCH_MINUTES after.
    3. A "sweep" happens when price trades through one of these levels
       (e.g. dips below support). That alone isn't the signal -- lots of
       sweeps just keep going. The signal is a REVERSAL: a bar's CLOSE
       moves back on the other side of the level after it was swept
       (confirming buyers/sellers stepped back in, not just a random
       wick). This can happen on the very same bar (a long wick that
       closes back above the level -- the cleanest version) or a later
       bar.
    4. Entry: the close of the confirming bar.
       Stop: the most extreme price reached during the sweep (if price
       takes that back out, the reversal idea is wrong).
       Target: a MODEST target sized off risk (see TARGET_R_MULTIPLE
       below), not the far opposite level -- see "2026-08-16 target rule
       change" below for why.

2026-08-16 -- CONFIRMATION RULE, THREE VARIANTS (not yet decided):
    Jason doesn't yet have a strong feel for which confirmation rule is
    right, so rather than guess, this file supports three, selectable via
    a command-line argument, each logged as its own separate experiment
    for later comparison instead of picking a winner now:
      - "close_any" (the original/default): any close back beyond the
        level counts, same bar or later.
      - "close_min_distance": the close must clear the level by at least
        MIN_CONFIRM_DISTANCE_POINTS -- filters out marginal/barely-over
        closes. That point value is an arbitrary illustrative choice, not
        derived from data yet.
      - "full_bar_range": the ENTIRE confirming bar (not just its close)
        must be back beyond the level -- i.e. its low (support case) or
        high (resistance case) also cleared the level. This is strictly
        stronger than close_any and, by construction, can never fire on
        the same bar that did the sweep (since that bar's low/high is
        what swept it in the first place) -- confirmation always comes on
        a later bar under this rule.

2026-08-16 -- TARGET RULE CHANGE:
    The original version targeted the opposite level, which -- reviewed
    against research/raw/2026-08-16-video-reference-chart.md -- doesn't
    match what was actually visible in the reference video. That trade's
    real target (30060) was only 27 points from its entry (30033) against
    a 20-point risk (stop at 30013) -- a modest ~1.35x-risk target, NOT
    the far opposite level (price later ran 8-10x further, but that was
    what happened after the trade, not the target itself). TARGET_R_MULTIPLE
    below (1.35) is that ratio, taken directly from the one concrete
    example we have -- not statistically derived, and worth revisiting
    once there's more than one reference trade to calibrate from.

NOTE ON WHERE THIS CAME FROM: built from reading price levels and an
entry/stop/target box visible in a screenshot Jason shared of someone
else's trading video -- reverse-engineered from what was visible on
screen, not copied from their code (which we don't have and couldn't
ethically replicate exactly anyway). "Watch for reversals at meaningful
reference levels" is a generic, widely-taught trading concept, not
proprietary to that video -- this is our own implementation of that
general idea. The specific level choices and confirmation rule here are
Jason's calls, made together in conversation.

HOW TO RUN:
    python3 src/detect_level_sweep.py                       # default: close_any
    python3 src/detect_level_sweep.py close_any
    python3 src/detect_level_sweep.py close_min_distance
    python3 src/detect_level_sweep.py full_bar_range
"""

import sys
import pandas as pd
from pathlib import Path

OPEN_HOUR, OPEN_MINUTE = 8, 30
WATCH_MINUTES = 90  # how long after the open to watch for a sweep + reversal

CONFIRMATION_MODES = ["close_any", "close_min_distance", "full_bar_range"]
MIN_CONFIRM_DISTANCE_POINTS = 5.0  # arbitrary placeholder for close_min_distance -- see file header

TARGET_R_MULTIPLE = 1.35  # derived from the one video reference trade -- see file header

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_latest_data() -> tuple[pd.DataFrame, bool]:
    candidates = sorted(DATA_DIR.glob("NQ_1min_*.csv"))
    if not candidates:
        raise FileNotFoundError("No data file found in data/. Run data_fetch.py or generate_sample_data.py first.")
    real_files = [c for c in candidates if "SYNTHETIC" not in c.name]
    chosen = real_files[-1] if real_files else candidates[-1]
    print(f"Loading: {chosen.name}")
    df = pd.read_csv(chosen, index_col="timestamp_ny")
    # See detect_setups.py's load_latest_data() for why this can't be a
    # plain parse_dates=True -- files spanning a DST change mix UTC
    # offsets, which that silently fails to parse correctly.
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
    return df, ("SYNTHETIC" in chosen.name)


def compute_levels(df: pd.DataFrame, day, prior_day) -> dict | None:
    """
    Returns the support/resistance levels for `day`, or None if we don't
    have enough data (e.g. it's the first day in the dataset, so there's
    no "yesterday," or there are no pre-market bars before the open).
    """
    prior_day_bars = df[df.index.date == prior_day]
    if prior_day_bars.empty:
        return None

    tz = df.index.tz
    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    day_bars = df[df.index.date == day]
    premarket_bars = day_bars[day_bars.index < open_ts]
    if premarket_bars.empty:
        return None  # no pre-market data for today -- can't compute a pre-market level

    prior_day_high = prior_day_bars["High"].max()
    prior_day_low = prior_day_bars["Low"].min()
    premarket_high = premarket_bars["High"].max()
    premarket_low = premarket_bars["Low"].min()

    if prior_day_low <= premarket_low:
        support, support_source = prior_day_low, "prior_day_low"
    else:
        support, support_source = premarket_low, "premarket_low"

    if prior_day_high >= premarket_high:
        resistance, resistance_source = prior_day_high, "prior_day_high"
    else:
        resistance, resistance_source = premarket_high, "premarket_high"

    return {
        "support": support, "support_source": support_source,
        "resistance": resistance, "resistance_source": resistance_source,
        "open_ts": open_ts,
    }


def _support_confirmed(bar, support, mode) -> bool:
    """Has this bar confirmed a reversal back above a swept support level?"""
    if mode == "close_any":
        return bar["Close"] > support
    if mode == "close_min_distance":
        return bar["Close"] > support + MIN_CONFIRM_DISTANCE_POINTS
    if mode == "full_bar_range":
        return bar["Low"] > support  # the WHOLE bar, not just the close, is back above
    raise ValueError(f"Unknown confirmation mode: {mode}")


def _resistance_confirmed(bar, resistance, mode) -> bool:
    """Has this bar confirmed a reversal back below a swept resistance level?"""
    if mode == "close_any":
        return bar["Close"] < resistance
    if mode == "close_min_distance":
        return bar["Close"] < resistance - MIN_CONFIRM_DISTANCE_POINTS
    if mode == "full_bar_range":
        return bar["High"] < resistance  # the WHOLE bar, not just the close, is back below
    raise ValueError(f"Unknown confirmation mode: {mode}")


def scan_for_signal(day_df: pd.DataFrame, levels: dict, confirmation_mode: str = "close_any") -> dict | None:
    """
    Walks forward bar-by-bar from the open, tracking whether support or
    resistance has been swept, and whether a reversal has confirmed under
    the given confirmation_mode (see CONFIRMATION_MODES / file header).
    Returns whichever signal (long or short) confirms first, or None if
    neither does within the watch window.

    Entry is always the confirming bar's close. Stop is always the most
    extreme price reached during the sweep. Target is a modest
    TARGET_R_MULTIPLE-times-risk target (see file header for where that
    number comes from) -- no longer the opposite level.
    """
    watch_end = levels["open_ts"] + pd.Timedelta(minutes=WATCH_MINUTES)
    watch_bars = day_df[(day_df.index >= levels["open_ts"]) & (day_df.index < watch_end)]

    support_swept = False
    support_extreme = None
    resistance_swept = False
    resistance_extreme = None

    for ts, bar in watch_bars.iterrows():
        # --- support side (watching for a long reversal) ---
        if not support_swept and bar["Low"] < levels["support"]:
            support_swept = True
            support_extreme = bar["Low"]
        elif support_swept:
            support_extreme = min(support_extreme, bar["Low"])

        if support_swept and _support_confirmed(bar, levels["support"], confirmation_mode):
            entry = bar["Close"]
            risk = entry - support_extreme
            return {
                "direction": "long",
                "level_swept": levels["support"],
                "level_source": levels["support_source"],
                "sweep_extreme": support_extreme,
                "signal_time": ts,
                "entry": entry,
                "stop": support_extreme,
                "target": entry + TARGET_R_MULTIPLE * risk,
            }

        # --- resistance side (watching for a short reversal) ---
        if not resistance_swept and bar["High"] > levels["resistance"]:
            resistance_swept = True
            resistance_extreme = bar["High"]
        elif resistance_swept:
            resistance_extreme = max(resistance_extreme, bar["High"])

        if resistance_swept and _resistance_confirmed(bar, levels["resistance"], confirmation_mode):
            entry = bar["Close"]
            risk = resistance_extreme - entry
            return {
                "direction": "short",
                "level_swept": levels["resistance"],
                "level_source": levels["resistance_source"],
                "sweep_extreme": resistance_extreme,
                "signal_time": ts,
                "entry": entry,
                "stop": resistance_extreme,
                "target": entry - TARGET_R_MULTIPLE * risk,
            }

    return None


def main():
    confirmation_mode = sys.argv[1] if len(sys.argv) > 1 else "close_any"
    if confirmation_mode not in CONFIRMATION_MODES:
        print(f"Unknown confirmation mode '{confirmation_mode}'. Choose one of: {CONFIRMATION_MODES}")
        return

    df, is_synthetic = load_latest_data()
    if is_synthetic:
        print("NOTE: using SYNTHETIC data -- signal counts below are for testing the pipeline only.")
    print(f"Confirmation mode: {confirmation_mode}")

    all_days = sorted(set(df.index.date))
    signals = []
    skipped_no_levels = 0
    no_signal_days = 0

    for i, day in enumerate(all_days):
        if i == 0:
            continue  # first day in the dataset has no "prior day"
        prior_day = all_days[i - 1]

        levels = compute_levels(df, day, prior_day)
        if levels is None:
            skipped_no_levels += 1
            continue

        day_df = df[df.index.date == day]
        signal = scan_for_signal(day_df, levels, confirmation_mode)
        if signal is not None:
            signal["date"] = day
            signals.append(signal)
        else:
            no_signal_days += 1

    signals_df = pd.DataFrame(signals)
    if not signals_df.empty:
        signals_df = signals_df[["date", "direction", "level_source", "level_swept", "sweep_extreme",
                                  "signal_time", "entry", "stop", "target"]]
        for col in ["level_swept", "sweep_extreme", "entry", "stop", "target"]:
            signals_df[col] = signals_df[col].round(2)

    out_path = DATA_DIR / f"setups_level_sweep_{confirmation_mode}.csv"
    signals_df.to_csv(out_path, index=False)

    print(f"\nScanned {len(all_days) - 1} days (excluding the first, which has no prior day).")
    print(f"  Signals found: {len(signals_df)}")
    if not signals_df.empty:
        print(f"    Long:  {(signals_df['direction'] == 'long').sum()}")
        print(f"    Short: {(signals_df['direction'] == 'short').sum()}")
    print(f"  Days skipped (missing prior-day or pre-market data): {skipped_no_levels}")
    print(f"  Days with no sweep+reversal in the watch window: {no_signal_days}")
    print(f"\nSaved signal log to: {out_path}")
    if not signals_df.empty:
        print("\nFirst few signals:")
        print(signals_df.head())


if __name__ == "__main__":
    main()

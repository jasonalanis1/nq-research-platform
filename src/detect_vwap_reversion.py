"""
detect_vwap_reversion.py
===========================

Implements the "VWAP Mean Reversion (2sigma / 3sigma Bands)" setup
frozen in `research/setups/vwap-mean-reversion.md`. First setup in this
project sourced from external day-trading-technique research (at
Jason's request) rather than a market-structure concept applied fresh
or a direct mechanical translation of one of this project's own
characterization findings.

WHICH SETUP THIS IMPLEMENTS:

    1. Session VWAP and its volume-weighted standard deviation band
       (sigma), computed CAUSALLY bar-by-bar from the 8:30 AM ET open
       (OPEN_HOUR/OPEN_MINUTE, imported from detect_ib_breakout.py, not
       redefined) using each bar's typical price (High+Low+Close)/3.
    2. A 30-minute warm-up window (WARMUP_MINUTES, matching the Initial
       Balance convention already used elsewhere in this project) --
       sigma is meaningless on too few bars, so no signal is considered
       until it ends.
    3. After warm-up, the first bar whose Close closes beyond
       VWAP +/- 2*sigma is the day's signal -- no flip-flopping if the
       other band is touched later.
    4. Direction: fade it -- short above the upper band, long below the
       lower band.
    5. Entry: the signal bar's Close (which can land past the 2-sigma
       trigger line, not always right at it -- see the note below).
       Stop: exactly 1*sigma from ENTRY (not a fixed vwap+3*sigma band
       level -- see the fix note below). Target: VWAP itself, same bar.
       This gives at least a 2:1 R:R (risk is always exactly 1sigma;
       reward is at least 2sigma, more if entry overshot further past
       the 2-sigma trigger), a floor that falls directly out of the
       2sigma band convention, not tuned to this setup or this data.

    A REAL BUG FOUND AND FIXED DURING TESTING (2026-09-02): the first
    version of this detector set the stop to a FIXED vwap+3*sigma (or
    vwap-3*sigma) band level, assuming entry always sits close to the
    2-sigma trigger line. On the real Discovery slice, ~17% of signals
    had a triggering bar that closed well past 2 sigma -- sometimes past
    the fixed 3-sigma level itself -- which put the "stop" on the WRONG
    SIDE of entry (already in-the-money at the moment of entry, for a
    short/long that hadn't even started yet). This produced wildly
    unstable R-multiples (average win +2.62R, average loss -2.49R,
    versus the intended +2R/-1R) that were a bookkeeping artifact, not a
    real result. Fixed by defining the stop relative to ENTRY (always
    exactly 1 sigma away, same direction as the excursion) instead of a
    fixed absolute band level -- this guarantees risk is always exactly
    1 sigma and the stop is always on the correct side of entry, by
    construction, regardless of how far past the 2-sigma trigger the
    actual closing bar landed.
    6. Resolution: no artificial time cutoff (unlike Fade the Gap) --
       held via backtest.py's own unmodified simulate_trade() until
       stop or target is hit, or the day's data ends.

VWAP/sigma ARE COMPUTED WITH THE STANDARD O(n) WEIGHTED-VARIANCE
IDENTITY (avoiding an O(n^2) nested loop):
    variance[t] = sum(V[i]*P[i]^2 for i in 0..t)/sum(V[i] for i in 0..t) - VWAP[t]^2
which is algebraically identical to
    sum(V[i]*(P[i]-VWAP[t])^2 for i in 0..t) / sum(V[i] for i in 0..t)
(the setup doc's definition) -- expand the square and substitute
VWAP[t] = sum(V*P)/sum(V) to see the two are the same formula.

NO LOOK-AHEAD: VWAP[t] and sigma[t] at any bar t use only that bar and
everything before it in the same session (both are running/cumulative
sums), and the entry is that same bar's own Close.

HOW TO RUN:
    python3 src/detect_vwap_reversion.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

from data_loader import load_price_data
from detect_ib_breakout import OPEN_HOUR, OPEN_MINUTE

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

WARMUP_MINUTES = 30      # matches this project's Initial Balance window convention
N_SIGMA_ENTRY = 2.0      # band that triggers a signal
STOP_SIGMA_FROM_ENTRY = 1.0   # stop is this many sigma FROM ENTRY (not a fixed absolute band --
                               # see detect_vwap_reversion_for_day()'s note on why)


def compute_session_vwap_bands(session_bars: pd.DataFrame) -> pd.DataFrame:
    """Adds vwap/sigma columns to a copy of session_bars, computed
    causally (each row uses only itself and prior rows in session_bars).
    session_bars must already be sorted by time and start at the
    session's own open -- this function does not know or care what
    "the open" means, it just runs cumulative sums top to bottom."""
    out = session_bars.copy()
    typical_price = (out["High"] + out["Low"] + out["Close"]) / 3.0
    volume = out["Volume"]

    cum_v = volume.cumsum()
    cum_pv = (typical_price * volume).cumsum()
    cum_pv2 = (typical_price.pow(2) * volume).cumsum()

    vwap = cum_pv / cum_v
    variance = cum_pv2 / cum_v - vwap.pow(2)
    # Floating-point noise can push variance a hair below zero when it
    # should be exactly zero (e.g. the first bar, or a run of identical
    # prices) -- clip rather than let sqrt produce NaN.
    variance = variance.clip(lower=0.0)
    sigma = np.sqrt(variance)

    out["vwap"] = vwap
    out["sigma"] = sigma
    return out


def detect_vwap_reversion_for_day(day_df: pd.DataFrame, day) -> dict | None:
    """
    Looks at one day's worth of bars and returns a signal dict if a
    clean VWAP-band reversion trigger happened after the warm-up window,
    or None if the day didn't produce one (no band touch, not enough
    data to define the session at all, or a degenerate zero-sigma
    stretch throughout the watch window).
    """
    tz = day_df.index.tz
    open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
    session_bars = day_df[day_df.index >= open_ts]
    if session_bars.empty:
        return None

    warmup_end_ts = open_ts + pd.Timedelta(minutes=WARMUP_MINUTES)
    banded = compute_session_vwap_bands(session_bars)
    watch_bars = banded[banded.index >= warmup_end_ts]

    for ts, bar in watch_bars.iterrows():
        vwap = bar["vwap"]
        sigma = bar["sigma"]
        if not sigma > 0:
            continue  # degenerate/zero-width band this bar -- not a real signal, skip to the next

        upper = vwap + N_SIGMA_ENTRY * sigma
        lower = vwap - N_SIGMA_ENTRY * sigma
        close = bar["Close"]

        if close > upper:
            entry = close
            # Risk is always exactly STOP_SIGMA_FROM_ENTRY*sigma from
            # ENTRY, not a fixed absolute band level -- see the module
            # docstring's "entry can overshoot the 2-sigma trigger"
            # note. A stop pinned to a fixed vwap+3*sigma level would
            # sometimes land BEHIND a badly-overshot entry (confirmed on
            # the real Discovery slice: ~17% of signals), which is not
            # a real "the move already invalidated the trade" case,
            # just a bookkeeping error in the exit level.
            stop = entry + STOP_SIGMA_FROM_ENTRY * sigma
            if round(entry, 2) == round(stop, 2):
                # A second real edge case, also only found via the real
                # Discovery-slice run: when sigma is a tiny fraction of
                # a point (a very quiet stretch right after warmup),
                # rounding entry and stop to the instrument's own 2-
                # decimal convention can collapse them to the identical
                # price -- a zero-risk signal after rounding, same
                # failure class as detect_fvg_entry.py's zero-risk-
                # signal fix. Not a real, tradeable setup -- skip this
                # bar and keep watching, rather than returning it.
                continue
            return {
                "date": day,
                "direction": "short",
                "signal_time": ts,
                "vwap": round(float(vwap), 2),
                "sigma": round(float(sigma), 4),
                "entry": round(float(entry), 2),
                "stop": round(float(stop), 2),
                "target": round(float(vwap), 2),
            }
        if close < lower:
            entry = close
            stop = entry - STOP_SIGMA_FROM_ENTRY * sigma
            if round(entry, 2) == round(stop, 2):
                continue  # zero-risk signal after rounding -- see the short branch's note above
            return {
                "date": day,
                "direction": "long",
                "signal_time": ts,
                "vwap": round(float(vwap), 2),
                "sigma": round(float(sigma), 4),
                "entry": round(float(entry), 2),
                "stop": round(float(stop), 2),
                "target": round(float(vwap), 2),
            }

    return None  # never closed beyond either band after warm-up -- no signal today


def scan_all_days(df: pd.DataFrame) -> tuple[list[dict], dict]:
    """Walks every day in df and returns (raw signal dicts, stats). Same
    shape/convention as every other detector's scan_all_days()."""
    all_days = sorted(set(df.index.date))
    signals = []
    no_signal_days = 0
    missing_session_days = 0

    for day in all_days:
        day_df = df[df.index.date == day]
        signal = detect_vwap_reversion_for_day(day_df, day)
        if signal is not None:
            signals.append(signal)
        else:
            tz = day_df.index.tz if len(day_df) else None
            if tz is None:
                missing_session_days += 1
                continue
            open_ts = pd.Timestamp(day, tz=tz).replace(hour=OPEN_HOUR, minute=OPEN_MINUTE)
            if day_df[day_df.index >= open_ts].empty:
                missing_session_days += 1
            else:
                no_signal_days += 1

    stats = {
        "total_days": len(all_days),
        "no_signal_days": no_signal_days,
        "missing_session_days": missing_session_days,
    }
    return signals, stats


STRATEGY_NAME = "vwap_mean_reversion"
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
                "date": str(s["date"]), "vwap": s["vwap"], "sigma": s["sigma"],
            },
        ))
    return out


def main():
    df, is_synthetic = load_price_data(context="detect_vwap_reversion.py")
    if is_synthetic:
        print("NOTE: using SYNTHETIC data -- signal counts below are for testing the pipeline only.")

    signals, stats = scan_all_days(df)

    signals_df = pd.DataFrame(signals)
    out_path = DATA_DIR / "setups_vwap_reversion.csv"
    signals_df.to_csv(out_path, index=False)

    print(f"\nScanned {stats['total_days']} days.")
    print(f"  Signals found: {len(signals_df)}")
    if not signals_df.empty:
        print(f"    Long:  {(signals_df['direction'] == 'long').sum()}")
        print(f"    Short: {(signals_df['direction'] == 'short').sum()}")
    print(f"  Days with no band touch after warm-up: {stats['no_signal_days']}")
    print(f"  Days with no usable session data: {stats['missing_session_days']}")
    print(f"\nSaved signal log to: {out_path}")
    if not signals_df.empty:
        print("\nFirst few signals:")
        print(signals_df.head())


if __name__ == "__main__":
    main()

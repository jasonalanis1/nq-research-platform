"""
test_detect_vwap_reversion.py
================================
Automated tests for the VWAP Mean Reversion detection logic
(research/setups/vwap-mean-reversion.md).

Same tiny-fake-dataset approach as every other detector's tests -- build
a DataFrame where the VWAP/sigma math can be verified by hand, run the
real code, check the answer.

WORKED MATH USED BELOW (30 calm warmup bars at a flat price P, volume v
each, followed by one watch bar at price X, volume v): with N=30 prior
bars, the causal VWAP/sigma identity reduces to a clean closed form --

    vwap  = (100*N + X) / (N + 1)
    sigma = sqrt(N) * |X - 100| / (N + 1)
    stop  = X +/- 1*sigma   (from ENTRY, not a fixed band level -- see
                             detect_vwap_reversion.py's bug-fix note)

(derived from the module's own variance identity, with P=100 here) --
used to compute exact expected entry/stop/target below rather than
duplicating the implementation's arithmetic blindly.

HOW TO RUN ALL TESTS:
    cd nq_research_platform
    pytest
"""
from datetime import date
import pandas as pd
import detect_vwap_reversion as vr


def make_bars(day, tz, bars):
    """Helper: builds a small DataFrame of price bars from a simple list
    of (hour, minute, open, high, low, close, volume) tuples."""
    rows = []
    index = []
    for hour, minute, o, h, l, c, v in bars:
        ts = pd.Timestamp(day, tz=tz).replace(hour=hour, minute=minute)
        index.append(ts)
        rows.append({"Open": o, "High": h, "Low": l, "Close": c, "Volume": v})
    return pd.DataFrame(rows, index=index)


def flat_warmup_bars(day, tz, price=100.0, volume=10.0, n=30):
    """n calm bars (8:30 through 8:30+n-1 minutes) all flat at `price` --
    the exact 30-minute WARMUP_MINUTES window when n=30."""
    bars = [(8, 30 + m, price, price, price, price, volume) for m in range(n)]
    return make_bars(day, tz, bars)


def test_short_signal_when_close_above_upper_band():
    """30 flat warmup bars at 100, then one watch bar (9:00, right after
    warmup ends) closing at 110. Exact expected values from the
    module's own closed form with N=30, X=110:
    vwap=3110/31=100.32258..., sigma=10*sqrt(30)/31=1.76684696...,
    stop=entry+1*sigma=111.76684..., rounds to entry=110.0, stop=111.77,
    target=vwap=100.32. (Stop is relative to ENTRY, not a fixed band
    level -- see detect_vwap_reversion.py's bug-fix note: this specific
    watch bar overshoots the 2-sigma trigger by a lot, which is exactly
    the case that broke the original fixed-band stop.)"""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    warmup = flat_warmup_bars(day, tz, price=100.0, volume=10.0, n=30)
    watch = make_bars(day, tz, [(9, 0, 110.0, 110.0, 110.0, 110.0, 10.0)])
    day_df = pd.concat([warmup, watch])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "short"
    assert signal["entry"] == 110.0
    assert signal["vwap"] == 100.32
    assert signal["stop"] == 111.77
    assert signal["target"] == 100.32
    assert signal["stop"] > signal["entry"]  # stop must be on the adverse side of entry


def test_long_signal_when_close_below_lower_band():
    """Mirror of the short test: one watch bar closing at 90 (10 points
    below the 100 baseline). By the same closed form (|X-100|=10, same
    magnitude): vwap=3090/31=99.67741..., sigma unchanged at 1.76684696,
    stop=entry-1*sigma=88.23315..., rounds to entry=90.0, stop=88.23,
    target=99.68."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    warmup = flat_warmup_bars(day, tz, price=100.0, volume=10.0, n=30)
    watch = make_bars(day, tz, [(9, 0, 90.0, 90.0, 90.0, 90.0, 10.0)])
    day_df = pd.concat([warmup, watch])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "long"
    assert signal["entry"] == 90.0
    assert signal["vwap"] == 99.68
    assert signal["stop"] == 88.23
    assert signal["target"] == 99.68
    assert signal["stop"] < signal["entry"]  # stop must be on the adverse side of entry


def test_stop_stays_on_adverse_side_even_for_a_large_overshoot():
    """Regression test for the bug found on the real Discovery slice: a
    watch bar that overshoots the 2-sigma trigger by a huge amount (far
    past where a fixed 3-sigma band would have sat) must still produce
    a stop on the correct/adverse side of entry, since the stop is now
    always exactly 1*sigma from ENTRY rather than a fixed absolute band
    level."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    warmup = flat_warmup_bars(day, tz, price=100.0, volume=10.0, n=30)
    # A massive overshoot -- roughly 30 sigma past vwap with these warmup
    # bars, far beyond where a fixed vwap+3*sigma band would have been.
    watch = make_bars(day, tz, [(9, 0, 250.0, 250.0, 250.0, 250.0, 10.0)])
    day_df = pd.concat([warmup, watch])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "short"
    assert signal["stop"] > signal["entry"]  # would have failed under the old fixed-band stop
    assert signal["target"] < signal["entry"]


def test_zero_risk_signal_skipped_after_rounding():
    """Regression test for a second real edge case found on the real
    Discovery slice: an extremely tiny deviation (0.001 points) still
    mathematically crosses the 2-sigma trigger with N=30 calm warmup
    bars (the trigger condition is magnitude-independent -- see the
    module's own worked-math comment), but produces a sigma so small
    that entry and stop round to the identical price at this
    instrument's usual 2-decimal precision -- a zero-risk signal after
    rounding. Must be skipped (treated as no signal), not returned with
    a zero/NaN-producing risk."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    warmup = flat_warmup_bars(day, tz, price=100.0, volume=10.0, n=30)
    watch = make_bars(day, tz, [(9, 0, 100.001, 100.001, 100.001, 100.001, 10.0)])
    day_df = pd.concat([warmup, watch])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is None


def test_no_signal_within_bands():
    """Warmup bars alternate 99/101 (vwap=100, sigma=1 exactly by
    construction), then an hour of watch bars sitting right at the
    vwap (100) -- comfortably inside any reasonable band. Must not
    produce a signal."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    warmup_bars = []
    for m in range(30):
        price = 99.0 if m % 2 == 0 else 101.0
        warmup_bars.append((8, 30 + m, price, price, price, price, 10.0))
    warmup = make_bars(day, tz, warmup_bars)

    watch_bars = [(9 + h, m, 100.0, 100.0, 100.0, 100.0, 10.0)
                  for h in range(2) for m in range(60)]
    watch = make_bars(day, tz, watch_bars)
    day_df = pd.concat([warmup, watch])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is None


def test_warmup_period_suppresses_early_signals():
    """A huge deviation (50 points) occurring at 8:59 -- still inside
    the 30-minute warmup window (8:30-9:00) -- must NOT produce a
    signal, even though the same deviation after warmup would. Flat
    bars after warmup (whose vwap/band the spike has already widened
    considerably) must also not trigger, so the whole day returns
    None."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    calm = [(8, 30 + m, 100.0, 100.0, 100.0, 100.0, 10.0) for m in range(29)]
    spike = [(8, 59, 150.0, 150.0, 150.0, 150.0, 10.0)]  # still within warmup (before 9:00)
    warmup = make_bars(day, tz, calm + spike)

    watch_bars = [(9 + h, m, 100.0, 100.0, 100.0, 100.0, 10.0)
                  for h in range(2) for m in range(60)]
    watch = make_bars(day, tz, watch_bars)
    day_df = pd.concat([warmup, watch])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is None


def test_first_signal_only_no_flip_flop():
    """If a short trigger fires first, a later long trigger the same day
    must be ignored -- only the first qualifying event is tradeable,
    matching every other setup in this project."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    warmup = flat_warmup_bars(day, tz, price=100.0, volume=10.0, n=30)
    short_trigger = make_bars(day, tz, [(9, 0, 110.0, 110.0, 110.0, 110.0, 10.0)])
    later_long_trigger = make_bars(day, tz, [(9, 5, 10.0, 10.0, 10.0, 10.0, 10.0)])
    day_df = pd.concat([warmup, short_trigger, later_long_trigger])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is not None
    assert signal["direction"] == "short"
    assert signal["entry"] == 110.0


def test_missing_session_returns_none():
    """If a day has no bars at/after 8:30 AM ET at all, there's no
    session to define VWAP over -- skip cleanly."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    day_df = make_bars(day, tz, [(7, 0, 100.0, 100.0, 100.0, 100.0, 10.0)])

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is None


def test_zero_volume_bars_do_not_crash():
    """All-zero volume produces a 0/0 VWAP (NaN) -- must be handled
    safely (skipped, not treated as a signal, no crash), not just
    happen to not raise by accident."""
    day = date(2024, 1, 2)
    tz = "America/New_York"
    bars = [(8, 30 + m, 100.0, 105.0, 95.0, 100.0, 0.0) for m in range(30)]
    bars += [(9, m, 100.0, 105.0, 95.0, 100.0, 0.0) for m in range(60)]
    day_df = make_bars(day, tz, bars)

    signal = vr.detect_vwap_reversion_for_day(day_df, day)

    assert signal is None


def test_scan_all_days_counts_missing_session_separately():
    """scan_all_days()'s stats should distinguish a day with no usable
    session data from an ordinary no-signal day."""
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    tz = "America/New_York"

    day1_df = make_bars(day1, tz, [(7, 0, 100.0, 100.0, 100.0, 100.0, 10.0)])  # no 8:30+ bars

    warmup_bars = []
    for m in range(30):
        price = 99.0 if m % 2 == 0 else 101.0
        warmup_bars.append((8, 30 + m, price, price, price, price, 10.0))
    watch_bars = [(9, m, 100.0, 100.0, 100.0, 100.0, 10.0) for m in range(30)]
    day2_df = pd.concat([make_bars(day2, tz, warmup_bars), make_bars(day2, tz, watch_bars)])

    df = pd.concat([day1_df, day2_df])

    signals, stats = vr.scan_all_days(df)

    assert signals == []
    assert stats["total_days"] == 2
    assert stats["missing_session_days"] == 1
    assert stats["no_signal_days"] == 1

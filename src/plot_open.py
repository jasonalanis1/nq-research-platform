"""
plot_open.py
=============

WHAT THIS FILE DOES:
Reads the minute-bar CSV data we saved earlier and draws a chart of price
action around the 8:30 AM New York open, for a handful of recent days, so
we can visually sanity-check the data before building anything more
complex on top of it.

HOW TO RUN:
    python3 src/plot_open.py

This will save a PNG image into the charts/ folder.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from data_loader import load_price_data

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHARTS_DIR = PROJECT_ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

N_DAYS_TO_PLOT = 5          # how many recent trading days to show
MINUTES_BEFORE_OPEN = 30    # how far before 8:30 to show
MINUTES_AFTER_OPEN = 60     # how far after 8:30 to show


def plot_open_windows(df: pd.DataFrame, is_synthetic: bool):
    """
    Draws one subplot per recent trading day, each showing the close price
    from 30 minutes before the 8:30 open through 60 minutes after it, with
    a vertical line marking 8:30 exactly.
    """
    # unique calendar dates present in the data, most recent last
    dates = sorted(set(df.index.date))
    recent_dates = dates[-N_DAYS_TO_PLOT:]

    fig, axes = plt.subplots(len(recent_dates), 1, figsize=(10, 3 * len(recent_dates)), sharex=False)
    if len(recent_dates) == 1:
        axes = [axes]

    for ax, day in zip(axes, recent_dates):
        day_df = df[df.index.date == day]

        open_ts = pd.Timestamp(day, tz=df.index.tz).replace(hour=8, minute=30)
        window_start = open_ts - pd.Timedelta(minutes=MINUTES_BEFORE_OPEN)
        window_end = open_ts + pd.Timedelta(minutes=MINUTES_AFTER_OPEN)
        window_df = day_df[(day_df.index >= window_start) & (day_df.index <= window_end)]

        if window_df.empty:
            continue

        ax.plot(window_df.index, window_df["Close"], color="#2f6fed", linewidth=1.2)
        ax.axvline(open_ts, color="#d64545", linestyle="--", linewidth=1, label="8:30 AM NY open")
        ax.set_title(str(day))
        ax.set_ylabel("Price")
        ax.legend(loc="upper left", fontsize=8)
        ax.tick_params(axis="x", rotation=30)

    title_suffix = " (SYNTHETIC DATA -- not real prices)" if is_synthetic else ""
    fig.suptitle(f"NQ price around the 8:30 AM NY open{title_suffix}", fontsize=13, y=1.0)
    fig.tight_layout()

    out_path = CHARTS_DIR / "open_window_recent_days.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved chart to: {out_path}")


def main():
    df, is_synthetic = load_price_data(context="plot_open.py")
    if is_synthetic:
        print("NOTE: plotting SYNTHETIC data -- this is for testing the pipeline only.")
    plot_open_windows(df, is_synthetic)


if __name__ == "__main__":
    main()

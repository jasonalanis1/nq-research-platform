"""
plot_setup_example.py
=======================

Draws a few real example days showing the Opening Range Breakout setup
detected by detect_setups.py: the range box, the breakout point, the stop,
and the target -- so you can SEE what the numbers in setups_orb.csv
actually mean on a chart, not just read them as a table.

HOW TO RUN:
    python3 src/plot_setup_example.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from data_loader import load_price_data
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHARTS_DIR = PROJECT_ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

N_EXAMPLES = 4
BLUE = "#2a78d6"
GRAY = "#8a8a86"
AQUA = "#1baf7a"   # long / target
RED = "#e34948"    # short / stop


def main():
    price_df, is_synthetic = load_price_data(context="plot_setup_example.py")
    signals_df = pd.read_csv(DATA_DIR / "setups_orb.csv", parse_dates=["date", "breakout_time"])

    if signals_df.empty:
        print("No signals in setups_orb.csv -- run detect_setups.py first.")
        return

    # Take a spread of examples: first two long signals and first two short
    # signals we can find, so we see both directions.
    longs = signals_df[signals_df["direction"] == "long"].head(2)
    shorts = signals_df[signals_df["direction"] == "short"].head(2)
    examples = pd.concat([longs, shorts]).head(N_EXAMPLES)

    fig, axes = plt.subplots(len(examples), 1, figsize=(9, 3.2 * len(examples)))
    if len(examples) == 1:
        axes = [axes]

    for ax, (_, sig) in zip(axes, examples.iterrows()):
        day = sig["date"].date()
        day_df = price_df[price_df.index.date == day]
        tz = day_df.index.tz
        open_ts = pd.Timestamp(day, tz=tz).replace(hour=8, minute=30)
        window_start = open_ts - pd.Timedelta(minutes=15)
        window_end = open_ts + pd.Timedelta(minutes=90)
        plot_df = day_df[(day_df.index >= window_start) & (day_df.index <= window_end)]

        ax.plot(plot_df.index, plot_df["Close"], color=BLUE, linewidth=1.3)
        ax.axhspan(sig["range_low"], sig["range_high"], color=GRAY, alpha=0.15)
        ax.axvline(open_ts, color=GRAY, linewidth=1, linestyle=":")

        signal_color = AQUA if sig["direction"] == "long" else RED
        ax.axhline(sig["target"], color=AQUA, linewidth=1, linestyle="--")
        ax.axhline(sig["stop"], color=RED, linewidth=1, linestyle="--")
        ax.scatter([sig["breakout_time"]], [sig["entry"]], color=signal_color, zorder=5, s=40)
        ax.annotate(f"{sig['direction'].upper()} entry {sig['entry']}", xy=(sig["breakout_time"], sig["entry"]),
                    xytext=(10, 10), textcoords="offset points", color=signal_color, fontsize=9)
        ax.text(plot_df.index[-1], sig["target"], "target", color=AQUA, fontsize=8, va="bottom", ha="right")
        ax.text(plot_df.index[-1], sig["stop"], "stop", color=RED, fontsize=8, va="top", ha="right")

        ax.set_title(f"{day}  —  Opening Range Breakout ({sig['direction']})", fontsize=10, loc="left")
        ax.set_xticks([])

    title_suffix = " (SYNTHETIC DATA)" if is_synthetic else ""
    fig.suptitle(f"Opening Range Breakout — example detected signals{title_suffix}", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    out_path = CHARTS_DIR / "orb_examples.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()

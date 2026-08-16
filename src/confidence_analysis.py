"""
confidence_analysis.py
========================
Answers a different question than backtest.py/score_results.py: not "what
happened in this one specific backtest" but "how much should we trust
that result, and what's a realistic RANGE of outcomes we might see if we
kept trading this way?"

WHY THIS MATTERS (plain language): a single backtest gives you ONE
possible history -- the trades that happened to occur, in the order they
happened to occur. But if the setup has some underlying (say) 40% chance
of winning any given trade, that doesn't mean every 10 trades produces
exactly 4 wins -- sometimes you'd see 2, sometimes 7, purely from
randomness. A single equity curve can look great or terrible just from
which order the wins and losses happened to fall in. This script uses a
standard statistical technique called BOOTSTRAP RESAMPLING to show a
realistic spread of what could plausibly happen, instead of pretending
the one curve we got is the only possible outcome.

HOW BOOTSTRAP RESAMPLING WORKS, IN PLAIN ENGLISH: take the actual list of
trade results (net of costs) we already have. Randomly draw from that
list, WITH replacement (each draw can pick the same trade again), to
build a new simulated sequence of the same length. Do that thousands of
times. Each simulated sequence is an equally-plausible "alternate
history" using the exact same underlying trades, just in different
combinations. Looking at the spread across all of them tells us how much
of our one real result was signal versus how much was luck of the draw.

HOW TO RUN:
    python3 src/confidence_analysis.py
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHARTS_DIR = PROJECT_ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

N_SIMULATIONS = 2000     # how many alternate histories to simulate
RANDOM_SEED = 11          # fixes randomness so results are reproducible

BLUE = "#2a78d6"
GRAY = "#8a8a86"
RED = "#e34948"

DEFAULT_RESULTS_FILE = "backtest_results.csv"


def main():
    results_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS_FILE
    results_path = DATA_DIR / results_filename
    if not results_path.exists():
        print(f"No {results_filename} found -- run backtest.py first.")
        return

    if results_filename == "backtest_results.csv":
        chart_out_path = CHARTS_DIR / "confidence_fan_chart.png"
    else:
        suffix = results_filename.replace("backtest_results_", "").replace(".csv", "")
        chart_out_path = CHARTS_DIR / f"confidence_fan_chart_{suffix}.png"

    df = pd.read_csv(results_path)
    resolved = df[~df["exit_reason"].str.startswith("unresolved")]
    r_values = resolved["r_multiple_net"].to_numpy()
    n = len(r_values)

    # backtest.py records whether the underlying price data was real or
    # synthetic in an is_synthetic column. Older results files saved before
    # this column existed are treated as unknown rather than guessed at.
    if "is_synthetic" in df.columns and len(df) > 0:
        is_synthetic = bool(df["is_synthetic"].iloc[0])
        data_label = "SYNTHETIC-data-derived" if is_synthetic else "real-data-derived"
    else:
        data_label = "data source unknown -- re-run backtest.py to record it"

    if n < 5:
        print(f"Only {n} resolved trades -- not enough to do a meaningful confidence analysis yet.")
        return

    rng = np.random.default_rng(RANDOM_SEED)

    # --- Simulation 1: reshuffle the SAME trades (sequence risk) ---
    # Same underlying trades, different possible orderings/combinations --
    # shows how much of the equity curve's shape (especially drawdown) was
    # just the luck of which order things happened to occur in.
    reshuffled_finals = []
    reshuffled_drawdowns = []
    for _ in range(N_SIMULATIONS):
        sample = rng.choice(r_values, size=n, replace=True)
        cum = np.cumsum(sample)
        running_max = np.maximum.accumulate(cum)
        drawdown = (cum - running_max).min()
        reshuffled_finals.append(cum[-1])
        reshuffled_drawdowns.append(drawdown)
    reshuffled_finals = np.array(reshuffled_finals)
    reshuffled_drawdowns = np.array(reshuffled_drawdowns)

    # --- Simulation 2: project forward N_FUTURE more trades ---
    # Assumes the same underlying distribution of outcomes continues --
    # a real assumption worth questioning, not a guarantee -- and shows a
    # realistic spread of where you could plausibly be after that many
    # more trades, instead of one single-line prediction.
    n_future = max(n, 100)
    fan_paths = np.zeros((N_SIMULATIONS, n_future))
    for i in range(N_SIMULATIONS):
        sample = rng.choice(r_values, size=n_future, replace=True)
        fan_paths[i] = np.cumsum(sample)
    final_after_future = fan_paths[:, -1]

    def pct(arr, p):
        return np.percentile(arr, p)

    print("=" * 60)
    print(f"CONFIDENCE ANALYSIS -- based on {n} resolved trades (net of estimated costs)")
    print("=" * 60)
    print(f"\nReshuffling the SAME {n} trades {N_SIMULATIONS} times (sequence-risk check):")
    print(f"  Final cumulative R:  5th pct {pct(reshuffled_finals, 5):+.2f}R"
          f"   median {pct(reshuffled_finals, 50):+.2f}R"
          f"   95th pct {pct(reshuffled_finals, 95):+.2f}R")
    print(f"  Max drawdown seen:   5th pct {pct(reshuffled_drawdowns, 5):.2f}R"
          f"   median {pct(reshuffled_drawdowns, 50):.2f}R"
          f"   95th pct {pct(reshuffled_drawdowns, 95):.2f}R (this is the WORST-case tail)")

    print(f"\nProjecting {n_future} FUTURE trades forward (assumes the same distribution holds --"
          f" a real assumption, not a guarantee):")
    print(f"  Cumulative R after {n_future} trades:  5th pct {pct(final_after_future, 5):+.1f}R"
          f"   median {pct(final_after_future, 50):+.1f}R"
          f"   95th pct {pct(final_after_future, 95):+.1f}R")
    pct_profitable = (final_after_future > 0).mean()
    print(f"  Share of simulations that end up net profitable: {pct_profitable:.1%}")
    print("=" * 60)
    print("\nReminder: this describes uncertainty GIVEN the current sample. It cannot fix a small")
    print("sample or a setup with no real edge -- more real trades and out-of-sample testing are")
    print("what actually narrow this range over time, not this script alone.")

    # --- Fan chart of simulated future paths ---
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(1, n_future + 1)
    for p_low, p_high, alpha in [(5, 95, 0.10), (25, 75, 0.20)]:
        lo = np.percentile(fan_paths, p_low, axis=0)
        hi = np.percentile(fan_paths, p_high, axis=0)
        ax.fill_between(x, lo, hi, color=BLUE, alpha=alpha, linewidth=0)
    median_path = np.percentile(fan_paths, 50, axis=0)
    ax.plot(x, median_path, color=BLUE, linewidth=1.8, label="median simulated path")
    ax.axhline(0, color=GRAY, linewidth=1, linestyle="--")
    ax.set_xlabel(f"Trade number (next {n_future} simulated trades)")
    ax.set_ylabel("Cumulative R")
    ax.set_title(f"Simulated range of outcomes ({N_SIMULATIONS} bootstrap runs, {data_label})",
                 fontsize=11, loc="left")
    ax.legend(loc="upper left", fontsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(chart_out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"\nSaved fan chart to: {chart_out_path}")


if __name__ == "__main__":
    main()

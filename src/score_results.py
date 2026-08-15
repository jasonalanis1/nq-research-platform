"""
score_results.py
==================
Stage 4 of the roadmap: turn the raw trade-by-trade results from
backtest.py into the numbers that actually tell you whether a setup has
promise -- not just "did it win or lose" but win rate, average win vs
average loss, expectancy, and an equity curve.

KEY TERMS EXPLAINED (beginner-friendly):

  R-multiple: "R" = how much you risked on a trade (the distance from
  entry to stop). A trade's R-multiple is its profit or loss measured in
  units of that risk. A trade that made twice what it risked is "+2R." A
  trade that lost exactly what it risked (hit the stop) is "-1R." This
  lets us compare trades fairly even if their dollar risk sizes differ.

  Win rate: percent of resolved trades that hit target instead of stop.

  Expectancy: the average R-multiple you'd expect per trade, long run.
  Expectancy = (win_rate * avg_win_R) + (loss_rate * avg_loss_R). This is
  arguably the single most important number here -- a setup can have a
  LOW win rate and still be profitable if its average win is big enough
  relative to its average loss, and vice versa. Expectancy captures that
  trade-off in one number. Positive = the setup made money on average in
  this test; negative = it lost money on average. Being positive on a
  small/synthetic sample is NOT proof of a real edge -- it just means
  this specific test batch came out ahead.

  Profit factor: total points won divided by total points lost. Above 1
  means more was won than lost; below 1 means the opposite.

  Max drawdown: the largest peak-to-trough dip in the running total of
  R-multiples over time -- i.e. the worst losing stretch in this test.
  Useful for gut-checking whether you could stomach the ride.

HOW TO RUN:
    python3 src/score_results.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHARTS_DIR = PROJECT_ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

BLUE = "#2a78d6"
RED = "#e34948"
GRAY = "#8a8a86"


def main():
    results_path = DATA_DIR / "backtest_results.csv"
    if not results_path.exists():
        print("No backtest_results.csv found -- run backtest.py first.")
        return

    df = pd.read_csv(results_path, parse_dates=["date", "exit_time"])
    resolved = df[~df["exit_reason"].str.startswith("unresolved")].copy()
    unresolved_count = len(df) - len(resolved)

    if resolved.empty:
        print("No resolved trades to score yet (all were unresolved -- likely a data-window issue).")
        return

    wins = resolved[resolved["r_multiple"] > 0]
    losses = resolved[resolved["r_multiple"] <= 0]

    win_rate = len(wins) / len(resolved)
    loss_rate = 1 - win_rate
    avg_win_r = wins["r_multiple"].mean() if len(wins) else 0.0
    avg_loss_r = losses["r_multiple"].mean() if len(losses) else 0.0
    expectancy_r = win_rate * avg_win_r + loss_rate * avg_loss_r

    gross_win_points = wins["pnl_points"].sum()
    gross_loss_points = abs(losses["pnl_points"].sum())
    profit_factor = (gross_win_points / gross_loss_points) if gross_loss_points else float("inf")

    # Equity curve: running total of R-multiples, in trade order.
    resolved = resolved.sort_values("date")
    resolved["cumulative_r"] = resolved["r_multiple"].cumsum()
    running_max = resolved["cumulative_r"].cummax()
    drawdown = resolved["cumulative_r"] - running_max
    max_drawdown_r = drawdown.min()

    print("=" * 60)
    print("SCORECARD (synthetic data -- pipeline test, not a real result)")
    print("=" * 60)
    print(f"Resolved trades:      {len(resolved)}   (unresolved/excluded: {unresolved_count})")
    print(f"Win rate:             {win_rate:.1%}")
    print(f"Average win:          +{avg_win_r:.2f}R")
    print(f"Average loss:         {avg_loss_r:.2f}R")
    print(f"Expectancy per trade: {expectancy_r:+.3f}R")
    print(f"Profit factor:        {profit_factor:.2f}")
    print(f"Max drawdown:         {max_drawdown_r:.2f}R")
    print(f"Total R (sum):        {resolved['r_multiple'].sum():+.2f}R")
    print("=" * 60)

    # --- Equity curve chart ---
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(range(1, len(resolved) + 1), resolved["cumulative_r"], color=BLUE, linewidth=1.8)
    ax.axhline(0, color=GRAY, linewidth=1, linestyle="--")
    ax.fill_between(range(1, len(resolved) + 1), resolved["cumulative_r"], 0,
                     where=(resolved["cumulative_r"] >= 0), color=BLUE, alpha=0.08)
    ax.fill_between(range(1, len(resolved) + 1), resolved["cumulative_r"], 0,
                     where=(resolved["cumulative_r"] < 0), color=RED, alpha=0.08)
    ax.set_xlabel("Trade number (in date order)")
    ax.set_ylabel("Cumulative R")
    ax.set_title("Equity curve — cumulative R-multiple per trade (SYNTHETIC DATA)", fontsize=11, loc="left")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    out_path = CHARTS_DIR / "equity_curve.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"\nSaved equity curve chart to: {out_path}")


if __name__ == "__main__":
    main()

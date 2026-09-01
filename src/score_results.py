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

  Confidence interval (added 2026-08-16): a small sample can make a
  setup look better or worse than it really is, purely by chance -- flip
  a fair coin 10 times and getting 7 heads (70%!) isn't rare. The
  confidence interval below is a rough range for where the TRUE win rate
  probably falls, given how many trades we actually have. A narrow range
  means we have enough trades to trust the number; a wide range means
  "we don't really know yet, we need more trades." This uses everything
  from backtest.py's NET (cost-adjusted) numbers, not the optimistic
  gross ones, since net is what you'd actually keep.

HOW TO RUN:
    python3 src/score_results.py
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHARTS_DIR = PROJECT_ROOT / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

BLUE = "#2a78d6"
RED = "#e34948"
GRAY = "#8a8a86"

# Works with any setup's backtest results now -- run as
# `python3 src/score_results.py backtest_results_level_sweep.csv` for a
# different setup. Defaults to the original ORB results.
DEFAULT_RESULTS_FILE = "backtest_results.csv"


def main():
    results_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RESULTS_FILE
    results_path = DATA_DIR / results_filename
    if not results_path.exists():
        print(f"No {results_filename} found -- run backtest.py first.")
        return

    # Chart filename mirrors the input, same convention as backtest.py.
    if results_filename == "backtest_results.csv":
        chart_out_path = CHARTS_DIR / "equity_curve.png"
    else:
        suffix = results_filename.replace("backtest_results_", "").replace(".csv", "")
        chart_out_path = CHARTS_DIR / f"equity_curve_{suffix}.png"

    df = pd.read_csv(results_path, parse_dates=["date", "exit_time"])
    resolved = df[~df["exit_reason"].str.startswith("unresolved")].copy()
    unresolved_count = len(df) - len(resolved)

    # backtest.py records whether the underlying price data was real or
    # synthetic in an is_synthetic column. Older results files saved before
    # this column existed are treated as unknown rather than guessed at.
    if "is_synthetic" in df.columns and len(df) > 0:
        is_synthetic = bool(df["is_synthetic"].iloc[0])
        data_label = "SYNTHETIC DATA -- pipeline test, not a real result" if is_synthetic \
            else "real data"
    else:
        data_label = "data source unknown -- re-run backtest.py to record it"

    if resolved.empty:
        print("No resolved trades to score yet (all were unresolved -- likely a data-window issue).")
        return

    wins = resolved[resolved["r_multiple_net"] > 0]
    losses = resolved[resolved["r_multiple_net"] <= 0]
    n = len(resolved)

    win_rate = len(wins) / n
    loss_rate = 1 - win_rate
    avg_win_r = wins["r_multiple_net"].mean() if len(wins) else 0.0
    avg_loss_r = losses["r_multiple_net"].mean() if len(losses) else 0.0
    expectancy_r = win_rate * avg_win_r + loss_rate * avg_loss_r

    win_points = wins["pnl_points_net"].sum()
    loss_points = abs(losses["pnl_points_net"].sum())
    profit_factor = (win_points / loss_points) if loss_points else float("inf")

    # R-normalized profit factor (added 2026-09-01, per docs/BACKLOG.md's
    # "score_results.py's profit_factor unit mismatch" item, found while
    # reviewing exp-025): the profit_factor above sums raw price POINTS,
    # with no per-trade risk normalization. That can diverge from -- and
    # even contradict the sign of -- R-based expectancy whenever winning
    # and losing trades carry systematically different risk sizes (a
    # setup with variable per-trade stop distances). This version sums
    # R-MULTIPLES instead, so it can never disagree with expectancy about
    # which side of breakeven a result is on. Both are printed below;
    # neither replaces the other -- they answer different questions
    # (points actually made/lost vs. risk-adjusted edge).
    win_r_total = wins["r_multiple_net"].sum()
    loss_r_total = abs(losses["r_multiple_net"].sum())
    profit_factor_r = (win_r_total / loss_r_total) if loss_r_total else float("inf")

    # --- Confidence interval on the win rate (normal approximation) ---
    # Standard error of a proportion: sqrt(p*(1-p)/n). 1.96x that gives a
    # rough 95% confidence interval -- "we're 95% confident the TRUE win
    # rate is somewhere in this range," not "the win rate IS this range."
    # This approximation gets shaky below ~30 trades, so we say so plainly.
    se = (win_rate * (1 - win_rate) / n) ** 0.5 if n > 0 else float("nan")
    ci_low = max(0.0, win_rate - 1.96 * se)
    ci_high = min(1.0, win_rate + 1.96 * se)

    # Equity curve: running total of NET R-multiples, in trade order.
    resolved = resolved.sort_values("date")
    resolved["cumulative_r"] = resolved["r_multiple_net"].cumsum()
    running_max = resolved["cumulative_r"].cummax()
    drawdown = resolved["cumulative_r"] - running_max
    max_drawdown_r = drawdown.min()

    print("=" * 60)
    print(f"SCORECARD -- NET of estimated costs ({data_label})")
    print("=" * 60)
    print(f"Resolved trades:      {n}   (unresolved/excluded: {unresolved_count})")
    print(f"Win rate:             {win_rate:.1%}   (rough 95% confidence range: {ci_low:.1%} - {ci_high:.1%})")
    if n < 30:
        print("  ^ fewer than 30 trades -- treat this range as very approximate, not reliable yet.")
    print(f"Average win:          +{avg_win_r:.2f}R")
    print(f"Average loss:         {avg_loss_r:.2f}R")
    print(f"Expectancy per trade: {expectancy_r:+.3f}R")
    print(f"Profit factor:        {profit_factor:.2f}   (raw price points, not risk-normalized)")
    print(f"Profit factor (R):    {profit_factor_r:.2f}   (R-multiple-normalized -- prefer this one; see docs/BACKLOG.md)")
    print(f"Max drawdown:         {max_drawdown_r:.2f}R")
    print(f"Total R (sum):        {resolved['r_multiple_net'].sum():+.2f}R")
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
    ax.set_ylabel("Cumulative R (net of estimated costs)")
    ax.set_title(f"Equity curve — cumulative R-multiple per trade, net of costs ({data_label})",
                 fontsize=11, loc="left")
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    fig.savefig(chart_out_path, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"\nSaved equity curve chart to: {chart_out_path}")


if __name__ == "__main__":
    main()

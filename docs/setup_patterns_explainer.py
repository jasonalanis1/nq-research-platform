"""
setup_patterns_explainer.py
=============================
Generates a single educational image explaining four common "setups"
traders watch for around a market open. This is NOT price data -- it's a
hand-drawn idealized sketch of each pattern's shape, purely to help build
visual intuition before we write detection code for whichever one Jason
picks.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "charts" / "setup_patterns_explainer.png"

# Colors (from the project's validated palette)
BLUE = "#2a78d6"     # price line
GRAY = "#8a8a86"      # range / reference lines
ORANGE = "#eb6834"    # gap / annotation
AQUA = "#1baf7a"      # bullish / continuation signal
RED = "#e34948"       # bearish / reversal / failure signal
INK = "#0b0b0b"
MUTED = "#52514e"


def smooth(x_pts, y_pts, n=200):
    """Simple helper: turns a few hand-placed waypoints into a smooth-ish
    line by linear interpolation with a little noise, so it reads as a
    price line rather than a ruler-straight sketch."""
    x_pts = np.array(x_pts, dtype=float)
    y_pts = np.array(y_pts, dtype=float)
    xs = np.linspace(x_pts.min(), x_pts.max(), n)
    ys = np.interp(xs, x_pts, y_pts)
    rng = np.random.default_rng(7)
    ys = ys + rng.normal(0, 0.35, size=n)
    # keep endpoints anchored
    ys[0], ys[-1] = y_pts[0], y_pts[-1]
    return xs, ys


fig, axes = plt.subplots(2, 2, figsize=(11, 9))
fig.suptitle("Four common \"setups\" traders watch for at the open (idealized sketches, not real data)",
             fontsize=12, color=INK, y=0.99)

OPEN_X = 5  # the 8:30 open, on an arbitrary 0-10 x-axis per panel

# ---------------------------------------------------------------------
# 1) Range breakout
# ---------------------------------------------------------------------
ax = axes[0, 0]
x, y = smooth([0, 1, 2, 3, 4, 4.8, 5, 5.5, 6, 7, 8, 9, 10],
              [0, 0.3, -0.2, 0.2, -0.1, 0.1, 0.2, 1.5, 3, 4.2, 5, 5.6, 6])
ax.plot(x, y, color=BLUE, linewidth=2)
ax.axhspan(-0.4, 0.4, color=GRAY, alpha=0.15)
ax.axhline(0.4, color=GRAY, linewidth=1, linestyle="--")
ax.axhline(-0.4, color=GRAY, linewidth=1, linestyle="--")
ax.axvline(OPEN_X, color=MUTED, linewidth=1, linestyle=":")
ax.annotate("pre-open range", xy=(1, 0.4), xytext=(0.2, 2.2), color=MUTED, fontsize=9)
ax.annotate("breaks above the range\nwith conviction → go with it",
            xy=(5.8, 1.8), xytext=(5.6, -1.8), color=AQUA, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=AQUA))
ax.set_title("1. Range Breakout", fontsize=11, color=INK, loc="left")
ax.text(OPEN_X, ax.get_ylim()[1]*0.92, "8:30", color=MUTED, fontsize=8, ha="center")

# ---------------------------------------------------------------------
# 2) Failed break / reversal
# ---------------------------------------------------------------------
ax = axes[0, 1]
x, y = smooth([0, 1, 2, 3, 4, 4.8, 5, 5.4, 5.8, 6.3, 7, 8, 9, 10],
              [0, 0.3, -0.2, 0.2, -0.1, 0.1, 0.2, 1.4, 1.8, 0.3, -1.2, -2.6, -3.4, -3.8])
ax.plot(x, y, color=BLUE, linewidth=2)
ax.axhspan(-0.4, 0.4, color=GRAY, alpha=0.15)
ax.axhline(0.4, color=GRAY, linewidth=1, linestyle="--")
ax.axhline(-0.4, color=GRAY, linewidth=1, linestyle="--")
ax.axvline(OPEN_X, color=MUTED, linewidth=1, linestyle=":")
ax.annotate("breaks out...", xy=(5.8, 1.8), xytext=(4.6, 2.4), color=MUTED, fontsize=9)
ax.annotate("...then snaps back and\nreverses hard → fade the fakeout",
            xy=(6.3, 0.3), xytext=(6.0, -3.2), color=RED, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=RED))
ax.set_title("2. Failed Break / Reversal", fontsize=11, color=INK, loc="left")
ax.text(OPEN_X, ax.get_ylim()[1]*0.85, "8:30", color=MUTED, fontsize=8, ha="center")

# ---------------------------------------------------------------------
# 3) Gap fill
# ---------------------------------------------------------------------
ax = axes[1, 0]
x, y = smooth([0, 1, 2, 3, 4, 4.9, 5, 5.5, 6.5, 7.5, 8.5, 9.5, 10],
              [0, 0.2, -0.1, 0.1, 0, 0, 3.2, 3.1, 2.4, 1.5, 0.6, 0.05, 0])
ax.plot(x, y, color=BLUE, linewidth=2)
ax.axhline(0, color=GRAY, linewidth=1, linestyle="--")
ax.annotate("prior reference level\n(e.g. yesterday's close)", xy=(1, 0), xytext=(0.1, -1.6),
            color=MUTED, fontsize=9)
ax.axvline(OPEN_X, color=MUTED, linewidth=1, linestyle=":")
ax.annotate("gap up at the open", xy=(5, 3.2), xytext=(5.2, 4.0), color=ORANGE, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=ORANGE))
ax.annotate("drifts back to \"fill\" the\ngap → trade the fill",
            xy=(9.3, 0.2), xytext=(6.8, -1.6), color=ORANGE, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=ORANGE))
ax.set_title("3. Gap Fill", fontsize=11, color=INK, loc="left")
ax.text(OPEN_X, ax.get_ylim()[1]*0.9, "8:30", color=MUTED, fontsize=8, ha="center")

# ---------------------------------------------------------------------
# 4) Opening drive
# ---------------------------------------------------------------------
ax = axes[1, 1]
x, y = smooth([0, 1, 2, 3, 4, 4.9, 5, 6, 7, 8, 9, 10],
              [0, 0.2, -0.1, 0.1, 0, 0, 0.3, 1.8, 3.2, 4.4, 5.3, 6])
ax.plot(x, y, color=BLUE, linewidth=2)
ax.axvline(OPEN_X, color=MUTED, linewidth=1, linestyle=":")
ax.annotate("strong, decisive move right\nfrom the open, barely any\npullback → ride the momentum",
            xy=(7, 3.2), xytext=(5.6, -0.5), color=AQUA, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=AQUA))
ax.set_title("4. Opening Drive", fontsize=11, color=INK, loc="left")
ax.text(OPEN_X, ax.get_ylim()[1]*0.9, "8:30", color=MUTED, fontsize=8, ha="center")

for ax in axes.flat:
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRAY)

fig.tight_layout(rect=[0, 0, 1, 0.96])
OUT_PATH.parent.mkdir(exist_ok=True)
fig.savefig(OUT_PATH, dpi=150, bbox_inches="tight", facecolor="white")
print(f"Saved to {OUT_PATH}")

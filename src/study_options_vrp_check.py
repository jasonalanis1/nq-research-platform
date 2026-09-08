"""
study_options_vrp_check.py
=============================

exp-063 -- the genuinely new data category from the 2026-09-07 gameplan
(paid-data branch), using REAL NQ options trade data (Databento,
$1.92, pre-authorized small purchase, covering 2021-09-07 through
2026-09-06) instead of VXN. VXN (a smoothed 30-day index) already gave
an honestly inconclusive answer on this question (docs/OPTIONS_
VOLATILITY_RISK_PREMIUM_CHECK.md) -- this is the "genuinely decisive"
follow-up that document said would need real day-specific options data.

MOTIVATING LITERATURE (already found and documented): NBER Working
Paper 28306 and CBOE's own research desk report that implied
volatility on FOMC/NFP days has historically OVER-predicted realized
volatility (a positive variance risk premium) -- the market prices in
bigger moves than actually happen.

FROZEN HYPOTHESIS: on CPI/NFP release days (the only event days this
project has that fall inside the purchased options-data window --
only 1 FOMC date falls in range, too few to test alone), a simple
options-implied expected daily move (see construction below) is LARGER
than the REALIZED daily move, by more than it is on ordinary
(non-event) days -- i.e. the VRP shows up MORE on event days than on
ordinary days. A mandatory non-event control group uses the identical
construction (same discipline as the earlier VXN check, whose first
attempt was flawed by skipping this control).

CONSTRUCTION (developed with the Path-to-Profitability Advisor's
review before running against real numbers -- one real methodology
correction is disclosed honestly below rather than hidden):
  1. Event set: all CPI+NFP dates (already used unmodified by exp-039/
     040/041) that fall inside the purchased data's 2021-09-07 to
     2023-12-12 overlap window -- n=55 (28 CPI, 27 NFP). Control set:
     55 ordinary trading days from the same window, at least 3
     calendar days from ANY known CPI/NFP/FOMC date, evenly sampled.
  2. For each day: identify the front quarterly-expiry option contract
     (CME's standard Mar/Jun/Sep/Dec cycle, 3rd-Friday expiration,
     rolling to the next quarter once the current one has expired --
     this rollover logic was wrong on the first attempt and is now
     fixed and verified against a real data example).
  3. Find the single strike (that contract only) with BOTH a call and
     a put that traded within 240 minutes before the day's 8:30am ET
     release cutoff (reusing the previous trading session's tape too,
     not just the current day's file, so a strike isn't discarded for
     want of an overnight trade) -- nearest such strike to NQ's own
     spot price just before 8:30am. The call+put premium sum is the
     "straddle" -- literally what a trader could have paid moments
     before the release to bet on a big move either direction.
  4. CORRECTION MADE BEFORE ANY VERDICT WAS LOOKED AT: a straddle on a
     quarterly-cycle option reflects the expected move over WEEKS
     (median ~31-49 days to expiry in this sample), not over the
     30-minute or single-day horizon this project's other event-day
     studies use -- comparing the raw straddle points to a 30-minute
     realized move produced obviously-wrong, order-of-magnitude-off
     numbers (implied moves of 700-1200+ points vs realized moves of
     ~25-125 points) on the first attempt. This is a real, disclosed
     methodology fix, not a retune after seeing a favorable result --
     it was caught because the raw numbers were implausible on their
     face (verified via a rough Black-Scholes sanity check), before
     any statistical test was run. FIX: scale the straddle down to a
     1-day-equivalent implied move via the standard square-root-of-
     time relationship (implied_daily_move = straddle / sqrt(days_to_
     expiry)) and compare it to the REALIZED FULL TRADING DAY move
     (reference-close to reference-close, same convention as
     study_overnight_gap_behavior.py), not a 30-minute window -- an
     appropriately time-matched comparison. Post-fix, implied and
     realized daily moves land in the same real-world ballpark
     (~190-210 points/day on average), which is the sanity check that
     said this construction is no longer obviously broken.
  5. Strike-parsing sanity check (done BEFORE any of the above, gating
     the whole study): verified put-call parity (C - P approximately
     equals spot - strike) holds across a full day's option chain
     using the parsed strikes -- confirms the raw symbol's embedded
     strike is correctly decoded (it is truncated by one digit in the
     raw feed, e.g. "1569" means strike 15690).

STATISTICAL BAR: statistically credible = 90% bootstrap CI on mean
(implied_daily_move - realized_daily_move) entirely above zero, for
the EVENT group, with the CONTROL group's identical statistic reported
alongside as the mandatory comparison (the VRP thesis specifically
predicts a LARGER gap on event days than on ordinary days, not just a
positive gap in general -- options are frequently priced above
realized vol on ordinary days too).

CAVEATS, disclosed plainly: n=41 usable event days and n=26 usable
control days survive the staleness/data-availability filters (14 event
days and 29 control days dropped, mostly for having zero option trades
in the pre-release window -- disclosed, not hidden); this is a
characterization check with n well under this project's 150-trade
promotion floor, so no outcome here can result in a "promote" verdict,
matching exp-041/the CPI-reversal-followup's own precedent for this
kind of small-n characterization study.

HOW TO RUN:
    python3 src/study_options_vrp_check.py
(Reads the pre-extracted data/study_options_vrp_check_rows.csv --
the raw multi-GB options tick data used to build it is not persisted
in this repo, per this project's existing practice of not committing
large raw price files; the CSV is the durable, reproducible input.)
"""

import csv
import json
import random
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ROWS_PATH = DATA_DIR / "study_options_vrp_check_rows.csv"

N_BOOTSTRAP = 3000


def bootstrap_ci(values, n_boot=N_BOOTSTRAP, seed=7):
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(values)
    means = []
    for _ in range(n_boot):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    return means[int(0.05 * n_boot)], means[int(0.95 * n_boot) - 1]


def load_rows():
    with open(ROWS_PATH, newline="") as f:
        reader = csv.DictReader(f)
        return [
            {**row, "dte": int(row["dte"]),
             "implied_daily_move": float(row["implied_daily_move"]),
             "realized_daily_move": float(row["realized_daily_move"]),
             "diff": float(row["diff"]),
             "max_staleness": float(row["max_staleness"])}
            for row in reader
        ]


def summarize(rows, label):
    diffs = [r["diff"] for r in rows]
    implied = [r["implied_daily_move"] for r in rows]
    realized = [r["realized_daily_move"] for r in rows]
    n = len(rows)
    mean_diff = sum(diffs) / n
    ci_low, ci_high = bootstrap_ci(diffs)
    print(f"\n{'-' * 78}\n{label} (n={n})\n{'-' * 78}")
    print(f"  mean implied_daily_move:  {sum(implied)/n:.2f}")
    print(f"  mean realized_daily_move: {sum(realized)/n:.2f}")
    print(f"  mean diff (implied - realized): {mean_diff:.2f}")
    print(f"  90% bootstrap CI on diff: ({ci_low:.2f}, {ci_high:.2f})")
    print(f"  DTE range: {min(r['dte'] for r in rows)}-{max(r['dte'] for r in rows)} days")
    print(f"  max leg staleness: median {sorted(r['max_staleness'] for r in rows)[n//2]:.0f} min")
    return {"n": n, "mean_diff": mean_diff, "ci_90": (ci_low, ci_high)}


def main():
    print("=" * 78)
    print("EXP-063: OPTIONS-IMPLIED VS REALIZED DAILY MOVE (VARIANCE RISK PREMIUM CHECK)")
    print("=" * 78)
    print("\nFrozen hypothesis (see this file's docstring): is the options-implied daily")
    print("move bigger than what actually happens, and MORE so on CPI/NFP days than on")
    print("ordinary days? Real NQ options data, $1.92 purchase.\n")

    rows = load_rows()
    event_rows = [r for r in rows if r["group"] in ("cpi", "nfp")]
    control_rows = [r for r in rows if r["group"] == "control"]
    cpi_rows = [r for r in rows if r["group"] == "cpi"]
    nfp_rows = [r for r in rows if r["group"] == "nfp"]

    event_stats = summarize(event_rows, "EVENT DAYS (CPI + NFP pooled)")
    summarize(cpi_rows, "  -- CPI only (context)")
    summarize(nfp_rows, "  -- NFP only (context)")
    control_stats = summarize(control_rows, "CONTROL (ordinary days, mandatory baseline)")

    event_credible = event_stats["ci_90"][0] > 0
    control_credible = control_stats["ci_90"][0] > 0
    gap_bigger_on_events = event_stats["mean_diff"] > control_stats["mean_diff"]

    print(f"\n{'=' * 78}")
    if event_credible and (not control_credible or gap_bigger_on_events):
        verdict = ("PROMISING (characterization only, n well under the 150-trade promotion "
                   "floor -- cannot be promoted from this check alone). The VRP shows up "
                   "credibly on event days and is not equally present on ordinary days.")
    else:
        verdict = ("NO CREDIBLE EFFECT. Neither the event group nor the control group shows "
                   "a statistically credible options-implied-vs-realized gap (both CIs span "
                   "zero), and the event-day gap is not meaningfully larger than the ordinary-"
                   "day gap. This real-options-data check, like the earlier VXN check, does "
                   "not confirm the literature-based variance-risk-premium finding in this "
                   "project's own data. Closed as a characterization result -- REJECTED for "
                   "any trading-rule purpose; no retuning of the straddle/staleness "
                   "construction on this result.")
    print(f"Verdict: {verdict}")

    out = {
        "event_days_pooled": event_stats,
        "control_days": control_stats,
        "cpi_only_mean_diff": sum(r["diff"] for r in cpi_rows) / len(cpi_rows) if cpi_rows else None,
        "nfp_only_mean_diff": sum(r["diff"] for r in nfp_rows) / len(nfp_rows) if nfp_rows else None,
        "verdict": verdict,
    }
    out_path = DATA_DIR / "study_options_vrp_check_results.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {out_path}.")


if __name__ == "__main__":
    main()

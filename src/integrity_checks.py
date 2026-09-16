"""
integrity_checks.py -- UPGRADE 6: the Integrity Gate's MECHANICAL SUITE.
Frozen spec: research/infrastructure/upgrade-specs-2026-09-13.md (U6), with the
placebo check carried in from U7.

WHAT THIS IS
  Seven structural checks that run on a candidate's own observations BEFORE the
  blind Integrity Gate sees it. ops_checks-style: green/red, no judgment, no
  interpretation, no tuning. The suite does not close anything and does not
  clear anything -- per the spec, "any red is a blocking finding for the Gate,
  not an automatic close." It exists so the Gate's human/blind judgment is spent
  on the parts that need judgment, instead of on defects a machine can find.

  These are the defects the project has ALREADY paid for at least once:
  M9 died of roll-date/short-session contamination; the first idea-factory run
  produced a circular top result; H118's Validation leg turned out not to
  survive its own multiplicity correction. A mechanical suite is what stops the
  next one being found after promotion instead of before.

HONEST ABOUT WHAT IT CANNOT SEE
  Every check reports its own N and returns NOT APPLICABLE or INSUFFICIENT
  rather than a green when the input cannot support it. A green from a check
  that never ran is worse than no check at all -- that is the same rule
  src/execution_measurement.py follows for the 14 execution checks, and the
  reason both files exist before the samples they will eventually judge.

INPUT CONTRACT (deliberately small)
  observations: list of dicts, each {date, value, ...}
      value        the per-observation effect measurement, in whatever unit the
                   candidate registered (R multiple, ATR-normalised range ratio,
                   points -- the suite never converts and never assumes)
      risk_points  optional; required by cost_sensitivity, which cannot run
                   without knowing what a point of cost is worth in `value` units
      overnight / rth
                   optional; required by overnight_intraday_split
  null_value  the CORRECT null for this candidate (U7's `correct_null`): 0.0 for
              a directional R effect, 1.0 for a ratio-to-baseline outcome, or the
              instrument's own unconditional drift over the same horizon. Passing
              the wrong null here is the one thing the suite cannot catch for you.
  population + mask
              optional; the FULL day-set and the boolean selector that picked the
              observations out of it. Only the placebo check needs them, because
              a shifted or inverted signal cannot be built from the selected rows
              alone -- and a placebo that silently "passes" because it could not
              run is exactly the failure this file refuses to produce.

USAGE
    python3 src/integrity_checks.py --occurrences data/<file>.jsonl \\
        --value-field r --risk-field range_width --null 0.0
    python3 src/integrity_checks.py --hyp142      # the vxn HIGH next-day-range series
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# frozen thresholds -- from the U6 spec, never tuned to make a candidate pass
# ---------------------------------------------------------------------------
OVERNIGHT_SHARE_RED = 0.80       # >80% of a session effect in one leg
ROLL_SHARE_RED = 0.05            # >5% of observations on roll/short days
CONCENTRATION_TOP_FRAC = 0.05    # top 5% of observations...
CONCENTRATION_RED = 0.50         # ...contributing >50% of the effect
PLACEBO_COMPARABLE = 0.50        # placebo |effect| >= 50% of the real one
SHIFT_OVERLAP_MAX = 0.50         # above this, the t+1 placebo re-selects the real signal
COST_STRESS = 2.0                # cost_sensitivity re-runs at 2x costs
MIN_N = 30                       # below this a check reports INSUFFICIENT, never green
N_BOOT = 20000                   # matches stack_scan_runner.py
CI = 90                          # matches the project's CI90 convention

# THE COST MODEL LIVES IN src/cost_model.py (Jason's correction, September 16th
# 2026). These constants used to be defined here -- COMMISSION_PER_SIDE_USD =
# 2.50 with CONTRACT_MULTIPLIER = 20.0 -- and paper_book.py imported them and
# applied them to a MICRO contract, which produced the wrong "$6.00 per micro
# round trip = 3.00 index points". $2.50/side is a FULL-SIZE NQ figure. Nothing
# here defines a cost any more; it reads the one module that owns them, with the
# sources cited. cost_sensitivity still stresses the cost by 2x, which is the
# point of the check: does the result survive the assumption being wrong.
import cost_model  # noqa: E402

TICK_SIZE = cost_model.MNQ.tick_size_points
COMMISSION_PER_SIDE_USD = cost_model.MNQ.commission_per_side_usd
FEES_PER_SIDE_USD = cost_model.MNQ.fees_per_side_usd
SLIPPAGE_TICKS_PER_SIDE = cost_model.SLIPPAGE_TICKS_PER_SIDE
CONTRACT_MULTIPLIER = cost_model.MNQ.usd_per_point
# 1x cost of a round trip, in index points, on the decision basis (MNQ, market
# entry and exit) -- 1.30 pt, not the old 3.00 pt.
ROUND_TRIP_COST_POINTS_1X = cost_model.DEFAULT_POINTS_PER_ROUND_TRIP


def _result(name: str, status: str, n: int = 0, **detail) -> dict:
    return {"check": name, "status": status, "n": int(n), **detail}


def bootstrap_ci(values, n_boot: int = N_BOOT, ci: int = CI, seed: int = 0) -> tuple:
    """Percentile bootstrap of the mean. Chunked so a 20k x n draw matrix never
    has to exist at once. Seeded: the same input always gives the same CI, so a
    re-run of the suite can never quietly change a verdict."""
    v = np.asarray([x for x in values if np.isfinite(x)], dtype=float)
    if len(v) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot, dtype=float)
    step = max(1, min(2000, n_boot))
    for i in range(0, n_boot, step):
        k = min(step, n_boot - i)
        idx = rng.integers(0, len(v), size=(k, len(v)))
        means[i:i + k] = v[idx].mean(axis=1)
    lo, hi = (100 - ci) / 2, 100 - (100 - ci) / 2
    return (float(np.percentile(means, lo)), float(np.percentile(means, hi)))


def _credible(lo: float, hi: float, null: float) -> bool:
    """A CI that excludes the null. NaN is never credible."""
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return False
    return (lo > null) or (hi < null)


# ---------------------------------------------------------------------------
# 4. roll-date contamination -- pure, so it is testable without price data
# ---------------------------------------------------------------------------
def quarterly_roll_window(d, days_before: int = 1) -> bool:
    """True when `d` is a CME quarterly ROLL DAY: the third Friday of
    Mar/Jun/Sep/Dec (equity-index expiry) or the day before it (the day volume
    actually rolls to the next contract). This is the M9 defect -- a candidate
    whose occurrences cluster on roll days is measuring the roll, not the market.

    WHY THE DEFINITION IS NARROW, deliberately (fixed 2026-09-14, first run):
    the first implementation flagged the full 8-CALENDAR-DAY window up to
    expiry. That window contains ~32 sessions a year, a ~12.7% calendar base
    rate, so ANY candidate that trades most days lands ~12-13% of its
    observations inside it and trips the spec's 5% threshold every single time.
    A check that reds on normal calendar exposure is not a check; a false red
    costs the Gate exactly as much attention as a false green costs it safety.
    Two days a quarter (~3.2% base rate) is what makes the frozen 5% threshold
    mean "clustered on roll days" instead of "exists"."""
    d = pd.Timestamp(d)
    if d.month not in (3, 6, 9, 12):
        # a roll window can reach back into the previous month only if the
        # third Friday falls on the 15th-21st, which is always in-month.
        return False
    first = pd.Timestamp(year=d.year, month=d.month, day=1)
    # weekday(): Mon=0 .. Fri=4
    first_friday = 1 + ((4 - first.weekday()) % 7)
    third_friday = pd.Timestamp(year=d.year, month=d.month, day=first_friday + 14)
    return (third_friday - pd.Timedelta(days=days_before)) <= d <= third_friday


# ---------------------------------------------------------------------------
# the seven checks
# ---------------------------------------------------------------------------
def check_drift_null(vals, null_value: float, null_label: str) -> dict:
    """1. The effect re-measured against the correct null (the instrument's own
    unconditional drift / range reference over the same horizon), not zero.
    RED if subtracting the correct null flips the effect's sign."""
    if len(vals) < MIN_N:
        return _result("1. drift_null", "INSUFFICIENT", len(vals))
    raw = float(np.mean(vals))
    adj = raw - null_value
    flipped = (raw > 0) != (adj > 0) if null_value != 0 else False
    return _result("1. drift_null", "RED" if flipped else "GREEN", len(vals),
                   raw_mean=round(raw, 6), null_value=null_value, null_label=null_label,
                   effect_vs_null=round(adj, 6),
                   detail="sign flips once the correct null is subtracted" if flipped
                          else "sign survives the correct null")


def check_overnight_intraday_split(obs: list) -> dict:
    """2. The effect decomposed into overnight vs RTH legs. RED if more than 80%
    of a 'session' effect lives in one leg and the registered claim did not say
    so. NOT APPLICABLE when the observations carry no leg decomposition -- an
    intraday trade has no overnight leg, and inventing one would be worse than
    declining to judge."""
    legs = [(o.get("overnight"), o.get("rth")) for o in obs]
    usable = [(a, b) for a, b in legs if a is not None and b is not None
              and np.isfinite(a) and np.isfinite(b)]
    if not usable:
        return _result("2. overnight_intraday_split", "NOT APPLICABLE", 0,
                       detail="observations carry no overnight/rth decomposition "
                              "(e.g. an intraday effect, which has no overnight leg)")
    if len(usable) < MIN_N:
        return _result("2. overnight_intraday_split", "INSUFFICIENT", len(usable))
    on = float(np.mean([a for a, _ in usable]))
    rt = float(np.mean([b for _, b in usable]))
    tot = abs(on) + abs(rt)
    if tot == 0:
        return _result("2. overnight_intraday_split", "INSUFFICIENT", len(usable),
                       detail="both legs are zero")
    share_on = abs(on) / tot
    red = share_on > OVERNIGHT_SHARE_RED or (1 - share_on) > OVERNIGHT_SHARE_RED
    return _result("2. overnight_intraday_split", "RED" if red else "GREEN", len(usable),
                   overnight_mean=round(on, 6), rth_mean=round(rt, 6),
                   overnight_share=round(share_on, 4),
                   detail=f"{share_on:.0%} of the effect is in the overnight leg "
                          f"(red above {OVERNIGHT_SHARE_RED:.0%}); the registered claim must say so")


def check_cost_sensitivity(obs: list, vals, null_value: float, seed: int = 0) -> dict:
    """3. Per-trade effects re-run at 2x the cost assumption. RED if the CI
    crosses the null under 2x costs. NOT APPLICABLE without a per-observation
    risk size -- a cost in points cannot be expressed in the candidate's own
    units without one, and assuming a risk size would be fabricating data."""
    risks = [o.get("risk_points") for o in obs]
    usable = [(v, r) for v, r in zip(vals, risks)
              if r is not None and np.isfinite(r) and r > 0 and np.isfinite(v)]
    if not usable:
        return _result("3. cost_sensitivity", "NOT APPLICABLE", 0,
                       detail="no per-observation risk_points, so a points cost cannot be "
                              "converted into the candidate's own units (a non-trade outcome, "
                              "e.g. a range ratio, has no round-trip cost at all)")
    if len(usable) < MIN_N:
        return _result("3. cost_sensitivity", "INSUFFICIENT", len(usable))
    cost_pts = ROUND_TRIP_COST_POINTS_1X * COST_STRESS
    stressed = [v - cost_pts / r for v, r in usable]
    lo, hi = bootstrap_ci(stressed, seed=seed)
    crosses = not _credible(lo, hi, null_value)
    mean_1x = float(np.mean([v for v, _ in usable]))
    mean_2x = float(np.mean(stressed))
    # The spec's literal rule is "red if the CI crosses zero under 2x costs".
    # Taken alone that GREENS a candidate whose edge has become credibly
    # NEGATIVE under costs -- its CI does not cross the null, it has moved
    # cleanly to the wrong side of it. Caught by this check's own first test
    # run, 2026-09-14. A sign flip under costs is at least as disqualifying as
    # a CI that widens across the null, so both are red.
    flipped = (mean_1x - null_value > 0) != (mean_2x - null_value > 0)
    red = crosses or flipped
    why = ("CI crosses the null under 2x costs" if crosses else
           "effect FLIPS SIGN under 2x costs (credibly the wrong side of the null)" if flipped
           else "survives 2x costs")
    return _result("3. cost_sensitivity", "RED" if red else "GREEN", len(usable),
                   cost_multiplier=COST_STRESS, round_trip_cost_points=round(cost_pts, 4),
                   mean_1x=round(mean_1x, 6), mean_2x=round(mean_2x, 6),
                   ci90_2x=[round(lo, 6), round(hi, 6)],
                   ci_crosses_null=crosses, sign_flips=flipped, detail=why)


def check_roll_date_contamination(obs: list, vals, null_value: float,
                                   short_session_dates=None, seed: int = 0) -> dict:
    """4. Share of observations on CME quarterly roll days or short/missing-RTH
    sessions -- the M9 defect. RED if that share exceeds 5%, OR if excluding
    them flips the verdict (credible -> not, or a sign change)."""
    if len(vals) < MIN_N:
        return _result("4. roll_date_contamination", "INSUFFICIENT", len(vals))
    short = set(str(d) for d in (short_session_dates or []))
    flags = [bool(quarterly_roll_window(o["date"])) or str(o["date"]) in short for o in obs]
    n_bad = sum(flags)
    share = n_bad / len(flags)
    clean = [v for v, f in zip(vals, flags) if not f]
    lo_a, hi_a = bootstrap_ci(vals, seed=seed)
    verdict_flips = False
    if len(clean) >= MIN_N:
        lo_c, hi_c = bootstrap_ci(clean, seed=seed)
        cred_all, cred_clean = _credible(lo_a, hi_a, null_value), _credible(lo_c, hi_c, null_value)
        sign_flip = (np.mean(vals) - null_value > 0) != (np.mean(clean) - null_value > 0)
        verdict_flips = (cred_all != cred_clean) or sign_flip
        clean_mean = round(float(np.mean(clean)), 6)
    else:
        clean_mean = None
    # the calendar base rate over the SAME span, so the share is readable as
    # excess-vs-exposure rather than as a bare number
    days = pd.date_range(min(pd.Timestamp(o["date"]) for o in obs),
                         max(pd.Timestamp(o["date"]) for o in obs), freq="B")
    base = float(np.mean([quarterly_roll_window(d) for d in days])) if len(days) else float("nan")
    red = share > ROLL_SHARE_RED or verdict_flips
    return _result("4. roll_date_contamination", "RED" if red else "GREEN", len(vals),
                   n_contaminated=n_bad, share=round(share, 4),
                   calendar_base_rate=round(base, 4),
                   mean_all=round(float(np.mean(vals)), 6), mean_excluding=clean_mean,
                   verdict_flips_when_excluded=verdict_flips,
                   detail=f"{share:.1%} of observations on roll/short sessions "
                          f"(calendar base rate {base:.1%}; red above {ROLL_SHARE_RED:.0%})"
                          + ("; excluding them FLIPS the verdict" if verdict_flips else ""))


def check_subperiod_stability(obs: list, vals, null_value: float, seed: int = 0) -> dict:
    """5. Chronological halves. RED if only one half is credible AND the halves
    differ in sign -- i.e. the whole-sample result is carried by one era."""
    if len(vals) < 2 * MIN_N:
        return _result("5. subperiod_stability", "INSUFFICIENT", len(vals))
    order = np.argsort([pd.Timestamp(o["date"]).value for o in obs])
    v = np.asarray(vals, dtype=float)[order]
    mid = len(v) // 2
    a, b = v[:mid], v[mid:]
    lo_a, hi_a = bootstrap_ci(a, seed=seed)
    lo_b, hi_b = bootstrap_ci(b, seed=seed + 1)
    cred_a, cred_b = _credible(lo_a, hi_a, null_value), _credible(lo_b, hi_b, null_value)
    sign_differs = (float(a.mean()) - null_value > 0) != (float(b.mean()) - null_value > 0)
    red = (cred_a != cred_b) and sign_differs
    return _result("5. subperiod_stability", "RED" if red else "GREEN", len(v),
                   first_half={"n": len(a), "mean": round(float(a.mean()), 6),
                               "ci90": [round(lo_a, 6), round(hi_a, 6)], "credible": cred_a},
                   second_half={"n": len(b), "mean": round(float(b.mean()), 6),
                                "ci90": [round(lo_b, 6), round(hi_b, 6)], "credible": cred_b},
                   signs_differ=sign_differs,
                   detail="only one half is credible AND the halves disagree in sign" if red
                          else "halves are not in contradiction")


def check_concentration(vals, null_value: float) -> dict:
    """6. Share of the total effect contributed by the top 5% of observations.
    RED above 50%. Contribution is measured as each observation's departure from
    the null, ranked in the direction the effect actually points, so a result
    carried by a handful of days cannot hide behind an average.

    A share ABOVE 100% is possible and is not a bug: it means the net effect is
    a small residual left over from large offsetting contributions, i.e. the top
    5% carry more than the whole result and the rest of the sample works against
    them. That is a stronger version of the defect this check exists to find,
    not a weaker one."""
    if len(vals) < MIN_N:
        return _result("6. concentration", "INSUFFICIENT", len(vals))
    dep = np.asarray(vals, dtype=float) - null_value
    total = float(dep.sum())
    if total == 0 or not np.isfinite(total):
        return _result("6. concentration", "INSUFFICIENT", len(vals),
                       detail="total departure from the null is zero -- nothing to apportion")
    ordered = np.sort(dep)[::-1] if total > 0 else np.sort(dep)
    k = max(1, int(round(CONCENTRATION_TOP_FRAC * len(ordered))))
    share = float(ordered[:k].sum()) / total
    red = share > CONCENTRATION_RED
    return _result("6. concentration", "RED" if red else "GREEN", len(vals),
                   top_k=k, top_frac=CONCENTRATION_TOP_FRAC, share_of_effect=round(share, 4),
                   detail=f"top {CONCENTRATION_TOP_FRAC:.0%} of observations carry "
                          f"{share:.0%} of the effect (red above {CONCENTRATION_RED:.0%})")


def check_placebo(population=None, mask=None, null_value: float = 0.0,
                  real_effect: float = None, seed: int = 0) -> dict:
    """7. (from U7) Shifted-signal (t+1) and inverted-signal versions. RED if
    either produces an effect at least half the size of the real one.

    Needs the FULL population and the selector mask: a shifted or inverted
    signal cannot be reconstructed from the selected rows alone. Returns NOT
    APPLICABLE rather than a green when they are missing -- a placebo that
    'passes' because it never ran is the single most dangerous green in the
    whole suite."""
    if population is None or mask is None:
        return _result("7. placebo", "NOT APPLICABLE", 0,
                       detail="needs the full population and the selector mask; "
                              "a shifted/inverted signal cannot be built from the selected rows alone")
    pop = np.asarray(population, dtype=float)
    m = np.asarray(mask, dtype=bool)
    if len(pop) != len(m):
        return _result("7. placebo", "INSUFFICIENT", 0, detail="population and mask differ in length")
    if real_effect is None:
        sel = pop[m]
        if len(sel) < MIN_N:
            return _result("7. placebo", "INSUFFICIENT", len(sel))
        real_effect = float(np.nanmean(sel)) - null_value

    shifted_mask = np.roll(m, 1); shifted_mask[0] = False
    out, gating = {}, {}
    # A SHIFTED PLACEBO IS ONLY A PLACEBO IF IT SELECTS DIFFERENT DAYS.
    # For a PERSISTENT state (a volatility tercile, a regime flag) the t+1
    # selection is largely the same sample, so it reproduces the real effect by
    # construction and would red every persistent-state candidate that exists.
    # Measured, not assumed: the overlap is computed below and reported, and the
    # shifted leg stops gating only when it exceeds SHIFT_OVERLAP_MAX. The
    # INVERTED leg -- the one that actually asks whether the direction means
    # anything -- always gates. See the 2026-09-14 note in KNOWLEDGE.md: this is
    # a structural fix for a class of candidate, NOT a threshold loosened to let
    # a particular one through.
    overlap = float(np.mean(m[shifted_mask])) if shifted_mask.sum() else float("nan")
    for label, mm in (("shifted_t+1", shifted_mask), ("inverted", ~m)):
        sub = pop[mm]
        sub = sub[np.isfinite(sub)]
        val = None if len(sub) < MIN_N else round(float(sub.mean()) - null_value, 6)
        out[label] = val
        if label == "shifted_t+1" and np.isfinite(overlap) and overlap > SHIFT_OVERLAP_MAX:
            continue          # reported, but cannot gate -- it is not an independent sample
        if val is not None:
            gating[label] = val
    if not gating:
        return _result("7. placebo", "INSUFFICIENT", int(m.sum()),
                       real_effect=round(real_effect, 6), placebo_effects=out,
                       shifted_overlap_with_real=None if not np.isfinite(overlap) else round(overlap, 4),
                       detail="no placebo leg could gate: the t+1 selection overlaps the real signal "
                              f"{overlap:.0%} (a persistent state), and no other leg reached the floor")
    worst_label = max(gating, key=lambda k: abs(gating[k]))
    worst = abs(gating[worst_label])
    comparable = abs(real_effect) > 0 and worst >= PLACEBO_COMPARABLE * abs(real_effect)
    note = ""
    if np.isfinite(overlap) and overlap > SHIFT_OVERLAP_MAX:
        note = (f" [shifted_t+1 reported but NOT gating: it re-selects {overlap:.0%} of the real "
                f"sample, so it is not an independent placebo for a persistent state]")
    return _result("7. placebo", "RED" if comparable else "GREEN", int(m.sum()),
                   real_effect=round(real_effect, 6), placebo_effects=out,
                   gating_legs=list(gating), threshold_fraction=PLACEBO_COMPARABLE,
                   shifted_overlap_with_real=None if not np.isfinite(overlap) else round(overlap, 4),
                   detail=(f"{worst_label} reaches {gating[worst_label]:.4f} vs the real "
                           f"{real_effect:.4f} (red at {PLACEBO_COMPARABLE:.0%})" if comparable
                           else "no gating placebo comes close to the real effect") + note)


# ---------------------------------------------------------------------------
# the suite
# ---------------------------------------------------------------------------
def run_suite(observations: list, null_value: float = 0.0, null_label: str = "zero",
              population=None, mask=None, short_session_dates=None,
              candidate: str = "unnamed", seed: int = 0) -> dict:
    obs = [o for o in observations if o.get("value") is not None and np.isfinite(o["value"])]
    vals = [float(o["value"]) for o in obs]

    checks = [
        check_drift_null(vals, null_value, null_label),
        check_overnight_intraday_split(obs),
        check_cost_sensitivity(obs, vals, null_value, seed=seed),
        check_roll_date_contamination(obs, vals, null_value, short_session_dates, seed=seed),
        check_subperiod_stability(obs, vals, null_value, seed=seed),
        check_concentration(vals, null_value),
        check_placebo(population, mask, null_value,
                      real_effect=(float(np.mean(vals)) - null_value) if vals else None, seed=seed),
    ]
    reds = [c["check"] for c in checks if c["status"] == "RED"]
    not_run = [c["check"] for c in checks if c["status"] in ("NOT APPLICABLE", "INSUFFICIENT")]
    return {
        "candidate": candidate, "n_observations": len(vals),
        "null_value": null_value, "null_label": null_label,
        "checks": checks, "reds": reds, "any_red": bool(reds), "not_run": not_run,
        "rule": "A RED is a BLOCKING FINDING for the Integrity Gate, not an automatic close "
                "(U6 spec). A check that reports NOT APPLICABLE or INSUFFICIENT has NOT passed -- "
                "it did not run, and the Gate must be told which ones those were.",
        "session_report_row": (f"integrity_checks[{candidate}]: "
                               f"{len(checks) - len(reds) - len(not_run)} green, {len(reds)} red, "
                               f"{len(not_run)} not run (n={len(vals)})"
                               + (f" -- RED: {', '.join(reds)}" if reds else "")),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _load_jsonl(path: Path) -> list:
    return [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]


def _hyp142_series():
    """hyp-000142: vxn_level_vs_trailing HIGH tercile -> next-day RTH range vs the
    trailing-20d average range. Built the same way risk_state_engine.py builds its
    own inputs, on the Discovery slice, so the suite is judging the candidate's
    real series rather than a re-derivation of it."""
    from data_loader import load_price_data
    from data_split import get_discovery_data
    from market_state_primitives import build_state_frame
    from market_state_primitives_v2 import extend_state_frame
    df, synthetic = load_price_data(context="integrity_checks")
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    disc = get_discovery_data(df)
    st = extend_state_frame(build_state_frame(disc), disc)
    idx = pd.to_datetime(pd.Index(st.index))
    rng = pd.Series((st["High"] - st["Low"]).to_numpy(dtype=float), index=idx)
    trail = rng.rolling(20, min_periods=20).mean().shift(1)
    ratio = (rng / trail).shift(-1)          # NEXT day's range vs today's trailing average
    vxn = pd.Series(st["vxn_level_vs_trailing"].to_numpy(dtype=float), index=idx)
    edge = float(np.nanpercentile(vxn.replace([np.inf, -np.inf], np.nan).dropna(), 200 / 3))
    ok = ratio.notna() & vxn.notna() & np.isfinite(ratio) & np.isfinite(vxn)
    ratio, vxn, idx2 = ratio[ok], vxn[ok], idx[ok]
    mask = (vxn >= edge).to_numpy()
    obs = [{"date": str(d.date()), "value": float(v)}
           for d, v, m in zip(idx2, ratio.to_numpy(), mask) if m]
    return obs, ratio.to_numpy(), mask


def main():
    ap = argparse.ArgumentParser(description="U6 mechanical integrity suite")
    ap.add_argument("--occurrences", help="JSONL file, one observation per line")
    ap.add_argument("--value-field", default="r")
    ap.add_argument("--risk-field", default=None)
    ap.add_argument("--null", type=float, default=0.0)
    ap.add_argument("--null-label", default="zero")
    ap.add_argument("--candidate", default=None)
    ap.add_argument("--hyp142", action="store_true", help="run on hyp-000142's daily series")
    ap.add_argument("--out", default=None, help="write the JSON block here")
    a = ap.parse_args()

    if a.hyp142:
        obs, pop, mask = _hyp142_series()
        res = run_suite(obs, null_value=1.0,
                        null_label="unconditional range ratio (1.0 = no change vs trailing average)",
                        population=pop, mask=mask, candidate=a.candidate or "hyp-000142")
    elif a.occurrences:
        raw = _load_jsonl(Path(a.occurrences))
        obs = [{"date": r["date"], "value": r.get(a.value_field),
                "risk_points": r.get(a.risk_field) if a.risk_field else None} for r in raw]
        res = run_suite(obs, null_value=a.null, null_label=a.null_label,
                        candidate=a.candidate or Path(a.occurrences).stem)
    else:
        ap.error("give --occurrences or --hyp142")

    print(json.dumps(res, indent=2, default=str))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2, default=str))
        print(f"\nwritten -> {a.out}")


if __name__ == "__main__":
    main()

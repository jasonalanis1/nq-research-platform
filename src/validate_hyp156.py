"""
validate_hyp156.py -- the ONE-SHOT Validation test for hyp-000156 (M23: the London
open volatility burst in 6E), written and frozen BEFORE the Validation data exists.

Why this file exists in this form: the blind Integrity Gate (2026-09-13) ruled
CONDITIONAL and one of its five conditions was BLOCKING-but-curable -- "the Validation
script does not exist, and cannot be 'Scan 030 with the loader swapped', because Scan 030
computes neither the paired diff nor a Sidak CI." So the script is written now, its
sha256 is recorded in research/studies/hyp156-validation-spec-frozen.md, and running it
is mechanical. If this file changes, the spec's recorded hash stops matching and the run
is not the pre-registered test any more.

THE ONE TEST (Gate condition 1 -- paired vs unpaired, resolved):
  PAIRED, per day. For each Validation session d:
      x_d = |ret(London hour, d)| / ATR14_d  -  mean over the 6 US-RTH hourly bins of
                                                |ret(bin, d)| / ATR14_d
  and the gating statistic is the mean of x_d across days, with a block bootstrap CI.
  This is the Statistical stage's construction, not Scan 030's unpaired pooled-mean
  difference. It is chosen because it was the construction the candidate was PROMOTED on;
  switching to the unpaired version now would be choosing a test after seeing Discovery
  results. The paired form is also the more conservative of the two: it removes each day's
  own volatility level before comparing.

THE NULL, NAMED HONESTLY (Gate condition 1, second half):
  The baseline is the **US-RTH hourly baseline** (09:30-16:00 ET, six one-hour bins), NOT
  a 24-hour baseline, and it is labelled that way everywhere. 6E trades nearly 24 hours;
  US RTH is its high-activity stretch, so this baseline is deliberately HARD to beat. The
  mechanism doc's Section 4 said "every hourly window across the 24-hour session"; that
  wording is superseded here, in writing, before the test -- not silently after it.

MULTIPLICITY (Gate condition 3):
  SIDAK_N = max(20, N_validation_at_run). Frozen as a rule, not a number, so it cannot
  drift downward. N_BOOT = 20000, because at the adjusted tail the 3000 draws Scan 030
  used would put ~8 draws in the region that decides the answer.

DST (Gate condition 3):
  The GATING window is 03:00-04:00 ET, identical to Discovery, because the test must be
  the same test. For roughly three weeks a year (the US/UK clock-change mismatch) London
  opens at 04:00 ET instead, so two NON-GATING diagnostics are pre-registered: the same
  statistic on the DST-aware window (08:00-09:00 Europe/London), and the gating statistic
  restricted to days where the two coincide.

ATR WARM-UP (Gate condition 3):
  ATR14 is a trailing 14-session mean of the 09:30-16:00 range, shifted one session. The
  first 14 Validation days take their warm-up from the DISCOVERY TAIL -- the series is
  built on the concatenated frame and only then restricted to Validation dates. No day is
  scored on a partial ATR, and no day is dropped for it.

PROVENANCE / ROLL PARITY (Gate condition 3):
  The Validation file must come from the same vendor, dataset and continuous-contract roll
  rule as the Discovery file. The script asserts this from the file metadata and REFUSES to
  run on a mismatch rather than reporting a number that is not comparable.

KILL DIAGNOSTICS (Gate condition 5) -- pre-registered, NON-GATING:
  (a) bar density: distinct minutes carrying a bar inside the window, per day;
  (b) first-5-minute share of the window's realized variance.
  Both are reported always. Neither can flip the verdict; they exist so a PASS driven by a
  data artifact is visible rather than invisible.

ORIGIN FIELD (Gate condition 4): the ledger's `strategy_origin: data_discovered` is this
project's convention for "surfaced by a scan of data we already had", as opposed to
`literature` or `operator_proposed`. It is NOT a confession of fishing: the mechanism doc
and the map entry predate Scan 030. The convention is stated here and in the packet.
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

GATING_WINDOW_ET = ("03:00", "04:00")
PRE_WINDOW_ET = ("02:00", "03:00")           # reported, never gating
LONDON_LOCAL_WINDOW = ("08:00", "09:00")     # DST-aware diagnostic, never gating
RTH_BINS = [("09:30", "10:30"), ("10:30", "11:30"), ("11:30", "12:30"),
            ("12:30", "13:30"), ("13:30", "14:30"), ("14:30", "15:30")]
ATR_WINDOW = 14
BLOCK = 10
N_BOOT = 20000
SEED = 20260913
SIDAK_FLOOR_N = 20
ALPHA = 0.10


def _hour_abs_return(day: pd.DataFrame, start: str, end: str) -> float:
    w = day.between_time(start, end, inclusive="left")
    if w.empty:
        return np.nan
    return abs(float(w["Close"].iloc[-1]) - float(w["Open"].iloc[0]))


def atr14(df: pd.DataFrame) -> pd.Series:
    """Trailing 14-session mean of the RTH range, shifted one session. Built on the
    WHOLE frame so Validation's first days warm up from the Discovery tail."""
    rth = df.between_time("09:30", "16:00", inclusive="left")
    rng = rth.groupby(rth.index.normalize()).apply(lambda g: float(g["High"].max() - g["Low"].min()))
    return rng.rolling(ATR_WINDOW).mean().shift(1)


def per_day_paired_diff(df: pd.DataFrame, atr: pd.Series, window=GATING_WINDOW_ET) -> pd.Series:
    out = {}
    for day, g in df.groupby(df.index.normalize()):
        a = float(atr.get(day, np.nan))
        if not np.isfinite(a) or a <= 0:
            continue
        w = _hour_abs_return(g, *window)
        if not np.isfinite(w):
            continue
        base = [_hour_abs_return(g, s, e) for s, e in RTH_BINS]
        base = [b for b in base if np.isfinite(b)]
        if len(base) < len(RTH_BINS):
            continue
        out[day] = (w / a) - float(np.mean(base) / a)
    return pd.Series(out, dtype=float)


def block_bootstrap_ci(x: np.ndarray, alpha: float = ALPHA, n_boot: int = N_BOOT,
                       block: int = BLOCK, seed: int = SEED) -> tuple:
    rng = np.random.default_rng(seed)
    n = x.size
    nb = int(np.ceil(n / block))
    means = np.empty(n_boot)
    for i in range(n_boot):
        starts = rng.integers(0, max(1, n - block + 1), nb)
        s = np.concatenate([x[st:st + block] for st in starts])[:n]
        means[i] = s.mean()
    return float(np.percentile(means, 100 * alpha / 2)), float(np.percentile(means, 100 * (1 - alpha / 2)))


def sidak_ci(mean: float, ci: tuple, n_trials: int) -> tuple:
    import project_wide_multiplicity as pwm
    se = (ci[1] - ci[0]) / (2 * 1.6449)
    z = pwm.sidak_z(max(SIDAK_FLOOR_N, int(n_trials)))
    return round(mean - z * se, 5), round(mean + z * se, 5)


def diagnostics(df: pd.DataFrame, window=GATING_WINDOW_ET) -> dict:
    dens, shares = [], []
    for _, g in df.groupby(df.index.normalize()):
        w = g.between_time(*window, inclusive="left")
        if w.empty:
            continue
        dens.append(int(w.index.minute.size))
        r = w["Close"].pct_change().dropna()
        if len(r) > 6:
            v = float((r ** 2).sum())
            if v > 0:
                shares.append(float((r.iloc[:5] ** 2).sum() / v))
    return {"bar_density_median": float(np.median(dens)) if dens else None,
            "bar_density_p05": float(np.percentile(dens, 5)) if dens else None,
            "first5min_variance_share_median": round(float(np.median(shares)), 4) if shares else None,
            "first5min_variance_share_p95": round(float(np.percentile(shares, 95)), 4) if shares else None,
            "note": "NON-GATING. Reported always; cannot change the verdict."}


def check_provenance(meta_validation: dict, meta_discovery: dict) -> None:
    for k in ("vendor", "dataset", "symbology", "roll_rule"):
        a, b = meta_validation.get(k), meta_discovery.get(k)
        if a != b:
            raise SystemExit(f"PROVENANCE MISMATCH on '{k}': validation={a!r} discovery={b!r}. "
                             f"Refusing to run -- a number from a differently-built series is not "
                             f"comparable to the Discovery result.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validation-file", required=True)
    ap.add_argument("--discovery-file", required=True)
    ap.add_argument("--meta", help="JSON with {'validation': {...}, 'discovery': {...}} provenance fields")
    ap.add_argument("--out", default="research/studies/hyp156-validation-result.json")
    a = ap.parse_args()

    if a.meta:
        m = json.loads(Path(a.meta).read_text())
        check_provenance(m["validation"], m["discovery"])

    from data_loader import read_price_csv
    disc = read_price_csv(Path(a.discovery_file))
    val = read_price_csv(Path(a.validation_file))
    full = pd.concat([disc, val]).sort_index()
    full = full[~full.index.duplicated(keep="first")]
    atr = atr14(full)

    start = val.index.min().normalize()
    vframe = full[full.index >= start]
    x = per_day_paired_diff(vframe, atr).dropna()
    if x.empty:
        raise SystemExit("no scorable Validation days -- refusing to report anything")

    import project_wide_multiplicity as pwm
    n_val_trials = pwm.compute_stage_trial_counts()["validation"]
    arr = x.to_numpy(dtype=float)
    ci = block_bootstrap_ci(arr)
    mean = float(arr.mean())
    adj = sidak_ci(mean, ci, n_val_trials)
    verdict = "PASS" if ci[0] > 0 and adj[0] > 0 else "FAIL"

    pre = per_day_paired_diff(vframe, atr, PRE_WINDOW_ET).dropna()
    london = vframe.tz_convert("Europe/London") if vframe.index.tz else vframe
    dst_aware = per_day_paired_diff(london, atr, LONDON_LOCAL_WINDOW).dropna() if vframe.index.tz else pd.Series(dtype=float)

    result = {
        "hypothesis": "hyp-000156", "family": "M23 London-open volatility burst, 6E",
        "test": "PAIRED per-day diff vs the US-RTH hourly baseline; gating window 03:00-04:00 ET",
        "n_days": int(arr.size), "mean_diff": round(mean, 5),
        "ci_90_block_bootstrap": (round(ci[0], 5), round(ci[1], 5)),
        "sidak_n_used": max(SIDAK_FLOOR_N, int(n_val_trials)),
        "sidak_adjusted_ci": adj, "n_boot": N_BOOT, "block": BLOCK, "seed": SEED,
        "VERDICT": verdict,
        "non_gating": {
            "pre_london_0200_0300_mean": round(float(pre.mean()), 5) if len(pre) else None,
            "dst_aware_london_local_mean": round(float(dst_aware.mean()), 5) if len(dst_aware) else None,
            "dst_aware_n": int(dst_aware.size),
            "diagnostics": diagnostics(vframe)},
        "one_shot": "This is the single pre-registered Validation run for hyp-000156. "
                    "No retuning, no alternate windows, no second attempt.",
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""
baseline_relative.py
====================

The TWO NULLS (methodology amendment, September 12th, 2026 -- see
research/studies/two-layer-methodology.md, "Amendment: the two nulls", and
research/mechanisms/cross-asset-correlation-convergence-m12.md Section 10).

Scan 019 showed NQ's unconditional forward drift over the Discovery slice
is about +0.18 to +0.20 ATR per 3 days (~15-16% annualized -- the real
equity risk premium, cross-checked against the index's actual return).
A LONG-ONLY directional claim whose 90% CI merely clears ZERO may have
rediscovered buy-and-hold. So:

  NULL 1 (directional claims): the effect is reported as
      mean(signal days) - mean(ALL days, same slice, same horizon, same
      units), with its own bootstrap CI on the DIFFERENCE.
  NULL 2 (cross-index claims): the OUTCOME is the residual
      r_target - beta * r_reference, with beta estimated from data strictly
      BEFORE the observation (rolling window) and frozen within each
      out-of-sample stage -- never refit on the stage being tested.

Sign-adjusted, ratio-based and long-minus-short constructions are baseline-
free by design and are unaffected.

Overlapping multi-day windows are autocorrelated, so an iid bootstrap
overstates precision. block_bootstrap_diff_ci() is provided for that case;
report both when horizons overlap.
"""
from __future__ import annotations

import numpy as np

N_BOOTSTRAP = 3000
RANDOM_SEED = 7


def _clean(a) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    return a[~np.isnan(a)]


def baseline_relative(signal_vals, all_vals) -> dict:
    """mean(signal) - mean(all), point estimate only. Units are the caller's."""
    s, a = _clean(signal_vals), _clean(all_vals)
    if len(s) < 2 or len(a) < 2:
        return {"n_signal": int(len(s)), "n_all": int(len(a)), "signal_mean": float("nan"),
                "all_mean": float("nan"), "diff": float("nan")}
    return {"n_signal": int(len(s)), "n_all": int(len(a)), "signal_mean": float(s.mean()),
            "all_mean": float(a.mean()), "diff": float(s.mean() - a.mean())}


def bootstrap_diff_ci(signal_vals, all_vals, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED, alpha=0.10):
    """iid bootstrap 90% CI on mean(signal) - mean(all)."""
    rng = np.random.default_rng(seed)
    s, a = _clean(signal_vals), _clean(all_vals)
    if len(s) < 2 or len(a) < 2:
        return float("nan"), float("nan")
    d = (rng.choice(s, size=(n_bootstrap, len(s)), replace=True).mean(axis=1)
         - rng.choice(a, size=(n_bootstrap, len(a)), replace=True).mean(axis=1))
    return float(np.percentile(d, 100 * alpha / 2)), float(np.percentile(d, 100 * (1 - alpha / 2)))


def _block_means(x: np.ndarray, block: int, n_bootstrap: int, rng) -> np.ndarray:
    """Moving-block bootstrap of the mean for an autocorrelated series."""
    n = len(x)
    if n <= block:
        return rng.choice(x, size=(n_bootstrap, n), replace=True).mean(axis=1)
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n - block + 1, size=(n_bootstrap, n_blocks))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_bootstrap, -1)[:, :n]
    return x[idx].mean(axis=1)


def block_bootstrap_diff_ci(signal_vals, all_vals, block: int, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED, alpha=0.10):
    """Moving-block bootstrap 90% CI on mean(signal) - mean(all). Use block =
    the overlap length (e.g. the forward horizon in days) when observations
    are overlapping windows in time order."""
    rng = np.random.default_rng(seed)
    s, a = _clean(signal_vals), _clean(all_vals)
    if len(s) < 2 or len(a) < 2:
        return float("nan"), float("nan")
    d = _block_means(s, block, n_bootstrap, rng) - _block_means(a, block, n_bootstrap, rng)
    return float(np.percentile(d, 100 * alpha / 2)), float(np.percentile(d, 100 * (1 - alpha / 2)))


def rolling_beta(r_target, r_reference, window: int) -> np.ndarray:
    """beta[t] = cov(target, reference) / var(reference) over the `window`
    observations strictly BEFORE t (no lookahead). NaN until enough history.
    Freeze the resulting series inside each out-of-sample stage."""
    y, x = np.asarray(r_target, dtype=float), np.asarray(r_reference, dtype=float)
    n = len(y)
    out = np.full(n, np.nan)
    for t in range(window, n):
        xs, ys = x[t - window:t], y[t - window:t]
        vx = np.var(xs, ddof=1)
        if vx > 0 and not np.isnan(vx):
            out[t] = float(np.cov(xs, ys, ddof=1)[0, 1] / vx)
    return out


def beta_residual(r_target, r_reference, beta) -> np.ndarray:
    """r_target - beta * r_reference, elementwise. NULL 2's outcome."""
    return np.asarray(r_target, dtype=float) - np.asarray(beta, dtype=float) * np.asarray(r_reference, dtype=float)

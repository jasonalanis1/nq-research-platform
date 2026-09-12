import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import baseline_relative as br  # noqa: E402


def test_baseline_relative_removes_common_drift():
    rng = np.random.default_rng(1)
    drift = 0.2
    all_days = drift + rng.normal(0, 1, 5000)
    signal = drift + rng.normal(0, 1, 800)          # NO real effect beyond the drift
    res = br.baseline_relative(signal, all_days)
    assert abs(res["signal_mean"] - drift) < 0.15    # vs zero it "looks" positive...
    lo, hi = br.bootstrap_diff_ci(signal, all_days)
    assert lo < 0 < hi                               # ...but vs baseline it is null


def test_real_effect_survives_baseline():
    rng = np.random.default_rng(2)
    all_days = 0.2 + rng.normal(0, 1, 5000)
    signal = 0.2 + 0.5 + rng.normal(0, 1, 800)       # genuine +0.5 above the drift
    lo, hi = br.bootstrap_diff_ci(signal, all_days)
    assert lo > 0.3 and hi < 0.7


def test_block_bootstrap_is_wider_for_autocorrelated_series():
    rng = np.random.default_rng(3)
    e = rng.normal(0, 1, 3000)
    x = np.convolve(e, np.ones(10) / 10, mode="same")  # overlapping-window style autocorrelation
    y = x[:600]
    iid = br.bootstrap_diff_ci(y, x)
    blk = br.block_bootstrap_diff_ci(y, x, block=10)
    assert (blk[1] - blk[0]) > (iid[1] - iid[0])


def test_rolling_beta_has_no_lookahead_and_residual_is_beta_neutral():
    rng = np.random.default_rng(4)
    x = rng.normal(0, 1, 400)
    y = 1.5 * x + rng.normal(0, 0.1, 400)
    b = br.rolling_beta(y, x, window=60)
    assert np.isnan(b[:60]).all() and abs(np.nanmean(b[60:]) - 1.5) < 0.05
    # change the future: past betas must not move
    y2 = y.copy(); y2[300:] += 100.0
    b2 = br.rolling_beta(y2, x, window=60)
    assert np.allclose(b[60:300], b2[60:300], equal_nan=True)
    resid = br.beta_residual(y[60:], x[60:], b[60:])
    assert abs(np.corrcoef(resid, x[60:])[0, 1]) < 0.15

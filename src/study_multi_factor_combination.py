"""
study_multi_factor_combination.py
====================================

Implements the frozen spec in
`research/studies/multi-factor-combination-scoping.md` (v3, signed off
by Jason 2026-09-06) -- exp-046. This is this project's twenty-third
hypothesis, and the first that combines multiple already-tested
features into one model rather than testing a single mechanism alone.

ONE frozen specification, tested once on Discovery. Not a search over
model types or feature sets -- see the "What this is NOT" section of
the scoping document.

Inputs: data/multi_factor_features_discovery.csv (built by
src/build_multi_factor_features.py, already Discovery-slice only).

Model: L1-regularized (Lasso-style) logistic regression predicting
target_next_day_return_sign from the 8 candidate features listed in
the scoping document. Regularization strength chosen via purged K-fold
cross-validation within Discovery (the `purgedcv` package), never
tuned against Validation or Holdout.

Two-stage evaluation exactly as frozen:
  Step 1 (statistical, no cost): out-of-fold ROC-AUC, checked via a
    bootstrap 90% CI on the out-of-fold predictions -- credible only if
    the CI's lower bound is above 0.5.
  Step 2 (costed rule, gated on Step 1): translate the SAME out-of-fold
    predicted probabilities into a position (long if p > 0.5, short if
    p < 0.5, no tuning), simulate day-by-day PnL with
    FLIP_COST_POINTS charged only on position changes, and test net
    PnL per trade against this project's standard bootstrap-CI /
    economic-threshold / trade-count gates.

Then the frozen stability check (chronological half-split, quantified
thresholds per the v3 revision) -- run BEFORE any move to Validation.

Implementation notes not pinned by the frozen spec (disclosed here,
not decided after seeing a result):
  - Rows with a missing feature (vol_regime/momentum_sign during their
    warmup windows, the single edge-of-dataset row missing
    overnight_gap_pts or the target) are dropped from the modeling
    population -- the same "insufficient history" convention already
    used by every single-factor study that touches these features.
  - 7 rows where the target is an exact zero return (a very rare
    edge case, not addressed by any prior study either) are dropped
    from the modeling population -- a 3-class target was never
    proposed or authorized.
  - Categorical features (day_of_week, event_type, vol_regime) are
    one-hot encoded with the first category dropped (standard logistic
    regression convention, avoids collinearity with the intercept).
  - Continuous features (overnight_gap_pts, cftc_signal) are
    standardized (zero mean, unit variance) using statistics computed
    from the TRAINING fold only in every CV split, never from the full
    dataset, to avoid leaking test-fold information into scaling.

HOW TO RUN:
    python3 src/study_multi_factor_combination.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

from backtest import ROUND_TRIP_COST_POINTS  # reused unmodified
from purgedcv import PurgedKFold  # reused unmodified

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IN_CSV = DATA_DIR / "multi_factor_features_discovery.csv"
OUT_JSON = DATA_DIR / "study_multi_factor_combination_results.json"

N_BOOTSTRAP = 2000              # matches every prior study's convention
RANDOM_SEED = 11                 # matches study_cpi_nfp_reversal_followup.py
FLIP_COST_POINTS = 2 * ROUND_TRIP_COST_POINTS  # frozen spec Gap 3, reused unmodified
ECONOMIC_THRESHOLD_POINTS = 2 * ROUND_TRIP_COST_POINTS  # same bar as every prior study
PROMOTION_BAR_MIN_TRADES = 150    # docs/RESEARCH_INTEGRITY_PROTOCOL.md
N_CV_SPLITS = 5                   # purged K-fold, chosen for a Discovery sample of ~1.7k rows
C_GRID = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0]  # L1 inverse-regularization-strength grid
INSTABILITY_AUC_FLOOR = 0.53      # frozen spec v3, Gap 5 quantified threshold

CATEGORICAL_COLS = ["day_of_week", "event_type", "vol_regime"]
BOOLEAN_COLS = ["turn_of_month", "is_expiration_week"]
CONTINUOUS_COLS = ["overnight_gap_pts", "cftc_signal"]
PASSTHROUGH_COLS = ["momentum_sign", "cftc_signal_available"]


def load_modeling_population() -> pd.DataFrame:
    df = pd.read_csv(IN_CSV, parse_dates=["date"]).set_index("date")
    required = CATEGORICAL_COLS + BOOLEAN_COLS + CONTINUOUS_COLS + PASSTHROUGH_COLS + [
        "target_next_day_return_sign"
    ]
    before = len(df)
    df = df.dropna(subset=required).copy()
    dropped_na = before - len(df)

    zero_target_mask = df["target_next_day_return_sign"] == 0
    n_zero_target = int(zero_target_mask.sum())
    df = df.loc[~zero_target_mask].copy()

    df["y"] = (df["target_next_day_return_sign"] > 0).astype(int)
    return df, dropped_na, n_zero_target


def build_design_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode categoricals (drop-first), pass through booleans
    and the already-numeric momentum_sign/cftc_signal_available flag,
    leave continuous columns unscaled here -- scaling happens per-fold
    inside the CV loop and once more on the full Discovery set for the
    final reported coefficients."""
    parts = [df[BOOLEAN_COLS].astype(int)]
    for col in CATEGORICAL_COLS:
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True).astype(int)
        parts.append(dummies)
    parts.append(df[PASSTHROUGH_COLS])
    parts.append(df[CONTINUOUS_COLS])
    X = pd.concat(parts, axis=1)
    return X


def prediction_evaluation_times(df: pd.DataFrame) -> tuple:
    """prediction_time = the day itself (features known as of that
    day's reference close); evaluation_time = the next classifiable
    day (when target_next_day_return_sign is realized) -- this is what
    PurgedKFold purges training rows whose label horizon overlaps a
    test fold's label horizons on."""
    dates = df.index.to_series()
    # Each row's own next-classifiable-day date is not stored directly;
    # approximate evaluation_time as prediction_time + 1 day is wrong
    # for weekends/holidays. Instead use the next row's date (rows are
    # already sorted chronologically and one-per-trading-day).
    eval_times = dates.shift(-1)
    eval_times.iloc[-1] = dates.iloc[-1] + pd.Timedelta(days=1)  # harmless placeholder, last row
    return dates.values, eval_times.values


def fit_scaled_logreg(X_train, y_train, C) -> tuple:
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_train_scaled[CONTINUOUS_COLS] = scaler.fit_transform(X_train[CONTINUOUS_COLS])
    model = LogisticRegression(penalty="l1", solver="liblinear", C=C, random_state=RANDOM_SEED)
    model.fit(X_train_scaled, y_train)
    return model, scaler


def predict_scaled(model, scaler, X) -> np.ndarray:
    X_scaled = X.copy()
    X_scaled[CONTINUOUS_COLS] = scaler.transform(X[CONTINUOUS_COLS])
    return model.predict_proba(X_scaled)[:, 1]


def cv_out_of_fold_probs(X, y, pred_times, eval_times, C) -> np.ndarray:
    splitter = PurgedKFold(
        n_splits=N_CV_SPLITS,
        prediction_times=pred_times,
        evaluation_times=eval_times,
        purge_horizon=pd.Timedelta(days=1),
        embargo=pd.Timedelta(days=1),
    )
    oof_probs = np.full(len(X), np.nan)
    for train_idx, test_idx in splitter.split(X):
        model, scaler = fit_scaled_logreg(X.iloc[train_idx], y.iloc[train_idx], C)
        oof_probs[test_idx] = predict_scaled(model, scaler, X.iloc[test_idx])
    return oof_probs


def bootstrap_auc_ci(y_true, y_prob, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED) -> tuple:
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    n = len(y_true)
    aucs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        yt, yp = y_true[idx], y_prob[idx]
        if len(np.unique(yt)) < 2:
            continue
        aucs.append(roc_auc_score(yt, yp))
    aucs = np.array(aucs)
    return float(np.percentile(aucs, 5)), float(np.percentile(aucs, 95))


def bootstrap_mean_ci(values, n_bootstrap=N_BOOTSTRAP, seed=RANDOM_SEED) -> tuple:
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    means = np.array([arr[rng.integers(0, n, n)].mean() for _ in range(n_bootstrap)])
    return float(np.percentile(means, 5)), float(np.percentile(means, 95))


def simulate_costed_pnl(df, oof_probs) -> pd.DataFrame:
    """One 'trade' = one full trading day held (prior day's reference
    close to current day's reference close), per Gap 3's frozen daily-
    resolution convention. Position = sign(p - 0.5), no tuning.
    FLIP_COST_POINTS charged only on days the position differs from the
    immediately prior day's position (first day charged once, entering
    from flat)."""
    sim = df[["target_next_day_return_pts"]].copy()
    sim["prob_up"] = oof_probs
    sim["position"] = np.where(sim["prob_up"] > 0.5, 1, -1)
    prev_position = sim["position"].shift(1).fillna(0)
    sim["flipped"] = sim["position"] != prev_position
    sim["gross_pnl"] = sim["position"] * sim["target_next_day_return_pts"]
    sim["net_pnl"] = sim["gross_pnl"] - np.where(sim["flipped"], FLIP_COST_POINTS, 0.0)
    return sim


def main():
    df, dropped_na, n_zero_target = load_modeling_population()
    X = build_design_matrix(df)
    y = df["y"]
    pred_times, eval_times = prediction_evaluation_times(df)

    print("=" * 78)
    print("MULTI-FACTOR COMBINATION MODEL (exp-046) -- Discovery slice")
    print("=" * 78)
    print(f"\nRows in multi_factor_features_discovery.csv: 1717")
    print(f"Dropped (missing required feature/target): {dropped_na}")
    print(f"Dropped (exact-zero target, no sign): {n_zero_target}")
    print(f"Modeling population: {len(df)} rows, {df.index.min().date()} .. {df.index.max().date()}")
    print(f"Class balance: up={int(y.sum())} ({y.mean():.1%})  down={int((1 - y).sum())} ({1 - y.mean():.1%})")
    print(f"Design matrix columns ({X.shape[1]}): {list(X.columns)}")

    print("\n--- Choosing L1 regularization strength via purged 5-fold CV (Discovery only) ---")
    cv_results = {}
    for C in C_GRID:
        oof = cv_out_of_fold_probs(X, y, pred_times, eval_times, C)
        auc = roc_auc_score(y, oof)
        cv_results[C] = {"auc": auc, "oof_probs": oof}
        print(f"  C={C:<6} out-of-fold AUC={auc:.4f}")

    best_C = max(cv_results, key=lambda c: cv_results[c]["auc"])
    best_oof = cv_results[best_C]["oof_probs"]
    print(f"\nSelected C={best_C} (highest out-of-fold AUC={cv_results[best_C]['auc']:.4f})")

    print("\n--- STEP 1: statistical check (out-of-fold AUC, no cost) ---")
    auc_point = roc_auc_score(y, best_oof)
    auc_ci_low, auc_ci_high = bootstrap_auc_ci(y, best_oof)
    step1_pass = auc_ci_low > 0.5
    print(f"  Out-of-fold AUC: {auc_point:.4f}")
    print(f"  90% bootstrap CI: [{auc_ci_low:.4f}, {auc_ci_high:.4f}]")
    print(f"  Step 1 gate (CI lower bound > 0.5): {'PASS' if step1_pass else 'FAIL'}")

    step2_result = None
    if step1_pass:
        print("\n--- STEP 2: costed translation rule (gated on Step 1 passing) ---")
        sim = simulate_costed_pnl(df, best_oof)
        n_trades = len(sim)
        mean_net = float(sim["net_pnl"].mean())
        ci_low, ci_high = bootstrap_mean_ci(sim["net_pnl"])
        n_flips = int(sim["flipped"].sum())
        meets_min_trades = n_trades >= PROMOTION_BAR_MIN_TRADES
        significant = ci_low > 0
        economically_meaningful = mean_net >= ECONOMIC_THRESHOLD_POINTS
        step2_result = {
            "n_trades": n_trades, "n_flips": n_flips, "mean_net_pnl_pts": mean_net,
            "mean_net_pnl_dollars": mean_net * 20.0, "ci_90": (ci_low, ci_high),
            "meets_min_trades": meets_min_trades, "significant": significant,
            "economically_meaningful": economically_meaningful,
        }
        print(f"  Trades: {n_trades} (position flips: {n_flips})")
        print(f"  Net PnL per day, mean: {mean_net:+.3f} pts (${mean_net * 20.0:+.2f})")
        print(f"  90% CI: [{ci_low:+.3f}, {ci_high:+.3f}]")
        print(f"  Trade-count gate (>= {PROMOTION_BAR_MIN_TRADES}): {meets_min_trades}")
        print(f"  Statistically credible (CI > 0): {significant}")
        print(f"  Economically meaningful (>= {ECONOMIC_THRESHOLD_POINTS:.3f} pts): {economically_meaningful}")
    else:
        print("\n--- STEP 2 skipped: Step 1 did not clear, no coin-flip model is worth costing out ---")

    print("\n--- STABILITY CHECK (chronological half-split, run before any move to Validation) ---")
    midpoint = len(df) // 2
    half_results = {}
    full_model, full_scaler = fit_scaled_logreg(X, y, best_C)
    full_coefs = dict(zip(X.columns, full_model.coef_[0]))
    for label, (start, end) in (("first_half", (0, midpoint)), ("second_half", (midpoint, len(df)))):
        X_half, y_half = X.iloc[start:end].reset_index(drop=True), y.iloc[start:end].reset_index(drop=True)
        pt_half, et_half = pred_times[start:end], eval_times[start:end]
        oof_half = cv_out_of_fold_probs(X_half, y_half, pt_half, et_half, best_C)
        auc_half = roc_auc_score(y_half, oof_half)
        model_half, _ = fit_scaled_logreg(X_half, y_half, best_C)
        coefs_half = dict(zip(X.columns, model_half.coef_[0]))
        half_results[label] = {"auc": auc_half, "coefs": coefs_half, "n": len(X_half)}
        print(f"  {label}: n={len(X_half)}  out-of-fold AUC={auc_half:.4f}")

    sign_flips = []
    for feat in X.columns:
        c1 = half_results["first_half"]["coefs"][feat]
        c2 = half_results["second_half"]["coefs"][feat]
        if c1 != 0 and c2 != 0 and np.sign(c1) != np.sign(c2):
            sign_flips.append(feat)
    auc_floor_breach = (
        half_results["first_half"]["auc"] <= INSTABILITY_AUC_FLOOR
        or half_results["second_half"]["auc"] <= INSTABILITY_AUC_FLOOR
    )
    instability_flag = bool(sign_flips) or auc_floor_breach
    print(f"  Coefficients flipping sign (nonzero in both halves): {sign_flips if sign_flips else 'none'}")
    print(f"  Either half's AUC <= {INSTABILITY_AUC_FLOOR} floor: {auc_floor_breach}")
    print(f"  INSTABILITY FLAG: {'YES -- do not proceed to Validation' if instability_flag else 'no'}")

    print("\n--- Frozen-model coefficients (full Discovery fit, L1-regularized) ---")
    for feat, coef in sorted(full_coefs.items(), key=lambda kv: -abs(kv[1])):
        tag = "(zeroed by L1)" if coef == 0 else ""
        print(f"  {feat:<28} {coef:+.4f} {tag}")

    print("\n" + "=" * 78)
    if not step1_pass:
        verdict = "kill -- Step 1 (statistical) gate not cleared, model is not distinguishable from a coin flip"
    elif instability_flag:
        verdict = "kill -- Step 1/Step 2 passed but the stability check flagged real instability; per the frozen spec this blocks any move to Validation regardless"
    elif step2_result and step2_result["significant"] and step2_result["economically_meaningful"] and step2_result["meets_min_trades"]:
        verdict = "PROMOTE-ELIGIBLE for a Validation-slice test -- clears Step 1, Step 2, and the stability check"
    elif step2_result and step2_result["significant"] and step2_result["economically_meaningful"]:
        verdict = "retest -- promising, underpowered (n < 150-trade promotion bar)"
    else:
        verdict = "kill -- Step 1 passed but Step 2's costed rule is not statistically credible and/or not economically meaningful"
    print(f"Verdict: {verdict}")

    out = {
        "modeling_population": {
            "n_rows": len(df), "dropped_na": dropped_na, "dropped_zero_target": n_zero_target,
            "date_range": [str(df.index.min().date()), str(df.index.max().date())],
            "class_balance_up": float(y.mean()),
        },
        "cv_grid": {str(c): cv_results[c]["auc"] for c in C_GRID},
        "selected_C": best_C,
        "step1": {"auc": auc_point, "ci_90": (auc_ci_low, auc_ci_high), "pass": step1_pass},
        "step2": step2_result,
        "stability_check": {
            "first_half_auc": half_results["first_half"]["auc"],
            "second_half_auc": half_results["second_half"]["auc"],
            "sign_flips": sign_flips,
            "auc_floor_breach": auc_floor_breach,
            "instability_flag": instability_flag,
        },
        "full_discovery_coefficients": full_coefs,
        "verdict": verdict,
    }
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nSaved full results to {OUT_JSON}.")


if __name__ == "__main__":
    main()

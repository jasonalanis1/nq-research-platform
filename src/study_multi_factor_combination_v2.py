"""
study_multi_factor_combination_v2.py
========================================

exp-070 -- ensemble v2, frozen spec: research/studies/ensemble-v2-scoping.md.
Second attempt at the multi-factor combination idea (v1 = exp-046,
hyp-000016, REJECTED). Reuses every function from
study_multi_factor_combination.py UNMODIFIED (imported, not copied) --
the only change is the input file (multi_factor_features_v2_discovery.csv,
built by build_multi_factor_features_v2.py) and CONTINUOUS_COLS, which
adds the new `event_day_realized_move_zscore` column alongside the
existing `overnight_gap_pts` and `cftc_signal`.

Same target variable, same statistical gate, same stability check, same
no-retuning discipline as v1.

DISCLOSED UP FRONT (per the Path-to-Profitability Advisor's review of
the scoping draft): the premise this leans on -- that CPI/NFP release-
day move MAGNITUDE carries information -- is NOT a confirmed edge going
in. exp-063 (hyp-000036, the just-closed real-options-data VRP check)
found no credible gap between what options implied and what actually
happened on those days. This column uses a different, more modest
claim (raw realized-move size as an ordinary feature, not an implied-
vs-realized comparison), but it has never been tested predictive on
its own before this run -- expectations should be calibrated
accordingly, exactly as this project's other honest characterization
studies are.

HOW TO RUN:
    python3 src/study_multi_factor_combination_v2.py
"""

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

import study_multi_factor_combination as v1

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IN_CSV = DATA_DIR / "multi_factor_features_v2_discovery.csv"
OUT_JSON = DATA_DIR / "study_multi_factor_combination_v2_results.json"

CONTINUOUS_COLS_V2 = ["overnight_gap_pts", "cftc_signal", "event_day_realized_move_zscore"]


def load_modeling_population_v2():
    import pandas as pd
    df = pd.read_csv(IN_CSV, parse_dates=["date"]).set_index("date")
    required = v1.CATEGORICAL_COLS + v1.BOOLEAN_COLS + CONTINUOUS_COLS_V2 + v1.PASSTHROUGH_COLS + [
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


def build_design_matrix_v2(df):
    import pandas as pd
    parts = [df[v1.BOOLEAN_COLS].astype(int)]
    for col in v1.CATEGORICAL_COLS:
        dummies = pd.get_dummies(df[col], prefix=col, drop_first=True).astype(int)
        parts.append(dummies)
    parts.append(df[v1.PASSTHROUGH_COLS])
    parts.append(df[CONTINUOUS_COLS_V2])
    return pd.concat(parts, axis=1)


def fit_scaled_logreg_v2(X_train, y_train, C):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = X_train.copy()
    X_train_scaled[CONTINUOUS_COLS_V2] = scaler.fit_transform(X_train[CONTINUOUS_COLS_V2])
    model = LogisticRegression(penalty="l1", solver="liblinear", C=C, random_state=v1.RANDOM_SEED)
    model.fit(X_train_scaled, y_train)
    return model, scaler


def predict_scaled_v2(model, scaler, X):
    X_scaled = X.copy()
    X_scaled[CONTINUOUS_COLS_V2] = scaler.transform(X[CONTINUOUS_COLS_V2])
    return model.predict_proba(X_scaled)[:, 1]


def cv_out_of_fold_probs_v2(X, y, pred_times, eval_times, C):
    import pandas as pd
    from purgedcv import PurgedKFold
    splitter = PurgedKFold(
        n_splits=v1.N_CV_SPLITS,
        prediction_times=pred_times,
        evaluation_times=eval_times,
        purge_horizon=pd.Timedelta(days=1),
        embargo=pd.Timedelta(days=1),
    )
    oof_probs = np.full(len(X), np.nan)
    for train_idx, test_idx in splitter.split(X):
        model, scaler = fit_scaled_logreg_v2(X.iloc[train_idx], y.iloc[train_idx], C)
        oof_probs[test_idx] = predict_scaled_v2(model, scaler, X.iloc[test_idx])
    return oof_probs


def main():
    df, dropped_na, n_zero_target = load_modeling_population_v2()
    X = build_design_matrix_v2(df)
    y = df["y"]
    pred_times, eval_times = v1.prediction_evaluation_times(df)

    print("=" * 78)
    print("MULTI-FACTOR COMBINATION MODEL v2 (exp-070) -- Discovery slice")
    print("=" * 78)
    print(f"\nDropped (missing required feature/target): {dropped_na}")
    print(f"Dropped (exact-zero target, no sign): {n_zero_target}")
    print(f"Modeling population: {len(df)} rows, {df.index.min().date()} .. {df.index.max().date()}")
    print(f"Class balance: up={int(y.sum())} ({y.mean():.1%})  down={int((1 - y).sum())} ({1 - y.mean():.1%})")
    print(f"Design matrix columns ({X.shape[1]}): {list(X.columns)}")

    print("\n--- Choosing L1 regularization strength via purged 5-fold CV (Discovery only) ---")
    cv_results = {}
    for C in v1.C_GRID:
        oof = cv_out_of_fold_probs_v2(X, y, pred_times, eval_times, C)
        auc = roc_auc_score(y, oof)
        cv_results[C] = {"auc": auc, "oof_probs": oof}
        print(f"  C={C:<6} out-of-fold AUC={auc:.4f}")

    best_C = max(cv_results, key=lambda c: cv_results[c]["auc"])
    best_oof = cv_results[best_C]["oof_probs"]
    print(f"\nSelected C={best_C} (highest out-of-fold AUC={cv_results[best_C]['auc']:.4f})")

    print("\n--- STEP 1: statistical check (out-of-fold AUC, no cost) ---")
    auc_point = roc_auc_score(y, best_oof)
    auc_ci_low, auc_ci_high = v1.bootstrap_auc_ci(y, best_oof)
    step1_pass = auc_ci_low > 0.5
    print(f"  Out-of-fold AUC: {auc_point:.4f}")
    print(f"  90% bootstrap CI: [{auc_ci_low:.4f}, {auc_ci_high:.4f}]")
    print(f"  Step 1 gate (CI lower bound > 0.5): {'PASS' if step1_pass else 'FAIL'}")

    step2_result = None
    if step1_pass:
        print("\n--- STEP 2: costed translation rule (gated on Step 1 passing) ---")
        sim = v1.simulate_costed_pnl(df, best_oof)
        n_trades = len(sim)
        mean_net = float(sim["net_pnl"].mean())
        ci_low, ci_high = v1.bootstrap_mean_ci(sim["net_pnl"])
        n_flips = int(sim["flipped"].sum())
        meets_min_trades = n_trades >= v1.PROMOTION_BAR_MIN_TRADES
        significant = ci_low > 0
        economically_meaningful = mean_net >= v1.ECONOMIC_THRESHOLD_POINTS
        step2_result = {
            "n_trades": n_trades, "n_flips": n_flips, "mean_net_pnl_pts": mean_net,
            "ci_90": (ci_low, ci_high), "meets_min_trades": meets_min_trades,
            "significant": significant, "economically_meaningful": economically_meaningful,
        }
        print(f"  Trades: {n_trades} (flips: {n_flips})  mean net pnl: {mean_net:+.3f} pts  "
              f"ci_90=({ci_low:+.3f},{ci_high:+.3f})")
        print(f"  Significant: {significant}  Economically meaningful: {economically_meaningful}  "
              f"Meets trade-count: {meets_min_trades}")
    else:
        print("\n--- STEP 2 skipped: Step 1 did not clear ---")

    print("\n--- STABILITY CHECK (chronological half-split) ---")
    midpoint = len(df) // 2
    half_results = {}
    full_model, full_scaler = fit_scaled_logreg_v2(X, y, best_C)
    full_coefs = dict(zip(X.columns, full_model.coef_[0]))
    for label, (start, end) in (("first_half", (0, midpoint)), ("second_half", (midpoint, len(df)))):
        X_half, y_half = X.iloc[start:end].reset_index(drop=True), y.iloc[start:end].reset_index(drop=True)
        pt_half, et_half = pred_times[start:end], eval_times[start:end]
        oof_half = cv_out_of_fold_probs_v2(X_half, y_half, pt_half, et_half, best_C)
        auc_half = roc_auc_score(y_half, oof_half)
        model_half, _ = fit_scaled_logreg_v2(X_half, y_half, best_C)
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
        half_results["first_half"]["auc"] <= v1.INSTABILITY_AUC_FLOOR
        or half_results["second_half"]["auc"] <= v1.INSTABILITY_AUC_FLOOR
    )
    instability_flag = bool(sign_flips) or auc_floor_breach
    print(f"  Sign flips: {sign_flips if sign_flips else 'none'}  AUC floor breach: {auc_floor_breach}")
    print(f"  INSTABILITY FLAG: {'YES' if instability_flag else 'no'}")

    print("\n--- Frozen-model coefficients (full Discovery fit) ---")
    for feat, coef in sorted(full_coefs.items(), key=lambda kv: -abs(kv[1])):
        tag = "(zeroed by L1)" if coef == 0 else ""
        print(f"  {feat:<32} {coef:+.4f} {tag}")

    print("\n" + "=" * 78)
    if not step1_pass:
        verdict = "kill -- Step 1 gate not cleared, model not distinguishable from a coin flip"
    elif instability_flag:
        verdict = "kill -- stability check flagged real instability"
    elif step2_result and step2_result["significant"] and step2_result["economically_meaningful"] and step2_result["meets_min_trades"]:
        verdict = "PROMOTE-ELIGIBLE for a Validation-slice test"
    elif step2_result and step2_result["significant"] and step2_result["economically_meaningful"]:
        verdict = "retest -- promising, underpowered"
    else:
        verdict = "kill -- Step 1 passed but Step 2 not credible/meaningful"
    print(f"Verdict: {verdict}")

    out = {
        "modeling_population": {
            "n_rows": len(df), "dropped_na": dropped_na, "dropped_zero_target": n_zero_target,
            "date_range": [str(df.index.min().date()), str(df.index.max().date())],
            "class_balance_up": float(y.mean()),
        },
        "cv_grid": {str(c): cv_results[c]["auc"] for c in v1.C_GRID},
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

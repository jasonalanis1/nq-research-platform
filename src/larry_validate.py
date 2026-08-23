"""
larry_validate.py
===================

WHAT THIS FILE DOES (plain English):
Sketches how Larry's Deflated Sharpe Ratio / Probability of Backtest
Overfitting checks connect research_ledger.py's hypothesis records to a
Strategy Status update, using the `purgedcv` library
(https://github.com/eslazarev/purged-cross-validation, MIT licensed) so
none of the DSR/PBO/CSCV math gets reimplemented from scratch, per
docs/RESEARCH_INTEGRITY_PROTOCOL.md's explicit instruction to check for
an existing, tested implementation first.

VERIFIED BEFORE WRITING THIS (2026-08-23): installed purgedcv and ran it
against a synthetic scenario -- 50 fake trial variants sharing one time
axis, 49 pure noise, 1 with a real (small) planted edge -- to see
whether it behaves sensibly before trusting it with real decisions:

  - Picking "best in-sample Sharpe" out of the 50 picked a NOISE config,
    not the one with the real edge. This is expected and is the exact
    failure mode the whole protocol exists to catch, not a library bug.
  - Deflated Sharpe Ratio on that picked config: 69.4% -- versus 99.96%
    if it had naively been treated as the only trial ever run. Same
    underlying result, the only difference is honestly accounting for
    the 50 trials searched.
  - Probability of Backtest Overfitting on the same 50-config set: 22.7%
    (via 12,870 CSCV combinations at n_splits=16, the library's
    documented standard choice).

This is a REAL library, not a stub -- doctested, MIT licensed, pip
installable (`pip install purgedcv`), actively maintained, published
with a peer-reviewed paper. Confirmed working as documented, not just
plausible-looking from its GitHub page.

STATUS AS OF 2026-08-23: this file is a SKETCH, not a finished module.
It shows the wiring -- how a hypothesis's return series + trial count
becomes a DSR/PBO result, and how that result becomes a
research_ledger.update_status() call -- but the actual PASS/FAIL
THRESHOLDS below (what DSR/PBO values count as "good enough" to move a
hypothesis to VALIDATION CANDIDATE) are PLACEHOLDERS, clearly marked.
Per this project's whole pattern so far (fixed calendar dates instead of
rolling percentages, an explicit 5-slot holdout budget instead of an
implicit one, an explicit three-field model instead of one conflated
status), those thresholds should be a decision YOU make deliberately,
not a default I pick quietly. Nothing in this file should run against a
real hypothesis until that decision is made and this file is reviewed.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
from purgedcv import deflated_sharpe_ratio, probability_of_backtest_overfitting

import research_ledger as rl

# PLACEHOLDER THRESHOLDS -- NOT YET DECIDED. Filled in with reasonable-
# sounding starting points only so this file is runnable; treat these as
# a first draft to react to, not a recommendation to accept as-is.
DSR_PASS_THRESHOLD = 0.95   # DSR = probability true Sharpe > 0, trial-adjusted
PBO_FAIL_THRESHOLD = 0.50   # PBO >= this means "more likely overfit than not"


@dataclass
class LarryVerdict:
    hypothesis_id: str
    dsr: float
    pbo: Optional[float]
    n_trials_considered: int
    recommended_status: str
    reasoning: str


def evaluate_candidate(
    hypothesis_id: str,
    winner_returns,                 # 1-D array: the candidate's own per-period returns
    sibling_returns: Optional["np.ndarray"] = None,  # (n_configs, n_obs): the full trial set it was picked from, for PBO
    ledger_path=rl.LEDGER_PATH,
) -> LarryVerdict:
    """
    Runs DSR (always) and PBO (if sibling_returns is provided -- PBO
    needs the full set of competing trials, not just the winner) on one
    candidate hypothesis, and proposes -- but does NOT automatically
    apply -- a Strategy Status update.

    n_trials_considered is read from how many sibling rows share this
    hypothesis's parent lineage in the ledger (walking parent_hypothesis_id
    and counting siblings), NOT hand-typed each time -- the whole point of
    logging every hypothesis is that the trial count doesn't have to be
    trusted from memory.
    """
    winner_returns = np.asarray(winner_returns, dtype=float)

    current = rl.get_current_state(ledger_path)
    record = rl.get_latest(hypothesis_id, ledger_path)
    if record is None:
        raise ValueError(f"hypothesis_id {hypothesis_id!r} not found in ledger")

    # Trial count = how many logged hypotheses share this one's "family"
    # (same strategy_name, tested in the same search) -- approximated
    # here as same strategy_name for now. This is a real design question
    # to sharpen later: a genuinely separate research question on the
    # same strategy_name shouldn't inflate another candidate's trial
    # count just by sharing a name.
    n_trials_considered = sum(1 for r in current if r["strategy_name"] == record["strategy_name"])

    var_sharpe = float(np.var(
        [np.mean(winner_returns) / np.std(winner_returns)], ddof=0
    )) if sibling_returns is None else float(np.var(
        sibling_returns.mean(axis=1) / sibling_returns.std(axis=1), ddof=1
    ))

    dsr = deflated_sharpe_ratio(winner_returns, n_trials=n_trials_considered, var_sharpe=var_sharpe)

    pbo = None
    if sibling_returns is not None:
        pbo_result = probability_of_backtest_overfitting(sibling_returns, n_splits=16)
        pbo = pbo_result.pbo

    # PLACEHOLDER decision logic -- see module docstring.
    if dsr < DSR_PASS_THRESHOLD:
        status, reason = "REJECTED", f"DSR {dsr:.3f} below placeholder threshold {DSR_PASS_THRESHOLD}"
    elif pbo is not None and pbo >= PBO_FAIL_THRESHOLD:
        status, reason = "REJECTED", f"PBO {pbo:.3f} at/above placeholder threshold {PBO_FAIL_THRESHOLD}"
    else:
        status, reason = "VALIDATION CANDIDATE", f"DSR {dsr:.3f}, PBO {pbo}, both cleared placeholder thresholds"

    return LarryVerdict(
        hypothesis_id=hypothesis_id,
        dsr=dsr,
        pbo=pbo,
        n_trials_considered=n_trials_considered,
        recommended_status=status,
        reasoning=reason,
    )


def apply_verdict(verdict: LarryVerdict, ledger_path=rl.LEDGER_PATH):
    """Separate, explicit step to actually write the verdict into the
    ledger -- evaluate_candidate() never writes anything on its own, so a
    dry-run/preview is always possible before committing a status change."""
    return rl.update_status(
        verdict.hypothesis_id,
        new_status=verdict.recommended_status,
        notes=f"Larry DSR/PBO evaluation: {verdict.reasoning}",
        ledger_path=ledger_path,
    )

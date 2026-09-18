"""
overlap_check_s013_vs_s011.py -- the MANDATORY pre-SPECIFY independence check
for S013 (opening-auction order imbalance, lineage hyp-000076), pre-registered
in the S013 SOURCE row of research/ledger/strategies.jsonl, condition (2).

THE QUESTION (the one that killed hyp-000162 at Portfolio): is S013 a separate
bet, or does it select substantially the same sessions, in substantially the
same direction, over substantially the same holding window as S011?

WHAT IS MEASURED, on Discovery only, no costs, no expectancy, no outcome:
  1. session selection overlap -- |A n B| / |A u B| and each side's share.
  2. DIRECTIONAL agreement on the jointly selected sessions. Both strategies
     enter on session T and exit at 15:55 ET of session T, so on a session where
     both fire in the same direction the two are the same position.

S011 rule (frozen module, read not re-implemented): fade sign(Close-Open) of the
prior RTH session, enter at the 09:30 open of T, exit 15:55 T.
S013 candidate rule (hyp-000076 as closed): sum of sign(Close-Open)*Volume over
the 09:30-10:00 bars of T, traded in that direction from 10:00, exit same session.
Nothing here is frozen or registered; this is a measurement, not a strategy.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import bot_stack_paper_run as bpr  # noqa: E402
import strategy_s011_daily_reversal_vs_own_drift as s011  # noqa: E402
from data_loader import load_price_data  # noqa: E402
from data_split import get_discovery_data  # noqa: E402

PROJECT_ROOT = ROOT.parent


def s013_direction(day_df):
    """sign( sum over 09:30-09:59 bars of sign(Close-Open)*Volume ). 0 = no signal."""
    win = day_df.between_time("09:30", "09:59")
    if win.empty or "volume" not in {c.lower() for c in win.columns}:
        return 0, 0.0
    vol_col = [c for c in win.columns if c.lower() == "volume"][0]
    o = [c for c in win.columns if c.lower() == "open"][0]
    c = [c for c in win.columns if c.lower() == "close"][0]
    imb = float((((win[c] - win[o]).apply(lambda x: (x > 0) - (x < 0))) * win[vol_col]).sum())
    return ((imb > 0) - (imb < 0)), imb


def main() -> int:
    df, synthetic = load_price_data(context="overlap_check_s013_vs_s011", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data: refusing to measure overlap")
    disc = get_discovery_data(df)
    s011.precompute(disc)

    a_dirs, b_dirs = {}, {}
    for day, day_df in disc.groupby(disc.index.date):
        sigs = bpr._signals(s011.generate_signals, day_df, disc)
        if sigs:
            a_dirs[str(day)] = sigs[0].direction.lower()
        d, imb = s013_direction(day_df)
        if d != 0:
            b_dirs[str(day)] = "long" if d > 0 else "short"

    A, B = set(a_dirs), set(b_dirs)
    both = A & B
    same_dir = [d for d in both if a_dirs[d] == b_dirs[d]]
    out = {
        "slice": "discovery",
        "s011_sessions": len(A),
        "s013_sessions": len(B),
        "jointly_selected": len(both),
        "jaccard_session_overlap_pct": round(100.0 * len(both) / len(A | B), 2) if (A | B) else 0.0,
        "share_of_s013_sessions_also_s011_pct": round(100.0 * len(both) / len(B), 2) if B else 0.0,
        "same_direction_on_joint_sessions": len(same_dir),
        "same_direction_pct": round(100.0 * len(same_dir) / len(both), 2) if both else 0.0,
        "opposite_direction_on_joint_sessions": len(both) - len(same_dir),
        "note": ("both enter on session T and exit 15:55 ET of T; a same-direction "
                 "joint session is the same position, not a second bet"),
    }
    print(json.dumps(out, indent=2))
    (PROJECT_ROOT / "data" / "overlap_S013_vs_S011.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

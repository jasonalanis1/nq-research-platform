#!/usr/bin/env python3
"""UPGRADE 4 -- the BLIND Integrity Gate packet.

The Gate is not independent when the session that produced a number then
reviews it. So the two checkpoints (before Validation, before Holdout) run
in a FRESH context that receives only this packet: the frozen spec, the
scan/test code, the mechanism doc, and the ledger history for the family --
with every result figure MASKED. It rules on whether the PROCEDURE could
fool us. Only after it rules are the numbers unmasked and the ruling logged
alongside them.

Continuous-role duties (freeze rules, resurrection, multiplicity tracking)
stay in-session. Only the checkpoints go blind.

    python3 src/integrity_blind_packet.py --family <idea_key> \\
        --spec research/studies/<spec>.md --code src/<study>.py \\
        [--mechanism research/mechanisms/<doc>.md] -o research/_blind/<name>.md
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "research" / "ledger" / "hypotheses.jsonl"

# Ledger fields that ARE results (masked) vs. procedure (kept).
RESULT_FIELDS = ("trade_count", "expectancy_r", "profit_factor", "max_drawdown_r",
                 "strategy_status", "notes")
KEEP_FIELDS = ("hypothesis_id", "logged_at", "strategy_name", "strategy_origin", "parameters",
               "data_slice_used", "parent_hypothesis_id", "experiment_doc_id", "holdout_slot_id",
               "search_batch_id")

MASK = "[masked]"
# Result-looking tokens in prose: signed decimals with an optional R, n=NNN,
# CI brackets, percentages, PASS/FAIL verdict words, and win/expectancy words
# followed by a number. Bucket edges and horizons are procedure and are kept
# where they are written as plain integers (e.g. "10-day", "tercile 3").
_PATTERNS = [
    re.compile(r"\[\s*[-+]?\d+(?:\.\d+)?\s*,\s*[-+]?\d+(?:\.\d+)?\s*\]"),      # [0.05, 0.52]
    re.compile(r"(?i)\b(?:n|trades?|sample)\s*=\s*\d+"),                       # n=213
    re.compile(r"[-+]?\d+\.\d+\s*R\b"),                                         # +0.28R
    re.compile(r"[-+]?\d+\.\d+\s*%"),                                           # 12.5%
    re.compile(r"(?i)\b(?:mean_r|mean r|expectancy|win rate|profit factor|ci_90|ci90|"
               r"p-value|p =|sharpe|drawdown)\b[^\n]{0,40}?[-+]?\d+(?:\.\d+)?"),
    re.compile(r"(?i)\b(?:DISCOVERY|PROSPECTIVE|HOLDOUT|VALIDATION)_(?:PASS|FAIL)\b"),
    re.compile(r"(?i)\b(?:CI entirely above zero|CI clears zero|clears zero|fails to clear)\b"),
    # Any number with two or more decimals is a measured quantity (ratios,
    # R, correlations). Procedure constants are integers or one-decimal
    # (20-day, 20th percentile, 1.0 threshold) and survive.
    re.compile(r"[-+]?\d+\.\d{2,}"),
    re.compile(r"(?i)\b(?:first|second) half\s+mean\s*=?\s*" + MASK.replace("[", "\\[").replace("]", "\\]")),
]


def mask_text(text: str) -> str:
    out = text
    for pat in _PATTERNS:
        out = pat.sub(MASK, out)
    return out


def family_rows(key: str) -> list[dict]:
    rows = []
    if not LEDGER.exists():
        return rows
    for line in LEDGER.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if key.lower() in (r.get("strategy_name") or "").lower():
            row = {k: r.get(k) for k in KEEP_FIELDS} | {f: MASK for f in RESULT_FIELDS if f in r}
            # "parameters" mixes procedure (windows, thresholds) with results
            # (mean_ratio, ci) on older rows -- mask it as prose.
            if row.get("parameters") is not None:
                row["parameters"] = mask_text(json.dumps(row["parameters"], default=str))
            rows.append(row)
    return rows


def build(family: str, spec: Path, code: Path, mechanism: Path | None) -> str:
    parts = [
        "# BLIND INTEGRITY GATE PACKET",
        "",
        "You are the Integrity Gate, in a fresh context. Standing brief: assume this",
        "candidate is wrong; find every reason the PROCEDURE could be fooling us.",
        "Every result figure below is masked on purpose. Rule PASS / VETO / CONDITIONAL",
        "on procedure only: leakage, contamination, post-hoc selection, frozen-before-",
        "test, resurrection, multiplicity accounting, direction pre-registered, cost model",
        "measured not assumed, review point sized (power) before freezing.",
        "Output: Finding / Confidence / Novelty / Research Value / Recommendation.",
        "",
        f"## Family: {family}",
        "",
        "## Frozen spec (masked)",
        "",
        mask_text(spec.read_text(errors="replace")),
        "",
        "## Mechanism doc (masked)",
        "",
        mask_text(mechanism.read_text(errors="replace")) if mechanism and mechanism.exists()
        else "(NONE ON DISK -- that is itself a Mechanism Gate finding)",
        "",
        "## Test / scan code (as-is; contains no results)",
        "",
        "```python",
        code.read_text(errors="replace"),
        "```",
        "",
        "## Ledger history for this family (results masked)",
        "",
        "```json",
        json.dumps(family_rows(family), indent=1, default=str),
        "```",
    ]
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--family", required=True)
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--code", required=True, type=Path)
    ap.add_argument("--mechanism", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    a = ap.parse_args()
    packet = build(a.family, a.spec, a.code, a.mechanism)
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(packet)
        print(f"wrote {a.out} ({len(packet)} chars)")
    else:
        print(packet)


if __name__ == "__main__":
    main()

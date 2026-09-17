#!/usr/bin/env python3
"""
rerun_salvages.py -- re-run every Salvage check that was decided on INVENTED
reference labels, and re-decide the candidates those salvages spawned.

WHY THIS EXISTS (Jason, September 16th 2026, follow-up 1)
    "Once VXN and the calendar are current, rerun every Salvage check done with
     the bad labels (S007-S010), and re-decide S009a and S010a from the
     corrected results. Mark the old salvage results superseded, don't delete
     them."

WHAT WAS WRONG WITH THE OLD RESULTS
    src/salvage_check.py's menu condition 4 asked `d in FOMC_SET` and called
    every miss QUIET. The sourced lists end 2021-09-22 (FOMC), 2023-12-12 (CPI)
    and 2023-12-08 (NFP), and the honest macro coverage end is the MINIMUM of
    the three -- so any trade dated after 2021-09-22 was "a day with no
    scheduled release" because the list stops there, not because the day was
    quiet. Menu condition 1 had the same shape of defect against the VXN series
    (a forward-filled close), though as it happens no salvage's trades reach
    past the VXN end. Conditions 2 and 3 are derived from price bars and the
    clock only and were never affected.

THE RULE THIS SCRIPT ENFORCES, AND THE POINT OF IT
    IT REFUSES TO RUN ON STALE DATA. A rerun computed on the same invented
    labels would be worthless and would look authoritative, which is worse than
    no rerun at all. Every salvage names the series its menu conditions read;
    each of those series must cover EVERY TRADE DATE in that salvage's screen
    result before it will run. Otherwise it prints what is missing, which
    updater extends it, and exits non-zero having written nothing.

WHAT IT DOES WHEN COVERAGE IS CURRENT
    * re-runs each owed salvage against the SAME frozen screen result and the
      SAME frozen strategy module -- nothing is re-specified, re-screened or
      re-fit, so the only thing that changes is the reference labels;
    * writes a NEW salvage artefact and a NEW registry SALVAGE row that says
      what it supersedes. The originals are never deleted or edited;
    * re-decides the spawned candidates (S009a, S010a) from the corrected
      results under directive s.7: ONE salvage per strategy, MENU CONDITIONS
      ONLY, and a condition that can only be known after the fact is refused as
      a filter (see EX_POST_ONLY below) -- a spawn must be a rule a trader could
      have followed on the morning of the session.

USAGE
    python3 src/rerun_salvages.py                 # check coverage, report, do nothing
    python3 src/rerun_salvages.py --run           # re-run (refuses if coverage is stale)
    TONY_PRODUCTION=1 python3 src/rerun_salvages.py --run --write   # + registry rows
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

DATA_DIR = PROJECT_ROOT / "data"

# Which reference series each Salvage MENU condition reads (directive s.7).
CONDITION_SERIES = {
    1: ["VXN"],                 # VXN vs its trailing level
    2: [],                      # the day's own RTH range vs trailing -- price only
    3: [],                      # the signal's trigger time -- clock only
    4: ["FOMC", "CPI", "NFP"],  # scheduled-news day
}
MENU_SERIES = sorted({s for v in CONDITION_SERIES.values() for s in v})

# Conditions that are EX-POST ONLY: knowable only after the session they
# describe is over, so they cannot become a filter on a new candidate. Menu
# condition 2 measures the day's OWN RTH range against its trailing average --
# a trader at 09:30 does not have it. Conditions 1 (prior day's VXN close),
# 3 (the signal's own trigger time) and 4 (a published schedule) are all known
# before the trade. The Integrity Gate rejects a salvage that reads as "find the
# slice that looks good"; this is the same rule applied to time.
EX_POST_ONLY = {2}

# Spec-named `--extra` fields that are known AT SIGNAL TIME and may therefore
# carry a spawn. Anything not listed is refused rather than assumed tradeable.
EX_ANTE_SPEC_FIELDS = {"level_source", "direction"}

# The owed reruns. `screen` and `extra` reproduce EXACTLY the inputs the original
# salvage ran on -- the frozen screen result and the same spec-named fields --
# so the reference labels are the only thing that differs.
SALVAGE_INPUTS = {
    # S004 is NOT a rerun: it was KILLED on 2026-09-17 by
    # research/studies/S004-scrutiny-2026-09-17.md and its FIRST salvage is owed,
    # blocked by the same series. It joins this table because the refusal, the
    # coverage check and the s.7 spawn rules are identical whether a salvage is
    # owed for the first time or owed again. Its screen output nests the trades
    # under "strategy" (two arms), hence `trades_path`.
    "S004": {"screen": "data/screen_S004_with_baseline.json",
             "trades_path": ["strategy", "trades_detail"], "extra": ["direction"],
             "original": None, "spawn": "S004a"},
    "S007": {"screen": "data/screen_S007.json", "extra": ["direction"],
             "original": "data/salvage_S007_2026-09-16.json", "spawn": None},
    "S009": {"screen": "data/screen_S009.json", "extra": ["direction"],
             "original": "data/salvage_S009_2026-09-16.json", "spawn": "S009a"},
    "S010": {"screen": "data/screen_S010.json", "extra": ["direction"],
             "original": "data/salvage_S010_2026-09-16.json", "spawn": "S010a"},
    "S001": {"screen": "data/screen_S001_2026-09-15.json",
             "extra": ["level_source", "direction"],
             "original": "data/salvage_S001_2026-09-15.json", "spawn": "S001a"},
}


class CoverageStale(RuntimeError):
    """Raised instead of producing a rerun on the same invented labels."""


# ---------------------------------------------------------------------------
# what is owed
# ---------------------------------------------------------------------------
def owed(registry_rows: list | None = None) -> list[str]:
    """Every salvage this module is on the hook for, in registry order:

      * a SUPERSEDED salvage row with no later SALVAGE row -- a RERUN owed
        because the original was decided on invented labels (S007, S009); and
      * a KILL with no SALVAGE row at all -- a FIRST salvage owed because the
        s.7 check was blocked by the reference-data gate when the KILL was
        recorded (S004, killed 2026-09-17 on
        research/studies/S004-scrutiny-2026-09-17.md).

    Both are owed for the same reason and are refused for the same reason, so
    they run through the same door. THE REGISTRY IS THE AUTHORITY on what is
    owed -- never this module's table; an id with no SALVAGE_INPUTS entry is
    left out because this module has no inputs to run it on, not because it is
    not owed."""
    import strategy_registry as sr
    rows = registry_rows if registry_rows is not None else sr.read_rows()
    out = [r["strategy_id"] for r in sr.superseded_salvages(rows)]
    has_salvage = {r["strategy_id"] for r in rows if r.get("stage") == "SALVAGE"}
    for r in sr.salvage_queue(rows):
        sid = r["strategy_id"]
        if sid not in has_salvage and sid not in out and sid in SALVAGE_INPUTS:
            out.append(sid)
    return out


def screen_trades(strategy_id: str) -> list:
    """The frozen screen result's trade list, wherever that file keeps it."""
    meta = SALVAGE_INPUTS[strategy_id]
    res = json.loads((PROJECT_ROOT / meta["screen"]).read_text())
    node = res
    for key in meta.get("trades_path", ["trades_detail"]):
        node = node[key]
    return node


def screen_strategy_name(strategy_id: str) -> str | None:
    meta = SALVAGE_INPUTS[strategy_id]
    res = json.loads((PROJECT_ROOT / meta["screen"]).read_text())
    for key in meta.get("trades_path", ["trades_detail"])[:-1]:
        res = res[key]
    return res.get("strategy_name")


def trade_dates(strategy_id: str) -> list:
    return sorted({date.fromisoformat(str(t["date"])[:10])
                   for t in screen_trades(strategy_id)})


# ---------------------------------------------------------------------------
# the refusal
# ---------------------------------------------------------------------------
_UNSET = object()   # "look it up"; an explicit None means "no coverage at all"


def coverage_check(strategy_id: str, vxn_end=_UNSET, macro_end=_UNSET) -> dict:
    """Does every series this salvage's menu conditions read cover every trade
    date in its screen result?

    A missing coverage end is treated as NOT COVERING anything (fail closed) --
    'we have no record of how far it reaches' is not evidence that it reaches
    far enough."""
    if vxn_end is _UNSET:
        from reference_data import vxn_coverage_end
        try:
            vxn_end = vxn_coverage_end()
        except Exception:  # noqa: BLE001
            vxn_end = None
    if macro_end is _UNSET:
        from reference_data import macro_coverage_end
        macro_end = macro_coverage_end()

    dates = trade_dates(strategy_id)
    last = max(dates) if dates else None
    ends = {"VXN": vxn_end, "FOMC": macro_end, "CPI": macro_end, "NFP": macro_end}
    series = {}
    for name in MENU_SERIES:
        end = ends.get(name)
        uncovered = [d for d in dates if end is None or d > end]
        series[name] = {
            "covered_through": end.isoformat() if isinstance(end, date) else None,
            "last_trade_date": last.isoformat() if last else None,
            "uncovered_trades": len(uncovered),
            "first_uncovered": uncovered[0].isoformat() if uncovered else None,
            "ok": not uncovered,
            "updater": ("src/data_topup_vxn.py" if name == "VXN"
                        else "src/data_topup_macro_calendar.py"),
        }
    missing = sorted(n for n, r in series.items() if not r["ok"])
    return {"strategy_id": strategy_id, "ok": not missing, "series": series,
            "stale_series": missing, "n_trades": len(dates),
            "reason": ("every series the menu reads covers every trade date" if not missing else
                       "; ".join(f"{n} covers through {series[n]['covered_through']} but "
                                 f"{series[n]['uncovered_trades']} trade(s) fall after it "
                                 f"(first {series[n]['first_uncovered']})" for n in missing))}


def require_current(strategy_id: str, **kw) -> dict:
    chk = coverage_check(strategy_id, **kw)
    if not chk["ok"]:
        fixes = sorted({chk["series"][n]["updater"] for n in chk["stale_series"]})
        raise CoverageStale(
            f"REFUSING to re-run the {strategy_id} salvage: {chk['reason']}. "
            f"A rerun on the same invented labels would look authoritative and be worth nothing, "
            f"which is worse than no rerun. Extend coverage first -- {', '.join(fixes)} -- "
            f"from Jason's own Terminal (the sandboxed shells are HTTP 403 at the proxy for "
            f"cboe.com, federalreserve.gov and bls.gov).")
    return chk


# ---------------------------------------------------------------------------
# re-decide a spawn from a corrected salvage (directive s.7)
# ---------------------------------------------------------------------------
def _condition_number(condition_label: str) -> int | None:
    head = str(condition_label).strip()[:2].strip().rstrip(".")
    return int(head) if head.isdigit() else None


def redecide_spawn(salvage_result: dict, strategy_id: str) -> dict:
    """Directive s.7, applied to a corrected salvage result.

    ONE salvage per strategy: exactly one condition may carry a spawn, and it is
    the best profitable EX-ANTE condition. Menu conditions only, plus the
    spec-named fields the Mechanism agent declared -- and only those knowable at
    signal time. An ex-post-only condition (menu 2) and an unlisted spec field
    are REFUSED as filters and said so out loud, not silently dropped."""
    eligible, refused = [], []
    for f in salvage_result.get("profitable_conditions", []):
        label = f["condition"]
        num = _condition_number(label)
        if num in EX_POST_ONLY:
            refused.append({**f, "refused_because": (
                f"menu condition {num} is EX-POST ONLY -- it measures the session's own outcome, so it "
                "cannot be a filter a trader could apply before the trade")})
            continue
        if num is None:
            field = label.split(":", 1)[-1].strip()
            if field not in EX_ANTE_SPEC_FIELDS:
                refused.append({**f, "refused_because": (
                    f"spec-named field {field!r} is not on the ex-ante whitelist "
                    f"{sorted(EX_ANTE_SPEC_FIELDS)} -- refused rather than assumed tradeable")})
                continue
        eligible.append(f)

    eligible.sort(key=lambda f: (f["net_usd_1"], f["n"]), reverse=True)
    taken = eligible[0] if eligible else None
    return {
        "strategy_id": strategy_id,
        "spawn": taken is not None,
        "taken": taken,
        "not_taken": eligible[1:],
        "refused": refused,
        "rule": ("directive s.7: one salvage per strategy, menu conditions only, and a condition that "
                 "is only knowable after the session cannot become a filter"),
        "verdict": (f"condition taken: {taken['condition']} = {taken['side']} "
                    f"(n={taken['n']}, net ${taken['net_usd_1']:+,.2f}, avg {taken['avg_r_net']:+.3f}R)"
                    if taken else
                    "NOTHING TAKEN -- no ex-ante menu condition was profitable with enough trades; "
                    "the strategy stays KILLED and the spawn is dropped to LEARN"),
    }


# ---------------------------------------------------------------------------
# the rerun
# ---------------------------------------------------------------------------
def rerun_one(strategy_id: str, df=None, today=None) -> dict:
    """Re-run ONE owed salvage against its own frozen screen result. Refuses
    first; never writes anything on a refusal."""
    require_current(strategy_id)
    import salvage_check as sc
    meta = SALVAGE_INPUTS[strategy_id]
    out = sc.run(screen_trades(strategy_id), df, list(meta["extra"]))
    out["strategy_name"] = screen_strategy_name(strategy_id)
    out["screen_source"] = meta["screen"]
    out["rerun_of"] = meta["original"]
    out["rerun_at"] = (today or datetime.now(timezone.utc).date()).isoformat()
    out["rerun_reason"] = (
        ("the original was computed on reference labels past the macro calendar's "
         "coverage end; menu condition 4 defaulted to QUIET. Same frozen screen "
         "result, same frozen module, corrected labels.") if meta["original"] else
        ("FIRST salvage, not a rerun: the mandatory s.7 check was BLOCKED by the "
         "reference-data gate when the KILL was recorded, and was never run partially "
         "and never defaulted. Same frozen screen result, same frozen module."))
    out["condition_2_note"] = ("price-derived, unchanged by this rerun -- kept in the output so the two "
                               "results can be compared line for line")
    if meta.get("spawn"):
        out["spawn_decision"] = redecide_spawn(out, meta["spawn"])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--run", action="store_true", help="actually re-run (refuses on stale coverage)")
    ap.add_argument("--write", action="store_true", help="also append registry SALVAGE rows")
    ap.add_argument("--only", default="", help="comma-separated strategy ids")
    a = ap.parse_args(argv)

    todo = owed()
    if a.only:
        wanted = {x.strip() for x in a.only.split(",") if x.strip()}
        todo = [s for s in todo if s in wanted]
    print("=" * 78)
    print("SALVAGE RERUNS -- owed: " + (", ".join(todo) if todo else "none"))
    print("=" * 78)
    if not todo:
        print("  Nothing is owed: no SUPERSEDED salvage row is missing its rerun and no "
              "KILL is missing its first salvage.")
        return 0

    checks = {s: coverage_check(s) for s in todo}
    for s, c in checks.items():
        print(f"  [{'ok' if c['ok'] else 'STALE'}] {s}: {c['reason']}")
    stale = [s for s, c in checks.items() if not c["ok"]]
    if stale:
        print()
        print("REFUSING TO RUN. The whole point of the rerun is that the old results were computed on")
        print("invented labels; producing new ones the same way would be worse than producing none.")
        for s in stale:
            for n in checks[s]["stale_series"]:
                print(f"  {s} <- {n}: extend with {checks[s]['series'][n]['updater']} "
                      f"(Jason's own Terminal -- the sandboxed shells are 403 at the proxy)")
        return 2
    if not a.run:
        print("\n  Coverage is CURRENT. Re-run with --run (add --write to record the registry rows).")
        return 0

    from data_loader import load_price_data
    from data_split import get_discovery_data
    full, synthetic = load_price_data(context="rerun_salvages", apply_holdout=True)
    if synthetic:
        raise SystemExit("synthetic data -- refusing")
    df = get_discovery_data(full)

    stamp = datetime.now(timezone.utc).date().isoformat()
    for s in todo:
        out = rerun_one(s, df)
        path = DATA_DIR / f"salvage_{s}_rerun_{stamp}.json"
        path.write_text(json.dumps(out, indent=1, default=str))
        print(f"\n  {s}: {out['verdict']}\n    -> {path}")
        if out.get("spawn_decision"):
            print(f"    spawn {out['spawn_decision']['strategy_id']}: {out['spawn_decision']['verdict']}")
        if a.write:
            import strategy_registry as sr
            from production_paths import enable_production
            enable_production("salvage rerun registry rows")
            sr.append({"strategy_id": s, "name": out.get("strategy_name") or s, "stage": "SALVAGE",
                       "verdict": out["verdict"],
                       "notes": ((f"RERUN OF RECORD, superseding {out['rerun_of']} (Jason's follow-up 1, "
                                  f"September 16th 2026). " if out["rerun_of"] else
                                  "FIRST salvage (directive s.7), owed since the KILL and blocked until "
                                  "coverage was current. ") + f"{out['rerun_reason']} Artefact: "
                                 f"{path.relative_to(PROJECT_ROOT)}. The original row and artefact are "
                                 f"untouched."),
                       "lineage": s})
            sd = out.get("spawn_decision")
            if sd:
                sr.append({"strategy_id": sd["strategy_id"],
                           "name": f"{sd['strategy_id']} re-decided from the corrected salvage",
                           "stage": "SPECIFY" if sd["spawn"] else "LEARN",
                           "notes": f"{sd['verdict']} ({sd['rule']}). Released from "
                                    f"BLOCKED_PENDING_REFERENCE_DATA by {path.relative_to(PROJECT_ROOT)}.",
                           "lineage": s})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

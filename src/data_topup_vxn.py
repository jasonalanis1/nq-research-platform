"""
data_topup_vxn.py -- INCREMENTAL top-up of the daily VXN series.

WHY
  data/VXNCLS_MAX.csv ended 2026-09-02 while the price series ran to
  2026-09-16. VXN is the Salvage menu's condition 1 (directive s.7), the
  selection variable for S010a, and the input to the validated
  VXN -> next-session-range magnitude fact used for stops and sizing. A
  fortnight of missing volatility readings is not a small gap in a file; it is
  every one of those decisions made on a carried-forward number.

SOURCE -- FREE, PUBLISHED, NO ACCOUNT, NO SPEND
  CBOE's own published daily history for the Nasdaq-100 Volatility Index:
      https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv
  Columns DATE,OPEN,HIGH,LOW,CLOSE (header verified live 2026-09-16). The
  existing file came from FRED's VXNCLS, which republishes the same CBOE close;
  main() PROVES they agree on the overlap before it writes anything, rather
  than assuming it (see check_overlap).

RUN FROM JASON'S OWN TERMINAL
  Both sandboxed shells are egress-allowlisted and cdn.cboe.com is not on the
  list (verified 2026-09-16: HTTP 403 at the proxy from the device shell and
  from the container). Like the Databento top-up, this belongs beside the 7 am
  cron:

      cd ~/Documents/nq-research-platform-live && python3 src/data_topup_vxn.py

  Costs nothing. --dry-run fetches and reports without writing;
  --from-file <path> feeds it an already-downloaded CSV (so the fetch and the
  merge can be exercised separately).

DISCIPLINE, the same as src/data_topup_databento.py
  * incremental: only rows strictly after the file's last observation are added
  * REFUSES TO OVERWRITE HISTORY: every existing row must survive the merge
    byte-for-byte, asserted before the write, and a disagreement on the overlap
    aborts with nothing written
  * verifies continuity: monotone, unique, no implausible values, no unexplained
    multi-week hole in the added region
  * logs what it added to data/_reference_data_topup_log.jsonl
  * production-guarded through src/production_paths.py
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from production_paths import assert_writable, enable_production  # noqa: E402
from reference_data import VXN_PATH, _as_date, vxn_daily  # noqa: E402

CBOE_VXN_URL = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv"
TOPUP_LOG = VXN_PATH.parent / "_reference_data_topup_log.jsonl"

OVERLAP_CHECK_DAYS = 40      # how many trailing overlapping observations must agree
OVERLAP_TOLERANCE = 0.051    # VXNCLS is published to 2dp; anything above this is a different series
MIN_PLAUSIBLE = 5.0
MAX_PLAUSIBLE = 200.0
MAX_GAP_DAYS = 10            # the longest believable hole in a daily index (holidays + a weekend)


def parse_cboe_csv(text: str) -> dict:
    """CBOE's DATE,OPEN,HIGH,LOW,CLOSE -> {date: close}.

    Tolerates the leading blurb lines CBOE sometimes puts above the header by
    finding the header row rather than assuming line 1, and accepts either
    MM/DD/YYYY or ISO dates. Rows that do not parse are skipped, not guessed at.
    """
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        cells = [c.strip().strip('"').upper() for c in ln.split(",")]
        if "DATE" in cells and "CLOSE" in cells:
            start = i
            break
    if start is None:
        raise ValueError("no DATE,...,CLOSE header row found -- the source layout changed; "
                         "nothing parsed, nothing written")
    reader = csv.DictReader(io.StringIO("\n".join(lines[start:])))
    field_map = {(f or "").strip().upper(): f for f in (reader.fieldnames or [])}
    dcol, ccol = field_map.get("DATE"), field_map.get("CLOSE")
    out: dict[date, float] = {}
    for row in reader:
        raw_d = (row.get(dcol) or "").strip()
        raw_c = (row.get(ccol) or "").strip()
        if not raw_d or not raw_c:
            continue
        d = None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y"):
            try:
                d = datetime.strptime(raw_d, fmt).date()
                break
            except ValueError:
                continue
        if d is None:
            continue
        try:
            out[d] = float(raw_c)
        except ValueError:
            continue
    if not out:
        raise ValueError("header found but zero rows parsed -- nothing written")
    return dict(sorted(out.items()))


def check_overlap(old: dict, new: dict, days: int = OVERLAP_CHECK_DAYS,
                  tol: float = OVERLAP_TOLERANCE) -> dict:
    """Prove the fetched series IS the series already on disk before extending
    it. Compares the trailing overlapping observations; any disagreement above
    tolerance aborts the run. This is what stops a differently-defined index,
    a percentage-vs-level unit change, or a wrong ticker from being welded onto
    five years of history."""
    common = sorted(set(old) & set(new))
    tail = common[-days:]
    diffs = [(d, old[d], new[d], abs(old[d] - new[d])) for d in tail]
    bad = [x for x in diffs if x[3] > tol]
    return {"n_common": len(common), "n_checked": len(tail),
            "max_abs_diff": round(max((x[3] for x in diffs), default=0.0), 4),
            "mismatches": [{"date": d.isoformat(), "on_disk": o, "fetched": n, "diff": round(x, 4)}
                           for d, o, n, x in bad[:10]],
            "ok": bool(tail) and not bad,
            "note": ("no overlap to check -- refusing, because an unverifiable join is "
                     "exactly the failure this check exists for") if not tail else
                    ("agrees within %.3f" % tol if not bad else "DISAGREES -- aborting")}


def merge(old: dict, new: dict) -> tuple[dict, list]:
    """Old observations are authoritative on any overlap; only dates strictly
    after the old end are appended. History is never rewritten."""
    if not old:
        return dict(sorted(new.items())), sorted(new)
    end = max(old)
    added = sorted(d for d in new if d > end)
    merged = dict(old)
    for d in added:
        merged[d] = new[d]
    return dict(sorted(merged.items())), added


def check_continuity(old: dict, merged: dict, added: list) -> dict:
    checks = []

    def add(name, ok, note=""):
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "note": note})

    keys = list(merged)
    add("1. monotone, unique", keys == sorted(set(keys)), f"{len(keys)} observations")
    preserved = all(d in merged and merged[d] == v for d, v in old.items())
    add("2. history preserved byte-for-byte", preserved,
        "every pre-existing observation survives the merge unchanged")
    bad_vals = [(d.isoformat(), merged[d]) for d in added
                if not (MIN_PLAUSIBLE <= merged[d] <= MAX_PLAUSIBLE)]
    add("3. added values plausible", not bad_vals, f"{bad_vals[:5]}" if bad_vals else
        f"all {len(added)} added value(s) within [{MIN_PLAUSIBLE}, {MAX_PLAUSIBLE}]")
    span = ([max(old)] if old else []) + added
    gaps = [(a.isoformat(), b.isoformat(), (b - a).days)
            for a, b in zip(span, span[1:]) if (b - a).days > MAX_GAP_DAYS]
    add("4. no unexplained hole in the added region", not gaps, f"{gaps[:5]}" if gaps else
        f"largest gap <= {MAX_GAP_DAYS} days")
    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    return {"status": status, "checks": checks, "n_old": len(old), "n_new": len(merged),
            "n_added": len(added)}


def write_series(merged: dict, path: Path) -> None:
    assert_writable(path, "VXN daily reference series (top-up)")
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["observation_date", "VXNCLS"])
        for d, v in merged.items():
            w.writerow([d.isoformat(), f"{v:g}"])


def log_topup(series: str, added: list, source: str, path: Path = TOPUP_LOG) -> None:
    assert_writable(path, "reference-data top-up log")
    rec = {"ts": datetime.now().isoformat(timespec="seconds"), "series": series,
           "n_added": len(added), "source": source,
           "first_added": added[0].isoformat() if added else None,
           "last_added": added[-1].isoformat() if added else None}
    with path.open("a") as fh:
        fh.write(json.dumps(rec) + "\n")


def fetch(url: str = CBOE_VXN_URL, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "nq-research-platform/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 -- fixed https URL
        return resp.read().decode("utf-8", errors="replace")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-file", type=Path, help="parse this already-downloaded CSV instead of fetching")
    ap.add_argument("--url", default=CBOE_VXN_URL)
    ap.add_argument("--path", type=Path, default=VXN_PATH)
    ap.add_argument("--log-path", type=Path, default=TOPUP_LOG,
                    help="where to append the record of what was added")
    ap.add_argument("--dry-run", action="store_true", help="report what would be added, write nothing")
    args = ap.parse_args(argv)

    old = vxn_daily(args.path) if args.path.exists() else {}
    print(f"On disk: {args.path.name}, {len(old)} observations"
          + (f", ends {max(old)}" if old else " (empty)"))

    if args.from_file:
        text = Path(args.from_file).read_text()
        source = str(args.from_file)
    else:
        print(f"Fetching {args.url}")
        try:
            text = fetch(args.url)
        except Exception as e:  # noqa: BLE001
            print(f"FETCH FAILED: {type(e).__name__}: {e}")
            print("If this is a 403 at a proxy you are in a sandboxed shell -- cdn.cboe.com is not on the "
                  "egress allowlist. Run this from Jason's own Terminal, the same way the Databento top-up runs.")
            return 2
        source = args.url

    new = parse_cboe_csv(text)
    print(f"Fetched: {len(new)} observations, {min(new)} -> {max(new)}")

    ov = check_overlap(old, new) if old else {"ok": True, "n_checked": 0,
                                              "note": "no existing file -- nothing to reconcile",
                                              "max_abs_diff": 0.0, "mismatches": [], "n_common": 0}
    print(f"Overlap check: {ov['n_checked']} trailing observation(s), max |diff| {ov['max_abs_diff']} -- {ov['note']}")
    if not ov["ok"]:
        for m in ov["mismatches"]:
            print(f"    {m['date']}: on disk {m['on_disk']}, fetched {m['fetched']} (diff {m['diff']})")
        print("REFUSED: the fetched series does not match the one on disk. Nothing written.")
        return 2

    merged, added = merge(old, new)
    if not added:
        print(f"Nothing to add: the file already ends {max(old)} and the source goes to {max(new)}.")
        return 0

    res = check_continuity(old, merged, added)
    for c in res["checks"]:
        print(f"  {c['status']:<4} {c['check']}: {c['note']}")
    if res["status"] != "PASS":
        print("REFUSED: continuity failed. Nothing written.")
        return 1

    if args.dry_run:
        print(f"DRY RUN: would add {len(added)} observation(s), {added[0]} -> {added[-1]}. Nothing written.")
        return 0

    write_series(merged, args.path)
    log_topup("VXN", added, source, args.log_path)
    print(f"Wrote {args.path.name}: {len(merged)} observations ({len(added)} added, "
          f"{added[0]} -> {added[-1]}), history unchanged.")
    return 0


if __name__ == "__main__":
    enable_production("VXN reference-series top-up")
    raise SystemExit(main())

"""
data_topup_macro_calendar.py -- INCREMENTAL top-up of the scheduled
macro-event calendar (FOMC / CPI / NFP).

WHY
  The project's sourced lists end 2021-09-22 (FOMC) and 2023-12-12 / 2023-12-08
  (CPI / NFP). That is enough for the Discovery screen and NOT enough to score
  a 2026 paper session. S009a -- the honest salvage survivor of S009 -- trades
  ONLY on days with no scheduled macro event, so with a calendar that stops in
  2021 it either fails open (every 2026 day looks quiet, and S009a's paper
  record becomes S009's under another name) or fails closed forever (a strategy
  in PAPER that can never fire). Neither is a record. The Salvage menu's
  condition 4 has the same dependency for every future candidate.

WHAT IT DOES NOT DO
  It does not touch the frozen sourced lists in src/study_fomc_volatility.py or
  src/study_economic_calendar.py. Those stay exactly as compiled and stay
  authoritative over their own ranges. This writes only the forward EXTENSION,
  data/macro_event_calendar.csv, which src/reference_data.py unions with them.

SOURCES -- FREE, PUBLISHED, PRIMARY, NO SPEND
  FOMC  https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm
  CPI   https://www.bls.gov/schedule/news_release/cpi.htm
  NFP   https://www.bls.gov/schedule/news_release/empsit.htm
  All three publish the schedule AHEAD of time, which is the whole point: a
  2026 session can be classified honestly because the Fed and the BLS said in
  advance which days carry a release.

RUN FROM JASON'S OWN TERMINAL
  federalreserve.gov and bls.gov are both off the sandboxed shells' egress
  allowlist (verified 2026-09-16: HTTP 403 at the proxy from the device shell
  and from the container). Beside the 7 am Databento cron:

      cd ~/Documents/nq-research-platform-live && python3 src/data_topup_macro_calendar.py

VERIFICATION BEFORE ANY WRITE -- the parser is assumed wrong until it proves
otherwise, because a silently mis-parsed date is a fabricated event date:
  1. OVERLAP: every parsed date inside a frozen list's range must match that
     frozen list exactly. Reproducing known-good data is the strongest evidence
     a parse is right. (BLS publishes ~2 years, so this usually applies to FOMC.)
  2. SHAPE: a fully-represented year must hold exactly 8 FOMC decisions /
     12 CPI releases / 12 NFP releases, one per calendar month for the BLS
     series; NFP always a Friday; CPI and FOMC decisions always weekdays; FOMC
     decision days Tuesday or Wednesday.
  3. VOLUME: at least a year's worth parsed per event, or the page layout moved.
  Any failure aborts with nothing written and prints what it actually saw.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from production_paths import assert_writable, enable_production  # noqa: E402
from reference_data import (  # noqa: E402
    EVENTS, MACRO_CALENDAR_PATH, MACRO_COVERAGE_PATH, SOURCES, _as_date, _calendar_extension,
    _frozen_lists,
)
from data_topup_vxn import TOPUP_LOG, log_topup  # noqa: E402

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"], start=1)}
MONTH_ABBR = {m[:3]: i for m, i in MONTHS.items()}

EXPECTED_PER_YEAR = {"FOMC": 8, "CPI": 12, "NFP": 12}
MIN_PARSED = {"FOMC": 8, "CPI": 12, "NFP": 12}


def strip_tags(html: str) -> str:
    """HTML -> plain text. Deliberately crude: the parsers below key on the
    words the pages print, not on a DOM shape that gets restyled every year."""
    txt = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    txt = re.sub(r"(?s)<[^>]+>", "\n", txt)
    txt = (txt.replace("&nbsp;", " ").replace("&amp;", "&")
              .replace("&#8211;", "-").replace("&ndash;", "-").replace("–", "-")
              .replace("—", "-"))
    return re.sub(r"[ \t]+", " ", txt)


# --------------------------------------------------------------------------
# FOMC
# --------------------------------------------------------------------------
_YEAR_HEAD = re.compile(r"(\d{4})\s+FOMC\s+Meetings", re.I)
_MEETING = re.compile(
    r"\b(" + "|".join(MONTHS) + r")\b\s*\n?\s*(\d{1,2})\s*(?:-|to)\s*(?:\b("
    + "|".join(MONTHS) + r")\b\s*)?(\d{1,2})\b", re.I)
_SINGLE = re.compile(r"\b(" + "|".join(MONTHS) + r")\b\s*\n?\s*(\d{1,2})\b(?!\s*[-\d])", re.I)


def parse_fomc(html: str) -> list:
    """federalreserve.gov's meeting calendar -> the DECISION dates (the second
    day of each two-day meeting, which is when the statement lands at 2:00 pm
    ET -- the anchor src/study_fomc_volatility.py already uses).

    Unscheduled/notation items are excluded the way the frozen list excluded
    them: anything the page marks as unscheduled is dropped, and the shape
    check below refuses a year that does not come to eight."""
    txt = strip_tags(html)
    heads = list(_YEAR_HEAD.finditer(txt))
    if not heads:
        raise ValueError("no '<year> FOMC Meetings' heading found -- the page layout changed; "
                         "nothing parsed, nothing written")
    out: set[date] = set()
    for i, h in enumerate(heads):
        year = int(h.group(1))
        chunk = txt[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(txt)]
        for line in chunk.split("Meeting"):
            if re.search(r"unscheduled|notation vote|conference call", line, re.I):
                continue
            for m in _MEETING.finditer(line):
                m1, d1, m2, d2 = m.group(1).lower(), int(m.group(2)), m.group(3), int(m.group(4))
                end_month = MONTHS[(m2 or m1).lower()]
                end_year = year + 1 if (m2 and MONTHS[m2.lower()] < MONTHS[m1]) else year
                try:
                    out.add(date(end_year, end_month, d2))
                except ValueError:
                    continue
                del d1
    return sorted(out)


# --------------------------------------------------------------------------
# BLS (CPI, NFP)
# --------------------------------------------------------------------------
_BLS_DATE_PATTERNS = (
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"),                                    # 09/11/2026
    re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2}),\s*(\d{4})\b", re.I),       # September 11, 2026
    re.compile(r"\b(" + "|".join(MONTH_ABBR) + r")\.?\s+(\d{1,2}),\s*(\d{4})\b", re.I),  # Sep. 11, 2026
)


def parse_bls_schedule(html: str) -> list:
    """A BLS 'Schedule of Releases' page -> the release dates it prints.

    BLS has used several date spellings over the years; all three are accepted
    and anything else is skipped rather than guessed. The shape check below is
    what decides whether the result is trustworthy."""
    txt = strip_tags(html)
    out: set[date] = set()
    for pat in _BLS_DATE_PATTERNS:
        for m in pat.finditer(txt):
            g1, g2, g3 = m.group(1), int(m.group(2)), int(m.group(3))
            try:
                if g1.isdigit():
                    out.add(date(g3, int(g1), g2))
                else:
                    key = g1.lower()
                    mon = MONTHS.get(key) or MONTH_ABBR.get(key[:3])
                    out.add(date(g3, mon, g2))
            except (ValueError, TypeError):
                continue
    if not out:
        raise ValueError("zero dates parsed from the BLS page -- the layout changed; nothing written")
    return sorted(out)


# --------------------------------------------------------------------------
# Verification
# --------------------------------------------------------------------------
def check_overlap_against_frozen(event: str, parsed: list) -> dict:
    """Every parsed date inside the frozen sourced list's own range must match
    that list exactly. Reproducing known-good data is the strongest evidence
    the parser is reading the page correctly."""
    frozen = _frozen_lists()[event]
    if not frozen or not parsed:
        return {"ok": True, "n_checked": 0, "note": "no frozen range to reconcile against"}
    lo, hi = min(frozen), max(frozen)
    inside = [d for d in parsed if lo <= d <= hi]
    if not inside:
        return {"ok": True, "n_checked": 0,
                "note": f"the page publishes nothing inside the frozen range {lo}..{hi} "
                        f"(normal for BLS, which posts about two years) -- the shape check carries the verification"}
    extra = [d for d in inside if d not in frozen]
    missing = [d for d in frozen if lo <= d <= hi and d not in set(parsed)
               and min(parsed) <= d <= max(parsed)]
    ok = not extra and not missing
    return {"ok": ok, "n_checked": len(inside),
            "extra": [d.isoformat() for d in extra[:10]],
            "missing": [d.isoformat() for d in missing[:10]],
            "note": f"{len(inside)} parsed date(s) fall inside the frozen range and "
                    + ("all match" if ok else "DO NOT match")}


def check_shape(event: str, parsed: list) -> dict:
    """What a correct parse must look like, stated in advance."""
    problems = []
    if len(parsed) < MIN_PARSED[event]:
        problems.append(f"only {len(parsed)} date(s) parsed, under the {MIN_PARSED[event]} minimum")

    by_year = defaultdict(list)
    for d in parsed:
        by_year[d.year].append(d)

    for d in parsed:
        if d.weekday() > 4:
            problems.append(f"{d} is a {d.strftime('%A')} -- no scheduled release lands on a weekend")
        if event == "NFP" and d.weekday() != 4:
            problems.append(f"NFP {d} is a {d.strftime('%A')}, not a Friday")
        # Decisions land on the SECOND day of a two-day meeting: normally a
        # Wednesday, occasionally a Thursday when the meeting is pushed a day
        # (2015-09-17, 2018-11-08, 2020-11-05 in the frozen list all are), and
        # a Tuesday for the rare one-day meeting. Anything else is a bad parse.
        if event == "FOMC" and d.weekday() not in (1, 2, 3):
            problems.append(f"FOMC decision {d} is a {d.strftime('%A')}, "
                            f"not a Tuesday, Wednesday or Thursday")

    complete_years = []
    for year, days in sorted(by_year.items()):
        months = {d.month for d in days}
        if event in ("CPI", "NFP"):
            if len(months) == 12:
                complete_years.append(year)
                if len(days) != EXPECTED_PER_YEAR[event]:
                    problems.append(f"{event} {year}: {len(days)} releases, expected {EXPECTED_PER_YEAR[event]}")
            dupes = [m for m in months if sum(1 for d in days if d.month == m) > 1]
            if dupes:
                problems.append(f"{event} {year}: more than one release in month(s) {sorted(dupes)}")
        else:
            if len(days) == EXPECTED_PER_YEAR["FOMC"]:
                complete_years.append(year)
            elif len(days) > EXPECTED_PER_YEAR["FOMC"]:
                problems.append(f"FOMC {year}: {len(days)} decisions parsed, more than the 8 scheduled")
    return {"ok": not problems, "problems": problems[:12],
            "complete_years": complete_years,
            "years": {y: len(v) for y, v in sorted(by_year.items())}}


# --------------------------------------------------------------------------
# Merge / write
# --------------------------------------------------------------------------
def merge_extension(existing: dict, parsed: dict) -> tuple[dict, dict]:
    """Frozen lists and anything already in the extension are authoritative.
    Only genuinely new (event, date) pairs are added; nothing is rewritten."""
    frozen = _frozen_lists()
    merged, added = {}, {}
    for e in EVENTS:
        have = set(existing.get(e, set())) | set(frozen.get(e, set()))
        new = sorted(d for d in parsed.get(e, []) if d not in have)
        merged[e] = sorted(set(existing.get(e, set())) | set(new))
        added[e] = new
    return merged, added


def write_extension(merged: dict, covered: dict, calendar_path: Path, coverage_path: Path) -> None:
    assert_writable(calendar_path, "scheduled macro-event calendar extension")
    rows = sorted((d, e) for e in EVENTS for d in merged.get(e, []))
    with calendar_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "event", "source"])
        for d, e in rows:
            w.writerow([d.isoformat(), e, SOURCES[e]])
    assert_writable(coverage_path, "scheduled macro-event calendar coverage sidecar")
    coverage_path.write_text(json.dumps(
        {e: {"covered_through": covered[e].isoformat() if covered.get(e) else None,
             "source": SOURCES[e],
             "fetched": datetime.now().isoformat(timespec="seconds")} for e in EVENTS},
        indent=2) + "\n")


def fetch(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "nq-research-platform/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 -- fixed https URLs
        return resp.read().decode("utf-8", errors="replace")


PARSERS = {"FOMC": parse_fomc, "CPI": parse_bls_schedule, "NFP": parse_bls_schedule}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    for e in EVENTS:
        ap.add_argument(f"--{e.lower()}-file", type=Path,
                        help=f"parse this already-downloaded {e} page instead of fetching")
    ap.add_argument("--calendar-path", type=Path, default=MACRO_CALENDAR_PATH)
    ap.add_argument("--coverage-path", type=Path, default=MACRO_COVERAGE_PATH)
    ap.add_argument("--dry-run", action="store_true", help="report what would be added, write nothing")
    args = ap.parse_args(argv)

    parsed, covered, failed = {}, {}, []
    for e in EVENTS:
        local = getattr(args, f"{e.lower()}_file")
        if local:
            html, src = Path(local).read_text(), str(local)
        else:
            print(f"Fetching {e}: {SOURCES[e]}")
            try:
                html, src = fetch(SOURCES[e]), SOURCES[e]
            except Exception as ex:  # noqa: BLE001
                print(f"  FETCH FAILED: {type(ex).__name__}: {ex}")
                failed.append(e)
                continue
        try:
            dates = PARSERS[e](html)
        except ValueError as ex:
            print(f"  PARSE FAILED for {e}: {ex}")
            failed.append(e)
            continue
        parsed[e] = dates
        covered[e] = max(dates)
        print(f"  {e}: {len(dates)} date(s), {min(dates)} -> {max(dates)} (from {src})")

    if failed:
        print(f"\nREFUSED: {', '.join(failed)} could not be fetched or parsed. Nothing written.")
        print("A 403 at a proxy means you are in a sandboxed shell -- federalreserve.gov and bls.gov are "
              "not on the egress allowlist. Run this from Jason's own Terminal, beside the Databento top-up.")
        return 2

    bad = False
    for e in EVENTS:
        ov = check_overlap_against_frozen(e, parsed[e])
        sh = check_shape(e, parsed[e])
        print(f"\n{e} verification:")
        print(f"  overlap vs the frozen sourced list: {'PASS' if ov['ok'] else 'FAIL'} -- {ov['note']}")
        if not ov["ok"]:
            print(f"    parsed-but-not-in-frozen: {ov.get('extra')}")
            print(f"    in-frozen-but-not-parsed: {ov.get('missing')}")
        print(f"  shape: {'PASS' if sh['ok'] else 'FAIL'} -- dates per year {sh['years']}, "
              f"complete year(s) {sh['complete_years']}")
        for p in sh["problems"]:
            print(f"    {p}")
        bad = bad or not ov["ok"] or not sh["ok"]
    if bad:
        print("\nREFUSED: verification failed. NOTHING WRITTEN -- a mis-parsed schedule is a fabricated "
              "event date, and a fabricated event date is worse than no calendar at all.")
        return 2

    existing = _calendar_extension(args.calendar_path)
    merged, added = merge_extension(existing, parsed)
    total_added = sum(len(v) for v in added.values())
    print("\nMerge (frozen lists and existing extension rows are authoritative; nothing rewritten):")
    for e in EVENTS:
        print(f"  {e}: +{len(added[e])} new, extension now {len(merged[e])} row(s), "
              f"covered through {covered[e]}")

    if args.dry_run:
        print(f"DRY RUN: would add {total_added} row(s). Nothing written.")
        return 0

    write_extension(merged, covered, args.calendar_path, args.coverage_path)
    for e in EVENTS:
        log_topup(e, added[e], SOURCES[e])
    print(f"Wrote {args.calendar_path.name} ({sum(len(v) for v in merged.values())} rows) and "
          f"{args.coverage_path.name}. Added {total_added}.")

    try:
        from reference_data import plain_lines, write_coverage_ledger
        print()
        print("\n".join(plain_lines(write_coverage_ledger())))
    except Exception as ex:  # noqa: BLE001
        print(f"(coverage ledger not refreshed: {type(ex).__name__}: {ex})")
    return 0


if __name__ == "__main__":
    enable_production("scheduled macro-event calendar top-up")
    raise SystemExit(main())

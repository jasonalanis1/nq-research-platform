"""
reference_data.py -- THE SINGLE OWNER of the project's non-price reference
series, and the FAIL-CLOSED accessors every scoring consumer must use.

WHY THIS EXISTS (2026-09-16, the 7:00 pm cycle)
  Two consecutive cycles stalled on the same wall. S009a cannot be specified
  at all because its one added rule needs a scheduled-macro-event calendar and
  the project's sourced lists end 2021-09-22 (FOMC) and 2023-12-12 (CPI/NFP).
  S010a has the same shape of problem: the VXN series it selects on ends
  2026-09-02. Both are inputs to the standing directive's Salvage menu (s.7
  conditions 1 and 4), so a stale calendar or a stale VXN series quietly
  degrades EVERY future salvage, not just those two candidates.

  The dangerous failure is the silent one. `d in FOMC_SET` returns False for a
  2026 date not because the day was quiet but because the list stops in 2021,
  and a forward-filled VXN carries a two-week-old volatility reading into a
  session as though it were today's. Both read as data. Neither is.

THE RULE THIS MODULE ENFORCES
  A session past a series' coverage end is REFUSED, never guessed. Every
  accessor here raises ReferenceDataUnavailable rather than returning a
  default. Fail open is how a paper record becomes a lie.

COVERAGE, and where it comes from
  VXN    data/VXNCLS_MAX.csv -- the daily series itself; its last observation
         IS its coverage end. Topped up by src/data_topup_vxn.py from CBOE's
         published daily history.
  FOMC / CPI / NFP
         The frozen, sourced Python lists in src/study_fomc_volatility.py and
         src/study_economic_calendar.py remain authoritative over their own
         ranges and are NEVER edited here. data/macro_event_calendar.csv
         EXTENDS them forward; data/macro_event_calendar_coverage.json records
         how far each event's published schedule was verified to reach.
         Topped up by src/data_topup_macro_calendar.py.
  With no sidecar, coverage falls back to the frozen lists' own last date --
  conservative in the right direction (it refuses more, never less).

A PUBLISHED SCHEDULE COVERS THE FUTURE. That is the point: the Fed and the BLS
publish next year's dates in advance, so `covered_through` is normally ahead of
today and a 2026 session can be classified honestly. What is never allowed is
treating "past the end of what we fetched" as "no event".
"""
from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"
LEDGER_DIR = PROJECT_ROOT / "research" / "ledger"

VXN_PATH = DATA_DIR / "VXNCLS_MAX.csv"
MACRO_CALENDAR_PATH = DATA_DIR / "macro_event_calendar.csv"
MACRO_COVERAGE_PATH = DATA_DIR / "macro_event_calendar_coverage.json"
COVERAGE_LEDGER_PATH = LEDGER_DIR / "data_coverage.json"

EVENTS = ("FOMC", "CPI", "NFP")

# Who reads each series. Kept here so the coverage ledger and the preflight
# row can name the blast radius of a stale series without a grep.
CONSUMERS = {
    "VXN": [
        "src/market_state_primitives_v2.py:_load_vxn_daily/extend_state_frame (vxn_level_vs_trailing)",
        "src/salvage_check.py:vxn_labels (directive s.7 Salvage menu condition 1)",
        "src/study_s002_night_leg_menu.py",
        "src/idea_factory.py",
        "src/observatory_free_look.py",
        "src/study_vxn_level_signal.py / study_vxn_roc_signal.py / study_vxn_pricing_check.py",
        "validated magnitude fact: VXN -> next-session range (stop and sizing input at SPECIFY)",
        "S010a (queued at SOURCE): selects LOW-VXN sessions only",
    ],
    "FOMC": [
        "src/salvage_check.py:news_labels (directive s.7 Salvage menu condition 4)",
        "src/study_fomc_volatility.py, src/study_pre_fomc_drift.py",
        "S009a (queued at SOURCE): trades only on days with no scheduled macro event",
    ],
    "CPI": [
        "src/salvage_check.py:news_labels (directive s.7 Salvage menu condition 4)",
        "src/study_economic_calendar.py, src/validate_exp039_economic_calendar.py",
        "S009a (queued at SOURCE)",
    ],
    "NFP": [
        "src/salvage_check.py:news_labels (directive s.7 Salvage menu condition 4)",
        "src/study_economic_calendar.py, src/study_pre_nfp_drift.py",
        "S009a (queued at SOURCE)",
    ],
}

SOURCES = {
    "VXN": "CBOE published daily history: https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv",
    "FOMC": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
    "CPI": "https://www.bls.gov/schedule/news_release/cpi.htm",
    "NFP": "https://www.bls.gov/schedule/news_release/empsit.htm",
}


class ReferenceDataUnavailable(RuntimeError):
    """A session was asked about that lies past a reference series' coverage.

    Raised, never swallowed into a default. Carries the series, the day asked
    for, the coverage end and the command that fixes it."""

    def __init__(self, series: str, day, covered_through, extra: str = ""):
        self.series = series
        self.day = day
        self.covered_through = covered_through
        fix = {
            "VXN": "python3 src/data_topup_vxn.py",
        }.get(series, "python3 src/data_topup_macro_calendar.py")
        msg = (f"{series} reference data does not cover {day}: covered through "
               f"{covered_through}. REFUSING to score this session rather than "
               f"guessing (no stale carry-forward, no 'assume no event'). "
               f"Run `{fix}` from Jason's own Terminal to extend coverage.")
        if extra:
            msg += " " + extra
        super().__init__(msg)


def _as_date(day) -> date:
    if isinstance(day, datetime):
        return day.date()
    if isinstance(day, date):
        return day
    return datetime.fromisoformat(str(day)[:10]).date()


# --------------------------------------------------------------------------
# VXN
# --------------------------------------------------------------------------
def vxn_daily(path: Path | None = None) -> dict:
    """{date: close}. Plain dict, no pandas -- this is read by the guard on
    paths that must not carry a heavy import."""
    p = Path(path) if path else VXN_PATH
    out: dict[date, float] = {}
    with p.open(newline="") as fh:
        for row in csv.DictReader(fh):
            raw = (row.get("VXNCLS") or "").strip()
            if not raw or raw == ".":
                continue
            out[_as_date(row["observation_date"])] = float(raw)
    return dict(sorted(out.items()))


def vxn_coverage_end(path: Path | None = None) -> date:
    series = vxn_daily(path)
    if not series:
        raise ReferenceDataUnavailable("VXN", "any date", "nothing -- the series file is empty")
    return max(series)


def vxn_close(day, path: Path | None = None) -> float:
    """FAIL-CLOSED. The close for `day`, or the last close at or before it,
    but ONLY inside coverage. A day past the coverage end raises -- it never
    silently receives the last known level."""
    d = _as_date(day)
    series = vxn_daily(path)
    end = max(series) if series else None
    if end is None or d > end:
        raise ReferenceDataUnavailable("VXN", d, end)
    at_or_before = [v for k, v in series.items() if k <= d]
    if not at_or_before:
        raise ReferenceDataUnavailable("VXN", d, end,
                                       "the day also precedes the start of the series.")
    return at_or_before[-1]


# --------------------------------------------------------------------------
# Scheduled macro events
# --------------------------------------------------------------------------
def _frozen_lists() -> dict:
    """The sourced lists already in the project. Read, never written."""
    out = {e: set() for e in EVENTS}
    try:
        from study_fomc_volatility import FOMC_SET
        out["FOMC"] = set(FOMC_SET)
    except Exception:  # noqa: BLE001 -- a missing study must not make the guard fail open
        pass
    try:
        from study_economic_calendar import CPI_SET, NFP_SET
        out["CPI"] = set(CPI_SET)
        out["NFP"] = set(NFP_SET)
    except Exception:  # noqa: BLE001
        pass
    return out


def _calendar_extension(path: Path | None = None) -> dict:
    p = Path(path) if path else MACRO_CALENDAR_PATH
    out = {e: set() for e in EVENTS}
    if not p.exists():
        return out
    with p.open(newline="") as fh:
        for row in csv.DictReader(fh):
            ev = (row.get("event") or "").strip().upper()
            if ev in out:
                out[ev].add(_as_date(row["date"]))
    return out


def macro_events(calendar_path: Path | None = None) -> dict:
    """{event: set of dates}, frozen sourced lists UNION the fetched extension."""
    frozen = _frozen_lists()
    ext = _calendar_extension(calendar_path)
    return {e: frozen[e] | ext[e] for e in EVENTS}


def macro_coverage_by_event(calendar_path: Path | None = None,
                            coverage_path: Path | None = None) -> dict:
    """{event: covered_through date}.

    The sidecar written by the top-up is authoritative when present, because a
    published schedule covers dates that carry no event (the calendar knows
    March 2027 holds no CPI release on the 3rd). With no sidecar the frozen
    list's own last date is used -- conservative: it refuses more, never less.
    """
    cov = {}
    sidecar = {}
    p = Path(coverage_path) if coverage_path else MACRO_COVERAGE_PATH
    if p.exists():
        try:
            sidecar = json.loads(p.read_text())
        except Exception:  # noqa: BLE001
            sidecar = {}
    events = macro_events(calendar_path)
    for e in EVENTS:
        ends = []
        if events[e]:
            ends.append(max(events[e]))
        rec = sidecar.get(e) or {}
        if rec.get("covered_through"):
            ends.append(_as_date(rec["covered_through"]))
        cov[e] = max(ends) if ends else None
    return cov


def macro_coverage_end(calendar_path: Path | None = None,
                       coverage_path: Path | None = None) -> date | None:
    """The date through which ALL THREE event series are covered -- the
    MINIMUM, because a day is only honestly classifiable as 'quiet' when every
    series that could have put an event on it has been checked."""
    by_event = macro_coverage_by_event(calendar_path, coverage_path)
    ends = [v for v in by_event.values() if v is not None]
    return min(ends) if ends else None


def scheduled_events_on(day, calendar_path: Path | None = None,
                        coverage_path: Path | None = None) -> set:
    """FAIL-CLOSED. The set of scheduled macro events on `day` ('FOMC', 'CPI',
    'NFP'); the empty set means a VERIFIED quiet day. A day past coverage
    raises instead of coming back empty -- that confusion is exactly the bug
    this module exists to make impossible."""
    d = _as_date(day)
    end = macro_coverage_end(calendar_path, coverage_path)
    if end is None or d > end:
        by_event = macro_coverage_by_event(calendar_path, coverage_path)
        detail = ", ".join(f"{e}: {by_event[e]}" for e in EVENTS)
        raise ReferenceDataUnavailable("macro calendar", d, end, f"Per event -- {detail}.")
    events = macro_events(calendar_path)
    return {e for e in EVENTS if d in events[e]}


def is_scheduled_news_day(day, calendar_path: Path | None = None,
                          coverage_path: Path | None = None) -> bool:
    """FAIL-CLOSED wrapper used by the Salvage menu's condition 4."""
    return bool(scheduled_events_on(day, calendar_path, coverage_path))


# --------------------------------------------------------------------------
# Coverage state -- what the cycle reads
# --------------------------------------------------------------------------
def _price_data_end():
    """Last complete price session on disk, so staleness is measured against
    the thing the paper loop actually scores rather than against the clock."""
    try:
        from data_loader import find_active_data_file
        name = find_active_data_file("NQ").name
        return _as_date(name.split("_")[-1].replace(".csv", "").rstrip("b"))
    except Exception:  # noqa: BLE001
        return None


def coverage(calendar_path: Path | None = None, coverage_path: Path | None = None,
             vxn_path: Path | None = None) -> dict:
    """The coverage state of every reference series, with its consumers."""
    price_end = _price_data_end()
    by_event = macro_coverage_by_event(calendar_path, coverage_path)
    events = macro_events(calendar_path)
    try:
        vxn_end = vxn_coverage_end(vxn_path)
    except Exception:  # noqa: BLE001
        vxn_end = None

    series = {
        "VXN": {"last_date": vxn_end.isoformat() if vxn_end else None,
                "n_observations": len(vxn_daily(vxn_path)) if vxn_end else 0,
                "file": str(VXN_PATH.relative_to(PROJECT_ROOT)),
                "updater": "src/data_topup_vxn.py",
                "source": SOURCES["VXN"],
                "consumers": CONSUMERS["VXN"]},
    }
    for e in EVENTS:
        series[e] = {"last_date": by_event[e].isoformat() if by_event[e] else None,
                     "n_events": len(events[e]),
                     "file": "frozen list + " + str(MACRO_CALENDAR_PATH.relative_to(PROJECT_ROOT)),
                     "updater": "src/data_topup_macro_calendar.py",
                     "source": SOURCES[e],
                     "consumers": CONSUMERS[e]}

    for name, rec in series.items():
        last = _as_date(rec["last_date"]) if rec["last_date"] else None
        rec["covers_price_data"] = bool(last and price_end and last >= price_end)
        rec["days_short_of_price_data"] = (
            (price_end - last).days if last and price_end and last < price_end else 0)
        rec["stale"] = not rec["covers_price_data"]

    stale = sorted(n for n, r in series.items() if r["stale"])
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "price_data_end": price_end.isoformat() if price_end else None,
        "macro_calendar_covered_through": (macro_coverage_end(calendar_path, coverage_path).isoformat()
                                           if macro_coverage_end(calendar_path, coverage_path) else None),
        "series": series,
        "stale_series": stale,
        "ok": not stale,
        "note": ("every reference series covers the price data on disk"
                 if not stale else
                 "STALE: " + ", ".join(f"{n} ends {series[n]['last_date']}" for n in stale)
                 + " -- consumers FAIL CLOSED past these dates (reference_data.ReferenceDataUnavailable), "
                   "they do not guess. Extend with the updater named on each series."),
    }


def write_coverage_ledger(path: Path | None = None, **kw) -> dict:
    from production_paths import assert_writable
    p = Path(path) if path else COVERAGE_LEDGER_PATH
    state = coverage(**kw)
    assert_writable(p, "reference-data coverage ledger")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2) + "\n")
    return state


def plain_lines(state: dict | None = None) -> list[str]:
    st = state or coverage()
    out = [f"REFERENCE DATA COVERAGE (price data ends {st['price_data_end']})"]
    for name, rec in st["series"].items():
        mark = "STALE" if rec["stale"] else "ok"
        short = f", {rec['days_short_of_price_data']}d short of the price data" if rec["stale"] else ""
        out.append(f"  [{mark}] {name:<5} covered through {rec['last_date']}{short} "
                   f"-- {len(rec['consumers'])} consumer(s); update with {rec['updater']}")
    out.append("  Consumers FAIL CLOSED past these dates: a session outside coverage is refused, never guessed.")
    return out


if __name__ == "__main__":
    import sys as _sys
    st = coverage()
    print("\n".join(plain_lines(st)))
    if "--write" in _sys.argv:
        from production_paths import enable_production
        enable_production("reference-data coverage ledger")
        write_coverage_ledger()
        print(f"wrote {COVERAGE_LEDGER_PATH}")
    raise SystemExit(0 if st["ok"] else 1)

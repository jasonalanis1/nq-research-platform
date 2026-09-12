"""Jason-facing time formatting. One rule: anything a human reads is Central time.

Internal timestamps (lock file, ledger, session filenames, console JSON keys)
stay UTC -- ops_checks and the console parser depend on that. This module is
the single place that converts UTC to the format Jason reads:
"September 11th, 1:00 pm CT". Use it for session-report headers, NEXT_UP.md,
_session_log.txt human lines, and any chat message stating a time.

Usage:  python3 src/local_time.py                 -> now, Central
        python3 src/local_time.py 2026-09-11T18:00:00Z
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

CENTRAL = ZoneInfo("America/Chicago")


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def to_central(ts: str | datetime | None = None) -> datetime:
    if ts is None:
        dt = datetime.now(timezone.utc)
    elif isinstance(ts, datetime):
        dt = ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    else:
        s = ts.strip().replace("Z", "+00:00")
        if "T" not in s:
            s = s.replace(" ", "T", 1)
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(CENTRAL)


def fmt_central(ts: str | datetime | None = None, with_date: bool = True) -> str:
    """'September 11th, 1:00 pm CT' (or '1:00 pm CT' when with_date=False)."""
    dt = to_central(ts)
    hour = dt.strftime("%I").lstrip("0") or "12"
    clock = f"{hour}:{dt.strftime('%M')} {dt.strftime('%p').lower()} CT"
    if not with_date:
        return clock
    return f"{dt.strftime('%B')} {_ordinal(dt.day)}, {clock}"


if __name__ == "__main__":
    print(fmt_central(sys.argv[1] if len(sys.argv) > 1 else None))

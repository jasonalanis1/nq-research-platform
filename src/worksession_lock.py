"""Work-session lock with owner, heartbeat, and safe handoff.

Why this exists (documented failures, 2026-09-10/11):
  * two sessions wrote RUNNING within seconds of each other and one clobbered
    the other's claim (no re-read before write);
  * sessions died mid-close-out, leaving RUNNING forever and blocking the next
    cycle, which then had to guess whether the holder was alive;
  * an interactive session and a scheduled cycle had no way to tell each other
    apart, so "lock is RUNNING" could mean "wait", "take over", or "skip".

Format stays backward compatible: research/_worksession.lock is still ONE line,
"RUNNING YYYY-MM-DD HH:MM:SS" or "FREE YYYY-MM-DD HH:MM:SS" (UTC, no suffix) --
ops_checks.py and generate_console_state.py parse exactly that. Everything
new lives beside it in research/_worksession.lock.meta (JSON): owner, started,
last heartbeat, session, note.

Decision table for `acquire`:
  FREE                              -> take it (exit 0, prints TAKEN)
  RUNNING, heartbeat fresh          -> refuse  (exit 2, prints BUSY <owner> <age>)
  RUNNING, heartbeat stale (>TTL)   -> take over, record the orphan (exit 0, prints TAKEN_OVER ...)
  RUNNING, same owner tag           -> refuse unless --force (a re-entrant claim is a bug, not a handoff)
Acquire is atomic: write a temp file, re-read the live lock, os.replace only if
it is still what we saw.

CLI:
  python3 src/worksession_lock.py acquire --owner interactive|cycle [--note ...]
  python3 src/worksession_lock.py heartbeat
  python3 src/worksession_lock.py release [--owner X]
  python3 src/worksession_lock.py status        (exit 0 free, 2 busy, 3 stale)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCK = ROOT / "research" / "_worksession.lock"
META = ROOT / "research" / "_worksession.lock.meta"
FMT = "%Y-%m-%d %H:%M:%S"
STALE_MINUTES = 30  # matches ops_checks.HEARTBEAT_MINUTES


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _stamp(dt: datetime | None = None) -> str:
    return (dt or _now()).strftime(FMT)


def _read_lock() -> tuple[str, str]:
    """('RUNNING'|'FREE'|'MISSING'|'BAD', raw text)."""
    if not LOCK.exists():
        return "MISSING", ""
    raw = LOCK.read_text()
    parts = raw.strip().split(None, 1)
    if len(parts) != 2 or parts[0].upper() not in ("RUNNING", "FREE"):
        return "BAD", raw
    return parts[0].upper(), raw


def _read_meta() -> dict:
    try:
        return json.loads(META.read_text())
    except Exception:  # noqa: BLE001
        return {}


def _write_atomic(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _heartbeat_age_minutes(meta: dict) -> float | None:
    hb = meta.get("heartbeat") or meta.get("started")
    if not hb:
        return None
    try:
        t = datetime.strptime(hb, FMT).replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (_now() - t).total_seconds() / 60


def status() -> tuple[int, str]:
    state, raw = _read_lock()
    meta = _read_meta()
    if state == "FREE":
        return 0, f"FREE since {raw.strip().split(None, 1)[1]}"
    if state in ("MISSING", "BAD"):
        return 0, f"{state} ({raw.strip()!r}) -- treated as free"
    age = _heartbeat_age_minutes(meta)
    owner = meta.get("owner", "unknown")
    if age is None:
        # RUNNING but no meta (a pre-tool session) -- fall back to the lock stamp.
        started = raw.strip().split(None, 1)[1]
        try:
            age = (_now() - datetime.strptime(started, FMT).replace(tzinfo=timezone.utc)).total_seconds() / 60
        except ValueError:
            age = 1e9
    if age > STALE_MINUTES:
        return 3, f"STALE RUNNING owner={owner} last_heartbeat={age:.0f}min_ago"
    return 2, f"BUSY owner={owner} last_heartbeat={age:.0f}min_ago note={meta.get('note','')!r}"


def acquire(owner: str, note: str = "", force: bool = False) -> int:
    code, line = status()
    meta_before = _read_meta()
    state_before, raw_before = _read_lock()
    if code == 2 and not force:
        if meta_before.get("owner") == owner:
            print(f"BUSY same owner ({owner}) -- re-entrant claim refused; use --force only if you are sure the earlier claim is yours and dead")
        else:
            print(line)
        return 2
    takeover = code == 3 or (code == 2 and force)
    now = _now()
    new_meta = {
        "owner": owner,
        "started": _stamp(now),
        "heartbeat": _stamp(now),
        "note": note,
        "session": os.environ.get("CLAUDE_SESSION", ""),
    }
    if takeover:
        new_meta["took_over_from"] = {
            "owner": meta_before.get("owner", "unknown"),
            "lock_line": raw_before.strip(),
            "last_heartbeat": meta_before.get("heartbeat"),
        }
    # Compare-and-swap: the lock must still read exactly as it did above.
    state_now, raw_now = _read_lock()
    if raw_now != raw_before:
        print(f"RACE: lock changed underneath us ({raw_before.strip()!r} -> {raw_now.strip()!r}); not taken")
        return 4
    _write_atomic(LOCK, f"RUNNING {_stamp(now)}\n")
    _write_atomic(META, json.dumps(new_meta, indent=1) + "\n")
    print(("TAKEN_OVER from " + json.dumps(new_meta["took_over_from"])) if takeover else f"TAKEN owner={owner} at {_stamp(now)}")
    return 0


def heartbeat() -> int:
    state, _ = _read_lock()
    if state != "RUNNING":
        print(f"NOT_RUNNING ({state}) -- nothing to heartbeat")
        return 2
    meta = _read_meta()
    meta["heartbeat"] = _stamp()
    _write_atomic(META, json.dumps(meta, indent=1) + "\n")
    print(f"BEAT {meta['heartbeat']} owner={meta.get('owner','unknown')}")
    return 0


def release(owner: str | None = None) -> int:
    state, _ = _read_lock()
    meta = _read_meta()
    if state == "RUNNING" and owner and meta.get("owner") and meta["owner"] != owner:
        print(f"REFUSED: lock is held by {meta['owner']!r}, not {owner!r} -- release with that owner or let it go stale")
        return 2
    now = _stamp()
    _write_atomic(LOCK, f"FREE {now}\n")
    if META.exists():
        hist = {"released_at": now, "released_by": owner or meta.get("owner"), "previous": meta}
        _write_atomic(META, json.dumps(hist, indent=1) + "\n")
    print(f"FREE {now}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire"); a.add_argument("--owner", required=True); a.add_argument("--note", default=""); a.add_argument("--force", action="store_true")
    sub.add_parser("heartbeat")
    r = sub.add_parser("release"); r.add_argument("--owner")
    sub.add_parser("status")
    ns = ap.parse_args(argv)
    if ns.cmd == "acquire":
        return acquire(ns.owner, ns.note, ns.force)
    if ns.cmd == "heartbeat":
        return heartbeat()
    if ns.cmd == "release":
        return release(ns.owner)
    code, line = status()
    print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())

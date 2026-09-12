"""The console state document is the ONLY source of status on the console
page (Jason, 2026-09-11: simpler tracker, cycle-maintained, not live). It
must stay small, carry the sweep, and never fabricate work for a closed
candidate."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import generate_console_state as g  # noqa: E402


def _state(tmp_path):
    out = tmp_path / "s.json"
    subprocess.run([sys.executable, str(ROOT / "src" / "generate_console_state.py"), "-o", str(out)],
                   check=True, capture_output=True)
    return json.loads(out.read_text()), out


def test_state_is_small_and_has_the_tracker_fields(tmp_path):
    d, out = _state(tmp_path)
    assert out.stat().st_size < 20_000, "state doc grew past the cheap-to-push budget"
    for k in ("generated_at_local", "next_run_local", "cadence", "ops", "funnel",
              "sweep", "waiting_on_jason", "h118_forward", "shelf", "recent_closures", "sessions"):
        assert k in d, k
    assert "audit" not in d and "stages" not in d
    assert len(d["sessions"]) <= 3
    assert all("agents" not in s for s in d["sessions"])


def test_sweep_feed_drops_hidden_rows_and_frozen_are_named():
    sweep = g.read_sweep()
    ids = {r["id"] for r in sweep["rows"]}
    raw = json.loads(g.SWEEP_JSON.read_text())
    hidden = {r["id"] for r in raw["rows"] if r.get("hidden")}
    assert not (ids & hidden)
    for r in sweep["rows"]:
        if r["tier"] == "FROZEN":
            assert "_" not in r["name"], r["name"]


def test_waiting_on_jason_is_only_gated_rows():
    sweep = g.read_sweep()
    w = g.waiting_on_jason(sweep)
    gated = {r["id"] for r in sweep["rows"] if r["tier"] == "GATED"}
    assert {x["id"] for x in w} == gated


def test_recent_closures_are_real_rejections():
    for c in g.recent_closures():
        assert c["id"].startswith("hyp-") and len(c["date"]) == 10

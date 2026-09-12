"""UPGRADE 4: the blind packet masks results and keeps procedure."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import integrity_blind_packet as b  # noqa: E402


def test_masks_result_tokens_and_keeps_procedure():
    src = ("Discovery n=554 mean_r=+0.617R ci_90=[0.453,0.785] DISCOVERY_PASS. "
           "Bucket: LOW tercile, 10-day time exit, edges frozen on Discovery. Win rate 61.2%.")
    out = b.mask_text(src)
    assert "0.713" not in b.mask_text("ratio 0.713 vs 1.160, threshold 1.0, 20-day")
    assert "1.0" in b.mask_text("threshold 1.0, 20-day") and "20-day" in b.mask_text("20-day")
    for tok in ("554", "0.617", "0.453", "DISCOVERY_PASS", "61.2"):
        assert tok not in out
    for tok in ("LOW tercile", "10-day", "edges frozen on Discovery"):
        assert tok in out


def test_family_rows_mask_results_keep_ids():
    rows = b.family_rows("vwap_dist_low_10d_drift_h118")
    assert rows, "H118 family must exist in the ledger"
    for r in rows:
        assert r["hypothesis_id"].startswith("hyp-")
        assert r["strategy_status"] == b.MASK and r["expectancy_r"] == b.MASK


def test_build_packet_from_h118_files(tmp_path):
    spec = ROOT / "research" / "studies" / "vwap-dist-low-10d-drift-h118-spec.md"
    code = ROOT / "src" / "study_vwap_dist_low_10d_drift_h118.py"
    mech = ROOT / "research" / "mechanisms" / "h118-vwap-dist-low.md"
    pk = b.build("vwap_dist_low_10d_drift_h118", spec, code, mech)
    assert "BLIND INTEGRITY GATE PACKET" in pk and "HOLDOUT_PASS" not in pk
    assert "def bootstrap_mean_ci" in pk

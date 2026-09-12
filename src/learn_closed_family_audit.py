"""LEARN closed-family audit -- mechanical part (item 0b, Jason 2026-09-11).

Groups every ledger row into an idea family (same key ops_checks uses),
then for every family with no live row reports: attempts spent (distinct
hypothesis_ids that ran a Discovery-slice test; a Validation row is the same
attempt continuing, not a new one), how it closed (keyword classification of
the family's notes, deepest slice first), and whether it has one attempt
left. The judgment call -- does any market_structure_map.md entry supply a
genuinely different mechanism claim -- is NOT scripted; it is written by
hand into the audit doc for the one-attempt-left families only.

Usage: python3 src/learn_closed_family_audit.py  -> prints markdown table,
       writes data/learn_closed_family_audit.json
"""
from __future__ import annotations
import collections, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ops_checks import _idea_key  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "research" / "ledger" / "hypotheses.jsonl"
OUT = ROOT / "data" / "learn_closed_family_audit.json"
CLOSED = {"REJECTED", "CLOSED", "ABANDONED"}
SLICE_ORDER = {"discovery": 1, "validation": 2, "prospective": 2, "holdout_gen1": 3, "holdout_gen2": 3}

RULES = [  # first match wins; deepest-slice note is classified first
    ("redundant / not incremental", r"redundant|separab|same latent|restat|double.?count|not incremental|known.?true"),
    ("multiplicity-corrected fail", r"multiplicit|sidak|corrected (90|ci|bound)"),
    ("cost-dominated", r"cost.?domin|cost floor|round.?trip|after cost|net of cost|slippage"),
    ("closed on Validation", r"validation.*(reject|fail|null)|prospective.*(reject|fail|null)|sign flip|did not replicate|failed to replicate"),
    ("regime / sample artifact", r"regime.?artifact|secular|thin.?sample|regime.?split|concentrat"),
    ("wrong direction", r"wrong.?direction|opposite.?sign|opposite direction"),
    ("clean null", r"null|crosses zero|not credible|no (effect|edge|relation)|ci.*(includes|contains|straddles) (0|zero)|-\d+\.\d+r to \+\d"),
    ("decisively negative", r"entirely below zero|below zero|negative expectancy"),
]

def classify(notes: str) -> str:
    n = (notes or "").lower()
    for label, pat in RULES:
        if re.search(pat, n):
            return label
    return "unclassified (read notes)"

# CLAIM CLUSTERS -- the 2-attempt limit is per idea (mechanism claim), not per
# variant name. Regex on the idea key -> cluster. Order matters; first match wins.
# Anything unmatched is its own single-name cluster.
CLUSTERS = [
    ("level-sweep reversal (liquidity sweep)", r"level_sweep|overlay_screen2|vol_regime_overlay_screen"),
    ("IB / opening-range breakout", r"initial_balance|ib_breakout"),
    ("gap / overnight-extreme open fade", r"fade_the_gap|gap_fade|gap_down_fade|open_fade|h89_position_sizing"),
    ("intraday VWAP fade", r"vwap_mean_reversion|vwap_narrow_open"),
    ("weekly / multi-day trend following (CTA proxy)", r"weekly_trend|nq_trend|trend_family|trend_alignment|cross_asset_weekly"),
    ("cross-asset short-term reversal", r"cross_asset_short"),
    ("cross-asset lead-lag (ZN / currency / oil)", r"zn_|currency_lead|oil_lead"),
    ("VXN level / ROC as direction", r"vxn_"),
    ("options VRP", r"options_vrp"),
    ("candlestick / bar patterns (daily + 60min)", r"bar_behavior"),
    ("intraday momentum continuation", r"momentum_continuation|momentum_burst"),
    ("multi-factor combination", r"multi_factor"),
    ("volume level / imbalance / vacuum", r"volume_level|opening_volume|volume_imbalance|volume_vacuum"),
    ("range-contraction / expansion cycle", r"range_contraction"),
    ("volume profile skew", r"volume_profile"),
    ("trend-day shape", r"trend_day_shape"),
    ("effort vs result absorption", r"effort_vs_result"),
    ("multi-day base breakout", r"multiday_base"),
    ("overnight coil -> RTH range", r"overnight_coil"),
    ("intraday lull re-engagement", r"lull_reengagement"),
    ("COT positioning", r"cot_positioning"),
    ("multi-day pullback continuation", r"pullback_continuation"),
    ("reference-level fades (prior close / open / round number / session open)", r"prior_close_rejection|reference_level_fade|round_number|session_open_retest"),
    ("release-day reaction (CPI / NFP)", r"cpi_"),
    ("pre-NFP drift", r"pre_nfp"),
    ("pre-FOMC drift", r"pre_fomc"),
    ("turn-of-month (unconditional)", r"turn_of_month"),
    ("witching volatility", r"witching"),
    ("closing-pressure reversal (unconditioned)", r"closing_pressure"),
    ("overnight_range_vs_atr mid -> 10d drift (H116)", r"overnight_range_mid"),
    ("location_in_range low + uptrend -> 10d drift (H117)", r"location_in_range"),
    ("vwap_dist_vs_atr low -> 1d (H118 sibling)", r"vwap_dist_low_1d"),
    ("|gap| magnitude -> same-day range", r"abs_gap_vs_atr"),
    ("overnight-vs-RTH return divergence", r"overnight_rth_divergence"),
    ("days_to_monthly_opex", r"days_to_monthly_opex"),
]

def cluster_of(key: str) -> str:
    key = re.sub(r"_STATUS_CORRECTION$", "", key)
    for name, pat in CLUSTERS:
        if re.search(pat, key):
            return name
    return key

def main():
    rows = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    latest = {}
    for r in rows:
        latest[r["hypothesis_id"]] = r
    fam = collections.defaultdict(list)
    for r in latest.values():
        fam[_idea_key(r["strategy_name"])].append(r)
    out = []
    for key, members in sorted(fam.items()):
        statuses = {m["strategy_status"] for m in members}
        if statuses - CLOSED:
            continue  # live family, not in scope
        disc_ids = sorted({m["hypothesis_id"] for m in members if (m.get("data_slice_used") or "discovery") == "discovery"
                           and not re.search(r"PROGRESSION_POINTER|MULTIPLICITY_REEXPRESSION|INTEGRITY_REVIEW|hygiene|correction", m["strategy_name"] + " " + (m.get("notes") or ""), re.I)})
        attempts = max(1, len(disc_ids))
        deepest = max(members, key=lambda m: (SLICE_ORDER.get(m.get("data_slice_used"), 1), m["logged_at"]))
        # classify from the deepest row's notes, fall back to any member's notes
        how = classify(deepest.get("notes") or "")
        if how.startswith("unclassified"):
            for m in sorted(members, key=lambda m: m["logged_at"], reverse=True):
                c = classify(m.get("notes") or "")
                if not c.startswith("unclassified"):
                    how = c; break
        deepest_slice = deepest.get("data_slice_used") or "discovery"
        if deepest_slice in ("validation", "prospective") and how in ("clean null", "unclassified (read notes)"):
            how = "closed on Validation"
        out.append({"family": key, "ids": sorted(m["hypothesis_id"] for m in members), "attempts": attempts, "disc_ids": disc_ids,
                    "deepest_slice": deepest_slice, "how_closed": how,
                    "one_attempt_left": attempts < 2,
                    "origin": sorted({m.get("strategy_origin") or "" for m in members}),
                    "note_head": (deepest.get("notes") or "")[:140].replace("\n", " ")})
    # aggregate name-level families into claim clusters
    agg = collections.OrderedDict()
    for o in out:
        cl = cluster_of(o["family"])
        a = agg.setdefault(cl, {"cluster": cl, "families": [], "ids": set(), "disc_ids": set(), "deepest_slice": "discovery", "how_closed": collections.Counter()})
        a["families"].append(o["family"]); a["ids"] |= set(o["ids"]); a["disc_ids"] |= set(o["disc_ids"])
        if SLICE_ORDER.get(o["deepest_slice"], 1) > SLICE_ORDER.get(a["deepest_slice"], 1): a["deepest_slice"] = o["deepest_slice"]
        a["how_closed"][o["how_closed"]] += 1
    clusters = []
    for a in agg.values():
        a["ids"] = sorted(a["ids"]); a["attempts"] = max(1, len(a["disc_ids"])); a["disc_ids"] = sorted(a["disc_ids"])
        a["how_closed"] = dict(a["how_closed"]); a["one_attempt_left"] = a["attempts"] < 2
        clusters.append(a)
    OUT.write_text(json.dumps({"name_level": out, "clusters": clusters}, indent=1))
    print("## Claim clusters\n")
    print("| cluster | hypothesis ids | attempts | deepest slice | how closed (count) | 1 left? |")
    print("|---|---|---|---|---|---|")
    for a in clusters:
        print(f"| {a['cluster']} | {', '.join(i[-3:] for i in a['ids'])} | {a['attempts']} | {a['deepest_slice']} | {a['how_closed']} | {'YES' if a['one_attempt_left'] else ''} |")
    print(f"\n{len(clusters)} claim clusters; {sum(a['one_attempt_left'] for a in clusters)} with one attempt left.\n")
    print("## Name-level families\n")
    print(f"| family | ids | attempts | deepest slice | how closed | 1 left? |")
    print(f"|---|---|---|---|---|---|")
    for o in out:
        print(f"| {o['family']} | {', '.join(i[-3:] for i in o['ids'])} | {o['attempts']} | {o['deepest_slice']} | {o['how_closed']} | {'YES' if o['one_attempt_left'] else ''} |")
    print(f"\n{len(out)} closed families; {sum(o['one_attempt_left'] for o in out)} with one attempt left; "
          f"how-closed counts: {dict(collections.Counter(o['how_closed'] for o in out))}")

if __name__ == "__main__":
    main()

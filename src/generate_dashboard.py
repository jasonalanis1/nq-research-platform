"""
generate_dashboard.py
=======================

WHAT THIS FILE DOES (plain English):
Reads the real project data -- research/experiments/_index.md, the
individual research/experiments/exp-*.md files, and whatever's in
data/ -- and builds dashboard.html, a single-page, no-code-required
summary of where this project currently stands. Nothing in the output
is hand-typed; every number comes from parsing the actual files, so
re-running this script after new experiments/data land keeps it honest
and current.

HOW TO RUN:
    python3 src/generate_dashboard.py
Then open dashboard.html (in the project's root folder) in any browser
-- just double-click it in Finder.
"""

import re
import html
from pathlib import Path
from datetime import datetime

import pandas as pd

from data_holdout import HOLDOUT_START_DATE
from data_loader import list_data_files, find_active_data_file, read_price_csv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
EXPERIMENTS_DIR = PROJECT_ROOT / "research" / "experiments"
INDEX_PATH = EXPERIMENTS_DIR / "_index.md"
OUT_PATH = PROJECT_ROOT / "dashboard.html"

# The project's named subagents -- this is short enough, and changes
# rarely enough, that it's kept here as plain data rather than parsed
# from anywhere. Tony is deliberately NOT an active subagent yet (no
# .claude/agents/tony.md exists) -- he's listed here as a documented,
# paused-on-purpose next step, per the project's safety rule that live
# automation only gets built with Jason's direct go-ahead at the time.
TEAM = [
    {
        "name": "Greg",
        "role": "Pulls fresh real price data (Yahoo or Databento).",
        "status": "active",
        "status_label": "Active",
        "detail": "Run anytime you want newer data -- just ask for Greg by name.",
    },
    {
        "name": "Larry",
        "role": "Runs the full detect → backtest → score → confidence pipeline for a setup/variant and logs it as a new numbered experiment.",
        "status": "active",
        "status_label": "Active",
        "detail": "Run anytime you want to test a setup or variant -- just ask for Larry by name.",
    },
    {
        "name": "Tony",
        "role": "Detects Level Sweep Reversal conditions and fires TradingView alerts (Pine Script). Never claims a signal is proven profitable.",
        "status": "paused",
        "status_label": "Experimental, unvalidated",
        "detail": "pine/level_sweep_close_min_distance.pine and pine/level_sweep_full_bar_range.pine exist (added 2026-08-16), each alert explicitly labeled 'Experimental Signal Detected -- not a proven edge.' Not yet compiled/tested in TradingView itself, and no setup has cleared validation -- do not trade these signals.",
    },
]

EXPECTANCY_R_PATTERN = re.compile(r"([+-]?\d+\.\d+)R")
NORMAL_COST_R_PATTERN = re.compile(r"was\s+([+-]?\d+\.\d+)R normal")


def normal_cost_expectancy_text(expectancy_text: str) -> str:
    """For the compact status cards, always show the NORMAL-cost number
    so variants are shown on a consistent basis at a glance -- some rows
    (the cost-stress-test ones) lead with a stress-cost figure instead,
    which would otherwise silently mix bases with the other rows."""
    m = NORMAL_COST_R_PATTERN.search(expectancy_text)
    if m:
        return f"{m.group(1)}R"
    return expectancy_text.split("(")[0].split(";")[0].strip()


# _index.md's structured columns (upgraded 2026-08-16, architecture
# review recommendation #3) -- in this exact order. Setup, Variant, and
# Sample Size are now real columns, not text scraped out of prose.
INDEX_COLUMNS = [
    "id", "setup", "variant", "date", "sample_size", "win_rate",
    "expectancy", "profit_factor", "max_drawdown", "significant", "verdict",
]


def parse_index_table():
    """Reads the structured markdown table in _index.md into a list of
    dicts, one per experiment row."""
    text = INDEX_PATH.read_text()
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("| exp-"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(INDEX_COLUMNS):
            continue  # malformed row -- skip rather than guess
        rows.append(dict(zip(INDEX_COLUMNS, cells)))
    return rows


def first_expectancy_value(expectancy_text: str):
    """Pulls the first R-multiple number out of an Expectancy cell, e.g.
    '+0.011R under 2x costs (was +0.043R...)' -> 0.011. Returns None if
    no number is found."""
    m = EXPECTANCY_R_PATTERN.search(expectancy_text)
    return float(m.group(1)) if m else None


def load_data_file_stats(path: Path):
    """Reads row count and NY-time date range for one price data CSV.
    Deliberately reads the FULL file via read_price_csv() (not the
    holdout-filtering load_price_data()) -- the dashboard's job is to
    report the research/holdout split as an inventory, not to enforce it."""
    df = read_price_csv(path)
    idx = df.index
    research_days = len(set(idx[idx < HOLDOUT_START_DATE].date))
    holdout_days = len(set(idx[idx >= HOLDOUT_START_DATE].date))
    return {
        "rows": len(df),
        "start": idx.min(),
        "end": idx.max(),
        "trading_days": len(set(idx.date)),
        "research_days": research_days,
        "holdout_days": holdout_days,
    }


def source_label(filename: str) -> str:
    if "SYNTHETIC" in filename:
        return "Synthetic (fake, pipeline-testing only)"
    if "databento" in filename:
        return "Databento (CME Globex GLBX.MDP3 -- real)"
    return "Yahoo Finance (real, free tier)"


def gather_data_coverage():
    candidates = list_data_files()
    if not candidates:
        return None, []
    active = find_active_data_file()

    all_files = []
    for path in candidates:
        stats = load_data_file_stats(path)
        all_files.append({
            "name": path.name,
            "label": source_label(path.name),
            "is_active": path == active,
            **stats,
        })
    active_info = next(f for f in all_files if f["is_active"])
    return active_info, all_files


def build_most_promising(rows_by_group):
    """Among Level Sweep Reversal's three named variants, pick whichever
    has the highest expectancy in its MOST RECENT logged experiment,
    restricted to variants whose latest result is still positive. ORB
    and the pre-variant-split baseline are never candidates."""
    candidates = []
    for (setup, variant), group_rows in rows_by_group.items():
        if setup != "Level Sweep Reversal" or variant not in (
            "close_any", "close_min_distance", "full_bar_range"
        ):
            continue
        latest = group_rows[-1]  # rows are appended in file order (exp-001, exp-002, ...)
        value = first_expectancy_value(latest["expectancy"])
        if value is not None and value > 0:
            candidates.append((value, variant, latest))

    if not candidates:
        return None
    candidates.sort(key=lambda c: c[0], reverse=True)
    value, variant, latest = candidates[0]
    return {"variant": variant, "value": value, "row": latest}


def build_setup_status(rows_by_group):
    """One-line latest status for ORB and for Level Sweep Reversal overall."""
    orb_rows = rows_by_group.get(("ORB", "placeholder"), [])
    orb_latest = orb_rows[-1] if orb_rows else None

    ls_variants = ["close_any", "close_min_distance", "full_bar_range"]
    ls_latest = {}
    for variant in ls_variants:
        group_rows = rows_by_group.get(("Level Sweep Reversal", variant), [])
        if group_rows:
            ls_latest[variant] = group_rows[-1]

    return orb_latest, ls_latest


def esc(text) -> str:
    return html.escape(str(text))


def render_team_section() -> str:
    cards = []
    for member in TEAM:
        cards.append(f"""
        <div class="team-card">
          <div class="team-name-row">
            <span class="team-name">{esc(member['name'])}</span>
            <span class="badge team-status-{esc(member['status'])}">{esc(member['status_label'])}</span>
          </div>
          <p class="team-role">{esc(member['role'])}</p>
          <p class="team-detail">{esc(member['detail'])}</p>
        </div>""")
    return "".join(cards)


def render_html(index_rows, rows_by_group, active_data, all_data_files, most_promising, orb_latest, ls_latest):
    generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    # --- Data coverage card ---
    if active_data:
        data_html = f"""
        <div class="stat-value">{active_data['rows']:,} bars</div>
        <div class="stat-detail">{esc(active_data['label'])}</div>
        <div class="stat-detail">{active_data['start'].strftime('%b %d, %Y')} &rarr; {active_data['end'].strftime('%b %d, %Y')}
          &nbsp;(~{active_data['trading_days']} trading days)</div>
        <div class="stat-detail" style="margin-top:8px;">
          <strong>{active_data['research_days']} research days</strong> (used for testing) +
          <strong>{active_data['holdout_days']} holdout days</strong> (untouched, since {HOLDOUT_START_DATE.strftime('%b %d, %Y')})
        </div>
        """
        if len(all_data_files) > 1:
            others = ", ".join(esc(f["name"]) for f in all_data_files if not f["is_active"])
            data_html += f'<div class="stat-footnote">Also on disk (not currently used): {others}</div>'
    else:
        data_html = '<div class="stat-value">No data found</div><div class="stat-detail">Run data_fetch.py or data_fetch_databento.py first.</div>'

    # --- ORB status card ---
    if orb_latest:
        orb_html = f"""
        <div class="stat-value">{esc(orb_latest['expectancy'].split('(')[0].strip())}</div>
        <div class="stat-detail">{esc(orb_latest['id'])} &middot; {esc(orb_latest['win_rate'])}</div>
        <div class="stat-footnote">{esc(orb_latest['verdict'])}</div>
        """
    else:
        orb_html = '<div class="stat-value">No ORB results yet</div>'

    # --- Level Sweep status card ---
    ls_lines = []
    variant_display = {"close_any": "close_any", "close_min_distance": "close_min_distance", "full_bar_range": "full_bar_range"}
    for variant, label in variant_display.items():
        row = ls_latest.get(variant)
        if not row:
            continue
        display_text = normal_cost_expectancy_text(row["expectancy"])
        display_value_match = EXPECTANCY_R_PATTERN.search(display_text)
        display_value = float(display_value_match.group(1)) if display_value_match else None
        sign_class = "positive" if (display_value is not None and display_value > 0) else "negative"
        ls_lines.append(
            f'<div class="mini-row"><span class="mini-label">{esc(label)}</span>'
            f'<span class="mini-value {sign_class}">{esc(display_text)}</span></div>'
        )
    ls_html = "".join(ls_lines) if ls_lines else "<div>No Level Sweep results yet</div>"
    if ls_lines:
        ls_html += '<div class="stat-footnote">Normal-cost expectancy shown here; see table below for cost-stress-test detail.</div>'

    # --- Most promising callout ---
    if most_promising:
        row = most_promising["row"]
        sig_plain = row["significant"].replace("**", "").strip()
        promising_html = f"""
        <h2>Most promising right now: <span class="highlight">Level Sweep Reversal &mdash; {esc(most_promising['variant'])}</span></h2>
        <p>Latest result ({esc(row['id'])}): expectancy leads the other variants at this checkpoint,
        win rate {esc(row['win_rate'])}, sample size {esc(row['sample_size'])} trades.
        Statistically distinguishable from zero: <strong>{esc(sig_plain)}</strong>.</p>
        <p class="why-label">Why not a stronger claim than that:</p>
        <p class="verdict-quote">&ldquo;{esc(row['verdict'])}&rdquo;</p>
        """
    else:
        promising_html = "<h2>Most promising right now: <span class=\"highlight\">nothing yet</span></h2><p>No Level Sweep variant currently shows a positive latest-result expectancy.</p>"

    # --- Full experiments table ---
    table_rows = []
    for row in index_rows:
        variant = row["variant"]
        verdict_word = row["verdict"].split("—")[0].strip().split(" ")[0].lower()
        verdict_class = {"kill": "verdict-kill", "keep": "verdict-keep"}.get(verdict_word, "verdict-retest")
        sig_plain = row["significant"].replace("**", "").strip()
        if sig_plain.lower().startswith("yes"):
            sig_class = "sig-yes"
        elif sig_plain.lower().startswith("no"):
            sig_class = "sig-no"
        else:
            sig_class = "sig-untested"
        table_rows.append(f"""
        <tr>
          <td class="mono">{esc(row['id'])}</td>
          <td>{esc(row['setup'])}{' / ' + esc(variant) if variant not in ('-', 'placeholder') else ''}</td>
          <td class="mono">{esc(row['date'])}</td>
          <td class="mono">{esc(row['sample_size'])}</td>
          <td class="mono">{esc(row['win_rate'])}</td>
          <td class="mono">{esc(row['expectancy'])}</td>
          <td class="mono">{esc(row['profit_factor'])}</td>
          <td class="mono">{esc(row['max_drawdown'])}</td>
          <td><span class="badge {sig_class}">{esc(sig_plain)}</span></td>
          <td><span class="badge {verdict_class}">{esc(row['verdict'])}</span></td>
        </tr>""")
    table_html = "".join(table_rows)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>NQ Research Platform &mdash; Dashboard</title>
<style>
  :root {{
    --bg: #f7f7f5; --card-bg: #ffffff; --border: #e3e2df; --text: #1f1e1c;
    --text-muted: #6b6a67; --accent: #2a5bd7; --positive: #1a7f4b; --negative: #c23b3b;
    --kill-bg: #fbe9e9; --kill-text: #9b2c2c; --keep-bg: #e6f4ec; --keep-text: #1a7f4b;
    --retest-bg: #eef1fb; --retest-text: #33459b;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 32px 24px 64px; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }}
  .wrap {{ max-width: 1100px; margin: 0 auto; }}
  header {{ margin-bottom: 28px; }}
  h1 {{ font-size: 1.6rem; margin: 0 0 4px; }}
  .subtitle {{ color: var(--text-muted); font-size: 0.9rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 16px; margin-bottom: 28px; }}
  .card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; }}
  .card h3 {{ margin: 0 0 10px; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); }}
  .stat-value {{ font-size: 1.4rem; font-weight: 600; margin-bottom: 4px; }}
  .stat-detail {{ font-size: 0.85rem; color: var(--text-muted); margin-bottom: 2px; }}
  .stat-footnote {{ font-size: 0.78rem; color: var(--text-muted); margin-top: 8px; }}
  .mini-row {{ display: flex; justify-content: space-between; padding: 4px 0; font-size: 0.9rem; }}
  .mini-label {{ font-family: ui-monospace, monospace; color: var(--text-muted); }}
  .mini-value.positive {{ color: var(--positive); font-weight: 600; }}
  .mini-value.negative {{ color: var(--negative); font-weight: 600; }}
  .promising {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 22px 26px; margin-bottom: 28px; }}
  .promising h2 {{ margin: 0 0 10px; font-size: 1.15rem; }}
  .highlight {{ color: var(--accent); }}
  .why-label {{ font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); margin: 14px 0 4px; }}
  .verdict-quote {{ font-style: italic; color: var(--text); margin: 0; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; font-size: 0.85rem; }}
  th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); vertical-align: top; }}
  th {{ background: #fafaf9; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.03em; color: var(--text-muted); }}
  tr:last-child td {{ border-bottom: none; }}
  .mono {{ font-family: ui-monospace, monospace; white-space: nowrap; }}
  .hypothesis-cell {{ max-width: 320px; color: var(--text-muted); }}
  .badge {{ display: inline-block; padding: 3px 9px; border-radius: 999px; font-size: 0.78rem; }}
  .verdict-kill {{ background: var(--kill-bg); color: var(--kill-text); }}
  .verdict-keep {{ background: var(--keep-bg); color: var(--keep-text); }}
  .verdict-retest {{ background: var(--retest-bg); color: var(--retest-text); }}
  .sig-yes {{ background: var(--keep-bg); color: var(--keep-text); }}
  .sig-no {{ background: var(--kill-bg); color: var(--kill-text); }}
  .sig-untested {{ background: #f0efec; color: var(--text-muted); }}
  .table-wrap {{ overflow-x: auto; }}
  section {{ margin-top: 32px; }}
  section > h2.section-title {{ font-size: 1.05rem; margin: 0 0 14px; }}
  .team-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
  .team-card {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 10px; padding: 18px 20px; }}
  .team-name-row {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
  .team-name {{ font-size: 1.1rem; font-weight: 600; }}
  .team-role {{ margin: 0 0 8px; font-size: 0.88rem; }}
  .team-detail {{ margin: 0; font-size: 0.8rem; color: var(--text-muted); }}
  .team-status-active {{ background: var(--keep-bg); color: var(--keep-text); }}
  .team-status-paused {{ background: #fbf1e0; color: #966a1a; }}
  footer {{ margin-top: 24px; color: var(--text-muted); font-size: 0.8rem; }}
  code {{ background: #efeeeb; padding: 1px 6px; border-radius: 4px; font-size: 0.85em; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>NQ Research Platform</h1>
    <div class="subtitle">Generated {esc(generated_at)} from research/experiments/ and data/ &mdash; regenerate anytime with <code>python3 src/generate_dashboard.py</code></div>
  </header>

  <div class="cards">
    <div class="card">
      <h3>Real Data On Hand</h3>
      {data_html}
    </div>
    <div class="card">
      <h3>ORB (placeholder setup)</h3>
      {orb_html}
    </div>
    <div class="card">
      <h3>Level Sweep Reversal &mdash; latest per variant</h3>
      {ls_html}
    </div>
  </div>

  <div class="promising">
    {promising_html}
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>ID</th><th>Setup / Variant</th><th>Date</th><th>Sample Size</th>
          <th>Win Rate</th><th>Expectancy</th><th>Profit Factor</th><th>Max Drawdown</th>
          <th>Statistically Significant</th><th>Verdict</th>
        </tr>
      </thead>
      <tbody>
        {table_html}
      </tbody>
    </table>
  </div>

  <section>
    <h2 class="section-title">Meet the team</h2>
    <div class="team-grid">
      {render_team_section()}
    </div>
  </section>

  <footer>
    Sample size is parsed from each experiment's own write-up file; shows &ldquo;-&rdquo; if the wording couldn't be matched.
    All numbers are net of estimated trading costs unless a row's Expectancy text says otherwise.
  </footer>
</div>
</body>
</html>
"""


def main():
    index_rows = parse_index_table()
    if not index_rows:
        print("No rows found in research/experiments/_index.md -- nothing to build.")
        return

    rows_by_group = {}
    for row in index_rows:
        key = (row["setup"], row["variant"])
        rows_by_group.setdefault(key, []).append(row)

    active_data, all_data_files = gather_data_coverage()
    most_promising = build_most_promising(rows_by_group)
    orb_latest, ls_latest = build_setup_status(rows_by_group)

    html_out = render_html(index_rows, rows_by_group, active_data, all_data_files, most_promising, orb_latest, ls_latest)
    OUT_PATH.write_text(html_out)
    print(f"Built {OUT_PATH} from {len(index_rows)} logged experiments.")
    print("Open it by double-clicking dashboard.html in Finder, or dragging it into a browser window.")


if __name__ == "__main__":
    main()

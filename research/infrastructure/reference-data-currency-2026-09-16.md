# Reference-data currency — the non-price series, made current and self-maintaining

**Written 2026-09-16 (7:00 pm cycle). Tony does not edit the standing directive; this is
infrastructure under it, in the shape of the price top-up that already works.**

## What was wrong

The price series is topped up daily. Nothing else was. Two consecutive cycles hit the same
wall, and by the second it was blocking the queue rather than a single candidate.

| Series | Covered through | Short of the price data | Who reads it |
|---|---|---|---|
| **VXN** (`data/VXNCLS_MAX.csv`) | **2026-09-02** | 14 days | `market_state_primitives_v2._load_vxn_daily` / `extend_state_frame` (`vxn_level_vs_trailing`), `salvage_check.vxn_labels` (**Salvage menu condition 1**), `study_s002_night_leg_menu`, `idea_factory`, `observatory_free_look`, the three `study_vxn_*` scripts, the validated VXN → next-session-range magnitude fact used for stops and sizing, and **S010a**, which selects LOW-VXN sessions only |
| **FOMC** (frozen list in `study_fomc_volatility.py`) | **2021-09-22** | 1,820 days | `salvage_check.news_labels` (**Salvage menu condition 4**), `study_fomc_volatility`, `study_pre_fomc_drift`, and **S009a**, which trades only on days with no scheduled macro event |
| **CPI** (frozen list in `study_economic_calendar.py`) | **2023-12-12** | 1,009 days | as above, plus `validate_exp039_economic_calendar` |
| **NFP** (same file) | **2023-12-08** | 1,013 days | as above, plus `study_pre_nfp_drift` |

Those ranges cover the Discovery screen. They do not cover a 2026 session the paper loop scores.

**The dangerous failure was the silent one.** `d in FOMC_SET` returned `False` for a 2026 date
not because the day was quiet but because the list stops in 2021 — and `extend_state_frame`
forward-filled the 2026-09-02 VXN close onto every session after it. Both read as data.
Neither is. Fail open would have made S009a's paper record S009's under another name.

## What was built

- **`src/reference_data.py`** — the single owner of reference-series coverage and the
  **fail-closed** accessors. `vxn_close()`, `scheduled_events_on()` and
  `is_scheduled_news_day()` raise `ReferenceDataUnavailable` for a session past coverage
  instead of returning a default. The frozen sourced lists are never edited; a fetched
  extension (`data/macro_event_calendar.csv` + a coverage sidecar) is unioned with them, and
  with no sidecar coverage falls back to the frozen lists' own last date — conservative in the
  right direction, it refuses more and never less. The macro coverage end is the **minimum**
  across FOMC/CPI/NFP, because a day is only honestly "quiet" once every series that could
  have put an event on it has been checked.
- **`src/data_topup_vxn.py`** — incremental top-up from CBOE's published daily history
  (`https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv`, header
  `DATE,OPEN,HIGH,LOW,CLOSE`, verified live 2026-09-16). Old observations win on every
  overlap; it **proves the fetched series is the one on disk** (trailing-40 comparison, abort
  on any disagreement) before extending it; continuity-checks the result; logs what it added;
  production-guarded.
- **`src/data_topup_macro_calendar.py`** — incremental top-up of the FOMC/CPI/NFP schedule
  from federalreserve.gov and bls.gov. **A mis-parsed schedule is a fabricated event date**,
  so the parser is assumed wrong until it proves otherwise: every parsed date inside a frozen
  list's range must reproduce that list exactly, and the result must have the shape a real
  schedule has (8 FOMC decisions a year on a Tue/Wed/Thu; 12 BLS releases a year, one a month;
  NFP always a Friday). Any failure writes **nothing** and prints what it saw.
- **Fail-closed wiring.** `salvage_check.news_labels` and `.vxn_labels` now refuse a session
  outside coverage rather than labelling it QUIET or carrying a stale level onto it.
  `extend_state_frame` still forward-fills a hole *inside* the series and now leaves the tail
  *past* the series end as NaN.
- **`research/ledger/data_coverage.json`** — the coverage state, each series with its last
  date, its consumers and its updater — refreshed by `python3 src/reference_data.py --write`
  and surfaced in `cycle_preflight.py`, so a future cycle sees staleness before it spends a
  candidate on it.

Tests: `tests/test_reference_data.py`, `tests/test_data_topup_vxn.py`,
`tests/test_data_topup_macro_calendar.py`, plus the fail-closed cases appended to
`tests/test_salvage_check.py` and `tests/test_cycle_preflight.py`.

## What Jason has to do — one line, once

`cdn.cboe.com`, `www.federalreserve.gov`, `www.bls.gov` and `fred.stlouisfed.org` are all off
the sandboxed shells' egress allowlist (verified 2026-09-16: HTTP 403 at the proxy from the
device shell **and** from the cloud container, the same wall `hist.databento.com` sits behind).
Both scripts run to completion and print exactly that when a cycle tries. They cost nothing —
no account, no key, no spend — and they belong beside the existing 7 am Databento top-up:

```cron
0 7 * * *  cd ~/Documents/nq-research-platform-live && /usr/bin/python3 src/data_topup_databento.py  >> data/_fetch_run.log 2>&1
5 7 * * *  cd ~/Documents/nq-research-platform-live && /usr/bin/python3 src/data_topup_vxn.py            >> data/_fetch_run.log 2>&1
10 7 * * 1 cd ~/Documents/nq-research-platform-live && /usr/bin/python3 src/data_topup_macro_calendar.py >> data/_fetch_run.log 2>&1
```

VXN daily, the calendar weekly (a published schedule changes rarely). Run each once by hand
first — `python3 src/data_topup_vxn.py --dry-run` and
`python3 src/data_topup_macro_calendar.py --dry-run` write nothing and print what they would
add. **The macro-calendar parsers have never met the live pages** (no shell here can reach
them), so the first real run is also their first test; that is exactly why they refuse to write
anything that fails verification, and why a failure prints the dates it actually parsed.

Until that happens the series stay stale and every consumer refuses the affected sessions out
loud. That is the intended state: a refusal is visible, a guess is not.

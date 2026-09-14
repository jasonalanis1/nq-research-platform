# hyp-000156 (M23) — frozen one-shot Validation spec

Frozen: September 13th, ~7:10 pm CT, before any Validation data exists on disk.
Status: **CONDITIONS RESOLVED (September 13th ~9:30 pm CT); BLOCKED ON DATA** — 6E on disk covers 2015-01-01 → 2021-10-03 (the Discovery
slice only). The Validation slice, 2021-10-04 → 2024-01-03, has never been fetched.

Revised September 13th, ~9:30 pm CT to resolve the five blind-Gate conditions
(research/integrity/gate-hyp156-blind-2026-09-13.md). The test itself is unchanged in
substance; what changed is that every ambiguity the Gate named is now decided **in
writing, before the data exists**, and the script is written and hashed.

## Gate conditions — resolved

**C1 · paired vs unpaired, and which null.** ONE test: the **paired per-day difference**,
the construction the Statistical stage used and the construction this candidate was
promoted on. Scan 030's unpaired pooled-mean difference is not the test; switching to it
now would be choosing a test after seeing Discovery results. The baseline is named
honestly as the **US-RTH hourly baseline** (six one-hour bins, 09:30–16:00 ET), not a
24-hour baseline. 6E trades nearly around the clock, so comparing the London hour against
its US-RTH hours is deliberately the harder comparison. The mechanism doc's §4 wording
("every hourly window across the 24-hour session") is superseded by this paragraph,
before the test, not after it.

**C2 · script written, frozen, hashed.** `src/validate_hyp156.py` exists as of this
revision. Šidák is written as a **rule, not a number** — `max(20, N_validation at run)`,
so it cannot drift downward. `N_BOOT = 20000` (at the adjusted tail, Scan 030's 3,000
draws would leave ~8 draws deciding the answer). Block bootstrap, block = 10, seed
20260913.
sha256 of the frozen script: `e679fba6968e00339e7a809520a8f65cf51ad1ffcc3f57532e49114d506a790f`
If that hash does not match at run time, the run is not this pre-registered test.

**C3 · timezone, DST, ATR warm-up, provenance.**
*Timezone*: the data index is America/New_York (`timestamp_ny`, verified on the Discovery
file), so the ET windows mean what they say.
*DST*: the **gating** window stays 03:00–04:00 ET, identical to Discovery, because the
test must be the same test. For the ~3 weeks a year when the US and UK clock changes are
out of step London opens at 04:00 ET; two **non-gating** diagnostics are pre-registered
for that — the same statistic on the DST-aware window (08:00–09:00 Europe/London), and
the count of days where the two windows coincide. No days are excluded.
*ATR warm-up*: ATR14 is built on the concatenated Discovery+Validation frame and only then
restricted to Validation dates, so the first 14 Validation sessions warm up from the
Discovery tail. No day is scored on a partial ATR and no day is dropped for it.
*Provenance / roll parity*: the Validation file must match the Discovery file on vendor,
dataset, symbology and continuous-contract roll rule. The script asserts this and refuses
to run on a mismatch rather than printing a number that is not comparable.

**C4 · the origin field, explained not changed.** `strategy_origin: data_discovered` is
this project's ledger convention for "surfaced by a scan of data already held", as opposed
to `literature` or `operator_proposed`. It is not a record of fishing: the map entry (M23)
and the mechanism doc both predate Scan 030. The convention is now stated in the blind
packet itself (`src/integrity_blind_packet.py`), so a fresh reviewer is not left to guess,
and the masked Statistical-stage output is attached to the packet rather than omitted.

**C5 · kill diagnostics, pre-registered and non-gating.** Two are added: minute-bar
**density** inside the window (median and 5th percentile of distinct minutes carrying a
bar), and the **first-five-minute share of the window's realized variance**. Both are
reported on every run. Neither can change the verdict — they exist so that a PASS produced
by a data artifact is visible rather than invisible. The original first-minute share check
is kept.

**Not resolved, and deliberately so.** The Gate's point 8 — whether paying for data to
validate a characterization with no product path in *this* entry is a good use of money —
is a Director/Jason question, not a procedural one. It is answered by the family framing:
this is the scheduled-event and session-transition volatility family (M20 + M21 + M23), and
the monetization question belongs to the family. Jason decides whether to spend.

## The one test
The frozen construction on the Validation slice, per C1 above:
per day, |return 03:00–04:00 ET| / ATR14 (ATR14 = trailing-14-session mean of the
09:30–16:00 range, shifted one day) minus that day's mean unconditional hourly
|return| / ATR14 over 09:30–16:00. Block bootstrap block=10, N_BOOT=20000,
SEED=20260913, 90% CI. **PASS = CI on the mean diff entirely above zero AND the
Šidák-adjusted CI at `max(20, N_validation at run)` also above zero.**
Pre-London specificity cell (02:00–03:00) reported, not gated. First-minute share
kill check as in Scan 030. One shot; no retuning; no alternate windows examined.

## Power (from the Statistical stage)
Discovery sd of the per-day diff = 0.2066; Discovery effect +0.0537. Validation
n will be ~570 trading days if the slice is fetched in full; at that n, power at
the Discovery effect ≈ 1.0, at half the effect ≈ 0.97 — the test is decisive
either way. No outcome on Validation has been examined (none exists on disk).

## What this needs from Jason
One data pull: 6E 1-minute OHLCV, 2021-10-04 → 2024-01-03, from Databento via
`src/quote_data_pulls.py` on his Terminal (neither the device shell nor the cloud
can reach Databento). Expected cost is in the same band as the September 12th
quotes (ES $14.69 for a longer span) — under the $5+ rule it is his call. This is
NOT a Data Acquisition Trigger question (it is the same data type, for the slice
the protocol already requires), but the dollar rule still applies.

## After the pull
Run `src/validate_hyp156.py` (already written and hashed; check the hash first) → Monetization (v2.5 order) → blind Gate → Holdout request. Monetization note
in advance: 6E has no base strategy in this project; M6E micro contracts exist;
this is the scheduled-event / session-transition volatility family (M20+M21+M23),
so the monetization question is the family's, not this entry's alone.

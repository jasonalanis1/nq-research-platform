# S012 — monthly opex-week delta-hedge unwind: CLOSED TO LEARN WITHOUT A SPECIFY, A FREEZE OR A SCREEN

9:00 am cycle, 2026-09-18 (Tony, scheduled, unattended). Directive
`research/infrastructure/standing-directive-2026-09-15.md` s.2 (SOURCE → SPECIFY), s.9 (revamp
list; clean nulls stay dead), Amendment 1 (SOURCE priority).

**Verdict: S012 must not be built. Its question was already asked, answered against the correct
baseline, with an adequate sample, and its closure form forbids the retest by name.**

---

## 1. What S012 was sourced as

`research/ledger/strategies.jsonl`, row `S012`, `ts` 2026-09-18T04:14:01Z, stage SOURCE:
*"S012 monthly opex-week delta-hedge unwind, NQ (M25 / hyp-000158)"*, registered last cycle so
the queue would not sit empty after S011 moved to BLOCKED_PENDING_REFERENCE_DATA. Its own
sourcing note argued it was safe to advance under the reference-data gate because it is
**price + clock only** (the third Friday is computable). That part is true and is not the
problem.

## 2. Why it cannot be built — three findings, any one of which is sufficient

### (a) The gating test S012 would have to pass has already been run, and it failed

`research/ledger/hypotheses.jsonl`, `hyp-000158` (Scan 032, 2026-09-13), status **REJECTED**:

> P1 gate (expiration-week NQ return, ATR14-normalized, **net of NQ's own unconditional weekly
> drift**) **FAILED**: mean **+0.1872**, ci_90 **(−0.0291, +0.3950)**, n = **80 expiration weeks**.

That P1 is *already the two-nulls test* — the own-drift baseline gate this project now builds
into every spec, the one that killed H118 and S004. S012's SPECIFY would have had to add an
own-drift baseline arm; **that arm has already been run and the candidate did not clear it.**
P2 (expiration minus non-expiration) was also not credible: diff +0.2429, ci_90 (−0.1167, +0.5907).

The scan's own note anticipates the trap precisely: NULL1's unconditional weekly mean is itself
**+0.3343** (NQ's known positive drift), *"so a positive raw expiration-week number is expected
regardless of any expiration-specific effect, which is exactly why the NULL1-relative test is the
one that governs."* A screen run against zero would have printed a profitable-looking number that
means nothing. This is the S004 failure re-run in advance.

### (b) The closure form forbids this retest verbatim

`research/ledger/closures.jsonl`, `hyp-000158`, form U8-1.0:

| field | value |
|---|---|
| `status` | **clean null** |
| `sample` | **adequate (80 weeks)** |
| `mech` | **falsified for NQ** |
| `not_retest` | **"Opex-week directional claims on NQ."** |
| `condition` | **none** |
| `action` | reduce family (literature calendar) |

S012 *is* an opex-week directional claim on NQ. `condition: none` means there is no re-entry
route — unlike hyp-000152 (which permits one conditioning on a validated state) or hyp-000157 and
hyp-000159 (attempt 2 of 2 under the 8-condition protocol). Directive s.9's bottom rule, clean
nulls stay dead, governs. **This is the S006 precedent exactly**
(`research/studies/S006-stack-a-not-rebuilt-2026-09-17.md`, 9:00 pm cycle September 17th), one
cycle later, and it is the second time a queue row was registered at SOURCE without its closure
form being read first.

### (c) The named fallback is banned on identical grounds

The queue's next item, **hyp-000147 (intraday periodicity, M17)**, is in the same position and
was checked before being taken:

- `hyp-000147` (Scan 022): **P1 FAIL**, OPEN slot −0.013 ATR ci_90 (−0.026, +0.001); CLOSE −0.003
  (−0.011, +0.005); MIDDAY control −0.005 — *no slot distinguishable from any other*, n = 1,632.
- Closure form: `status` **clean null**, `sample` **adequate**, `mech` **falsified**,
  `not_retest` **"Intraday return periodicity on NQ."**, `condition` **none**.

Also checked and also unavailable: **hyp-000146 / M16** (first-30 → last-30 intraday momentum,
Gao-Han-Li-Zhou) — P1 FAIL, every cell null, and its own LEARN line closes *"session-anchored
continuation claims from the literature channel"*; the practitioner follow-on it named, **P-2
opening-drive exhaustion**, was re-ruled and **CLOSED** in `research/sourcing/practitioner.md`
(the whole P-1…P-4 practitioner stream is RULED out). The point estimate of M16 running slightly
negative is **not** a licence to build the fade: its CI spans zero, and building on the sign of a
null's point estimate is failure mode #7.

## 3. Note on the whole calendar-anomaly channel

Amendment 1 puts published calendar anomalies **LAST** in the SOURCE priority, "0 for 4". With
M25 (opex week) added to M28, M32, M33, M34 and M35, the directional-lane record on published
calendar anomalies is now **0 for 9**. S012 was a calendar anomaly wearing a dealer-flow label;
the label did not change the result, and the record says to stop drawing from this channel while
any other channel has stock.

## 4. What this cycle did instead of a screen

**No SPECIFY, no FREEZE, no SCREEN was spent.** Nothing was screened against zero; no baseline
arm was run; no cost table was produced, because producing one would have implied a candidate
that has a live question. Per s.7, **no Salvage is owed** — a Salvage follows a KILL after a
screen, and there was no screen. S012 goes straight to **LEARN**.

## 5. This is NOT directive s.10 reason 2 — stated explicitly, with the check

Reason 2 requires **all four** of: the queue empty, the revamp list worked through, the Salvage
queue empty, and Discovery out of priority sources. Checked this cycle:

- **Revamp list: NOT worked through.** `research/ledger/revamp_list.json` holds 137 entries. In
  the top tier alone, `hyp-000136`, `hyp-000139`, `hyp-000021`, `hyp-000060` and the pre-Gate
  scan block `hyp-000072`–`hyp-000078` carry **no U8 closure row and no `not_retest` ban**.
- **Salvage queue: NOT empty.** S007, S009 and S004 are owed (`src/rerun_salvages.py`), currently
  gate-blocked on VXN/CPI/FOMC/NFP — blocked is not empty.

So the correct reading is **a bad queue row, not exhaustion.** The queue is re-sourced in s.6.

## 6. Replacement sourced: S013 (SOURCE only)

**S013 — opening-auction order imbalance, NQ (hyp-000076, pre-Gate scan tier).**
Chosen because it is the only remaining tier that is simultaneously (i) free of any `not_retest`
ban, (ii) **intraday and fires every session** — Amendment 1's top SOURCE preference, the
property S012 never had (~12 events/year, structurally SLOW) — and (iii) price+volume only, so
it is not blocked by the reference-data gate at SPECIFY, FREEZE or SCREEN.

`hyp-000076` (`opening_volume_imbalance`, Discovery) closed REJECTED at
**expectancy −0.0614 R**, best interval **(−0.1047, −0.0170)**, credibly negative — but it is a
**pre-Gate** row: **MED** mechanism, **no mechanism doc**, and, decisively, it was measured
**against zero, never against NQ's own drift over the same holding period**. That is the same
defect the revamp list's own top note raises for the H118 lineage.

**Three conditions are pre-registered here, before any work, so the next cycle cannot drift:**

1. **A mechanism doc naming the forced counterparty must be written FIRST**, before any scan or
   spec — the pre-Gate rows have none, and a MED "practitioner hypothesis with a stated reason"
   is not a mechanism.
2. **An explicit overlap check against S011 is mandatory before SPECIFY.** S011 already trades a
   Campbell-Grossman-Wang inventory-concession story at the 09:30 open. If S013's mechanism is
   the same flow at the same clock, it is an S011 variant and must be dropped, not built.
3. **Sign-flipping is forbidden as a rationale.** "The continuation rule lost money, so fade it"
   is not a mechanism; a credibly negative expectancy measured against zero on a drifting
   instrument is substantially a statement about drift and costs. If the mechanism paragraph
   cannot stand on its own without the minus sign, S013 closes at SOURCE too.

If S013 fails condition 1, 2 or 3 at the next cycle's SPECIFY, the honest next step is to work
down the remaining unbanned revamp tier rather than to force it.

## 7. Record

- `S012` → **LEARN**, registry row appended (no freeze, no screen, no salvage owed).
- `S013` → **SOURCE**, registry row appended with the three pre-registered conditions above.
- Standing lesson for `research/KNOWLEDGE.md`: **read the U8 closure form's `not_retest` and
  `condition` fields at SOURCE, not at SPECIFY.** Twice in two cycles (S006, S012) a candidate
  was registered into the queue and only found to be a forbidden retest when the next cycle
  opened it. The closure form is the cheapest gate this project owns and it was being read last.

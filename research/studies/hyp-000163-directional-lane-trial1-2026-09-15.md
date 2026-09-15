# hyp-000163 -- Directional Lane Trial 1: NYSE pre-holiday effect, NQ (Entry 32 / M28)

Written: 2026-09-15, ~11:00 pm CT (scheduled cycle). Discovery-stage result.

## What this is

Directional Lane trial 1 of 20 (research/infrastructure/refocus-2026-09-15.md
s.4; research/ledger/directional_lane.json). Sourced from the literature
channel (mechanism/calendar, non-state), so it qualifies under the memo's
sourcing rule. This is NOT the memo's own suggested "first candidate"
(overnight-vs-intraday split) -- that idea was already tested once as
hyp-000145 (research/ledger/hypotheses.jsonl:178, Entry 19/M15, Scan 020,
2026-09-12, clean null). Per research/NEXT_UP.md:625-640, the discrepancy
between the memo's framing and the ledger's actual history was reviewed by a
prior cycle (2026-09-15) and recorded there; that cycle's ruling was that
trial 1 goes to the next genuinely new non-state directional idea -- Entry 32
(M28, pre-holiday effect), sourced, drawable, and directional -- rather than
re-litigating the M15 family without new information. This cycle executed
that call and reports the discrepancy again here for the record.

Mechanism doc (written 2026-09-13, before any scan, before the memo existed):
research/mechanisms/pre-holiday-effect-nq-m28.md. Idea inventory entry:
research/idea_inventory.md:1876 ("ENTRY 32 -- M28 ... SOURCED, DRAWABLE").
Scan: src/market_behavior_discovery_scan_037.py (registered and run this
cycle, results: data/scan_037_2026-09-15_results.json).

## Claim (frozen before the run)

P1 (GATING): the RTH session immediately before an NYSE full-closure holiday
shows a credibly POSITIVE return relative to NQ's own unconditional daily RTH
return (NULL 1 convention, src/baseline_relative.py), 90% block-bootstrap CI
entirely positive.
P2 (reported): the session immediately AFTER a holiday does NOT show the same
elevation (specificity check).

## Method

NQ daily RTH return (close of last RTH bar minus open of first RTH bar),
Discovery slice ONLY (2015-01-01 -> 2021-10-03, src/data_split.py). NYSE
full-closure holiday calendar hardcoded in the scan script (9 recurring
holidays per year, observed closure dates, Juneteenth excluded as it postdates
the Discovery slice). Pre-holiday session = last Discovery session with RTH
data strictly before each holiday date; post-holiday session = first Discovery
session with RTH data strictly after. Block bootstrap, block=5, N_BOOT=3000,
SEED=20260913, 90% CI -- matching the M19/M22/M25 thin-annual-event-count
convention (mechanism doc Section 9). One shot, four pre-registered cells, no
retuning after seeing results.

## Result

Discovery RTH sessions usable: 1,686. NYSE holidays matched inside the
Discovery data on both sides: 60 of 61 in the calendar list (one, New Year's
Day 2015, has no prior Discovery session since Discovery starts 2015-01-01).

- **Cell 1 (P1, GATING):** pre-holiday session mean +0.3042 pts vs NULL 1
  (unconditional daily RTH mean) +2.7153 pts. diff **-2.4111 pts**, block CI
  90% **(-15.6156, +4.4224)** -- includes zero. **NOT credible. P1 FAILS.**
- **Cell 2 (P2, specificity, reported):** post-holiday session mean +12.2958
  pts vs NULL 1 +2.7153 pts. diff +9.5805 pts, CI (-3.9412, +24.9080) -- also
  not credible. Moot: P1 already fails, so specificity is not reached.
- **Cell 3 (NULL 1 reference):** unconditional Discovery daily RTH return
  mean +2.7153 pts, n=1,686.
- **Cell 4 (thin-sample disclosure):** n=60 pre-holiday sessions, clears the
  pre-registered 40-session floor (mechanism doc falsifier c). NOT a
  thin-sample result.

**VERDICT: P1_FAIL -- CLEAN NULL.** The pre-holiday session's own RTH return
does not credibly exceed NQ's ordinary daily RTH return; both the point
estimate (-2.41 pts) and the wide CI straddling zero say the historically
documented equity pre-holiday effect (Lakonishok & Smidt 1988, RFS; Ariel
1990, JFE) does not transfer to NQ futures at this data ceiling. This closes
per the mechanism doc's falsifier (a).

## Disposition

REJECTED at Discovery. Attempt 1 of 2 for the M28 family (mechanism doc
Section 7: NEW ruling, distinct from M6/M22/M24/M25). Per this project's
culture, a clean, correctly-specified null is a legitimate, reportable
outcome -- not a failure. No Statistical/Director/Gate/Validation stage run
this cycle: this is trial 1's Discovery-stage result only, one stage per
cycle at the current daytime cadence (research/NEXT_UP.md pipeline sweep
rule), and the frozen scope calls for exactly one Discovery shot with no
immediate follow-on for a failed gating cell. Ledger row:
research/ledger/hypotheses.jsonl (hyp-000163, appended
2026-09-15T04:1x CT). Directional lane ledger:
research/ledger/directional_lane.json (trial 1, used=1/20, 19 remaining).

## Note on the file-numbering discrepancy in the ledger note

The ledger row's `notes` field for hyp-000163 references this file as
`research/studies/hyp-XXXXXX-directional-lane-trial1-2026-09-15.md` (written
before the hypothesis ID was assigned, per this project's `log_hypothesis()`
ID-allocation order). The actual filename is
`research/studies/hyp-000163-directional-lane-trial1-2026-09-15.md`. Recorded
here rather than as a separate ledger status-update row, to avoid spending an
extra ledger line on a purely cosmetic pointer fix.

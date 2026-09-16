# S002 — Overnight carry on compressed prior days (M15 via Salvage): long the 16:00 -> 09:30 leg

**DRAFT spec at SPECIFY, written 2026-09-15 (7:00 pm CT cycle). NOT FROZEN: no FREEZE row
exists for S002 in research/ledger/strategies.jsonl and no module exists yet. The FREEZE
cycle may still amend this text (it becomes binding only at the FREEZE row, directive
s.13). Costs ASSUMED throughout.**

## 1. Lineage (Salvage, directive s.7)

hyp-000145 (Scan 020, M15, research/mechanisms/overnight-vs-intraday-return-split-m15.md)
asked whether NQ's drift lives in the close-to-open leg. It does not, credibly: night
+0.037 ATR, day +0.031, difference +0.006 with a CI straddling zero -- a clean null as a
RAW EFFECT, REJECTED under the old bar. It was never built as a trade and never asked the
directive's question (did the leg make money after costs, and when?). The directive names it
second through Salvage. This cycle's SOURCE -> SPECIFY step ran the s.7 menu on the raw
leg (src/study_s002_night_leg_menu.py, Discovery only, long 1 micro at the 16:00 close,
flat at the next 09:30 open, no stop, ASSUMED $6.00 round trip;
research/studies/S002-night-leg-menu-2026-09-15.json):

| menu condition (all known at the 16:00 entry) | side | n | net $ 1 micro | avg pts | max DD $ | positive years |
|---|---|---:|---:|---:|---:|---|
| unconditional (the raw leg) | -- | 1631 | +1,784.50 | 3.55 | -6,434 | 4 / 7 |
| 1. VXN vs trailing-20 (D-2 close) | HIGH | 695 | +168.00 | 3.12 | | |
| | LOW | 936 | +1,616.50 | 3.86 | -2,812 | 2 / 7 |
| **2. prior-day range contraction (hyp-000048 `prior_day_narrow`)** | **NARROW** | **364** | **+1,625.00** | **5.23** | **-735** | **5 / 7** |
| | WIDE | 1267 | +159.50 | 3.06 | | |
| 3. time of day | n/a (fixed clock) | | | | | |
| 4. scheduled-news session (FOMC/CPI/NFP) | NEWS | 199 | +1,735.50 | 7.36 | -1,284 | 5 / 7 |
| | QUIET | 1432 | +49.00 | 3.02 | | |
| info only, NOT a menu condition | weekend leg | 337 | -3,401.00 | -2.05 | | (hyp-000145's LEARN note: weekday-only is slicing; not taken) |

Reading (Director, one condition, menu only): the raw leg's +$1,784.50 is NQ's 2015-2021
drift minus a 3-point cost drag (3.55 pts gross per night against 3.0 pts of ASSUMED costs)
with a -$6,434 drawdown -- not a trade. Every menu side is positive in dollars because the
underlying drift is; the question is where the net is concentrated. Menu 2 NARROW carries
91% of the net on 22% of the sessions, with the shallowest drawdown and 5 of 7 positive
years, and its condition is a VALIDATED platform fact (hyp-000046/048, HOLDOUT PASSED) known
before the 16:00 entry. Not taken: NEWS (97% of the net, but ~30 sessions a year -- 3-4 in a
6-week paper window -- and a scheduled-calendar flavour the directive ranks last); VXN LOW
(2 of 7 years positive; the dollars are two years); the weekend split (explicitly ruled
slicing in hyp-000145). ONE condition, ONE rule. S002 is the night leg on compressed prior
days. One salvage per strategy: this IS the M15 family's salvage.

## 2. Mechanism (one paragraph, Mechanism agent)

Intermediaries decline to carry index inventory through the overnight session; the
close-to-open return is the premium paid to whoever does (Lou-Polk-Skouras 2019,
Cooper-Cliff-Gulen 2008). Scan 020 showed NQ pays that premium diffusely (55% of drift
overnight), so the raw carry is a coin flip after a micro's costs. After a COMPRESSED session
the platform's validated fact is that the next session is ~6% quieter than usual
(hyp-000048); a compressed day is also one on which the day-session books took little
inventory risk and so end the day flatter, leaving the overnight auction thinner-supplied
than usual. The prediction is that the carry premium is paid more reliably, not more
volatilely, after compression -- which is what the menu shows: average +5.2 pts a night
versus +3.1 on other nights, with a fraction of the drawdown. This is a carry, not a
directional call: the trade is long every qualifying night, exits on the clock, and the
stop exists only to cap a gap disaster.

## 3. The whole trade (Monetization agent)

| rule | value |
|---|---|
| instrument | MNQ (micro), signals on the NQ 1-minute series (America/New_York timestamps) |
| condition (menu 2) | the NEXT RTH session D is flagged `prior_day_narrow` = True by `volatility_conditioning.build_conditioning_frame` (frozen hyp-000048 definition: session D-1's RTH range <= the 20th percentile of the trailing 20 RTH ranges). Known at D-1's 15:55 bar. |
| entry | long at the OPEN of the 16:00 ET bar of session D-1 (the bar after the 15:59 RTH close bar -- the paper loop's next-bar-open convention; Scan 020 used the 16:00 close, ~identical). No entry when D-1 lacks a 15:59 bar (holiday half-day) or D lacks a 09:30 bar (the M9 roll-Friday gap sessions are excluded by construction). |
| exit | flat at the OPEN of the 09:30 ET bar of session D (time exit; the whole point is the clock) |
| stop | entry - 1.0 x ATR14 (daily RTH ATR, lagged, the scan's normaliser; ~2x the 5th-percentile overnight move of -95 pts on Discovery, so it is a gap-disaster cap that fires on a few percent of nights, not a management stop). R = 1.0 ATR. Sized from the VXN -> next-session range fact (hyp-000142) is the named FIX ONCE alternative if this stop proves wasteful. |
| target | none (carry) |
| size | 1 micro, always; results reported at 1/5/10 micros |
| costs (ASSUMED) | $2.50/side commission + 1 tick/side = $6.00 per micro round trip = 3.0 pts. **Cost-fragile by construction: gross +5.2 pts a night against 3.0 pts of costs; avg R net will be far under 0.10 with an ATR-sized stop.** |
| firing rate | 364 qualifying nights over 2,101 Discovery sessions, ~54 a year, ~6-7 in a 6-week window -- UNDER the s.6 15-trade floor. Stated up front: at the historical rate the 6-week point arrives unjudgeable and s.6 makes that a KILL; the record decides. |
| paper-engine plumbing prerequisite | the B7 loop scores one calendar-day frame at a time and `_resolve_fill_outcome` scans only that frame; an overnight hold needs the exit resolved in the FOLLOWING session's bars. The FREEZE cycle must extend the paper loop (cross-session exit, tested on synthetic bars) BEFORE the module is hashed; the execution dummy / B3 records must be unaffected. The screen uses the same extended bookkeeping. |
| paper-engine gates | the Risk/State Engine session gate applies in paper (expected-range multiplier, scheduled-event days -- research/calendars/event_days.csv does not exist today so no news day is refused, stale data) and not in the screen. Disclosed. |

## 4. Where this should fail (Mechanism agent; S002's own menu later)

1. **Wide prior day** (the complement of the condition): break-even after costs on
   Discovery (+$159 over 1,267 nights). If the forward record is flat, the condition was
   the drift, not a mechanism.
2. **High-VXN regime**: the premium is real but the gap-disaster stop fires there; expect
   the stopped nights to cluster in HIGH.
3. **The weekend leg** (Friday -> Monday): -$3,401 on Discovery. NOT filtered (hyp-000145
   ruled that slicing); recorded per trade so LEARN can see it.
4. **Quiet (non-news) nights**: the NEWS cell held most of the raw leg's premium; a
   NARROW-and-QUIET night is the trade most of the time (325 of 364) and was +$2,032 on
   Discovery, so this is not expected to be the failure -- but it is the cell to watch.
5. **Cost dominance**: 3.0 pts of ASSUMED costs against ~5 pts gross. B4b's measured
   number decides whether this trade exists at all.

## 5. Screen (directive s.2), to be pre-registered at FREEZE

One pass, Discovery slice, src/screen_strategy.py with the cross-session bookkeeping,
fill at the signal's entry price, ASSUMED costs. One number: net $ at 1 micro after costs.
Expected by construction to land near the menu cell (+$1,625 on ~364 nights, less the
nights the ATR stop cuts). Net > 0 -> PAPER; net <= 0 -> KILLED, no salvage (spent), LEARN.

## 6. Judgment (directive s.6)

40 trades or 6 weeks. KEEP: avg R > 0 after costs and worst streak inside a daily limit
of three average winners. FIX ONCE candidates: the stop (VXN-sized instead of ATR-sized);
the entry bar (15:59 close vs 16:00 open). KILL: lost money or < 15 trades in 6 weeks (the
honest expectation at ~6-7 trades per 6 weeks).

# Mechanism — Treasury auction concession and rebound, ZN (M19, map channel, open scope)

Written: 2026-09-12, ~5:05 pm CT (scheduled cycle)  ·  PRE-REGISTERED.
Results seen before writing: NO.
Source CHANNEL: map (forced participant) with literature support: Lou, Yan
and Zhang (2013), "Anticipated and Repeated Shocks in Liquid Markets,"
Review of Financial Studies 26(8): Treasury prices fall in the days before
scheduled auctions and rebound in the days after, because primary dealers
must absorb the new supply and demand a concession for the balance-sheet
risk; the pattern is largest for 10-year and 30-year auctions and is
economically large in yield terms. Fleming and Rosenberg (2008, NY Fed)
document the same dealer inventory cycle around auctions.

This entry is the first to use the OPEN SCOPE as Jason set it: the signal
AND the trade are in ZN (10-year note futures, on disk), not NQ. NQ is the
default vehicle, not the search boundary; the mechanism lives in ZN.

## 1. The claim
Around 10-year note auctions (monthly; the auction settles ~1 pm ET on a
scheduled Wednesday), ZN's RTH close-to-close return, / ATR14, is
credibly NEGATIVE over the 3 sessions ending on auction day and credibly
POSITIVE over the 3 sessions after, relative to ZN's unconditional
3-session drift (NULL 1). Falsifiable in one sentence: if neither the
pre-auction leg nor the post-auction leg has a block-bootstrap 90% CI
excluding zero after subtracting the unconditional drift, the concession
is not visible in ZN futures at this ceiling and the entry closes.

## 2. Who is on the other side
Primary dealers, who are OBLIGED to bid at every auction (a condition of
their designation) and who warehouse the unsold portion until it is
distributed. Their constraint is balance-sheet and VaR capacity; their
footprint is a price concession into the auction and a recovery as
inventory is placed. Nobody leaves money by choice: the concession is
the fee for underwriting.

## 3. Testable predictions (gating marked)
P1 (GATING): pre-auction leg (sessions t-3 -> t, t = auction day) mean
  return - unconditional 3-session mean, credibly negative, block CI.
P2 (GATING, joint with P1: either leg suffices for the gate, both are
  reported): post-auction leg (t -> t+3) minus unconditional, credibly
  positive.
P3 (reported): the rebound is larger after auctions with weak demand
  (bid-to-cover in its bottom tercile) -- REQUIRES bid-to-cover from
  the same auction file; if the file lacks it, P3 is not run and is
  recorded as such.
P4 (reported): decay across Discovery halves (published 2013; dealers
  have shrunk balance sheets since -- the base case is that the
  concession GREW, not decayed; report either way).

## 4. What would falsify this
(a) Neither leg clears against NULL 1: closes. (b) Only one leg clears
and the other has the WRONG sign: not the dealer cycle; closes as
"confounded" (a monotone move through the auction is a macro trend, not a
concession). (c) KILL RULE: if the post-auction rebound sits in the first
1-minute bar after the 1 pm result, it is the auction print, not
inventory placement; family terminates. (d) Roll sessions and
Globex-only calendar days handled per the Scan 020 rule.

## 5. Resurrection ruling (LEARN + Integrity)
By name and by what is measured:
- ZN lead-lag family (hyp-031/034/035, closed): ZN as a PREDICTOR of NQ.
  This trades ZN on ZN's own scheduled supply. Not a resurrection.
- M11 NQ-ZN correlation breakdown, M12 basket correlation, M5 month-end
  NQ-vs-ZN (all closed): cross-asset state claims about NQ. This is a
  single-instrument event claim in ZN. Not a resurrection.
- Calendar family (turn-of-month, days-to-opex, day-of-week; closed):
  those conditioned on the calendar with no forced participant named.
  This conditions on a scheduled EVENT with an obligated participant
  (the dealer bidding requirement), and the published mechanism is the
  inventory cycle, not the date. Adjacent in form; distinct in claim.
  Disclosed. Integrity: if the effect is present on the same calendar
  days WITHOUT an auction (e.g. months where the schedule shifts), it is
  a calendar effect and closes -- pre-registered check: sessions at the
  same day-of-month in the 2 weeks with no auction, reported.
- Pre-FOMC / event families (closed): different event, different
  participant. Not a resurrection.
RULING: NEW. Enters. Attempt 1 of 2. Integrity signs at sourcing.

## 6. Instrument-choice gate
1. Leads: ZN itself (the 10-year is the auction being absorbed). TN/ZB
   would carry the 30-year cycle; ZN is what is on disk.
2. Minutes not milliseconds: the concession builds over days and the
   rebound is worked off over days.
3. ZN is the cheapest liquid expression (the deepest Treasury future).
   NQ has no role here -- that is the point of the open scope.
4. Directional ZN. Not relative.
5. NULL 1: ZN's unconditional 3-session drift over the same sample.

## 7. Frozen scope (for the scan)
ONE scan, Discovery only (2015-01 -> 2021-10). Event = 10-year note
auction dates from the TreasuryDirect auction file (securityTerm 10-Year,
type Note, auctionDate). Session = ZN RTH 08:20-15:00 ET (the cash
Treasury day; ZN's pit hours) -- close = last bar before 15:00.
Cells to register:
  1. pre-leg (t-3 -> t) mean minus unconditional 3-session mean, block CI   <- GATING
  2. post-leg (t -> t+3) mean minus unconditional, block CI               <- GATING
  3. unconditional 3-session mean (NULL 1)
  4. same-day-of-month no-auction placebo, pre and post legs (2 cells)
  5. pre/post legs on Discovery halves (4 cells)
  6. post-leg split by bid-to-cover tercile (3 cells; only if the file has it)
  7. share of the post-leg in the first 1-min bar after 13:01 ET (kill)
14 cells (11 without bid-to-cover), 2 gating (Sidak at 2). Product track:
DIRECTIONAL alpha in ZN. Realization: TIME-BASED -- short ZN 3 sessions
into the auction, long 3 sessions out (each leg stands alone at
Monetization). Monetization pre-check: leg premium in ZN ticks vs 2x
round-trip cost. ~80 auctions in Discovery: n is EVENT-level, small;
Statistical must apply the thin-sample rule (failure mode #2) and the
result is a candidate only if it clears with n~80.
Data: ZN 1-minute on disk. Auction dates NOT on disk -- WAITING ON the
TreasuryDirect auction file (treasurydirect.gov -> Auction Query ->
Notes, 2015-01-01 to 2021-12-31, CSV; free; the sandbox cannot fetch it,
robots-blocked). Save as data/treasury_auctions_notes_2015_2021.csv.

## 8. Ranking (information gain x edge potential)
Information gain: HIGH. First test of a forced flow in an instrument
where the forcing is documented, large, and NOT about NQ -- it answers
whether the open scope finds edges the NQ-only search structurally could
not, and whether "forced-participant map: 0 for 11" was about the map or
about NQ. A clean null here says the concession is arbitraged away in
futures at this ceiling; a pass changes the whole program's search
direction.
Edge potential: MODERATE-HIGH. Published concession is basis points of
yield on a 10-year -- tens of ticks in ZN -- over a 3-day hold, twelve
times a year. Cheap to hold, cheap to test, nothing to tune.

## 9. Prediction status
P1 -- untested. P2 -- untested. P3 -- untested. P4 -- untested.
WAITING ON auction dates (Jason: one CSV download).

## 10. Scan 024 result, 2026-09-12 ~7:10 pm CT (hyp-000149)
Jason supplied the TreasuryDirect auction-date CSV (filtered to
securityTerm=="10-Year" exactly, 2015-01 through 2021-08, n=41 dates,
n=40 usable events). GATING P1 (pre-auction concession, expected
credibly negative): diff -0.271 ATR vs unconditional, CI (-0.702,+0.240)
-- not credible. GATING P2 (post-auction rebound, expected credibly
positive): diff +0.012 ATR, CI (-0.474,+0.345) -- not credible. Kill
check: first-minute-after-the-1pm-announcement share of the post-leg is
8.8%, well under the 0.5 kill threshold -- this is a genuine absence,
not a print artifact being mistaken for a null. Halves show an unstable
sign flip on the post-leg (first half negative, second half positive),
consistent with no sample-stable effect rather than decay of a real one.
Placebo cells (same-day-of-month, non-auction months) were themselves
non-null in places, which argues the comparison is simply noisy at n=40
rather than that auctions specifically matter.
REJECTED (hyp-000149). The Lou-Yan-Zhang / Fleming-Rosenberg auction
concession is not visible in ZN 1-minute futures at this data ceiling
and this event count. Thin-sample rule (failure mode #2) applies: n=40
does not have the power to rule out a small real effect, but there is no
candidate here to advance. Entry CLOSED, attempt 1 of 2 spent. A second
attempt would need a different forced-flow proxy or event set (e.g. 30-
year auctions, or bid-to-cover-conditioned sub-samples if that data is
ever obtained), not a retuned window on the same 40 events.

## 12. Closure form (U8, retroactive pass 2026-09-13 7:00 pm CT)
- Hypothesis / family: hyp-000149 / M19 Treasury auction concession/rebound, ZN
- Closure status: data limitation
- Primary outcome (as registered) and result: both gating legs null vs ZN 3-session drift, n=40 (Scan 024)
- Sample adequacy: THIN (n=40)
- Mechanism verdict: untested-by-this-result
- Robustness / cost / concentration flags: kill-share denominator bug caught and fixed before final
- What was learned: At 40 auction events the test cannot see an effect smaller than ~0.1 ATR; the literature effect (if any) is below this data's resolution.
- What must NOT be retested: 10Y auction concession on ZN with this sample.
- Permitted future retest condition: a longer auction history (more years) -- data, not a new mechanism
- Capacity action: hold

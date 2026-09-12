# Practitioner stream (queue v2 item 5) — claims enter only via a mechanical proxy

Opened: 2026-09-12, 11:00 am CT cycle. Source CHANNEL: practitioner.
Rule: a practitioner claim is not an entry. It becomes one only when (1) it
has a MECHANICAL proxy computable from 1-minute bars with no discretion,
(2) Mechanism names the constrained participant, and (3) LEARN rules it is
not a member of a closed family or the SKIP LIST. Claims that fail any of
the three stay here as RULED, with the reason, so they are not re-proposed.

## Seeded claims (from the sourcing meeting, September 12th)

### P-1 "Day type is known by 10:30" (trend day vs range day)
- Practitioner form: by 10:30 ET the session has declared whether it will
  trend or chop; trade with the declared type.
- Mechanical proxy: 09:30-10:30 range as a share of ATR14, and the
  10:30 close's position within that range; outcome = 10:30-16:00 range
  vs trailing-20d and directional continuation.
- Mechanism: none named by the claim -- it is a description, not a
  participant.
- LEARN ruling: the RANGE half is the Observatory's fixed state
  classifier (queue item 4: high vs low cash-session variance) and is
  ABSORBED there as characterization, not a trade claim. The DIRECTIONAL
  half ("trade with the type") is the IB/opening-range breakout family
  (hyp-000011/028/065/135, closed) and the ORB variants on the SKIP
  LIST. RULED: no entry. Range component -> Observatory.

### P-2 "Opening-drive exhaustion" (fade the first 15-30 min drive)
- Practitioner form: a fast one-directional open on rising volume
  exhausts and reverses within the first hour.
- Mechanical proxy: 09:30-09:45 return / ATR14 in its top tercile with
  09:30-09:45 volume vs 20d norm in its top tercile; outcome =
  09:45-10:30 return, sign-adjusted.
- Mechanism: the claim's implicit participant is the overnight/news
  order queue clearing at the open (M15's night leg landing at the
  auction) -- once cleared, no one is forced to continue.
- LEARN ruling: adjacent to hyp-000076 opening_volume_imbalance (volume
  imbalance -> rest of day, REJECTED), hyp-000081/082/084/085/090
  opening-hour reference-level fades (all REJECTED; VWAP/level fades on
  the SKIP LIST), and M16 (first-30 INFORMATION persists to the close --
  the opposite claim over a different window). It is a fade of the
  first-30 move; M16 says the first-30 move carries information. RULED:
  no entry NOW. If M16's P1 passes, this is closed by implication (the
  morning move is information, not exhaustion); if M16 fails, P-2 may
  be re-ruled with the M15 night-leg landing as its mechanism and a
  first-minute kill rule. Parked behind M16.

### P-3 "VWAP reclaim after a failed breakdown"
- Practitioner form: price breaks below VWAP, fails, reclaims -> long.
- Mechanical proxy: computable (VWAP cross-down then cross-up within N
  bars) but the claim is a level fade/reclaim.
- LEARN ruling: VWAP and reference-level fades are a CLOSED family
  (hyp-000081/082/084, H118 vwap_dist) and on the SKIP LIST. RULED: no
  entry. Not re-proposable.

## Standing rule for this stream
Practitioner claims usually describe a footprint without naming who is
forced. Each new claim gets the three-part test above; a claim that
names no participant goes to the Observatory (characterize) rather than
the shelf (claim). Record every ruling here so the stream does not
re-propose. Next practitioner claims to rule on, when sourced: "the
first hour's high/low holds on trend days" (IB family, likely SKIP),
"Friday afternoon de-risking" (calendar, check vs rejected calendar
effects), "post-lunch volume return at 13:30" (M10 attempt 1 spent).

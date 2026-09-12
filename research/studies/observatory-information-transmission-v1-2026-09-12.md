# Observatory — information-transmission map, v1 (NQ/ZN/6E/CL, 15-min RTH)

Written: September 12th, 3:xx pm CT (scheduled cycle, queue v2 item 4).
Characterization only, per the Observatory program's own rule: this
produces map-ready observations, not a trade claim and not a new Idea
Inventory entry.

## Scope (v1, deliberately narrow)
Pairwise return cross-correlation between NQ and each of ZN, 6E, CL at
15-minute bars, RTH session (09:30-16:00 ET) only, Discovery slice,
lags -4 to +4 bars (+/- 60 minutes). Script:
`src/observatory_information_transmission_v1.py`. The full program spec
(5/15/30/60-minute multi-resolution, shock -> first-responder -> lag ->
decay -> reversal, plus the fixed interpretable state classifier) is NOT
built here — this is one clean slice of it, done first, rather than a
half-built version of the whole thing.

## Result

| Pair | Contemporaneous corr (lag 0) | Largest |lag| ≠ 0 corr | n |
|---|---|---|---|
| NQ vs ZN | **-0.317** | 0.028 (lag -3) | ~42,000 |
| NQ vs 6E | -0.011 | 0.017 (lag +2) | ~33,500 |
| NQ vs CL | **+0.159** | -0.020 (lag -1) | ~43,600 |

Full lag table (lags -4..+4) on disk:
`data/observatory_info_transmission_v1_results.json`.

## Reading

- NQ-ZN and NQ-CL both show real, expected contemporaneous relationships
  (equities-vs-duration negative, equities-vs-oil positive) — consistent
  with known cross-asset structure, not a surprise.
- NQ-6E shows essentially no contemporaneous relationship at this
  resolution (-0.011).
- **The finding that matters for the search program**: in all three
  pairs, every non-zero lag's correlation is an order of magnitude
  smaller than the contemporaneous one (max 0.028 vs. -0.317 for ZN;
  0.017 vs. -0.011 for 6E; -0.020 vs. +0.159 for CL). At 15-minute
  resolution in this basket, information moves between these
  instruments essentially simultaneously — there is no detectable
  lead-lag structure to exploit. This is consistent with, not
  independent of, the two already-closed cross-asset nulls (M11
  NQ-ZN correlation-breakdown near-miss; M12 basket correlation
  convergence clean null) — three separate lenses on this basket now
  agree that the exploitable structure, if any, is not in simple
  correlation or lead-lag at this resolution.

## What this does NOT settle
- Only one resolution (15-min) and only RTH hours are checked. The
  overnight session (where M9's rebalance work and the M15/M16 entries
  suggest more happens) is untested here. 5/30/60-minute resolutions
  are untested. A shock-conditioned version (does a LARGE move change
  the lead-lag picture, even if the unconditional one is flat) is
  untested — unconditional correlation can mask conditional structure.
- This is not a ruling against M11/M12-style claims; those already
  closed on their own evidence. This is corroborating context for
  KNOWLEDGE.md's structural conclusion (four independent reads agree:
  scheduled/public cross-asset flows are heavily competed at this data
  ceiling), not a new independent test of any hypothesis.

## Next under this item
Extend to the overnight session and to 5-min/60-min resolution; add a
shock-conditioned view (top-decile move in one instrument -> reaction in
the others, by lag) before calling the "no lead-lag" read final. Then
the fixed state classifier (broad-equity agreement / NQ-only residual /
rate-confirmed / rate-conflicted / vol-state) per the original spec.

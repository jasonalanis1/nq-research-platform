# OBS-FINDING-001: Opening-Hour Reference-Level Touch Cluster (retroactive)

Written retroactively per the protocol addendum
(research/studies/observatory-finding-protocol-addendum.md), after H81
and H82 both failed. This does not reopen the behavior line -- it
documents, for the record, what the finding actually was, independent
of the two failed trade designs.

## Definition

Event: first touch (09:30-10:30 ET) of prior-day RTH high, overnight
session high, or session VWAP -> associated with BELOW-baseline forward
returns over the following measured horizons. First touch of the
overnight session low -> associated with ABOVE-baseline forward
returns. Source: Observatory v1 scan, 348 combinations, Discovery data.

## Measurement (from the Observatory scan, not from any hypothesis test)

15 of 18 "Promising" cells in the full scan cluster in the "open"
(09:30-10:30) time bucket with this consistent shape. Representative
cells: `vwap normal open` horizon 10, n=658, effect=-2.26;
`overnight_high wide open` horizon 15, n=142, effect=-9.36;
`overnight_low wide open` horizon 3, n=116, effect=+3.04. Effect signs
are consistent across all upper-level cells (negative) and the
lower-level cell (positive) -- i.e., a fade/mean-reversion shape, not
mixed signs.

## Judgment (measurement only, no trade design)

Real-looking, not an obvious scan artifact: the shape is coherent
across three independent upper reference levels (prior-day high,
overnight high, VWAP) rather than isolated to one, and the mirror
(overnight low) points the opposite direction as a fade story would
predict. Sample sizes are not thin (n in the hundreds for most cells).
Plausible mechanism: opening-range levels acting as short-term
liquidity/reference points that get faded once touched, consistent with
ordinary opening-hour mean-reversion around prior reference levels.

Caveat carried forward from Jason's own correction: this is descriptive
evidence from a 348-combination scan, not confirmatory evidence. The
upstream multiple-testing exposure means some fraction of the 18
Promising cells are expected to be noise even if the scan's ranking
method is sound. This finding was not independently re-validated on a
held-out slice before H81/H82 were attempted -- that re-validation
would need its own frozen design if this cluster (or the Observatory's
scan methodology generally) is revisited later.

## Outcome

Two independently designed monetization attempts (H81: generic
buffer-stop/1.35R; H82: excursion-derived fixed-point stop/target) both
failed Step 1+2 on the same underlying event definition. The finding
itself is not falsified by this -- a real conditional-return effect can
exist without any tested trade-execution shape capturing it profitably
net of cost. Status: CLOSED to further monetization attempts on this
specific event definition, per pre-commitment. The finding stands as
documented measurement, available for reference if the Observatory
scan methodology itself is revisited in the future.

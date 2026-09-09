# Observatory v6 Evaluation (value area / POC touches)

Ran 2026-09-09. Frozen spec: research/studies/observatory-v6-design-spec.md.
New volume_profile.py infrastructure built and reused (POC/VAH/VAL from
1-minute-bar volume approximation). 216 combinations scanned, Discovery
data only.

## Result

Label breakdown: 10 Promising, 13 Interesting, 192 Weak, 1 No-meaningful-
difference. Of the 10 Promising, only ONE clears the ATR-normalized cost
floor at adequate sample size (n>=40): `prior_poc | wide | open | 15min`,
n=92, effect=-6.93pts, ci_90=(-12.46, -1.70), atr_norm=0.054.

Checked this candidate's neighboring horizons (same event/regime/bucket,
1/3/5/10/30min) per the project's own coherence standard (the same check
that qualified OBS-FINDING-009 and disqualified nothing before it): the
15min reading is ISOLATED. 1/3/5min are small and POSITIVE
(non-credible), 10min and 30min are negative but non-credible, and none
of the surrounding horizons agree in sign or magnitude with the 15min
spike. This is the single-horizon-artifact pattern the finding protocol
exists to catch (research/studies/observatory-finding-protocol-addendum.md's
"real vs. scan artifact" judgment) -- not a coherent behavior. No
Behavioral Finding is written from it.

All other Promising/Interesting candidates fail the cost-viability
floor (effect too small relative to typical daily range) or the n>=40
sample-size bar.

## Verdict

Value-area/POC touches, as approximated from 1-minute-bar volume, do
not produce a coherent, cost-viable candidate in this scan. The new
volume_profile.py infrastructure itself worked correctly (built and
computed profiles for 1688/2101 Discovery days, ~80% coverage -- some
low-volume or incomplete-session days don't produce a usable profile)
and is available for reuse in future studies; this specific event
family (first-touch of POC/VAH/VAL) is closed for now. A finer-grained
profile (e.g., tick data instead of the 1-minute approximation) might
resolve the 15min-only signal differently, but that would require data
this project doesn't have -- not pursued.

## Status of the broader search

No open lead remains after v6. Three Observatory generations since the
2026-09-09 audit (v4 multi-day levels, v5 overnight-direction, v6
value-area/POC) have now run: v5 produced the project's only-ever
Discovery-slice pass (closed after failing prospective validation);
v4 and v6 both closed clean with the cost-aware/coherence screens
correctly filtering out non-viable or artifact candidates before any
hypothesis spec was written. Recommend pausing new Observatory scan
generations for now rather than continuing to generate new event
families on diminishing returns -- three scans in one day without a
surviving candidate suggests the easily-discoverable single-condition
behaviors in this data are largely exhausted; the more promising
unexplored direction, per the original pilot's own framing, is
comparing multi-condition/combination effects (in the spirit of the
collective-evidence pilots, hyp-000025/027) using the Observatory's
now-more-rigorous protocol, rather than more single-event-type scans.

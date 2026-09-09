# Collective-Evidence v2 Direction-Conditioned Follow-up -- Frozen Spec (exp-124)

Direct follow-up to OBS-FINDING-010's disclosed limitation, run before
any hypothesis spec, per the finding's own required-next-step.

## Method

For each Discovery day where 2+ of the 3 conditions fire (unchanged
from exp-123), assign each fired condition its own implied fade
direction, from each condition's own already-frozen definition (no new
threshold introduced):
- `cond_gap`: implied direction = LONG if the gap was down, SHORT if up.
- `cond_overnight`: implied direction = LONG always (only fires on
  overnight-down + wide regime, per OBS-FINDING-009's own scope).
- `cond_level`: implied direction = SHORT always (only checks upper-
  level touches -- prior-day-high, overnight-high, VWAP -- per
  OBS-FINDING-001's own scope; this scan never checked the lower-level
  mirror).

A day is SAME-DIRECTION if every fired condition (among the 2-3 that
fired) implies the same direction; MIXED otherwise. For SAME-DIRECTION
days, sign the 10-minute forward return by the implied direction (so a
correct LONG call is positive-signed, a correct SHORT call is also
positive-signed if price fell) -- i.e. compute realized "correctness"
in the same units as an R-multiple's sign, not raw points. Compare
SAME-DIRECTION days' signed return against the unconditional (all
days, unsigned-to-baseline-convention) baseline, and separately against
MIXED days, both via bootstrap-diff CI.

## Pre-commitment

No condition or direction-assignment rule is adjusted after seeing
this result. If SAME-DIRECTION does not show a materially stronger
effect than MIXED or than the OBS-FINDING-010 pooled result, this
closes the collective-evidence v2 line without a hypothesis spec --
the ambiguity would mean corroboration DID something real but not in a
way currently usable as a single-direction trading rule.

# Monetization — hyp-000148 (M20, EIA volatility jump, CL)

Written: September 12th, ~6:20 pm CT.

## Natural realization path
NOT a directional trade (the design deliberately gates on magnitude, and
the near-kill disclosure rules out a "trade the post-print drift" claim
without a fresh pre-registration). The only credible realization path is
as a VOLATILITY-CONDITIONING INPUT: on EIA release days, for the
10:30-11:30 ET hour specifically, expected realized range is ~2x the
unconditional hourly baseline. This could feed:
  (a) a stop-width / position-size adjustment for any CL strategy that
      trades through that hour on a release day (widen stops, reduce
      size, or stand aside, exactly the pattern volatility_conditioning.py
      already implements for the two validated day/overnight facts);
  (b) a same-day EVENT overlay added on top of trailing ATR, since
      trailing ATR by construction cannot see that a scheduled release is
      today -- this is the one genuinely new piece of information a
      release date carries that trailing history does not.

## Is there "no credible path"? -- the honest test
There is a narrow one (event-day sizing overlay), but it needs a
strategy that actually trades CL through that window to attach to, and
this project currently has ZERO live or paper CL strategies of any kind
-- the three validated volatility facts are NQ conditioning inputs, not
CL ones. Building a CL-specific conditioning module for a strategy that
does not exist is speculative infrastructure, not monetization of a
finding.

## Verdict
NO CREDIBLE PATH TODAY -- explicitly a valid, successful conclusion per
this project's own standing rule ("no credible path is a valid,
successful conclusion"), not a failure of the finding. Disposition:
KNOWN TRUE (characterization), filed as a volatility fact analogous to
the three already-validated ones, held for future use IF a CL strategy
is ever built, rather than pushed into a blind Integrity Gate check and
a Validation-slice spend for something with no strategy to attach to
yet. This preserves the Validation-slice attempt rather than spending it
on a fact with nowhere to land. Not promoted to GATED; not spending a
Holdout slot; no capital implication of any kind.

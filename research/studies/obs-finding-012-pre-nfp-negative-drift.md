# OBS-FINDING-012: Pre-NFP Overnight Drift Is NEGATIVE, Not Positive

Discovered 2026-09-09, via study_pre_nfp_drift.py (hyp-000112).
Frozen spec: research/studies/pre-nfp-drift-design-spec.md.

## What was tested

Pre-registered hypothesis (per Savor & Wilson 2013 / macro-announcement-
premium literature): overnight return into NFP (jobs report) release
days skews POSITIVE relative to non-NFP days.

## What was found

The opposite, and credibly so. NFP-day overnight return: -9.24pts mean.
Non-NFP-day overnight return: +5.58pts mean. Effect: -14.83pts,
90% bootstrap CI (-26.70, -3.48) -- entirely below zero, credible.
n=74 NFP-day observations, n=1243 complement. ATR-normalized effect
0.116 -- well above the 0.05 cost-viability floor.

This is the ONLY credible directional result this project has found
in ~112 hypotheses tested. It is REJECTED as a hypothesis test (per
protocol: the pre-registered direction was positive, and it came back
negative -- a hypothesis doesn't get to flip its own sign after
seeing the result, that's exactly the direction-ambiguity failure
mode the LEARN taxonomy exists to prevent).

## Why this is NOT the same as "just another null"

Every other rejection this session was either a clean null (CI spans
zero) or a non-credible thin sample. This is neither -- it's a
credible, cost-viable, well-powered (n=74) result. It's rejected
ONLY because the direction was pre-registered wrong, not because the
underlying behavior isn't real. Per the two-layer methodology, this
is exactly what Layer 1 (Observatory) is for: it surfaced real market
behavior even though the specific monetization hypothesis attached to
it (the positive-drift literature prediction) was wrong.

Plausible reasons the sign could differ from the (mostly pre-2015,
mostly S&P-focused) literature: sample period (our Discovery slice is
2015-2021-10-03, largely post-crisis and includes 2020's unusual
regime), NQ/Nasdaq-100 specifically vs. broad-market indices in the
literature, or the overnight-return proxy differing from the
literature's exact 4pm-to-8:25am pre-release window. Not yet
investigated -- flagging as open questions, not conclusions.

## Next step (per protocol -- NOT done yet)

This needs a FRESH, separately pre-registered hypothesis with the
NEGATIVE direction stated up front, run through the standard
Discovery -> Validation pipeline as its own 2-attempt hypothesis --
same treatment OBS-FINDING-011's wrong-direction Observatory result
got before hyp-105/106 confirmed it in Validation. This is NOT a
same-run flip of hyp-000112 (that would be curve-fitting on the result
we just saw) -- it is a new hypothesis, built on Observatory evidence,
same as the methodology has always required.

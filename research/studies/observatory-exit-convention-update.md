# Observatory Hypothesis Convention Update: ATR-Scaled Stops Become Default

Per the monetization diagnostic (research/studies/monetization-diagnostic-round1.md)
and H87's result: the 1-minute-bar buffer stop convention used in
H81-H86 produced risk distances (15-21 points) too tight for the fixed
0.75-point round-trip cost, wiping out real-but-small gross edges. H87
swapped to a `1.0x daily ATR(14)` stop and measurably improved the
cost-to-risk ratio (long leg came within a hair of passing).

**Effective now:** every future Observatory hypothesis defaults to an
ATR(14)-scaled stop (`entry -/+ 1.0 * daily ATR(14)`, target =
`1.35 * risk` as before) instead of the 1-minute-bar buffer, unless a
specific candidate has a stated reason to use something else (e.g. an
excursion-derived design, per the existing H82 precedent, still
requires its own disclosure and freeze-before-result procedure).

Not yet treated as fully validated -- H87 is one data point. The next
hypothesis (H88) tests the SAME convention on a different, previously
untested candidate to check whether the improvement generalizes or was
specific to the gap-fade setup.

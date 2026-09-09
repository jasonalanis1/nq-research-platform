# Full Project Audit Against the Two-Layer Methodology, and New Starting Point

Written 2026-09-09 per Jason's request: review everything the project has
completed against research/studies/two-layer-methodology.md and identify
where research should start from next.

## Ledger inventory (100 logged hypotheses)

- 81 REJECTED, 17 PROMISING (top-level status), 1 FORWARD VALIDATION
  (hyp-000020, superseded by later work), 1 VALIDATION CANDIDATE
  (hyp-000057).
- Of the 17 still-tagged PROMISING, 12 are STALE -- each already has a
  later ledger entry proving it failed its own required test
  (hyp-000003/005/007/008 corrected directly; hyp-000044/050/052/063
  corrected via hyp-000093-096; hyp-000023/025/027/031 corrected via
  hyp-000097-100 in the prior session). None of these 12 need further
  work.
- 4 are genuinely still-live and already VALIDATED as real, persistent
  behaviors (not stale, not yet monetized): hyp-000046/048
  (range-contraction persistence) and hyp-000056/048057 (overnight coil
  -> RTH range compression). Both are volatility/range-persistence
  facts, not directional return signals -- they do not by themselves
  clear the promotion bar, and are already built into
  src/volatility_conditioning.py as risk-sizing inputs rather than
  standalone strategies.
- 1 is an honest, permanent gap: hyp-000051 (5-day tight base ->
  breakout-day reversal), n=9, technically clears the CI test but far
  too thin to trust, never followed up. Not stale -- correctly labeled
  low-confidence at the time -- but never resolved either way.

## Origin mix and what each family has taught the project

- **jason_hypothesis / external_claim / data_discovered (bar patterns,
  candlestick shapes, at daily and 60-min resolution, ~20 hypotheses)**
  -- exhaustively tested, 0 survivors. This family is fully closed.
- **rd_generated (cross-asset standalone signals: VXN, ZN, currency,
  oil, options VRP, ~10 hypotheses)** -- exhaustively tested, 0
  survivors, and (per 2026-09-07 Advisor consult) the free/owned data
  well for this family is exhausted.
- **derivative (post-hoc filters/splits/overlays on existing signals,
  ~35 hypotheses, includes both legacy strategy-first re-mines and the
  collective-evidence pilot)** -- 0 survivors as monetized rules; 2
  successes at the pure-measurement level (range-contraction, coil),
  both already folded into volatility_conditioning.py; 3 separate
  overlay attempts to monetize those 2 findings on OTHER existing
  signals (hyp-000049, hyp-000058, hyp-000059) all failed -- but
  notably, all 3 overlay attempts were tried on already-dead Level
  Sweep Reversal variants, never on the project's actual
  closest-ever near-miss (H87/H89 gap-fade).
- **data_discovered / Observatory (hyp-000081-092, the 3-scan pilot
  round: v1 reference-levels, v2 round-numbers/pivots/session-open, v3
  gaps/volume-spikes)** -- 10 hypotheses across 8 Behavioral Findings,
  0 cleared the bar, but produced the project's single most useful
  diagnostic: most measured behaviors are gross-positive but
  COST-DOMINATED (fixed per-trade cost wipes out a real-but-small gross
  edge given typical risk distances of 15-21 points). ATR-scaled stops
  (adopted after this diagnosis) measurably narrowed the gap and
  produced the project's closest-ever near-miss: H87/H89 gap-down fade,
  long leg, n=128, mean_r=+0.068, ci_90=(-0.015, 0.152) -- narrowly
  missed, not a clean rejection.
- **The 4 legacy "unresolved" leads (hyp-000023/025/027/031)** --
  resolved as of the prior session: all already had a completed,
  non-clearing prospective test on record; all classified ABANDON.

## What this means under the corrected two-layer methodology

The project's actual state, stated plainly: Layer 1 (the Observatory,
plus its pre-Observatory equivalent work) has produced exactly 2 real,
prospectively-validated behavioral findings in its whole history --
both volatility/range-persistence facts, not return-generating signals.
Layer 2 (monetization) has never succeeded on either of them, nor on
any of the ~15 directional candidates tried across every origin family.
The single closest miss (H87/H89) is a directional gap-fade behavior
that has NOT been cross-checked against either of the 2 validated
volatility findings as a conditioning filter -- that specific
combination has never been tried.

Everything else -- every bar pattern, every cross-asset standalone
signal, every legacy strategy-first re-mine -- is exhaustively tested
and closed. There is no more unexploited legacy backlog. Continuing to
generate new legacy-style candidates (new bar patterns, new standalone
instruments) would just be re-running an already-exhausted search
strategy.

## New starting point

Two live threads, both consistent with the methodology (Observatory-
style, behavior-first, no retuning of anything already tested):

1. **Untried, cheap, uses only existing validated facts + existing near-
   miss data.** Screen whether either validated volatility finding
   (range-contraction, hyp-000046/048; overnight coil, hyp-000056/057)
   conditions the economics of the H87/H89 gap-fade near-miss, the same
   overlay-screen technique already built and used twice
   (hyp-000049/058/059) -- just pointed at the one candidate that was
   never tried. This is a Layer 2 monetization question about an
   already-frozen Layer 1 behavior (the gap-fade characterization
   itself doesn't change); a positive screen result would still need
   its own single pre-registered prospective test before being trusted,
   per the existing overlay-screen precedent.
2. **New Observatory scan generation (v4), with the cost-dominance
   lesson built into candidate selection up front.** Rather than
   ranking candidates by raw effect size (which produced the false
   positive H90 disproved), screen new Observatory candidates by
   effect-size-relative-to-typical-realized-range (ATR-normalized)
   before writing any hypothesis spec -- so obviously cost-dominated
   candidates are filtered out before a full monetization cycle is
   spent on them, without re-deriving thresholds from any past result
   (the screening logic itself is new, not a retune of a tested
   hypothesis). New event families not yet scanned: options-expiration
   effects, session-transition behavior (RTH close -> overnight open),
   and multi-day (not intraday) reference-level touches.

hyp-000051 (n=9 tight-base reversal) folds into thread 2 as a candidate
event definition for the v4 scan rather than being resurrected on its
own -- it needs a properly sized sample, which only a fresh scan across
the full Discovery window can give it; testing it again on the same 9
observations would violate no-retuning.

Recommendation: run thread 1 first -- it is nearly free (reuses
existing signals, existing overlay-screen code, existing frozen
findings, no new data needed) and directly tests the one meaningful
combination the project's own history flags as untried. Thread 2 is the
default ongoing generator regardless of thread 1's outcome, per the
methodology's standing instruction that Observatory-style research is
now the default starting point for new work.

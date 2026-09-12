# Midday-lull narrow leg — Director Re-Evaluation & Monetization (extraction)

hyp-000105 / hyp-000106 / hyp-000133 (midday_lull_afternoon_expansion).
Written 2026-09-11 22:00 UTC cycle to give the pipeline sweep a discrete,
filename-detectable record of work that already happened 2026-09-10 in
research/sessions/2026-09-10-0815.md (Statistical-stage pass session) --
no new analysis here, extraction + a pointer only, so
src/pipeline_sweep.py stops re-flagging "Director Re-Evaluation" as owed
on a candidate that already cleared it.

## Why this doc exists

src/pipeline_sweep.py's next_owed() hardcoded "Director Re-Evaluation" as
the owed stage for every VALIDATION CANDIDATE row, never checking whether
a Director Re-Eval/Monetization doc already existed (unlike the PROMISING
branch, which does check hits[...] at every stage). Found and fixed in
the same 2026-09-11 22:00 UTC cycle that wrote this doc -- see
src/pipeline_sweep.py's next_owed() and tests/test_pipeline_sweep.py.

## Director Re-Evaluation — RAN 2026-09-10 (research/sessions/2026-09-10-0815.md)

Scope: midday-lull narrow leg only (the one Validation leg, of five
checked across three candidates that session, to survive the project-wide
multiplicity correction — see research/studies/statistical-stage-pass-2026-09-10.md).

Finding: this is a volatility/range CHARACTERIZATION, not a directional
return-generating rule. Portfolio's returns-based activation bar does not
apply to it directly. What has been earned: the cleanest, most-replicated,
most mechanism-supported range-persistence finding in the project's
history, already partially operationalized
(src/volatility_conditioning.py's get_afternoon_conditioning(), built
2026-09-09 from hyp-000106). Further Statistical-stage spend on this same
characterization has rapidly diminishing value. The honest next step is
translating the characterization into a costed, returns-based test — a
Monetization question.

Confidence: MEDIUM-HIGH. Recommendation: CONTINUE to Monetization.

## Monetization — RAN 2026-09-10 (same session)

Finding: there IS a credible path, but a CONDITIONING path (wired into an
existing setup's stop/target or position sizing), not a standalone-signal
path. No costed test of that conditioning existed as of 2026-09-10. Two
honest paths identified:
  (a) design and pre-register a costed conditioning-overlay study (an
      existing setup + get_afternoon_conditioning()-style sizing vs. the
      same setup unconditioned) — in automated scope, no spend, no
      Holdout.
  (b) request a Holdout Gen2 slot to confirm the narrow-midday
      characterization itself on genuinely fresh data — BLOCKED, needs
      Jason's sign-off per standing rule (Holdout slot spend is never
      automated).

Confidence: MEDIUM. Recommendation: CONTINUE — queue path (a) as
next-session work; flag path (b) for Jason rather than act on it.

### Path (a) — attempted and CLOSED 2026-09-10, ~12:22-12:40 UTC

research/sessions/2026-09-10-1222.md,
research/studies/ib-breakout-afternoon-conditioned-stop-overlay-spec.md.
IB Breakout (hyp-000011) stop re-anchored at 14:00 ET using
get_afternoon_conditioning()'s confirmed multiplier. RESULT: only 82/1709
signals (4.8%) ever reached 14:00 still open — IB Breakout resolves too
fast for this test to have real power. Affected-only diff -0.0004R, CI
[-0.0571, 0.0456], not credible; null holds under 2x cost stress. CLOSED
per the pre-registered rule (hyp-000135 REJECTED, diagnostic, not a
promotion event on hyp-000105/106 themselves). Structural LEARN lesson
(distinct from "no edge to condition"): this conditioning fact needs a
setup with materially longer time-in-trade to get a fair test — IB
Breakout resolves too fast. No other longer-hold setup has been paired
with get_afternoon_conditioning() since. Path (a) is not exhausted in
general, only on this one pairing.

## What remains owed (unchanged by this doc — see NEXT_UP.md)

Per the PIPELINE SWEEP RULE's GATED tier: prepare the frozen Holdout spec
and run the Integrity Gate checkpoint (adversarial pre-registration
review) before this can be listed as ready for Jason to spend a Holdout
slot on. Deliberately NOT attempted in the same cycle that wrote this
extraction doc — a frozen Holdout-spec pre-registration is consequential
(Holdout Gen2 has a hard 5-slot budget, 1 already used) and deserves a
dedicated pass, not a rushed one appended to a ledger-hygiene cycle. Left
as the next owed step; see NEXT_UP.md queue item 0.

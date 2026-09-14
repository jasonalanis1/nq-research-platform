# Statistical stage — hyp-000162 (M30: opening-range width → midday range, NQ)

Run September 14th, 9:00 am CT scheduled cycle. Construction reproduced from
Scan 036 exactly — `opening_range_vs_atr` from the frozen state frame, Discovery
terciles (LOW ≤ 0.2767, HIGH ≥ 0.4063), midday 11:30–13:30 ET, outcome = midday
range ÷ trailing-20d mean midday range (shifted 1). Block bootstrap block=10,
N=3000, seed 20260913, 90% CI. Nothing was redefined at this stage: the question
is whether the registered result holds, not whether a better version of it would.

**Full sample:** n = 555 HIGH / 556 LOW, mean difference **+0.5193**,
ci_90 (+0.4475, +0.5975).

| Question | Result | Pass |
|---|---|---|
| Q1 stability (chronological halves) | 1st +0.4676 [+0.3851, +0.5696] · 2nd +0.5794 [+0.4707, +0.6979] | PASS |
| Q2 regime (trailing-20d RTH range median) | low-vol +0.4560 [+0.3600, +0.5337] · high-vol +0.6082 [+0.5047, +0.7308] | PASS |
| Q3 multiplicity (Šidák, N_discovery = 467, BINDING) | raw [+0.4475, +0.5975] → adjusted **[+0.3511, +0.6875]** | PASS |
| Q4 selection sensitivity (reported) | frozen 11:30–13:30 +0.5193 · 11:00–13:00 +0.4977 · 12:00–14:00 +0.5141 · 11:30–14:00 +0.5357 — all credible | reported |
| Power at one-shot Validation | n=700 sessions (~233/arm), power **1.000** at the Discovery effect, **0.815** at half of it | — |

**Verdict: PASS**

## What this stage did and did not settle

Both gating questions and the binding multiplicity correction pass, and they
pass with room: the Šidák-adjusted interval at the live project-wide Discovery
trial count (467) still sits entirely above zero. Q4 shows the result is not an
artefact of the midday window boundary — every alternative window tested lands
within ±0.04 of the frozen one. Validation is well powered: 81.5% even if the
true effect is half what Discovery showed, so a Validation null would be
informative rather than ambiguous.

**Q2 is the closest this stage legitimately gets to the open question, and it
does not close it.** The effect is credible in both volatility regimes, which
rules out "this only happens in turbulent weeks." But it is meaningfully
*larger* in the high-volatility half (+0.61 vs +0.46), which is consistent with
the finding the mechanical suite raised on this candidate.

## The U6 placebo red is carried forward UNCHANGED

`integrity_checks.py` flagged this candidate the day it was drawn: the
shifted-signal (t+1) placebo reproduces **74%** of the effect — *yesterday's*
opening range predicts today's midday range nearly as well as today's does.

That is not resolved here, deliberately. Separating "wide opening range" from
"wide multi-day volatility regime" requires a **new conditioning variable**
(prior-day opening range) and therefore a **new registered trial**. Running it
inside this stage would be scope creep past a frozen spec, and deciding to spend
a trial on it is the Director's call at the Validation gate, with the blind Gate
weighing the red. This stage's job was to test the registered claim; it did, and
the claim held.

Recorded for whoever picks it up: P3 in the original scan residualized on
prior-day **RANGE** (`range_vs_atr`) and retained 83.6%. Prior-day **OPENING**
range is a different variable and was never in the registered scope. The two
findings are not in conflict — they are about different controls.

## Owed next

The **blind Integrity Gate**, which must adjudicate the placebo red. It should
be handed the specific question — *is this a distinct fact, or a readable marker
of a multi-day volatility regime?* — rather than a general "is this real." A
general framing invites a general answer, and the general answer is already
known: yes, the association is real, stable, and survives correction. What is
not known is what it is an association *with*.

# Mechanism documents

## Why this folder exists

Every other stage of this pipeline produces a number, and numbers get logged
automatically. Mechanism produces an ARGUMENT, and nothing in the tooling
ever asked for one — so for 134 ledger entries, none was ever written down.

Worse: what has been filed under "Mechanism" was mostly a second statistical
pass. Regime splits, trend splits, volatility splits. Those are robustness
checks — they ask "is the number stable?", not "why does the number exist?".
Both are needed. Only one was happening.

## The gate rule (binding from 2026-09-10)

No candidate advances from Statistical to Monetization without a mechanism
document in this folder. A candidate with no mechanism is not promoted; it is
returned to Mechanism or closed. The Integrity Gate checks for this file's
existence and quality as part of its standing brief.

## What a mechanism document must contain

1. THE CLAIM. Why does this effect exist? One paragraph, in market terms —
   who is doing what, and why. Not "prices mean-revert." Who is selling, why
   are they selling, and why does someone else profit from taking the trade.

2. WHO IS ON THE OTHER SIDE. If we make money, someone loses it or is paying
   for a service. Name them. Forced sellers, hedgers paying for insurance,
   impatient traders paying for immediacy, leveraged accounts being
   liquidated. If you cannot name a counterparty and their reason, say so
   explicitly — that is a red flag, not a footnote.

3. TESTABLE PREDICTIONS. At least two things that must ALSO be true if the
   mechanism is right, which are NOT the original effect. A prediction that
   only restates the finding is not a prediction.

4. WHAT WOULD FALSIFY IT. Stated before checking.

5. PRE-REGISTERED OR POST-HOC. State plainly whether the mechanism was
   written before or after the results were seen. A post-hoc mechanism is a
   HYPOTHESIS, not evidence, and carries no weight until its predictions are
   confirmed on data it did not come from.

6. PREDICTION STATUS. Each prediction marked untested / confirmed / refuted,
   with the evidence.

## The honest warning

A mechanism story is the easiest thing in this project to fake. Humans are
extremely good at producing a plausible reason for any pattern after seeing
it. That is exactly why requirement 3 exists: the story earns nothing by
sounding good, only by correctly predicting something it was not built to
explain.

# Monetization Diagnostic — Why Do Measured Behaviors Keep Failing as Trades?

Frozen diagnostic spec (Path B), run alongside Observatory v3 (Path A)
per Jason's instruction to pursue both. Purely diagnostic -- reruns
existing frozen hypotheses' signal detection unchanged, adds a
gross-vs-net decomposition (same technique used earlier in this project
for the 7 pre-move-behavior nulls) to distinguish two different
failure modes:

- **Cost-dominated**: gross edge (before the 0.75-point round-trip
  cost) is close to zero or positive but the fixed cost eats it --
  same diagnosis as several historical nulls.
- **Genuinely negative gross edge**: the measured Observatory effect
  doesn't survive being turned into entry/stop/target at all, even
  before cost -- would suggest the trade-mechanics conversion itself
  (fixed touch-bar-close entry, buffer-based stop) is destroying the
  edge, e.g. by entering too late relative to where the measured effect
  was, or by using a stop distance that gets hit before the measured
  favorable move develops.

Reruns the two largest-n candidates from the pilot: H81 short leg
(n=1138, opening-hour reference-level fade) and H86 combined (n=559,
round-number continuation) -- unchanged detection/entry/stop/target
logic, output extended to report gross alongside net. No retuning; this
does not reopen either hypothesis, it explains them.

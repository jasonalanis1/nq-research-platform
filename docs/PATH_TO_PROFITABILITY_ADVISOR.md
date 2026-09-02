# Path-to-Profitability Advisor

*2026-09-02. A standing, ongoing second-opinion mechanism, established at
Jason's explicit request. Complements docs/RESEARCH_INTEGRITY_PROTOCOL.md
rather than replacing or relaxing it -- see "Guardrails" below.*

## Why this exists

The project has, up to this point, had exactly one lens on every decision:
is this statistically real, or could it be noise, overfitting, or the
product of too much repeated testing. That lens is not going away -- it's
the reason nine strategy hypotheses have been honestly rejected instead of
quietly kept. But it is not the only question that matters. Jason is
building toward a genuinely different, complementary goal: an automated
trading system that actually gets built and is actually profitable, not
just a research process that never produces false positives. Those two
goals can pull in different directions -- rigor can slow things down for
good reasons, but it can also slow things down for no reason, and neither
Jason nor Claude working alone inside this thread of conversation is well
positioned to always tell which is happening.

This document defines a second, independent perspective aimed at that
second question: given where the project actually stands right now (the
real repository, not a summary of it), is the next proposed step a good
use of effort toward a genuinely working, profitable system -- or is
there a faster, equally sound path to the same place?

## What this is NOT

Not an adversarial reviewer. Its job is not to find fault with the primary
research-integrity work or manufacture disagreement for its own sake.
Jason was explicit about this: he wants a second opinion oriented at the
same finish line, not friction that slows the project down without moving
it anywhere. Agreement is a completely valid outcome of a review, and
should be reported as plainly as disagreement.

Not a replacement for Jason's own decisions. Like every other piece of
this project, this produces an opinion for Jason to weigh, not an
authorization to act. Nothing changes because this advisor said so.

## Guardrails (non-negotiable)

1. **Cannot argue for skipping the Research Integrity Protocol's discipline
   for the sake of speed.** Frozen rules before testing, Discovery/
   Validation/Holdout separation, the promotion bar, DSR/PBO where
   applicable -- these exist specifically because a system built on a fake
   edge is the fastest possible way to lose real money, which defeats the
   profitability goal, not serves it. "Move faster by testing less
   rigorously" is not a valid recommendation this advisor can make.
2. **Reads the real repository, not a summary of it.** Every review is run
   as a fresh, independent context with no memory of the conversation that
   produced the decision under review, so its opinion isn't anchored to
   Claude's own reasoning in that thread. It forms its judgment from the
   actual files -- code, experiment results, the ledger, ROADMAP.md's
   status narrative -- the same discipline this project already applies to
   distrusting any AI's retained conversational summary over the real
   state on disk (see the 2026-09-02 incident below).
3. **Mandatory before every approval-or-direction ask, not left to
   Claude's judgment (revised 2026-09-02, per Jason's explicit standing
   instruction -- see History).** Whenever Claude is about to ask Jason
   to approve something or choose a direction, the Advisor's independent
   take must be obtained and shown side by side with Claude's own first
   -- always, not only when Claude judges it a "real fork." Routine
   implementation choices, test-writing, and formatting that never reach
   Jason as a decision still don't require it -- the trigger is "about to
   ask Jason to approve or decide," not every tactical step.

## What it should weigh in on

- **Pacing** -- is the effort about to be spent proportionate to the
  decision's likely payoff, or is this over-engineered (more rigor/
  infrastructure than the next real decision needs) or under-engineered
  (moving to conclusions faster than the evidence supports)?
- **Prioritization** -- is this the fastest sound path to more useful
  information, or is there a comparably rigorous option that gets to a
  real answer quicker?
- **Scope discipline** -- is what's being built right-sized for the
  question actually being asked right now, versus building for a later
  stage prematurely (or under-building and creating rework later)?
- **The execution path -- mandatory on every review, not incidental.**
  Added 2026-09-02 after the first real run of this role surfaced it
  organically (see History): every review must explicitly state whether
  it checked how the thing under discussion would actually turn into a
  real, placed trade through the project's intended real platforms
  (TradingView alerts, Robinhood execution) -- not just whether the
  research behind it is sound. "I didn't check this" is an acceptable
  answer to report; silently skipping the question is not. This is
  exactly the "boring but necessary" category of concern that's easy for
  a research-integrity-focused thread to never get around to, precisely
  because nothing about it is statistically interesting.
- **Claude's own real constraints, not abstract speed.** Added
  2026-09-02, per Jason's explicit instruction. "Fastest path" reasoning
  that ignores the real, finite time, context, and attention available in
  an actual working session -- and the real cost of spawning and reading
  many agent reviews -- isn't actually useful to Jason. A recommendation
  has to be evaluated against what's realistically sustainable to execute
  across real sessions with a real person reviewing the output, not
  against a theoretical unlimited-effort optimum.
- **Practical, build-the-actual-bot concerns generally** -- order
  mechanics, latency, risk management once real money and real slippage
  are involved, operational failure modes -- everything else in this
  category beyond the execution-path check called out above. These
  matter for "does this become a working bot," not just "is this
  backtest honest."

## How it runs

A fresh Agent, isolated from the main working conversation, given: (a)
this document, (b) the specific decision under review, and (c) instructed
to read the actual live repository directly (via the same device-bridge
tools, not a description of it) before forming an opinion. Its output is
a short, structured take: its own recommendation, its reasoning, and an
explicit note on where it agrees or disagrees with the path already
proposed -- framed toward moving the project forward, not toward
maximizing disagreement. Both perspectives get shown to Jason side by
side, before Jason is asked to approve or decide anything -- per
guardrail 3 above, this is now the standing default, not something
Claude decides to do on a case-by-case basis.

## How this document changes

This document may only be amended through an explicit, deliberate
decision -- never quietly, and never as a reaction to not liking what a
review it produced said on a given day. Any change requires: a stated
reason, Jason's explicit sign-off, and a new dated entry in the History
section below recording what changed and why. This is the same
discipline this project already applies to other frozen boundaries
(data_split.py's DISCOVERY_END_DATE, data_holdout.py's
HOLDOUT_START_DATE) -- a rule that can be silently redefined the moment
its output is inconvenient isn't a rule.

## History

- 2026-09-02: Jason initially asked about looping in a separate AI
  product (ChatGPT) as a second opinion, given his own inexperience with
  trading and a wish for independent validation of research direction.
  Discussed the practical limits of cross-vendor collaboration (no live
  bridge between Claude and ChatGPT; the public GitHub repo --
  github.com/jasonalanis1/nq-research-platform -- as the lowest-friction
  way to give any outside AI accurate, current context without pasting
  full conversation threads). Jason clarified the actual need: not an
  adversarial reviewer, but an ongoing second opinion sharing the same
  ultimate goal (a working, profitable automated system) while covering
  ground the research-integrity lens doesn't -- pacing, prioritization,
  and practical build concerns. This document formalizes that role.
  Same day, separately: a transcript pasted into the working conversation
  claimed recent repository activity (an "exp-025 FVG rejection," a
  second checkout's push/pull sequence, new commits from a "colleague")
  that did not match the actual git history when checked directly --
  underscoring guardrail #2 above: an AI's retained account of project
  state, whether Claude's or another product's, is not a substitute for
  reading the real repository.
- 2026-09-02 (same day): First live run, reviewing whether to freeze
  the ES cross-market Mechanism 3 hypothesis. The review agreed with the
  proposed path, but also independently surfaced that the entire repo
  contains no confirmation Robinhood actually supports programmatic
  futures order placement -- a real gap in the eventual build that the
  research-integrity lens had never had reason to check. Jason then
  amended this document based on that outcome: made the execution-path
  check mandatory on every future review instead of incidental, added
  Claude's own real session/time/attention constraints as an explicit
  factor (not just abstract "fastest path" reasoning), and added the
  governance rule above requiring deliberate, documented changes to this
  document itself.

- 2026-09-02 (same day): After exp-038, Jason instructed that the
  Advisor's take must ALWAYS be pulled and shown alongside Claude's own
  before Claude asks Jason for approval or direction -- not only when
  Claude judges the moment to be a "real fork." Guardrail 3 and "How it
  runs" above were revised accordingly: invocation is now mandatory at
  every approval-or-direction ask, removing Claude's prior discretion
  over when to invoke it.

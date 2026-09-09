# Mechanism-Candidate Research Agent -- Design Note

Written 2026-09-09, in direct response to Jason's request to build "an
agent that does this" (test more mechanism-grounded ideas in parallel).

## What actually needs to be parallel, and what must stay serial

Two different jobs got conflated in "more parallel compute," and they
have opposite constraints:

1. **Idea generation/vetting** (find candidate mechanisms, check
   whether they're documented, check data cost/availability, do a
   first-pass survivability check against our 0.75pt cost / 15-25pt
   risk distance). This has NO dependency on this project's git repo,
   ledger, or holdout boundary. It's pure research. This CAN run in
   parallel -- multiple candidates vetted simultaneously.

2. **Frozen-spec execution** (write the spec, implement the scan,
   run it against Discovery, log to the ledger, commit). This MUST
   stay serial. Reasons: (a) the ledger (hypotheses.jsonl) is a
   single append-only file -- concurrent writers risk corrupting or
   racing it; (b) the holdout boundary and frozen-spec-before-
   implementation rule exist specifically to prevent quietly running
   many variations and keeping the one that looks good -- parallelizing
   this step is the exact failure mode the protocol exists to prevent,
   not a throughput win; (c) it runs against Jason's actual git repo
   on his Mac via the device bridge, which is a single shared
   filesystem and branch -- concurrent agents committing there is a
   correctness risk, not just a technical inconvenience.

So the design below parallelizes step 1 and deliberately does NOT
parallelize step 2.

## Design: Mechanism Research Agent (step 1)

A repeatable Agent-tool invocation (general-purpose subagent, no
special tools needed -- it doesn't touch the repo) with a fixed prompt
template:

- Input: a market/mechanism area to investigate (e.g. "index
  reconstitution effects," "auction microstructure," "options
  expiration flows").
- Task: find real, documented, citable market microstructure
  phenomena in equity index futures (NQ specifically where possible,
  else ES/SPX as a reasonable proxy) in that area. Explicitly told
  what this project has ALREADY tested null (pulled from the ledger's
  REJECTED entries + LEARN taxonomy) so it doesn't re-propose dead
  ends.
- Output per candidate: name/mechanism, citation, data requirement
  and cost/availability, and an honest survivability assessment
  against our actual costs.
- Multiple areas can be dispatched as concurrent Agent-tool calls in
  one message -- this is the actual parallelism, and it's cheap
  because none of these calls touch the repo.

This already exists in usable form -- it's exactly what I ran once
today (agentId aa5e306a80b357167) to produce the 6-candidate list.
"Building the agent" mostly meant formalizing that into a repeatable
prompt template rather than a one-off, and documenting the boundary
above so it's never mistakenly used to parallelize step 2. That's
this file.

## Design: execution stays with me, one candidate at a time

For each vetted candidate that survives a first pass (real mechanism,
viable data cost, plausible survivability): I write the frozen spec,
implement the scan against the Discovery slice on Jason's actual repo,
run it once, log the result to the ledger (win or null), and commit.
One at a time, in the priority order the staff meeting sets. This is
unchanged from how every Observatory version has worked so far --
the new part is that candidates now arrive pre-vetted in parallel
batches from the Research Agent instead of one at a time from my own
guesses.

## Net effect on throughput

This does NOT make hypothesis testing itself faster (that was never
the bottleneck -- see LEARN retrospective, 2026-09-09). It makes
CANDIDATE SOURCING faster and higher-quality: instead of one guess at
a time, several externally-grounded, cited candidates arrive per
research cycle, pre-screened for data cost before any spec gets
written. That is a real answer to "idea quality, not throughput" --
it scales the input to the pipeline, not the pipeline's execution
step, which is intentionally kept slow and disciplined.

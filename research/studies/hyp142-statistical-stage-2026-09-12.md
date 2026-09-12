# Statistical stage — hyp-000142 (vxn_level_vs_trailing HIGH -> next-session RTH range)

September 11th, 9:49 pm CT (2026-09-12 02:49 UTC), extra cycle. Script: src/statistical_stage_hyp142.py; results: data/statistical_stage_hyp142_results.json. Discovery data only; frozen Scan 014 construction (tercile edges -0.0608 / +0.0258), nothing retuned. Validation data touched for ONE number only: the count of HIGH-tercile days at the frozen edges (n=198), for the power calculation -- no outcome examined.

Same-data selection disclosure: this candidate was selected on the same Discovery sample these questions are asked of (Scan 014 showed the sign and size before this pass). That is inherent to the Discovery Engine; the one-shot Validation is the genuine test.

| question | result | pass? |
|---|---|---|
| Q1 stability (chronological halves) | HIGH 1.267 / 1.344, LOW 0.802 / 0.791; same sign, all four halves credible | PASS |
| Q2 regime (trailing-range median) | HIGH 1.326 low-vol / 1.287 high-vol; LOW 0.828 / 0.768; credible in both regimes, not concentrated | PASS |
| Q3 magnitude, project-wide Sidak (N_discovery=302) | HIGH adjusted CI [1.203, 1.408]; LOW [0.736, 0.857]; both survive with room; \|dev\| 0.31 / 0.20 clear the 0.05 floor | PASS (the binding constraint) |
| Q4 selection sensitivity | quintile 1.401 / 0.745, tercile 1.305 / 0.796, quartile 1.348 / 0.761 -- monotone in cut width, no knife edge | PASS |
| P4 disentangle (residualise on overnight_range_vs_atr AND range_vs_atr terciles) | raw HIGH-LOW spread 0.493 -> 0.260 after both controls, 53% retained, residual HIGH still credible; corr(VXN state, prior-day range) +0.49 | PASS the pre-registered >= 50% bar, narrowly -- VXN does mirror realized range substantially; about half the effect is information beyond it |
| POWER at Validation (n=198 HIGH days, sd 0.675) | 1.00 if the true effect equals Discovery (dev 0.305); 0.97 at half; 0.79 at dev 0.10 | adequate -- a Validation null would be informative, not underpowered |

Verdict: ADVANCES. Strongest Discovery-stage result the project has produced on all four questions; the honest caveat is the disentangle -- 53% retained against two realized-range controls means the options market is roughly half echo, half information. Next owed (v2.5 order): Director capital call -> BLIND Integrity Gate -> frozen Validation spec -> one-shot Validation (automated under the OPEN-tier rule). If Validation passes this is a fourth range/conditioning fact, not a directional edge; Portfolio's incremental question follows Holdout as with hyp-000105.

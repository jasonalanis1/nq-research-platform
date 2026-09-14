# Idea Factory — pairwise interactions (U28), 2026-09-14

Discovery slice only, 1703 days. **K = 9910 distinct interaction cells looked at** (14740 label-rows: a timing tie emits both context/trigger orderings of the same cell, and K counts the DATA looked at, not the labels), **895 pairings dropped as circular** by the timing rule, **4405 cells below the n ≥ 100 floor**, across 11 states × 8 windows × 5 outcomes.

**Nothing below is a finding.** No hypothesis ID spent, no scan registered. This is a
ranked list of places to look. Any conditional stack sourced from it must carry
`look_cells_k=9910` into its registered spec (src/stack_spec.py) so the multiplicity
of this look is accounted for rather than forgotten.

**Timing rule, both layers:** a pairing is dropped when *either* state is not known
strictly before the window opens — a pairing is only as legitimate as its worst-timed
layer. Surviving pairs record which state may serve as the CONTEXT (the earlier-known
one; a tie emits both orderings).

**Ranked by `z_vs_additive` — the interaction proper.** A cell's distance from the
all-days mean (`z_vs_all`) or from the trigger-alone mean (`z_vs_trigger`) still carries
both states' own main effects inside it. Run 1 of this mode showed exactly why that
matters: ranked by `z_vs_trigger`, the entire top of the table was `vxn HIGH × anything
→ range`, which is the already-validated “volatile days have bigger ranges” fact with a
second state along for the ride. `z_vs_additive` measures the cell against what the two
states' separate effects predict *additively*, so a main effect cannot masquerade as an
interaction. All three are reported; the queue is ordered by the third.

> **Disclosed approximation:** every z here uses the all-days standard deviation and
> ignores that each cell is a subset of the groups it is compared against, so the
> standard errors are approximate. Acceptable here and only here, because nothing in
> this table is a test. Never quote a z from it as evidence.

Shortlist threshold |z_vs_additive| ≥ 2.5, n ≥ 100.

**Multiplicity yardstick (not a test):** with K = 9910 cells looked at, a single cell
would need |z| ≈ 4.56 to stand out family-wise; **0 cells clear that**.
Read the shortlist's length with that in mind — nested windows and terciles overlap
heavily, so a long shortlist is expected and is not itself evidence of anything.

## Candidate queue — 172 cells in 51 context×trigger families

### vxn_level_vs_trailing (context) × location_in_range (trigger) → range (13 cells, strongest |z_vs_additive| 4.4)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | LOW | morning | 390 | +0.530 | +0.583 | +0.537 | +0.497 | -4.4 | +2.7 |
| HIGH | LOW | next_rth | 390 | +0.975 | +1.084 | +1.014 | +0.916 | -4.4 | +2.4 |
| HIGH | LOW | last_hour | 377 | +0.388 | +0.428 | +0.376 | +0.350 | -4.4 | +4.1 |
| HIGH | LOW | midday | 390 | +0.456 | +0.500 | +0.455 | +0.419 | -3.9 | +3.3 |
| HIGH | LOW | afternoon | 377 | +0.415 | +0.458 | +0.399 | +0.381 | -3.8 | +3.0 |
| MID | LOW | last_hour | 127 | +0.270 | +0.327 | +0.275 | +0.350 | -3.6 | -5.1 |
| MID | LOW | midday | 130 | +0.338 | +0.407 | +0.361 | +0.419 | -3.5 | -4.1 |
| MID | LOW | afternoon | 127 | +0.300 | +0.365 | +0.306 | +0.381 | -3.3 | -4.2 |
| MID | HIGH | last_hour | 201 | +0.284 | +0.243 | +0.275 | +0.266 | +3.3 | +1.5 |
| LOW | HIGH | last_hour | 274 | +0.242 | +0.209 | +0.242 | +0.266 | +3.0 | -2.2 |
| MID | LOW | morning | 130 | +0.439 | +0.502 | +0.456 | +0.497 | -3.0 | -2.8 |
| MID | HIGH | morning | 211 | +0.463 | +0.419 | +0.456 | +0.414 | +2.7 | +3.0 |
| MID | HIGH | afternoon | 201 | +0.315 | +0.273 | +0.306 | +0.289 | +2.7 | +1.7 |

### vxn_level_vs_trailing (context) × vxn_minus_realized (trigger) → range (14 cells, strongest |z_vs_additive| 4.2)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | first30 | 316 | +0.277 | +0.233 | +0.302 | +0.305 | +4.2 | -2.6 |
| LOW | LOW | morning | 316 | +0.330 | +0.277 | +0.361 | +0.367 | +4.0 | -2.8 |
| LOW | LOW | next_rth | 313 | +0.649 | +0.542 | +0.698 | +0.690 | +3.9 | -1.5 |
| LOW | LOW | rth | 316 | +0.601 | +0.505 | +0.663 | +0.680 | +3.7 | -3.0 |
| MID | HIGH | overnight | 225 | +0.555 | +0.634 | +0.547 | +0.684 | -3.5 | -5.8 |
| MID | HIGH | rth | 222 | +0.867 | +0.969 | +0.825 | +0.983 | -3.3 | -3.8 |
| MID | LOW | overnight | 141 | +0.550 | +0.459 | +0.547 | +0.509 | +3.2 | +1.5 |
| MID | HIGH | first30 | 222 | +0.391 | +0.430 | +0.372 | +0.432 | -3.1 | -3.3 |
| MID | HIGH | morning | 222 | +0.480 | +0.530 | +0.456 | +0.526 | -3.1 | -2.9 |
| LOW | LOW | last_hour | 301 | +0.229 | +0.197 | +0.242 | +0.254 | +3.1 | -2.5 |
| LOW | LOW | midday | 316 | +0.278 | +0.240 | +0.305 | +0.309 | +3.0 | -2.5 |
| MID | HIGH | midday | 222 | +0.378 | +0.422 | +0.361 | +0.434 | -3.0 | -3.8 |
| LOW | MID | overnight | 182 | +0.551 | +0.479 | +0.484 | +0.591 | +2.9 | -1.6 |
| LOW | LOW | overnight | 322 | +0.448 | +0.396 | +0.484 | +0.509 | +2.8 | -3.2 |

### vxn_minus_realized (context) × vxn_level_vs_trailing (trigger) → range (14 cells, strongest |z_vs_additive| 4.2)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | first30 | 316 | +0.277 | +0.233 | +0.305 | +0.302 | +4.2 | -2.4 |
| LOW | LOW | morning | 316 | +0.330 | +0.277 | +0.367 | +0.361 | +4.0 | -2.3 |
| LOW | LOW | next_rth | 313 | +0.649 | +0.542 | +0.690 | +0.698 | +3.9 | -1.8 |
| LOW | LOW | rth | 316 | +0.601 | +0.505 | +0.680 | +0.663 | +3.7 | -2.4 |
| HIGH | MID | overnight | 225 | +0.555 | +0.634 | +0.684 | +0.547 | -3.5 | +0.4 |
| HIGH | MID | rth | 222 | +0.867 | +0.969 | +0.983 | +0.825 | -3.3 | +1.4 |
| LOW | MID | overnight | 141 | +0.550 | +0.459 | +0.509 | +0.547 | +3.2 | +0.1 |
| HIGH | MID | first30 | 222 | +0.391 | +0.430 | +0.432 | +0.372 | -3.1 | +1.5 |
| HIGH | MID | morning | 222 | +0.480 | +0.530 | +0.526 | +0.456 | -3.1 | +1.6 |
| LOW | LOW | last_hour | 301 | +0.229 | +0.197 | +0.254 | +0.242 | +3.1 | -1.3 |
| LOW | LOW | midday | 316 | +0.278 | +0.240 | +0.309 | +0.305 | +3.0 | -2.1 |
| HIGH | MID | midday | 222 | +0.378 | +0.422 | +0.434 | +0.361 | -3.0 | +1.1 |
| MID | LOW | overnight | 182 | +0.551 | +0.479 | +0.591 | +0.484 | +2.9 | +2.7 |
| LOW | LOW | overnight | 322 | +0.448 | +0.396 | +0.509 | +0.484 | +2.8 | -1.9 |

### vxn_level_vs_trailing (context) × opening_range_vs_atr (trigger) → range (7 cells, strongest |z_vs_additive| 4.2)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | midday | 280 | +0.265 | +0.209 | +0.305 | +0.278 | +4.2 | -1.0 |
| LOW | LOW | next_rth | 271 | +0.640 | +0.534 | +0.698 | +0.682 | +3.6 | -1.4 |
| LOW | LOW | last_hour | 255 | +0.222 | +0.186 | +0.242 | +0.242 | +3.3 | -1.8 |
| MID | HIGH | last_hour | 187 | +0.302 | +0.341 | +0.275 | +0.364 | -3.0 | -4.8 |
| MID | HIGH | next_rth | 184 | +0.903 | +1.009 | +0.826 | +1.028 | -3.0 | -3.5 |
| HIGH | LOW | midday | 120 | +0.301 | +0.359 | +0.455 | +0.278 | -2.9 | +1.1 |
| LOW | LOW | afternoon | 255 | +0.230 | +0.192 | +0.261 | +0.253 | +2.8 | -1.7 |

### range_vs_atr (context) × volume_vs_expected (trigger) → range (9 cells, strongest |z_vs_additive| 3.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | first30 | 247 | +0.485 | +0.531 | +0.451 | +0.454 | -3.9 | +2.6 |
| LOW | LOW | first30 | 207 | +0.294 | +0.251 | +0.309 | +0.316 | +3.3 | -1.7 |
| HIGH | HIGH | morning | 247 | +0.586 | +0.633 | +0.536 | +0.549 | -3.2 | +2.5 |
| HIGH | HIGH | overnight | 248 | +0.786 | +0.853 | +0.727 | +0.722 | -3.1 | +3.0 |
| HIGH | HIGH | next_rth | 248 | +1.028 | +1.123 | +0.972 | +0.997 | -3.1 | +1.0 |
| HIGH | HIGH | midday | 247 | +0.497 | +0.540 | +0.451 | +0.463 | -3.0 | +2.4 |
| HIGH | HIGH | rth | 247 | +1.077 | +1.161 | +0.992 | +1.007 | -2.9 | +2.4 |
| LOW | LOW | overnight | 215 | +0.477 | +0.413 | +0.506 | +0.503 | +2.8 | -1.1 |
| MID | HIGH | rth | 114 | +0.893 | +1.002 | +0.833 | +1.007 | -2.5 | -2.6 |

### volume_vs_expected (context) × range_vs_atr (trigger) → range (9 cells, strongest |z_vs_additive| 3.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | first30 | 247 | +0.485 | +0.531 | +0.454 | +0.451 | -3.9 | +2.9 |
| LOW | LOW | first30 | 207 | +0.294 | +0.251 | +0.316 | +0.309 | +3.3 | -1.1 |
| HIGH | HIGH | morning | 247 | +0.586 | +0.633 | +0.549 | +0.536 | -3.2 | +3.3 |
| HIGH | HIGH | overnight | 248 | +0.786 | +0.853 | +0.722 | +0.727 | -3.1 | +2.8 |
| HIGH | HIGH | next_rth | 248 | +1.028 | +1.123 | +0.997 | +0.972 | -3.1 | +1.8 |
| HIGH | HIGH | midday | 247 | +0.497 | +0.540 | +0.463 | +0.451 | -3.0 | +3.2 |
| HIGH | HIGH | rth | 247 | +1.077 | +1.161 | +1.007 | +0.992 | -2.9 | +2.9 |
| LOW | LOW | overnight | 215 | +0.477 | +0.413 | +0.503 | +0.506 | +2.8 | -1.3 |
| HIGH | MID | rth | 114 | +0.893 | +1.002 | +1.007 | +0.833 | -2.5 | +1.4 |

### vxn_minus_realized (context) × opening_range_vs_atr (trigger) → range (3 cells, strongest |z_vs_additive| 3.8)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | midday | 283 | +0.263 | +0.214 | +0.309 | +0.278 | +3.8 | -1.1 |
| LOW | LOW | next_rth | 277 | +0.612 | +0.526 | +0.690 | +0.682 | +3.0 | -2.4 |
| MID | HIGH | last_hour | 197 | +0.323 | +0.356 | +0.290 | +0.364 | -2.6 | -3.3 |

### volume_vs_expected (context) × opening_range_vs_atr (trigger) → range (3 cells, strongest |z_vs_additive| 3.8)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | afternoon | 128 | +0.283 | +0.356 | +0.369 | +0.309 | -3.8 | -1.3 |
| HIGH | MID | midday | 128 | +0.398 | +0.455 | +0.463 | +0.366 | -2.9 | +1.6 |
| HIGH | MID | last_hour | 128 | +0.297 | +0.340 | +0.354 | +0.284 | -2.7 | +0.8 |

### vxn_level_vs_trailing (context) × location_in_range (trigger) → mfe (6 cells, strongest |z_vs_additive| 3.5)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | LOW | next_rth | 390 | +0.493 | +0.556 | +0.498 | +0.458 | -3.5 | +2.0 |
| HIGH | LOW | midday | 390 | +0.223 | +0.251 | +0.220 | +0.207 | -3.4 | +2.0 |
| HIGH | LOW | last_hour | 377 | +0.190 | +0.214 | +0.188 | +0.172 | -3.3 | +2.6 |
| HIGH | LOW | afternoon | 377 | +0.201 | +0.224 | +0.189 | +0.188 | -3.1 | +1.7 |
| HIGH | LOW | morning | 390 | +0.272 | +0.299 | +0.263 | +0.248 | -3.0 | +2.8 |
| LOW | HIGH | morning | 290 | +0.173 | +0.145 | +0.175 | +0.183 | +2.7 | -1.0 |

### overnight_range_vs_atr (context) × opening_range_vs_atr (trigger) → range (6 cells, strongest |z_vs_additive| 3.4)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | midday | 228 | +0.264 | +0.213 | +0.309 | +0.278 | +3.4 | -1.0 |
| LOW | LOW | last_hour | 216 | +0.225 | +0.190 | +0.246 | +0.242 | +2.9 | -1.4 |
| HIGH | HIGH | midday | 229 | +0.542 | +0.585 | +0.481 | +0.477 | -2.9 | +4.4 |
| HIGH | HIGH | last_hour | 228 | +0.389 | +0.423 | +0.357 | +0.364 | -2.9 | +2.1 |
| LOW | LOW | afternoon | 216 | +0.245 | +0.206 | +0.275 | +0.253 | +2.6 | -0.5 |
| LOW | LOW | next_rth | 223 | +0.626 | +0.542 | +0.706 | +0.682 | +2.6 | -1.7 |

### directional_persistence (context) × location_in_range (trigger) → mfe (1 cells, strongest |z_vs_additive| 3.4)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | LOW | last_hour | 108 | +0.220 | +0.176 | +0.150 | +0.172 | +3.4 | +3.6 |

### range_vs_atr (context) × vxn_minus_realized (trigger) → range (5 cells, strongest |z_vs_additive| 3.3)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | HIGH | overnight | 183 | +0.560 | +0.643 | +0.555 | +0.684 | -3.3 | -5.0 |
| MID | LOW | overnight | 186 | +0.543 | +0.468 | +0.555 | +0.509 | +3.1 | +1.4 |
| MID | HIGH | morning | 182 | +0.462 | +0.512 | +0.438 | +0.526 | -2.9 | -3.6 |
| HIGH | MID | next_rth | 186 | +0.885 | +0.979 | +0.972 | +0.853 | -2.6 | +0.9 |
| HIGH | MID | last_hour | 182 | +0.315 | +0.349 | +0.358 | +0.290 | -2.6 | +1.9 |

### vxn_minus_realized (context) × range_vs_atr (trigger) → range (5 cells, strongest |z_vs_additive| 3.3)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | overnight | 183 | +0.560 | +0.643 | +0.684 | +0.555 | -3.3 | +0.2 |
| LOW | MID | overnight | 186 | +0.543 | +0.468 | +0.509 | +0.555 | +3.1 | -0.5 |
| HIGH | MID | morning | 182 | +0.462 | +0.512 | +0.526 | +0.438 | -2.9 | +1.4 |
| MID | HIGH | next_rth | 186 | +0.885 | +0.979 | +0.853 | +0.972 | -2.6 | -2.4 |
| MID | HIGH | last_hour | 182 | +0.315 | +0.349 | +0.290 | +0.358 | -2.6 | -3.3 |

### range_vs_atr (context) × location_in_range (trigger) → range (5 cells, strongest |z_vs_additive| 3.1)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | LOW | midday | 163 | +0.355 | +0.409 | +0.364 | +0.419 | -3.1 | -3.7 |
| LOW | HIGH | morning | 246 | +0.389 | +0.343 | +0.380 | +0.414 | +3.1 | -1.6 |
| LOW | HIGH | last_hour | 226 | +0.251 | +0.219 | +0.251 | +0.266 | +2.7 | -1.3 |
| MID | LOW | last_hour | 162 | +0.301 | +0.337 | +0.285 | +0.350 | -2.6 | -3.6 |
| MID | LOW | morning | 163 | +0.438 | +0.484 | +0.438 | +0.497 | -2.5 | -3.2 |

### vxn_level_vs_trailing (context) × vxn_minus_realized (trigger) → mfe (6 cells, strongest |z_vs_additive| 3.1)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | MID | overnight | 182 | +0.311 | +0.259 | +0.253 | +0.304 | +3.1 | +0.4 |
| MID | HIGH | rth | 222 | +0.366 | +0.434 | +0.371 | +0.458 | -3.0 | -4.1 |
| MID | LOW | overnight | 141 | +0.276 | +0.221 | +0.265 | +0.255 | +2.8 | +1.1 |
| MID | HIGH | midday | 222 | +0.163 | +0.193 | +0.165 | +0.204 | -2.8 | -3.8 |
| LOW | LOW | morning | 316 | +0.165 | +0.138 | +0.175 | +0.176 | +2.8 | -1.1 |
| MID | HIGH | overnight | 225 | +0.258 | +0.300 | +0.265 | +0.334 | -2.7 | -4.9 |

### vxn_minus_realized (context) × vxn_level_vs_trailing (trigger) → mfe (6 cells, strongest |z_vs_additive| 3.1)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | LOW | overnight | 182 | +0.311 | +0.259 | +0.304 | +0.253 | +3.1 | +3.5 |
| HIGH | MID | rth | 222 | +0.366 | +0.434 | +0.458 | +0.371 | -3.0 | -0.2 |
| LOW | MID | overnight | 141 | +0.276 | +0.221 | +0.255 | +0.265 | +2.8 | +0.6 |
| HIGH | MID | midday | 222 | +0.163 | +0.193 | +0.204 | +0.165 | -2.8 | -0.2 |
| LOW | LOW | morning | 316 | +0.165 | +0.138 | +0.176 | +0.175 | +2.8 | -1.0 |
| HIGH | MID | overnight | 225 | +0.258 | +0.300 | +0.334 | +0.265 | -2.7 | -0.4 |

### volume_vs_expected (context) × vxn_minus_realized (trigger) → range (2 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | afternoon | 125 | +0.317 | +0.377 | +0.369 | +0.330 | -3.0 | -0.7 |
| HIGH | HIGH | first30 | 203 | +0.477 | +0.512 | +0.454 | +0.432 | -2.7 | +3.4 |

### vxn_minus_realized (context) × volume_vs_expected (trigger) → range (2 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | HIGH | afternoon | 125 | +0.317 | +0.377 | +0.330 | +0.369 | -3.0 | -2.6 |
| HIGH | HIGH | first30 | 203 | +0.477 | +0.512 | +0.432 | +0.454 | -2.7 | +1.8 |

### directional_persistence (context) × location_in_range (trigger) → range (1 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | LOW | midday | 113 | +0.485 | +0.422 | +0.377 | +0.419 | +3.0 | +3.1 |

### overnight_range_vs_atr (context) × gap_vs_atr (trigger) → range (1 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | LOW | last_hour | 141 | +0.280 | +0.324 | +0.295 | +0.328 | -3.0 | -3.2 |

### gap_vs_atr (context) × overnight_range_vs_atr (trigger) → range (1 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | MID | last_hour | 141 | +0.280 | +0.324 | +0.328 | +0.295 | -3.0 | -1.0 |

### volume_vs_expected (context) × vxn_level_vs_trailing (trigger) → range (9 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | LOW | first30 | 154 | +0.332 | +0.287 | +0.359 | +0.302 | +3.0 | +2.0 |
| HIGH | MID | rth | 113 | +0.868 | +0.993 | +1.007 | +0.825 | -2.9 | +1.0 |
| LOW | LOW | rth | 189 | +0.627 | +0.530 | +0.706 | +0.663 | +2.9 | -1.1 |
| HIGH | MID | last_hour | 111 | +0.283 | +0.331 | +0.354 | +0.275 | -2.8 | +0.5 |
| MID | LOW | overnight | 154 | +0.517 | +0.443 | +0.555 | +0.484 | +2.8 | +1.2 |
| HIGH | HIGH | overnight | 222 | +0.819 | +0.879 | +0.722 | +0.753 | -2.7 | +2.9 |
| HIGH | HIGH | first30 | 222 | +0.494 | +0.527 | +0.454 | +0.447 | -2.6 | +3.8 |
| HIGH | MID | overnight | 114 | +0.593 | +0.673 | +0.722 | +0.547 | -2.5 | +1.5 |
| HIGH | MID | midday | 113 | +0.398 | +0.450 | +0.463 | +0.361 | -2.5 | +1.7 |

### vxn_level_vs_trailing (context) × volume_vs_expected (trigger) → range (9 cells, strongest |z_vs_additive| 3.0)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | MID | first30 | 154 | +0.332 | +0.287 | +0.302 | +0.359 | +3.0 | -1.8 |
| LOW | LOW | rth | 189 | +0.627 | +0.530 | +0.663 | +0.706 | +2.9 | -2.3 |
| MID | HIGH | rth | 113 | +0.868 | +0.993 | +0.825 | +1.007 | -2.9 | -3.2 |
| MID | HIGH | last_hour | 111 | +0.283 | +0.331 | +0.275 | +0.354 | -2.8 | -4.2 |
| LOW | MID | overnight | 154 | +0.517 | +0.443 | +0.484 | +0.555 | +2.8 | -1.4 |
| HIGH | HIGH | overnight | 222 | +0.819 | +0.879 | +0.753 | +0.722 | -2.7 | +4.3 |
| HIGH | HIGH | first30 | 222 | +0.494 | +0.527 | +0.447 | +0.454 | -2.6 | +3.2 |
| MID | HIGH | overnight | 114 | +0.593 | +0.673 | +0.547 | +0.722 | -2.5 | -4.1 |
| MID | HIGH | midday | 113 | +0.398 | +0.450 | +0.361 | +0.463 | -2.5 | -3.1 |

### volume_vs_expected (context) × vxn_minus_realized (trigger) → mae (1 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | afternoon | 125 | +0.147 | +0.200 | +0.195 | +0.173 | -2.9 | -1.5 |

### vxn_minus_realized (context) × volume_vs_expected (trigger) → mae (1 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | HIGH | afternoon | 125 | +0.147 | +0.200 | +0.173 | +0.195 | -2.9 | -2.7 |

### directional_persistence (context) × vxn_level_vs_trailing (trigger) → range (2 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | midday | 120 | +0.518 | +0.459 | +0.377 | +0.455 | +2.9 | +3.1 |
| HIGH | HIGH | overnight | 121 | +0.821 | +0.744 | +0.587 | +0.753 | +2.5 | +2.2 |

### vxn_level_vs_trailing (context) × directional_persistence (trigger) → range (2 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | midday | 120 | +0.518 | +0.459 | +0.455 | +0.377 | +2.9 | +6.9 |
| HIGH | HIGH | overnight | 121 | +0.821 | +0.744 | +0.753 | +0.587 | +2.5 | +7.7 |

### volume_vs_expected (context) × overnight_range_vs_atr (trigger) → range (2 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | morning | 106 | +0.484 | +0.551 | +0.549 | +0.454 | -2.9 | +1.4 |
| HIGH | MID | midday | 106 | +0.395 | +0.452 | +0.463 | +0.363 | -2.6 | +1.5 |

### range_vs_atr (context) × volume_vs_expected (trigger) → mae (1 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | HIGH | last_hour | 114 | +0.135 | +0.177 | +0.151 | +0.178 | -2.9 | -2.9 |

### volume_vs_expected (context) × range_vs_atr (trigger) → mae (1 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | last_hour | 114 | +0.135 | +0.177 | +0.178 | +0.151 | -2.9 | -1.1 |

### gap_vs_atr (context) × opening_range_vs_atr (trigger) → range (1 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | MID | midday | 177 | +0.366 | +0.415 | +0.422 | +0.366 | -2.9 | +0.0 |

### directional_persistence (context) × vxn_level_vs_trailing (trigger) → mfe (2 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | last_hour | 115 | +0.229 | +0.192 | +0.150 | +0.188 | +2.9 | +3.2 |
| HIGH | HIGH | midday | 120 | +0.263 | +0.226 | +0.182 | +0.220 | +2.5 | +3.0 |

### vxn_level_vs_trailing (context) × directional_persistence (trigger) → mfe (2 cells, strongest |z_vs_additive| 2.9)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | last_hour | 115 | +0.229 | +0.192 | +0.188 | +0.150 | +2.9 | +6.2 |
| HIGH | HIGH | midday | 120 | +0.263 | +0.226 | +0.220 | +0.182 | +2.5 | +5.5 |

### vxn_level_vs_trailing (context) × opening_range_vs_atr (trigger) → mae (1 cells, strongest |z_vs_additive| 2.8)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | midday | 280 | +0.146 | +0.109 | +0.162 | +0.145 | +2.8 | +0.0 |

### range_vs_atr (context) × opening_range_vs_atr (trigger) → range (2 cells, strongest |z_vs_additive| 2.8)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | midday | 280 | +0.249 | +0.211 | +0.307 | +0.278 | +2.8 | -2.2 |
| MID | HIGH | last_hour | 166 | +0.315 | +0.351 | +0.285 | +0.364 | -2.6 | -3.6 |

### overnight_range_vs_atr (context) × opening_range_vs_atr (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.8)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | afternoon | 216 | +0.113 | +0.085 | +0.125 | +0.114 | +2.8 | -0.1 |

### range_vs_atr (context) × vxn_minus_realized (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.7)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | HIGH | afternoon | 181 | +0.129 | +0.159 | +0.143 | +0.170 | -2.7 | -3.7 |

### vxn_minus_realized (context) × range_vs_atr (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.7)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | afternoon | 181 | +0.129 | +0.159 | +0.170 | +0.143 | -2.7 | -1.2 |

### vxn_level_vs_trailing (context) × location_in_range (trigger) → mae (2 cells, strongest |z_vs_additive| 2.7)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | LOW | last_hour | 127 | +0.140 | +0.177 | +0.151 | +0.178 | -2.7 | -2.8 |
| MID | LOW | afternoon | 127 | +0.141 | +0.186 | +0.161 | +0.193 | -2.5 | -2.9 |

### vxn_minus_realized (context) × opening_range_vs_atr (trigger) → mae (1 cells, strongest |z_vs_additive| 2.7)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | midday | 283 | +0.145 | +0.111 | +0.163 | +0.145 | +2.7 | -0.1 |

### vxn_minus_realized (context) × location_in_range (trigger) → range (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | last_hour | 184 | +0.283 | +0.318 | +0.350 | +0.266 | -2.6 | +1.3 |

### range_vs_atr (context) × volume_vs_expected (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | afternoon | 244 | +0.184 | +0.209 | +0.189 | +0.174 | -2.6 | +1.1 |

### volume_vs_expected (context) × range_vs_atr (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | afternoon | 244 | +0.184 | +0.209 | +0.174 | +0.189 | -2.6 | -0.5 |

### vxn_minus_realized (context) × location_in_range (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | last_hour | 184 | +0.130 | +0.157 | +0.170 | +0.133 | -2.6 | -0.3 |

### volume_vs_expected (context) × opening_range_vs_atr (trigger) → mae (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | afternoon | 128 | +0.141 | +0.187 | +0.195 | +0.161 | -2.6 | -1.1 |

### vxn_level_vs_trailing (context) × vxn_minus_realized (trigger) → mae (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | first30 | 316 | +0.152 | +0.127 | +0.162 | +0.155 | +2.6 | -0.4 |

### vxn_minus_realized (context) × vxn_level_vs_trailing (trigger) → mae (1 cells, strongest |z_vs_additive| 2.6)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | first30 | 316 | +0.152 | +0.127 | +0.155 | +0.162 | +2.6 | -1.1 |

### range_vs_atr (context) × volume_vs_expected (trigger) → move (1 cells, strongest |z_vs_additive| 2.5)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| MID | HIGH | last_hour | 114 | +0.038 | -0.013 | -0.011 | -0.002 | +2.5 | +2.0 |

### volume_vs_expected (context) × range_vs_atr (trigger) → move (1 cells, strongest |z_vs_additive| 2.5)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | MID | last_hour | 114 | +0.038 | -0.013 | -0.002 | -0.011 | +2.5 | +2.4 |

### vxn_level_vs_trailing (context) × opening_range_vs_atr (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.5)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| LOW | LOW | next_rth | 271 | +0.293 | +0.239 | +0.320 | +0.319 | +2.5 | -1.2 |

### range_vs_atr (context) × location_in_range (trigger) → mfe (1 cells, strongest |z_vs_additive| 2.5)

| context | trigger | window | n | cell mean | additive pred. | ctx alone | trg alone | z vs additive | z vs trigger |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| HIGH | HIGH | last_hour | 117 | +0.131 | +0.163 | +0.176 | +0.133 | -2.5 | -0.2 |

## Known restatements (both layers already-validated volatility states, size outcome)

| context | trigger | window | outcome | n | cell mean | additive pred. | z vs additive |
|---|---|---|---|---:|---:|---:|---:|
| range_vs_atr LOW | vxn_level_vs_trailing LOW | first30 | range | 278 | +0.281 | +0.237 | +3.9 |
| vxn_level_vs_trailing LOW | range_vs_atr LOW | first30 | range | 278 | +0.281 | +0.237 | +3.9 |
| range_vs_atr LOW | vxn_level_vs_trailing LOW | last_hour | range | 257 | +0.234 | +0.195 | +3.6 |
| vxn_level_vs_trailing LOW | range_vs_atr LOW | last_hour | range | 257 | +0.234 | +0.195 | +3.6 |
| range_vs_atr LOW | vxn_level_vs_trailing LOW | rth | range | 278 | +0.611 | +0.516 | +3.5 |
| vxn_level_vs_trailing LOW | range_vs_atr LOW | rth | range | 278 | +0.611 | +0.516 | +3.5 |
| range_vs_atr LOW | vxn_level_vs_trailing MID | overnight | range | 197 | +0.533 | +0.457 | +3.2 |
| vxn_level_vs_trailing MID | range_vs_atr LOW | overnight | range | 197 | +0.533 | +0.457 | +3.2 |
| range_vs_atr LOW | vxn_level_vs_trailing LOW | morning | range | 278 | +0.335 | +0.290 | +3.1 |
| vxn_level_vs_trailing LOW | range_vs_atr LOW | morning | range | 278 | +0.335 | +0.290 | +3.1 |
| range_vs_atr HIGH | vxn_level_vs_trailing MID | overnight | range | 150 | +0.591 | +0.677 | -3.1 |
| vxn_level_vs_trailing MID | range_vs_atr HIGH | overnight | range | 150 | +0.591 | +0.677 | -3.1 |
| range_vs_atr HIGH | vxn_level_vs_trailing MID | morning | range | 147 | +0.481 | +0.540 | -3.1 |
| vxn_level_vs_trailing MID | range_vs_atr HIGH | morning | range | 147 | +0.481 | +0.540 | -3.1 |
| range_vs_atr LOW | vxn_level_vs_trailing LOW | next_rth | range | 277 | +0.678 | +0.590 | +3.0 |
| vxn_level_vs_trailing LOW | range_vs_atr LOW | next_rth | range | 277 | +0.678 | +0.590 | +3.0 |
| range_vs_atr HIGH | vxn_level_vs_trailing MID | first30 | range | 147 | +0.404 | +0.449 | -2.9 |
| vxn_level_vs_trailing MID | range_vs_atr HIGH | first30 | range | 147 | +0.404 | +0.449 | -2.9 |
| vxn_level_vs_trailing MID | overnight_range_vs_atr HIGH | midday | mfe | 120 | +0.175 | +0.217 | -2.9 |
| vxn_level_vs_trailing MID | overnight_range_vs_atr LOW | last_hour | range | 167 | +0.262 | +0.223 | +2.8 |
| vxn_level_vs_trailing HIGH | overnight_range_vs_atr HIGH | midday | range | 231 | +0.522 | +0.562 | -2.8 |
| range_vs_atr LOW | vxn_level_vs_trailing LOW | afternoon | range | 257 | +0.246 | +0.208 | +2.8 |
| vxn_level_vs_trailing LOW | range_vs_atr LOW | afternoon | range | 257 | +0.246 | +0.208 | +2.8 |
| range_vs_atr HIGH | vxn_level_vs_trailing MID | last_hour | range | 144 | +0.293 | +0.335 | -2.8 |
| vxn_level_vs_trailing MID | range_vs_atr HIGH | last_hour | range | 144 | +0.293 | +0.335 | -2.8 |
| range_vs_atr MID | vxn_level_vs_trailing LOW | overnight | range | 185 | +0.511 | +0.443 | +2.8 |
| vxn_level_vs_trailing LOW | range_vs_atr MID | overnight | range | 185 | +0.511 | +0.443 | +2.8 |
| range_vs_atr HIGH | overnight_range_vs_atr MID | afternoon | range | 138 | +0.330 | +0.382 | -2.8 |
| range_vs_atr LOW | vxn_level_vs_trailing MID | morning | range | 193 | +0.431 | +0.385 | +2.8 |
| vxn_level_vs_trailing MID | range_vs_atr LOW | morning | range | 193 | +0.431 | +0.385 | +2.8 |

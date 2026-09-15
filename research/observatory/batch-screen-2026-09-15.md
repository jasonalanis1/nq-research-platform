# Batch screen — 2026-09-15

Lever C (research/infrastructure/acceleration-plan-2026-09-14.md), queue item 0-ACCEL. Discovery only. No hypothesis ID spent, no scan registered.

**25 cells screened this run** (batch K = 25 -- this run's own look count, not the 143-cell idea-factory sweep and not a cumulative total). **25 survivors** (Gate 1 clears the Sidak-adjusted bar at K=25). **18 placebo RED flags** (carried forward, not auto-rejected). **Cumulative cells screened project-wide: 25 / 143.**

Survival = Gate 1 alone (block-CI effect clears Sidak at the batch's own K). Gates 3 and 4 are diagnostic flags attached to every cell, survivor or not.

## Cells screened this run

### `opening_range_vs_atr` HIGH / midday / range — SURVIVOR

Idea-factory descriptive: n=558, mean=+0.4774, all_mean=+0.3738, z=+10.97. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1036 | Sidak(K=25) [+0.0787, +0.1349] | 90% unadj. [+0.0892, +0.1203]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.103582; legs={'shifted_t+1': 0.073956, 'inverted': -0.051838}; shifted_t+1 reaches 0.0740 vs the real 0.1036 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0517 | 90% [+0.0378, +0.0680] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` LOW / midday / range — SURVIVOR

Idea-factory descriptive: n=557, mean=+0.2779, all_mean=+0.3738, z=-10.15. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0959 | Sidak(K=25) [-0.1176, -0.0741] | 90% unadj. [-0.1089, -0.0826]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.095938; legs={'shifted_t+1': -0.053883, 'inverted': 0.047883}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 51% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0472 | 90% [-0.0600, -0.0350] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` HIGH / next_rth / range — SURVIVOR

Idea-factory descriptive: n=550, mean=+1.0277, all_mean=+0.8453, z=+8.79. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1823 | Sidak(K=25) [+0.1217, +0.2512] | 90% unadj. [+0.1464, +0.2232]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.182319; legs={'shifted_t+1': 0.138933, 'inverted': -0.091743}; shifted_t+1 reaches 0.1389 vs the real 0.1823 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0874 | 90% [+0.0538, +0.1218] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` HIGH / last_hour / range — SURVIVOR

Idea-factory descriptive: n=554, mean=+0.3645, all_mean=+0.2986, z=+8.77. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0660 | Sidak(K=25) [+0.0449, +0.0907] | 90% unadj. [+0.0523, +0.0796]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.065953; legs={'shifted_t+1': 0.056571, 'inverted': -0.034308}; shifted_t+1 reaches 0.0566 vs the real 0.0660 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0183 | 90% [+0.0089, +0.0275] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` LOW / first30 / range — SURVIVOR

Idea-factory descriptive: n=555, mean=+0.3046, all_mean=+0.3737, z=-8.71. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0694 | Sidak(K=25) [-0.0941, -0.0451] | 90% unadj. [-0.0838, -0.0544]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.069372; legs={'shifted_t+1': -0.05995, 'inverted': 0.034655}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0280 | 90% [-0.0415, -0.0161] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `volume_vs_expected` HIGH / first30 / range — SURVIVOR

Idea-factory descriptive: n=385, mean=+0.4537, all_mean=+0.3737, z=+8.41. Map anchor: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0762 | Sidak(K=25) [+0.0503, +0.1046] | 90% unadj. [+0.0613, +0.0924]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.076191; legs={'shifted_t+1': 0.048384, 'inverted': -0.039374}; inverted reaches -0.0394 vs the real 0.0762 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0168 | 90% [+0.0030, +0.0316] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` LOW / morning / range — SURVIVOR

Idea-factory descriptive: n=555, mean=+0.3672, all_mean=+0.4512, z=-8.37. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0845 | Sidak(K=25) [-0.1158, -0.0570] | 90% unadj. [-0.1015, -0.0685]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.0845; legs={'shifted_t+1': -0.075895, 'inverted': 0.042212}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0396 | 90% [-0.0549, -0.0264] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` HIGH / afternoon / range — SURVIVOR

Idea-factory descriptive: n=554, mean=+0.3981, all_mean=+0.3220, z=+8.20. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0761 | Sidak(K=25) [+0.0524, +0.1042] | 90% unadj. [+0.0622, +0.0912]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.076116; legs={'shifted_t+1': 0.048994, 'inverted': -0.039595}; shifted_t+1 reaches 0.0490 vs the real 0.0761 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0320 | 90% [+0.0189, +0.0455] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `volume_vs_expected` HIGH / morning / range — SURVIVOR

Idea-factory descriptive: n=385, mean=+0.5487, all_mean=+0.4512, z=+8.10. Map anchor: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0916 | Sidak(K=25) [+0.0572, +0.1308] | 90% unadj. [+0.0713, +0.1117]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.091569; legs={'shifted_t+1': 0.057326, 'inverted': -0.047321}; inverted reaches -0.0473 vs the real 0.0916 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0192 | 90% [+0.0017, +0.0388] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` LOW / rth / range — SURVIVOR

Idea-factory descriptive: n=555, mean=+0.6804, all_mean=+0.8382, z=-8.05. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.1585 | Sidak(K=25) [-0.2242, -0.1030] | 90% unadj. [-0.1930, -0.1221]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.158547; legs={'shifted_t+1': -0.137494, 'inverted': 0.079202}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0626 | 90% [-0.0917, -0.0337] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` LOW / next_rth / range — SURVIVOR

Idea-factory descriptive: n=547, mean=+0.6816, all_mean=+0.8453, z=-7.87. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.1638 | Sidak(K=25) [-0.2096, -0.1134] | 90% unadj. [-0.1908, -0.1328]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.163787; legs={'shifted_t+1': -0.140557, 'inverted': 0.081744}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 51% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0887 | 90% [-0.1155, -0.0597] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `volume_vs_expected` HIGH / midday / range — SURVIVOR

Idea-factory descriptive: n=385, mean=+0.4626, all_mean=+0.3738, z=+7.81. Map anchor: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0859 | Sidak(K=25) [+0.0536, +0.1230] | 90% unadj. [+0.0665, +0.1055]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.085902; legs={'shifted_t+1': 0.066789, 'inverted': -0.044392}; inverted reaches -0.0444 vs the real 0.0859 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0248 | 90% [+0.0065, +0.0443] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` LOW / next_rth / range — SURVIVOR

Idea-factory descriptive: n=552, mean=+0.6897, all_mean=+0.8453, z=-7.51. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.1569 | Sidak(K=25) [-0.2198, -0.0918] | 90% unadj. [-0.1930, -0.1176]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.156934; legs={'shifted_t+1': -0.140072, 'inverted': 0.077832}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0906 | 90% [-0.1257, -0.0581] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` HIGH / morning / range — SURVIVOR

Idea-factory descriptive: n=559, mean=+0.5256, all_mean=+0.4512, z=+7.44. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0738 | Sidak(K=25) [+0.0422, +0.1138] | 90% unadj. [+0.0545, +0.0941]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.073807; legs={'shifted_t+1': 0.067916, 'inverted': -0.03727}; inverted reaches -0.0373 vs the real 0.0738 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0270 | 90% [+0.0111, +0.0442] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` HIGH / rth / range — SURVIVOR

Idea-factory descriptive: n=559, mean=+0.9831, all_mean=+0.8382, z=+7.42. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1441 | Sidak(K=25) [+0.0766, +0.2177] | 90% unadj. [+0.1066, +0.1854]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.144124; legs={'shifted_t+1': 0.129742, 'inverted': -0.072778}; inverted reaches -0.0728 vs the real 0.1441 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0349 | 90% [+0.0060, +0.0661] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` HIGH / first30 / range — SURVIVOR

Idea-factory descriptive: n=559, mean=+0.4320, all_mean=+0.3737, z=+7.39. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0580 | Sidak(K=25) [+0.0318, +0.0879] | 90% unadj. [+0.0422, +0.0752]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.058049; legs={'shifted_t+1': 0.047176, 'inverted': -0.029313}; inverted reaches -0.0293 vs the real 0.0580 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0171 | 90% [+0.0048, +0.0301] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `volume_vs_expected` HIGH / overnight / range — SURVIVOR

Idea-factory descriptive: n=386, mean=+0.7224, all_mean=+0.5962, z=+7.37. Map anchor: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1289 | Sidak(K=25) [+0.0805, +0.1803] | 90% unadj. [+0.0999, +0.1552]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.128894; legs={'shifted_t+1': 0.085569, 'inverted': -0.06453}; inverted reaches -0.0645 vs the real 0.1289 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0002 | 90% [-0.0099, +0.0087] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=False |

### `vxn_minus_realized` HIGH / next_rth / range — SURVIVOR

Idea-factory descriptive: n=558, mean=+0.9957, all_mean=+0.8453, z=+7.30. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1490 | Sidak(K=25) [+0.0824, +0.2252] | 90% unadj. [+0.1084, +0.1918]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.148986; legs={'shifted_t+1': 0.132235, 'inverted': -0.075099}; inverted reaches -0.0751 vs the real 0.1490 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0752 | 90% [+0.0433, +0.1115] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` LOW / last_hour / range — SURVIVOR

Idea-factory descriptive: n=510, mean=+0.2423, all_mean=+0.2986, z=-7.18. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0563 | Sidak(K=25) [-0.0773, -0.0377] | 90% unadj. [-0.0673, -0.0444]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=-0.056277; legs={'shifted_t+1': -0.045103, 'inverted': 0.02588}; shifted_t+1 reaches -0.0451 vs the real -0.0563 (red at 50%) |
| 4. joint separability (T1) | OK | -0.0136 | 90% [-0.0230, -0.0036] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `volume_vs_expected` HIGH / rth / range — SURVIVOR

Idea-factory descriptive: n=385, mean=+1.0070, all_mean=+0.8382, z=+7.18. Map anchor: M31 (prior-day volume vs expected -> first-30-minute range, NQ; market_structure_map.md row M31)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.1653 | Sidak(K=25) [+0.0943, +0.2354] | 90% unadj. [+0.1240, +0.2076]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.165343; legs={'shifted_t+1': 0.124882, 'inverted': -0.085446}; inverted reaches -0.0854 vs the real 0.1653 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 60% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0370 | 90% [+0.0056, +0.0703] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` LOW / afternoon / range — SURVIVOR

Idea-factory descriptive: n=510, mean=+0.2530, all_mean=+0.3220, z=-7.13. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0690 | Sidak(K=25) [-0.0921, -0.0477] | 90% unadj. [-0.0805, -0.0561]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=-0.06899; legs={'shifted_t+1': -0.046064, 'inverted': 0.031727}; shifted_t+1 reaches -0.0461 vs the real -0.0690 (red at 50%) |
| 4. joint separability (T1) | OK | -0.0302 | 90% [-0.0426, -0.0175] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `vxn_minus_realized` HIGH / last_hour / range — SURVIVOR

Idea-factory descriptive: n=545, mean=+0.3503, all_mean=+0.2986, z=+6.82. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0519 | Sidak(K=25) [+0.0269, +0.0895] | 90% unadj. [+0.0340, +0.0697]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.051898; legs={'shifted_t+1': 0.046808, 'inverted': -0.026484}; inverted reaches -0.0265 vs the real 0.0519 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 88% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | +0.0087 | 90% [-0.0024, +0.0187] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=False |

### `vxn_minus_realized` LOW / midday / range — SURVIVOR

Idea-factory descriptive: n=555, mean=+0.3095, all_mean=+0.3738, z=-6.79. Map anchor: M29 (implied-minus-realized volatility gap, VXN vs NQ trailing realized vol -- STATE PRIMITIVE, market_structure_map.md row M29). NOTE: M29's own Stage-1 test is a dedicated HIGH-vs-LOW gap-tercile scan; a survivor here should be cross-checked against that entry's own construction before a mechanism doc is drafted, not assumed to be the same cell.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | -0.0645 | Sidak(K=25) [-0.0924, -0.0375] | 90% unadj. [-0.0806, -0.0482]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | GREEN | -- | -- | real=-0.06454; legs={'shifted_t+1': -0.052495, 'inverted': 0.032241}; no gating placebo comes close to the real effect [shifted_t+1 reported but NOT gating: it re-selects 87% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0281 | 90% [-0.0427, -0.0142] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `location_in_range` LOW / last_hour / range — SURVIVOR

Idea-factory descriptive: n=540, mean=+0.3503, all_mean=+0.2986, z=+6.79. Map anchor: M32 (open's location in the prior day's range -> later-session range, NQ; per idea_inventory.md ENTRY 36, which sourced and drew this anchor). NOTE: as of this script's writing, market_structure_map.md's own table has not yet been updated to add an M32 row -- a pre-existing maintenance gap this script did not create and is not the file to fix (out of scope: this script may only append to idea_inventory.md, never edit market_structure_map.md). Flagged for LEARN/Director.

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0519 | Sidak(K=25) [+0.0246, +0.0832] | 90% unadj. [+0.0344, +0.0690]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.051901; legs={'shifted_t+1': 0.031492, 'inverted': -0.02612}; inverted reaches -0.0261 vs the real 0.0519 (red at 50%) [shifted_t+1 reported but NOT gating: it re-selects 84% of the real sample, so it is not an independent placebo for a persistent state] |
| 4. joint separability (T1) | OK | -0.0108 | 90% [-0.0227, -0.0003] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

### `opening_range_vs_atr` HIGH / midday / mfe — SURVIVOR

Idea-factory descriptive: n=558, mean=+0.2214, all_mean=+0.1757, z=+6.71. Map anchor: M30 (opening-range width -> midday range/excursion, NQ; market_structure_map.md row M30)

| gate | status | point | interval | detail |
|---|---|---:|---|---|
| 1. block-CI effect | OK | +0.0457 | Sidak(K=25) [+0.0291, +0.0631] | 90% unadj. [+0.0356, +0.0558]; credible=True |
| 2. Sidak at batch K | -- | -- | -- | folded into gate 1; K=25 |
| 3. shifted placebo | RED | -- | -- | real=0.045654; legs={'shifted_t+1': 0.031266, 'inverted': -0.022848}; shifted_t+1 reaches 0.0313 vs the real 0.0457 (red at 50%) |
| 4. joint separability (T1) | OK | +0.0205 | 90% [+0.0112, +0.0312] | vs stack ['vxn_level_vs_trailing', 'overnight_range_vs_atr', 'range_vs_atr']; still_credible_after_stack=True |

## Non-survivors: "no edge in this data" is a valid result

Per the acceleration plan: "If the honest answer is 'no edge in this data', batch screening gets there sooner too, and that is also worth money." Full per-cell detail above; not repeated in research/idea_inventory.md, which is append-only for survivors.


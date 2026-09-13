# Idea Factory — candidate queue, 2026-09-13

Discovery slice only. **1045 descriptive cells ranked**, **315 dropped as circular** by the timing rule, across 11 market states × 8 windows × 5 outcomes.

No hypothesis ID spent. No scan registered. **Nothing below is a finding.** Each
queue entry is a candidate for a mechanism document, which is what licenses a test.

**The timing rule:** every state carries the moment its value is actually known, and
may only be crossed with a window starting at or after it. Run 1 of this engine
ranked `vwap_dist_vs_atr` (close vs session VWAP, known at the close) against the
same session's move at z = −20.4 — a definition restated. The rule drops it, and
315 cells like it, before ranking.

Thresholds: |z| ≥ 3.0 vs all days in the same window, n ≥ 120.

## Candidate queue — 143 cells in 19 families

### opening_range_vs_atr → range (8 cells, strongest |z| 11.0)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | midday | 558 | +0.477 | +0.374 | +11.0 |
| LOW | midday | 557 | +0.278 | +0.374 | -10.2 |
| HIGH | next_rth | 550 | +1.028 | +0.845 | +8.8 |
| HIGH | last_hour | 554 | +0.364 | +0.299 | +8.8 |
| HIGH | afternoon | 554 | +0.398 | +0.322 | +8.2 |
| LOW | next_rth | 547 | +0.682 | +0.845 | -7.9 |
| LOW | last_hour | 510 | +0.242 | +0.299 | -7.2 |
| LOW | afternoon | 510 | +0.253 | +0.322 | -7.1 |

### vxn_minus_realized → range (16 cells, strongest |z| 8.7)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | first30 | 555 | +0.305 | +0.374 | -8.7 |
| LOW | morning | 555 | +0.367 | +0.451 | -8.4 |
| LOW | rth | 555 | +0.680 | +0.838 | -8.1 |
| LOW | next_rth | 552 | +0.690 | +0.845 | -7.5 |
| HIGH | morning | 559 | +0.526 | +0.451 | +7.4 |
| HIGH | rth | 559 | +0.983 | +0.838 | +7.4 |
| HIGH | first30 | 559 | +0.432 | +0.374 | +7.4 |
| HIGH | next_rth | 558 | +0.996 | +0.845 | +7.3 |
| HIGH | last_hour | 545 | +0.350 | +0.299 | +6.8 |
| LOW | midday | 555 | +0.309 | +0.374 | -6.8 |
| HIGH | midday | 559 | +0.434 | +0.374 | +6.4 |
| HIGH | overnight | 565 | +0.684 | +0.596 | +6.2 |
| LOW | overnight | 566 | +0.509 | +0.596 | -6.2 |
| LOW | last_hour | 531 | +0.254 | +0.299 | -5.9 |
| LOW | afternoon | 531 | +0.276 | +0.322 | -4.8 |
| HIGH | afternoon | 545 | +0.359 | +0.322 | +4.0 |

### volume_vs_expected → range (16 cells, strongest |z| 8.4)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | first30 | 385 | +0.454 | +0.374 | +8.4 |
| HIGH | morning | 385 | +0.549 | +0.451 | +8.1 |
| HIGH | midday | 385 | +0.463 | +0.374 | +7.8 |
| HIGH | overnight | 386 | +0.722 | +0.596 | +7.4 |
| HIGH | rth | 385 | +1.007 | +0.838 | +7.2 |
| HIGH | last_hour | 381 | +0.354 | +0.299 | +6.1 |
| HIGH | next_rth | 386 | +0.997 | +0.845 | +6.1 |
| LOW | first30 | 360 | +0.316 | +0.374 | -5.9 |
| LOW | morning | 360 | +0.382 | +0.451 | -5.6 |
| LOW | overnight | 386 | +0.503 | +0.596 | -5.5 |
| LOW | rth | 360 | +0.706 | +0.838 | -5.4 |
| LOW | midday | 360 | +0.312 | +0.374 | -5.2 |
| LOW | next_rth | 360 | +0.733 | +0.845 | -4.4 |
| HIGH | afternoon | 381 | +0.369 | +0.322 | +4.2 |
| MID | last_hour | 376 | +0.265 | +0.299 | -3.7 |
| LOW | last_hour | 338 | +0.263 | +0.299 | -3.7 |

### location_in_range → range (9 cells, strongest |z| 6.8)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | last_hour | 540 | +0.350 | +0.299 | +6.8 |
| LOW | afternoon | 540 | +0.381 | +0.322 | +6.3 |
| LOW | midday | 557 | +0.419 | +0.374 | +4.8 |
| LOW | morning | 557 | +0.497 | +0.451 | +4.6 |
| HIGH | last_hour | 529 | +0.266 | +0.299 | -4.2 |
| HIGH | morning | 556 | +0.414 | +0.451 | -3.7 |
| HIGH | midday | 556 | +0.339 | +0.374 | -3.7 |
| HIGH | afternoon | 529 | +0.289 | +0.322 | -3.5 |
| LOW | next_rth | 556 | +0.916 | +0.845 | +3.4 |

### opening_range_vs_atr → mfe (8 cells, strongest |z| 6.7)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | midday | 558 | +0.221 | +0.176 | +6.7 |
| HIGH | afternoon | 554 | +0.194 | +0.154 | +6.5 |
| LOW | midday | 557 | +0.132 | +0.176 | -6.3 |
| LOW | afternoon | 510 | +0.114 | +0.154 | -6.0 |
| HIGH | last_hour | 554 | +0.181 | +0.146 | +6.0 |
| LOW | next_rth | 547 | +0.319 | +0.400 | -5.4 |
| HIGH | next_rth | 550 | +0.477 | +0.400 | +5.1 |
| LOW | last_hour | 510 | +0.116 | +0.146 | -5.1 |

### volume_vs_expected → mfe (10 cells, strongest |z| 6.6)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | morning | 385 | +0.271 | +0.213 | +6.6 |
| HIGH | midday | 385 | +0.218 | +0.176 | +5.2 |
| HIGH | rth | 385 | +0.481 | +0.396 | +5.0 |
| HIGH | first30 | 385 | +0.221 | +0.183 | +4.5 |
| HIGH | last_hour | 381 | +0.176 | +0.146 | +4.2 |
| HIGH | next_rth | 386 | +0.473 | +0.400 | +4.1 |
| LOW | next_rth | 360 | +0.338 | +0.400 | -3.3 |
| LOW | overnight | 386 | +0.261 | +0.298 | -3.2 |
| LOW | first30 | 360 | +0.155 | +0.183 | -3.2 |
| LOW | morning | 360 | +0.184 | +0.213 | -3.2 |

### opening_range_vs_atr → mae (8 cells, strongest |z| 6.3)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | midday | 558 | +0.256 | +0.198 | +6.3 |
| LOW | midday | 557 | +0.145 | +0.198 | -5.8 |
| HIGH | next_rth | 550 | +0.551 | +0.445 | +5.3 |
| HIGH | last_hour | 554 | +0.183 | +0.152 | +4.7 |
| HIGH | afternoon | 554 | +0.204 | +0.168 | +4.2 |
| LOW | next_rth | 547 | +0.363 | +0.445 | -4.1 |
| LOW | last_hour | 510 | +0.127 | +0.152 | -3.7 |
| LOW | afternoon | 510 | +0.139 | +0.168 | -3.4 |

### volume_vs_expected → mae (12 cells, strongest |z| 5.5)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | overnight | 386 | +0.390 | +0.298 | +5.5 |
| HIGH | first30 | 385 | +0.233 | +0.191 | +4.8 |
| HIGH | midday | 385 | +0.244 | +0.198 | +4.2 |
| HIGH | rth | 385 | +0.526 | +0.442 | +3.6 |
| LOW | rth | 360 | +0.359 | +0.442 | -3.4 |
| LOW | overnight | 386 | +0.242 | +0.298 | -3.3 |
| LOW | first30 | 360 | +0.161 | +0.191 | -3.3 |
| HIGH | next_rth | 386 | +0.523 | +0.445 | +3.3 |
| HIGH | last_hour | 381 | +0.178 | +0.152 | +3.2 |
| LOW | morning | 360 | +0.198 | +0.238 | -3.2 |
| HIGH | morning | 385 | +0.277 | +0.238 | +3.2 |
| LOW | midday | 360 | +0.162 | +0.198 | -3.2 |

### location_in_range → mfe (9 cells, strongest |z| 5.5)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | afternoon | 540 | +0.188 | +0.154 | +5.5 |
| LOW | morning | 557 | +0.248 | +0.213 | +4.8 |
| LOW | midday | 557 | +0.207 | +0.176 | +4.6 |
| LOW | last_hour | 540 | +0.172 | +0.146 | +4.3 |
| HIGH | morning | 556 | +0.183 | +0.213 | -4.0 |
| LOW | next_rth | 556 | +0.458 | +0.400 | +3.9 |
| HIGH | afternoon | 529 | +0.129 | +0.154 | -3.9 |
| HIGH | next_rth | 559 | +0.348 | +0.400 | -3.5 |
| HIGH | midday | 556 | +0.152 | +0.176 | -3.5 |

### gap_vs_atr → range (7 cells, strongest |z| 5.2)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | midday | 562 | +0.422 | +0.374 | +5.2 |
| LOW | morning | 562 | +0.502 | +0.451 | +5.1 |
| LOW | next_rth | 551 | +0.927 | +0.845 | +4.0 |
| LOW | last_hour | 548 | +0.328 | +0.299 | +3.8 |
| MID | morning | 552 | +0.417 | +0.451 | -3.4 |
| MID | midday | 552 | +0.342 | +0.374 | -3.3 |
| LOW | afternoon | 548 | +0.351 | +0.322 | +3.1 |

### vxn_minus_realized → mae (13 cells, strongest |z| 5.0)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | morning | 559 | +0.289 | +0.238 | +5.0 |
| LOW | first30 | 555 | +0.155 | +0.191 | -4.9 |
| LOW | morning | 555 | +0.191 | +0.238 | -4.7 |
| LOW | rth | 555 | +0.352 | +0.442 | -4.6 |
| LOW | next_rth | 552 | +0.355 | +0.445 | -4.5 |
| HIGH | rth | 559 | +0.525 | +0.442 | +4.2 |
| HIGH | next_rth | 558 | +0.529 | +0.445 | +4.2 |
| HIGH | last_hour | 545 | +0.180 | +0.152 | +4.2 |
| HIGH | first30 | 559 | +0.219 | +0.191 | +3.9 |
| LOW | midday | 555 | +0.163 | +0.198 | -3.8 |
| HIGH | overnight | 565 | +0.350 | +0.298 | +3.8 |
| HIGH | midday | 559 | +0.231 | +0.198 | +3.6 |
| LOW | overnight | 566 | +0.254 | +0.298 | -3.2 |

### vxn_minus_realized → mfe (15 cells, strongest |z| 5.0)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | morning | 555 | +0.176 | +0.213 | -5.0 |
| LOW | first30 | 555 | +0.149 | +0.183 | -4.8 |
| LOW | rth | 555 | +0.329 | +0.396 | -4.7 |
| LOW | overnight | 566 | +0.255 | +0.298 | -4.5 |
| HIGH | next_rth | 558 | +0.467 | +0.400 | +4.5 |
| HIGH | rth | 559 | +0.458 | +0.396 | +4.4 |
| LOW | next_rth | 552 | +0.335 | +0.400 | -4.4 |
| LOW | midday | 555 | +0.146 | +0.176 | -4.3 |
| HIGH | first30 | 559 | +0.213 | +0.183 | +4.3 |
| LOW | last_hour | 531 | +0.121 | +0.146 | -4.2 |
| HIGH | midday | 559 | +0.204 | +0.176 | +4.1 |
| HIGH | last_hour | 545 | +0.170 | +0.146 | +4.0 |
| HIGH | overnight | 565 | +0.334 | +0.298 | +3.7 |
| HIGH | morning | 559 | +0.237 | +0.213 | +3.3 |
| LOW | afternoon | 531 | +0.134 | +0.154 | -3.1 |

### day_of_week → mfe (1 cells, strongest |z| 4.7)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| Wed | afternoon | 336 | +0.191 | +0.154 | +4.7 |

### day_of_week → range (4 cells, strongest |z| 4.5)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| Wed | afternoon | 336 | +0.376 | +0.322 | +4.5 |
| Thu | midday | 344 | +0.414 | +0.374 | +3.4 |
| Mon | midday | 344 | +0.335 | +0.374 | -3.2 |
| Mon | afternoon | 313 | +0.283 | +0.322 | -3.1 |

### location_in_range → mae (1 cells, strongest |z| 3.9)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | last_hour | 540 | +0.178 | +0.152 | +3.9 |

### day_of_week → tte (2 cells, strongest |z| 3.9)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| Mon | overnight | 344 | +616.212 | +684.886 | -3.9 |
| Fri | overnight | 337 | +742.908 | +684.886 | +3.2 |

### gap_vs_atr → mfe (2 cells, strongest |z| 3.5)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | last_hour | 548 | +0.166 | +0.146 | +3.5 |
| LOW | midday | 562 | +0.198 | +0.176 | +3.3 |

### gap_vs_atr → mae (1 cells, strongest |z| 3.4)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| LOW | morning | 562 | +0.272 | +0.238 | +3.4 |

### location_in_range → tte (1 cells, strongest |z| 3.1)

| level | window | n | mean | all-days | z |
|---|---|---:|---:|---:|---:|
| HIGH | next_rth | 559 | +213.487 | +230.559 | -3.1 |

## Known restatements (not new — these feed the Risk/State Engine)

| state | level | window | outcome | n | mean | all-days | z |
|---|---|---|---|---:|---:|---:|---:|
| vxn_level_vs_trailing | HIGH | overnight | range | 566 | +0.753 | +0.596 | +11.1 |
| vxn_level_vs_trailing | HIGH | last_hour | range | 544 | +0.376 | +0.299 | +10.2 |
| overnight_range_vs_atr | HIGH | midday | range | 436 | +0.481 | +0.374 | +10.0 |
| range_vs_atr | HIGH | first30 | range | 555 | +0.451 | +0.374 | +9.7 |
| vxn_level_vs_trailing | HIGH | rth | range | 558 | +1.027 | +0.838 | +9.7 |
| range_vs_atr | HIGH | overnight | range | 568 | +0.727 | +0.596 | +9.3 |
| vxn_level_vs_trailing | HIGH | first30 | range | 558 | +0.447 | +0.374 | +9.3 |
| overnight_range_vs_atr | HIGH | morning | range | 436 | +0.554 | +0.451 | +9.1 |
| vxn_level_vs_trailing | LOW | first30 | range | 553 | +0.302 | +0.374 | -9.0 |
| vxn_level_vs_trailing | LOW | morning | range | 553 | +0.361 | +0.451 | -8.9 |
| vxn_level_vs_trailing | LOW | rth | range | 553 | +0.663 | +0.838 | -8.9 |
| vxn_level_vs_trailing | HIGH | midday | range | 558 | +0.455 | +0.374 | +8.6 |
| vxn_level_vs_trailing | HIGH | morning | range | 558 | +0.537 | +0.451 | +8.6 |
| range_vs_atr | HIGH | morning | range | 555 | +0.536 | +0.451 | +8.5 |
| range_vs_atr | LOW | first30 | range | 560 | +0.309 | +0.374 | -8.2 |
| vxn_level_vs_trailing | HIGH | next_rth | range | 559 | +1.014 | +0.845 | +8.2 |
| vxn_level_vs_trailing | HIGH | afternoon | range | 544 | +0.399 | +0.322 | +8.2 |
| range_vs_atr | HIGH | midday | range | 555 | +0.451 | +0.374 | +8.1 |
| vxn_level_vs_trailing | HIGH | overnight | mfe | 566 | +0.375 | +0.298 | +8.0 |
| vxn_level_vs_trailing | LOW | overnight | range | 566 | +0.484 | +0.596 | -8.0 |
| range_vs_atr | HIGH | rth | range | 555 | +0.992 | +0.838 | +7.9 |
| range_vs_atr | HIGH | last_hour | range | 544 | +0.358 | +0.299 | +7.8 |
| range_vs_atr | LOW | rth | range | 560 | +0.691 | +0.838 | -7.5 |
| vxn_level_vs_trailing | HIGH | rth | mfe | 558 | +0.502 | +0.396 | +7.5 |
| vxn_level_vs_trailing | LOW | last_hour | range | 528 | +0.242 | +0.299 | -7.3 |
| vxn_level_vs_trailing | LOW | midday | range | 553 | +0.305 | +0.374 | -7.3 |
| vxn_level_vs_trailing | HIGH | last_hour | mfe | 544 | +0.188 | +0.146 | +7.2 |
| vxn_level_vs_trailing | LOW | next_rth | range | 554 | +0.698 | +0.845 | -7.2 |
| range_vs_atr | LOW | morning | range | 560 | +0.380 | +0.451 | -7.1 |
| range_vs_atr | LOW | midday | range | 560 | +0.307 | +0.374 | -7.0 |
| overnight_range_vs_atr | LOW | morning | range | 437 | +0.373 | +0.451 | -6.9 |
| overnight_range_vs_atr | HIGH | afternoon | range | 435 | +0.394 | +0.322 | +6.9 |
| vxn_level_vs_trailing | HIGH | morning | mfe | 558 | +0.263 | +0.213 | +6.9 |
| overnight_range_vs_atr | HIGH | last_hour | range | 435 | +0.357 | +0.299 | +6.8 |
| overnight_range_vs_atr | HIGH | midday | mfe | 436 | +0.227 | +0.176 | +6.7 |
| vxn_level_vs_trailing | HIGH | first30 | mfe | 558 | +0.230 | +0.183 | +6.7 |
| vxn_level_vs_trailing | HIGH | next_rth | mfe | 559 | +0.498 | +0.400 | +6.6 |
| vxn_level_vs_trailing | LOW | afternoon | range | 528 | +0.261 | +0.322 | -6.5 |
| vxn_level_vs_trailing | HIGH | midday | mfe | 558 | +0.220 | +0.176 | +6.5 |
| range_vs_atr | LOW | overnight | range | 568 | +0.506 | +0.596 | -6.4 |

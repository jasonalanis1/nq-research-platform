# H118 baseline diagnostic -- September 12th, 2026

READ-ONLY. Question: does the LOW-tercile 10-day drift beat NQ's own 10-day drift over the same slice?
Units: H118's own net R-multiple ((close[t+10]-close[t]-cost)/atr14). Bucket edges frozen on Discovery.
Two CIs on the difference: iid bootstrap (H118's convention) and a 10-day moving-block bootstrap,
which is the honest one because 10-day windows overlap and are autocorrelated.

## Discovery slice (1717 days)

ALL days: n=1693 mean_r=+0.5004 ci_90=(+0.4114,+0.5909)

- low  n= 554 mean_r=+0.6166 vs_zero=(+0.4533,+0.7849) | minus ALL = +0.1162  iid=(-0.0688,+0.3145)  block10=(-0.2630,+0.4895)  <== H118
- mid  n= 555 mean_r=+0.4963 vs_zero=(+0.3620,+0.6464) | minus ALL = -0.0041  iid=(-0.1618,+0.1672)  block10=(-0.3204,+0.3429)
- high n= 555 mean_r=+0.4241 vs_zero=(+0.2722,+0.5836) | minus ALL = -0.0763  iid=(-0.2505,+0.1103)  block10=(-0.4349,+0.2846)

## Validation slice (582 days)

ALL days: n=558 mean_r=+0.1996 ci_90=(+0.0408,+0.3442)

- low  n= 216 mean_r=+0.2477 vs_zero=(+0.0131,+0.4877) | minus ALL = +0.0481  iid=(-0.2296,+0.3349)  block10=(-0.5851,+0.6255)  <== H118
- mid  n= 132 mean_r=-0.0543 vs_zero=(-0.3566,+0.2543) | minus ALL = -0.2539  iid=(-0.5833,+0.0895)  block10=(-0.8732,+0.4585)
- high n= 200 mean_r=+0.3212 vs_zero=(+0.0702,+0.5737) | minus ALL = +0.1215  iid=(-0.1712,+0.4285)  block10=(-0.5860,+0.6759)

## Verdict

Verdict (block bootstrap, the honest CI): LOW minus ALL-days does NOT clear zero on Discovery (+0.1162, block10 CI -0.2630..+0.4895) and does NOT clear zero on Validation (+0.0481, block10 CI -0.5851..+0.6255).

This changes nothing frozen. It is the comparison that should have been run when H118 was promoted; 
the ledger status is Jason's call after reading it.

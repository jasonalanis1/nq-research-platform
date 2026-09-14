# The $50–150 per-trade swing band has gone stale against NQ's price level

September 14th, evening, after the approved data top-up landed. Diagnostic:
`/tmp`-only script, figures reproduced below; source data is the refreshed NQ
series through 2026-09-14.

## What happened

The data refresh worked. Four complete sessions (Sept 8th–11th) went through the
B7 execution loop for real. **All four were blocked by capital protection, every
one for the same reason: the per-trade swing was outside the $50–150 band.**

| session | direction | stop distance | swing per micro |
|---|---|---:|---:|
| 2026-09-08 | short | 233.75 pts | $468 |
| 2026-09-09 | long | 152.00 pts | $304 |
| 2026-09-10 | long | 172.00 pts | $344 |
| 2026-09-11 | short | 136.00 pts | $272 |

This is not four unlucky days.

## The distribution, across every B3 signal on disk (2,721 signals, 2015→today)

| | swing per micro |
|---|---:|
| minimum | $4 |
| 10th percentile | $36 |
| **median** | **$132** |
| 90th percentile | $345 |
| maximum | $1,330 |

Share inside the current band: **36.2% overall** — but that average hides the
whole story:

| year | signals | share fitting $50–150 | median swing |
|---|---:|---:|---:|
| 2015 | 205 | 43.9% | $47 |
| 2016 | 234 | 34.2% | $41 |
| 2017 | 235 | 30.2% | $38 |
| 2018 | 234 | **77.4%** | $85 |
| 2019 | 227 | 76.2% | $72 |
| 2020 | 234 | 45.3% | $156 |
| 2021 | 231 | 35.9% | $174 |
| 2022 | 236 | 6.4% | $259 |
| 2023 | 236 | 36.4% | $166 |
| 2024 | 243 | 28.0% | $197 |
| 2025 | 238 | 11.8% | $265 |
| **2026** | 168 | **2.4%** | **$376** |

## The reading

**The band is denominated in dollars and the index has roughly six-tupled.** NQ
traded near 4,500 when a $50–150 micro swing was the typical ORB stop; it trades
near 29,500 today. The same *percentage* stop is now several times as many
dollars, so a rule written in fixed dollars has quietly drifted from "typical" to
"almost never".

At a 2.4% fit rate, B7 would see roughly one tradeable signal every 40 sessions.
**The 40-fill execution sample the entire back half of the roadmap waits on would
take years.** The order path is not broken and the gate is not malfunctioning —
B6 is doing exactly what it was built to do. What it is protecting against has
moved.

## This is a decision for Jason, not a fix to apply

The band is a frozen capital-protection parameter and B3 is a frozen spec.
Nothing here is changed automatically. Three options, stated plainly:

**(a) Leave it.** Honest and safe, and it means B7 accumulates a fill every few
months. The execution record — and everything gated on it, including the open
cost clause on hyp-000162 — stays frozen indefinitely.

**(b) Re-express the band so it scales with the instrument** — as a fraction of
contract notional, or in ATR units, rather than fixed dollars. This is the
principled fix: it restores the rule's *original intent* (a small, survivable
per-trade loss relative to the account) instead of its 2018 arithmetic. It does
change a frozen parameter, which needs saying out loud.

**(c) Keep the band and accept that B3 is not the strategy that produces the
record.** B3 is an explicit placeholder, so this is defensible — but it means
waiting for a strategy whose natural stop is small enough, and the project does
not currently have a validated directional candidate at all.

**Staff recommendation: (b), with the dollar band kept as an absolute ceiling.**
The intent of the rule is loss containment relative to capital; expressing it in
units that move with the instrument preserves that intent, where fixed dollars
have already lost it. Keeping an absolute ceiling alongside means the rule can
never scale into a genuinely dangerous per-trade loss.

Recorded, not acted on. Nothing about the band, B3, or B6 is changed by this
document.

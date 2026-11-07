# Postmortem: <title> (<YYYY-MM-DD>, SEV<n>)
Status: draft | reviewed | actions-closed   Authors: <roles>   Blameless: yes

## Summary
<2–3 sentences: what broke, who was affected, how long, how it was fixed.>

## Impact
- Users/players affected: <count or %>, platforms/regions: <...>
- Duration: detect <t0→t1>, mitigate <t1→t2>, resolve <t2→t3>
- SLO/error budget consumed: <% of monthly budget>
- Money/data: <failed purchases, wallet discrepancies, data loss — or "none">

## Timeline (UTC)
| Time | Event (facts, no blame) |
|---|---|
| <hh:mm> | <deploy / alert fired / page acked / mitigation> |

## Root cause and trigger
- Trigger: <the change/event that started it>
- Root cause(s): <the latent conditions — use 5 whys or contributing-factor list>
- Why detection took <x> min: <alerting gap or "alert worked">

## What went well / what went poorly / where we got lucky
- <...>

## Action items
| ID | Action (prevent / detect / mitigate) | Owner (role) | Due | Ticket |
|---|---|---|---|---|
| A1 | <...> | <role> | <date> | <link> |

## Lessons
- <generalizable learning; link runbook/ADR updates>

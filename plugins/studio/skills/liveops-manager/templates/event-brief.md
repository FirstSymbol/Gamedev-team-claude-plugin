# Event brief: <event-id>
Owner: <liveops-manager> · Status: <draft|review|approved|staged|live|done> · Updated: <YYYY-MM-DD>

## Goal
- Goal KPI: <one metric, e.g. sessions/DAU of level>=10 players>
- Success threshold: <+x% vs holdout | participation >= y% of eligible DAU>
- Guardrails: <D7 retention not below holdout - z pp; refund rate <= baseline x 1.5>

## Setup
- Type / template: <points LTE | tournament | pass | collection | offer | ...>
- Window (UTC): <YYYY-MM-DDTHH:MM> → <YYYY-MM-DDTHH:MM> · min client: <x.y.z>
- Audience: <segment ids> · Exclusions: <holdout, minors/unknown age, self-limited, geo>
- Holdout: <size %, randomization salt/experiment id>
- Overlaps: <concurrent events + shared point sources + combined multiplier cap>

## Mechanics & rewards
- Point sources / rules: <action → points>
- Milestones / prizes: <table or link to config>
- Expected completion: <% reaching milestone 1 / mid / grand prize, by segment>
- Currency/item injection: <per participant per segment; total vs weekly budget>
- Offers attached: <SKU, price, contents, cooldown> · Odds disclosure: <link if random>
- Economy sign-off: <economy-monetization-designer, date>

## Delivery
- Config CR: <CR-NNN> · Assets: <Addressables label / CCD badge> · Loc: <languages, due>
- Store surfaces: <Apple In-App Event / Google promo content: submit by date>
- Comms plan: <T-3d teaser, T0 push, T+1d inbox, T-24h reminder, results>
- QA on staging: <test accounts per segment, test ids, date>

## Operations
- Dashboard: <link> · Alerts: <metric → threshold → owner>
- On-call: <names, launch window>
- Kill switch: <flag/key> · Rollback: <previous config version / steps>
- Compensation tier if broken: <per policy>

## Results (after event)
- Post-event report: <.team/reports/liveops/post-event-<event-id>.md> · Verdict: <repeat|tune|retire>

# Analysis: <title>
Date: <YYYY-MM-DD>  Owner: data-analyst  Type: exploratory | experiment readout | KPI review | incident
Requested by: <role>  Decision this informs: <what will change based on the answer>

## TL;DR (≤ 5 lines)
- Answer/decision: <ship | don't ship | iterate | investigate>, because <key number with CI>.
- Confidence: <high/medium/low> — main caveat: <…>

## Question & hypothesis
- Question: <…>  · Hypothesis (if any): <X moves M by ≥ δ because …>

## Data
- Sources/tables: <…>  · Date range (UTC): <from–to>  · Snapshot taken: <date>
- Population/filters: <eligible users, excluded test users/bots/refunds>
- Metric definitions: <link .team/specs/analytics/metrics.md#…> (state retention method, gross/net)
- Data quality checks: <volumes, duplicates, nulls, reconciliation vs store/PSP> → <pass/issues>

## Experiment validity (readouts only)
- Plan: <link experiment-<id>.md>  · Split: <planned> vs <actual> · SRM p = <…>
- Exposure: <n per arm, start/end, trigger>  · Power/MDE planned: <…>  · Peeking/sequential: <method>

## Results
| Metric | Control | Treatment | Δ abs | Δ rel | 95% CI | p / P(better) | n (C/T) |
|---|---|---|---|---|---|---|---|
| <primary> | | | | | | | |
| <guardrail> | | | | | | | |
- Pre-declared segments: <platform, country, payer tier, new vs existing> → <consistent? Simpson check>
- Charts: <paths in .team/reports/assets/> (units, n, date range labeled)

## Interpretation & caveats
- <novelty/primacy, seasonality/live events, small n, observational confounders, tracking gaps>

## Recommendation & next steps
- <action> → <owner role>; follow-up read on <date> for <long-term metric>

## Reproducibility
- Queries/scripts: <paths>  · Parameters: <…>  · Runtime notes: <…>

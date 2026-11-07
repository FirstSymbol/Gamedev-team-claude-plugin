# Runbook: <Alert name or task>
Service: <name> | Owner: <team/on-call rotation> | Severity: <SEV1-4> | Last tested: <YYYY-MM-DD>

## Summary
- Trigger: <alert condition / when to use this runbook>
- Impact: <what players/users/ops experience; money at risk?>
- Dashboards: <name + link> | Logs: <query/link>

## Preconditions
- Access: <roles, VPN, kubectl context, admin panel permission>
- Tools: <kubectl x, az/aws CLI, psql>

## Diagnose
1. <Check> - `<command with <placeholders>>`
   Expected: <healthy output>. If <symptom>: go to Mitigate option <A/B>.
2. <Check> - `<command>`
   Expected: <...>

## Mitigate (fastest safe option first)
- **A. <name>**: `<command>` - effect: <...>; risk: <...>
- **B. <name>**: `<command>` - effect: <...>; risk: <...>
- Irreversible actions (data deletion, prod config changes affecting money): get approval from <role>.

## Verify
- <metric/alert returns to normal within <N> min>; <synthetic check passes>

## Rollback
- <how to undo mitigation>

## Escalate
| After | Contact | Channel |
|---|---|---|
| <15 min unresolved> | <role/team> | <pager/channel> |

## Follow-up
- Incident record/postmortem: <link template>; update this runbook with what was missing.

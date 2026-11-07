---
name: status
description: Summarize the studio team blackboard (.team/) - open tasks, risks, decisions, latest handoffs.
disable-model-invocation: true
argument-hint: "[project root]"
---
# /studio:status
1. Run `python "${CLAUDE_PLUGIN_ROOT}/skills/team-protocol/scripts/team_status.py" $ARGUMENTS` (default: cwd).
   Do not read `.team/` files manually unless the summary shows something that needs detail.
2. Reply in the user's language, ≤ 12 lines: progress (done/open), blocked items with the
   reason, top 3 risks, pending decisions for the human, recommended next action + role.

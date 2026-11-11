# Lessons: code-reviewer
| ID | Date | Sev | Tags | Rule | Evidence | Hits |
|---|---|---|---|---|---|---|
| G-081 | 2026-11-11 | S2 | cleanup,shared-dirs | Never bulk-delete in shared scratch/temp dirs; delete only files you created, by exact path recorded when you created them. | a branch review wiped top-level files in a session scratchpad used by other agents | 1 |

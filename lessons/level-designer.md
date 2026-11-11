# Lessons: level-designer
| ID | Date | Sev | Tags | Rule | Evidence | Hits |
|---|---|---|---|---|---|---|
| G-142 | 2026-11-11 | S3 | navmesh,timing,verification | Measure NavMesh path lengths between key points after the bake before trusting plan-based distance or timing estimates; baked paths differ from plan centre lines. | src: p:18488f2c32d61514:L-058; baked path was about 0.91x the plan line, close to the timing target | 1 |

# Lessons: producer
| ID | Date | Sev | Tags | Rule | Evidence | Hits |
|---|---|---|---|---|---|---|
| G-141 | 2026-11-11 | S3 | tooling,python,forecast | Run forecast and simulation scripts as standalone files by absolute path; never exec them via stdin or import siblings through sys.path[0], which python -I may point at the stdlib zip. | src: p:18488f2c32d61514:L-003; a Monte Carlo run failed on sys.path[0] under python -I | 1 |

# Blockout / greybox in Unity

Greyboxing = blocking out a level with simple shapes to test whether the layout supports the
gameplay before final art. Goal: cheapest geometry that answers the playtest questions.

## Packages (Unity 6.3 LTS; verify versions in Package Manager)
| Package | Id | Use |
|---|---|---|
| ProBuilder 6.x | `com.unity.probuilder` | in-scene modelling, greybox, collision meshes |
| Splines 2.x | `com.unity.splines` | paths: roads, rails, rivers, patrol/camera paths, prefab scatter |
| Terrain + Terrain Tools | built-in + `com.unity.terrain-tools` | outdoor heightmaps, sculpt/erosion |
| AI Navigation 2.x | `com.unity.ai.navigation` | NavMeshSurface/Modifier/Link for AI and reachability checks |
| Polybrush | `com.unity.polybrush` | vertex paint/sculpt/scatter on meshes (optional) |
| FBX Exporter | `com.unity.formats.fbx` | export greybox to DCC for art (optional) |

## Project setup
- Folder: `Assets/_Project/Levels/<LevelId>/` with `Greybox/`, `Gameplay/`, `Lighting/`.
- Split each level into additive scenes: `<Id>_Geo` (geometry), `<Id>_Gameplay` (spawns,
  triggers, checkpoints, encounters), `<Id>_Light` — parallel work, fewer merge conflicts.
  Use UnityYAMLMerge (Smart Merge) and file locking (Unity Version Control or Git LFS locks)
  for scenes/prefabs (see `stack-unity` skill for VCS setup).
- Grid: Unity's built-in grid snapping (Grid and Snap overlay; hold Ctrl/Cmd to increment-snap).
  Choose base unit 1 m (or 0.5 m for fine detail); kit pieces multiples of it.
- Greybox materials (one palette, used game-wide): e.g. floor = mid grey, wall = light grey,
  walkable/climbable affordance = yellow, interactable = blue, hazard = red, out-of-bounds =
  black, objective = green. Use a metre-checker/grid texture so scale reads in screenshots.

## ProBuilder workflow
1. Shape tool: boxes/stairs/arches/cylinders at metric sizes; Poly Shape for floor plans.
2. Edit faces/edges: extrude (Shift-drag), inset, bevel, connect, subdivide; merge objects
   per room to keep hierarchy readable.
3. Stairs/ramps sized from `LevelMetrics` (step 0.1–0.15 m; slope ≤ controller slope limit).
4. Mark trigger/collider volumes with ProBuilder "Set Trigger"/"Set Collider" actions.
5. "ProBuilderize" converts imported meshes for edits; export OBJ/FBX for art reference.
- ProBuilder meshes are unique per object; for production or mobile perf checks, replace with
  kit prefabs or combine + mark static (batching/occlusion) — don't ship hundreds of unique meshes.

## Prefab kit (preferred for modular/indoor and mobile)
- Pieces on a 1/2/4 m module: wall straight/corner/T/end, doorway, window, floor tiles,
  stairs, ramp, platforms (low/high cover heights), pillars, railing.
- Pivot at a grid corner at floor level; consistent forward axis; collider on prefab.
- Prefab Variants for themes; art replaces mesh in the base prefab → level updates in place.
- Kit sizes live in the metrics doc; level designers never scale kit pieces non-uniformly.

## Splines 2.x
- `SplineContainer` holds one or more splines (Bezier knots edited in Scene view).
- `SplineExtrude`: tube/road/pipe mesh along a spline (greybox roads, rails, rivers).
- `SplineInstantiate`: place prefabs along a spline (fences, lamp posts, cover rows, coins in
  runners). `SplineAnimate`: move objects (platforms, cameras, patrols) along a path.
- Use for runner/racing tracks: author track as spline, sample for length/curvature to
  check speed metrics (turn radius vs max speed).

## Terrain
- Set heightmap resolution and terrain size early (scale changes distort sculpts); paint
  layers as colour-coded zones in greybox; use Terrain Holes for caves/entrances.
- Check walkability with NavMesh bake (slope limit) and with the player controller.
- Mobile: Unity Terrain cost (draw calls, splat layers) can be high on low-end devices —
  validate with technical-artist; consider mesh terrain (verify on target device).

## Navigation & reachability
- Add `NavMeshSurface` per level geometry root; bake; `NavMeshLink` for jumps/drops;
  `NavMeshModifier` to exclude areas. Unreachable islands = layout bug or intended gate.
- Use a bot/agent walk of the critical path to measure time and catch blocked routes.

## Gameplay markup (in `<Id>_Gameplay` scene)
- Player start, checkpoints, spawn points (named `SP_<area>_<n>`), trigger volumes
  (`TRG_<purpose>`), encounter roots, pickups, kill volumes under the level.
- Gizmos/labels for designer intent (sightline cones, intended jump arcs).
- Request from unity-developer: checkpoint/respawn component, trigger → event component,
  debug teleport menu, position/death telemetry hook.

## Instrumentation for playtests
- Log `player_pos` every 1–2 s, `death{pos, cause}`, `checkpoint_reached`, `level_quit{pos}`,
  `stuck` (no progress > N s). Render heatmaps (data-analyst or editor tool).
- Record playtest video with input overlay where possible.

## Greybox → art handoff
- Gate: playtest sign-off on flow, metrics, encounter/puzzle readability.
- Deliver: level doc, top-down map with landmark list and moods per district, kit usage,
  collision notes (keep greybox collision or simplified), perf targets per area (draw
  calls/triangles from `85-tech-constraints.md`), "do-not-change" metric list.
- Art must keep footprint, collision and sightlines; changes to those go back to level-designer.

## Sources
- Unity Manual, ProBuilder (Unity 6.3 LTS) https://docs.unity3d.com/Manual/com.unity.probuilder.html
- Unity Learn, "Editing with ProBuilder" https://learn.unity.com/course/ai-ml-curricular-framework-resources/tutorial/editing-with-probuilder
- Unity Splines API (2.7) https://docs.unity3d.com/Packages/com.unity.splines@2.7/api/UnityEngine.Splines.html
- Unity AI Navigation package https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html (verify: latest 2.x)
- The Level Design Book, "Blockout" https://book.leveldesignbook.com/process/blockout
- Unity Manual, Smart Merge https://docs.unity3d.com/Manual/SmartMerge.html

# Phase 1.2a — ROS-independent metric map core

## Workflow contract

`ak-research → ak-brainstorm → ak-plan (--tdd semantics) → ak-cook → ak-debug/fix → ak-test → ak-code-review → review`

Uploaded skill packages are used as workflow contracts. Native AgentKit CLI execution is not claimed.

## Outcome

Create a deterministic, ROS-independent C++17 map-core layer for synthetic metric geometry, with a ROS 2 Jazzy packaging/test path and an independent sanitizer build path.

## Constraints

- Metric coordinates only (`*_m` identifiers); no longitude/latitude degree semantics in the public map-core API.
- Preserve the pinned legacy `MapService::distance` saturation behavior and Voronoi-field formula for synthetic fixtures.
- Do not fabricate or replace the missing `outside_ny_updated` legacy SQLite datasets.
- Do not change planner, controller, COLAV, Nav2 mission behavior, or vehicle actuation logic in this phase.

## Non-goals

- Real ENC/GDAL adapter.
- Real-map semantic parity.
- Planner migration or tuning.
- Runtime mission execution.

## TDD acceptance gates

| Gate | Acceptance |
|---|---|
| M12-01 | Public map-core headers contain no ROS API dependency. |
| M12-02 | Public geometry/distance API uses explicit metre identifiers. |
| M12-03 | Quadtree fixtures are deterministic. |
| M12-04 | Split-boundary/straddling objects are never lost and outside queries fail closed. |
| M12-05 | Collision intersection and saturated distance fixtures pass. |
| M12-06 | Synthetic Voronoi fixture matches the pinned legacy formula. |
| M12-07 | Standalone AddressSanitizer + UndefinedBehaviorSanitizer run passes. |
| M12-08 | Same core sources compile/run without ROS. |
| M12-09 | ROS 2 Jazzy `colcon build` + `colcon test` passes. |
| M12-10 | `BLOCKED_PENDING_LEGACY_ASSET` until original real-map SQLite assets are recovered. |

## Architecture

```text
Point2dM / AabbM / Segment2dM
             |
      +------+------+
      |             |
  Quadtree      SyntheticMap
                    |
                 MapQuery
                    |
       future Phase 1.2b adapter
```

The synthetic implementation deliberately avoids GDAL/GEOS. Phase 1.2b may adapt verified GDAL geometries into this metric contract without changing the core tests.

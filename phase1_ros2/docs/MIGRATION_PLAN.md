# Migration plan and acceptance gates

## P1.1 usv_model_core
Acceptance: deterministic C++ tests; zero-state equilibrium; finite integration; parameters explicitly typed.

## P1.2 usv_geodesy
Acceptance: WGS84→ENU→WGS84 round-trip tests; no degree-valued data in metric message contracts.

## P1.3 usv_map_core
Acceptance: all distance APIs are suffixed `_m`; no latitude/longitude envelope arithmetic for metric thresholds.

## P1.4 Hybrid A* core
Acceptance: legacy golden scenarios compared by path feasibility, length, clearance, node count and timing; known Quadtree defect must first have a deterministic regression fixture.

## P1.5 Nav2 adapter
Acceptance: plugin loads through pluginlib and returns `nav_msgs/Path`; algorithm remains isolated from Nav2 lifecycle/costmap orchestration.

No phase may claim parity solely because it compiles.

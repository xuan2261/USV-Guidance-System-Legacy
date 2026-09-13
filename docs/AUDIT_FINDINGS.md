# Phase 0 audit findings

## P0
- ROS Noetic is EOL; use only as a frozen legacy baseline.
- Geographic lon/lat values are mixed with local metric frame semantics in ROS messages.
- Upstream Hybrid A* source explicitly documents a rare fundamental Quadtree-builder failure.
- Original Dockerfile contains hard-coded passwords and a stale `usv_motion_planning` source path.

## P1
- LOS initializes `current_waypoint` as an empty Pose while first-waypoint logic checks for None.
- COLAV debug obstacle pose storage is initialized to four entries and indexed by obstacle ID.
- Dubins turning radius is hard-coded to 9.
- `usv_model` dependency declaration is incomplete relative to public headers.

## Recovery rule
Capture these as golden/regression cases before semantic fixes. Phase 1 should normalize internal navigation to local ENU meters and isolate WGS84 conversion at I/O boundaries.

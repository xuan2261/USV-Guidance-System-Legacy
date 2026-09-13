# Phase 1.1 build contract

Scope is intentionally limited to three non-operational core packages:

1. `usv_model_core` — standard-library-only 3-DOF dynamics and fixed RK4 compatibility path.
2. `usv_geodesy` — GeographicLib-backed WGS84 ↔ local ENU conversion.
3. `usv_map_core` — metric query interfaces only.

The Nav2 Hybrid A* adapter is **excluded** from Phase 1.1 build qualification.

## Required gates

- P11-01: ROS 2 Jazzy environment identified.
- P11-02: rosdep resolves selected package dependencies.
- P11-03: `colcon build` succeeds with `BUILD_TESTING=ON`.
- P11-04: `colcon test` and `colcon test-result` succeed.
- P11-05: equation-level model differential regression passes.
- P11-06: paired trajectory CSV comparison passes.
- P11-07: independent geodesy fixtures pass.

A Phase 1.1 PASS does **not** imply ROS1↔ROS2 system parity. That claim remains blocked until legacy Q10 closes.

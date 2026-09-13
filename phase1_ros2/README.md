# Phase 1 ROS 2 scaffold — v0.5

This directory now contains a build-ready **Phase 1.1 core** while preserving the Q10 guard against premature ROS1↔ROS2 parity claims.

## Selected baseline
- Ubuntu 24.04 Noble
- ROS 2 Jazzy
- Gazebo Harmonic
- VRX v3.1.0 / `jazzy` branch
- Nav2 Jazzy plugin API

## Phase 1.1 packages
1. `usv_model_core` — standard-library-only 3-DOF dynamics with legacy-compatible heading semantics by default.
2. `usv_geodesy` — WGS84 ↔ local ENU metric conversion using GeographicLib.
3. `usv_map_core` — metric maritime-map query contracts.

The `usv_nav2_hybrid_planner` package remains a guarded compile-time shell and is excluded from Phase 1.1 qualification.

## One-command Phase 1.1 build/test on Windows
```bat
RUN_PHASE11.cmd
```
Return artifact:
```text
PHASE11_RETURN.zip
```

## Pure differential regression without ROS 2
```bash
./scripts/run_phase1_regression.sh
```
This performs equation-level dynamics comparison, paired trajectory CSV comparison and independent geodesy fixture generation. If Jazzy/colcon exists locally, it also runs selected package build/tests.

## Parity guard
A Phase 1.1 PASS proves that the extracted core builds and passes its defined tests in Jazzy. It does **not** prove whole-system equivalence with ROS1. That remains blocked until legacy Q10 closes.

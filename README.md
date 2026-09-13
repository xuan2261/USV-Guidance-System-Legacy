# USV Guidance System — Legacy Recovery / Qualification Harness v0.6

Purpose: reproduce and characterize the pinned 2022 ROS 1 navigation/simulation research stack, always return failure evidence, and provide a **build-ready but parity-guarded** ROS 2 Jazzy Phase 1.1 core kit.

## Locked legacy upstream
- `sanderfu/USV-Guidance-System`
- commit `c930b938302d8cfe8c378dfa69748a33d3d76459` (2022-06-05)

## Legacy qualification on Windows
```bat
PRECHECK.cmd
RUN_ALL.cmd
```
Send back `QUALIFICATION_RETURN.zip` even when the run fails.

## Phase 1.1 core build on Windows
This is now a separate one-command harness:
```bat
cd phase1_ros2
RUN_PHASE11.cmd
```
It qualifies only:
- `usv_model_core`
- `usv_geodesy`
- `usv_map_core`

It always attempts to create `phase1_ros2/PHASE11_RETURN.zip`.

## v0.6 additions
- Phase 1.1 Jazzy Docker harness based on `ros:jazzy-ros-base-noble`.
- Runtime capture of the full pulled Docker RepoDigest.
- `rosdep → colcon build → colcon test → colcon test-result` evidence pipeline.
- `usv_model_core` now uses only the C++ standard library; unused Eigen/Boost dependencies were removed.
- Legacy final-state GTest fixtures for six dynamics scenarios.
- Paired trajectory CSV export and independent CSV comparator with explicit schema/units/tolerance.
- GeographicLib-backed geodesy package retains independent WGS84→ENU numeric fixtures.
- Phase 1.1 PASS remains explicitly `BLOCKED_PENDING_LEGACY_Q10` for system-parity claims.

## Safe scope
This recovery line is limited to navigation, vessel dynamics, geodesy, collision-avoidance infrastructure, simulation safety and reproducibility. It does not add target-interception, impact, or weapon functionality.

## GitHub Actions (v0.6)

Yes — the qualification lanes can now run on GitHub-hosted Actions. See `docs/GITHUB_ACTIONS.md` and `.github/workflows/`. Recommended order: static audit → Phase 1.1 ROS 2 → legacy `runtime_mode=none` → legacy `runtime_mode=smoke`. Both runtime workflows upload evidence bundles even on failure.
# USV-Guidance-System-Legacy

# Phase 1 differential regression — v0.4

## Goal
Reduce migration uncertainty before porting map/planner code by proving that the standalone vessel dynamics and coordinate contracts are understood and testable.

## Model result in artifact-build environment
- Reference source: pinned legacy commit `c930b938302d8cfe8c378dfa69748a33d3d76459`.
- Fixed-step RK4: 0.1 s.
- Scenarios: equilibrium, surge step, yaw step, combined state, wrap crossing, exact pi boundary.
- Result: PASS at equation level for `LegacyCompatible` policy.
- Exact pi is a semantic boundary: modern normalized remainder may choose the opposite turn sign. This behavior is now explicit via `HeadingPolicy` rather than hidden in an implementation detail.

## Geodesy result
Independent WGS84 ECEF→ENU fixtures pass locally. They are used as external numeric expectations for `GeographicLib::LocalCartesian` tests when the Jazzy environment is available.

## Not claimed
- No ROS1 runtime mission parity without `QUALIFICATION_RETURN.zip`.
- No Nav2 Hybrid A* parity.
- No VRX runtime parity.
- No weaponized or target-impact behavior is included.

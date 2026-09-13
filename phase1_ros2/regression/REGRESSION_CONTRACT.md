# Differential regression contract

Scope: benign USV dynamics / navigation infrastructure only.

The legacy reference is tied to `sanderfu/USV-Guidance-System` commit
`c930b938302d8cfe8c378dfa69748a33d3d76459`, file
`usv_model/src/model_library.cpp`.

## State
`[x_m, y_m, yaw_rad, u_mps, v_mps, r_radps]`

## Command
`[surge_mps, yaw_rad]`

## Comparison
- x/y/u/v/r: absolute error <= `1e-9` for the pure-equation fixed-RK4 comparison.
- yaw: compare both raw yaw and canonical yaw. Canonical yaw uses `atan2(sin(yaw),cos(yaw))`.
- exact ±pi is a named semantic boundary. A `LegacyCompatible` heading policy must preserve the original turn-sign. A modern normalized policy is allowed to differ only when explicitly selected and must be reported as a semantic change.

## Important limitation
This regression reproduces the legacy equations and fixed-step RK4 semantics in a ROS-independent reference. It does not replace the still-required ROS1 runtime qualification / golden mission evidence.

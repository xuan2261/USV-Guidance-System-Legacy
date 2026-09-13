# Web evidence refresh — v0.5 — 2026-09-13

- ROS Docker Official Image currently lists `jazzy-ros-base-noble` for Ubuntu Noble; runtime wrapper records full RepoDigest rather than treating the short web digest prefix as a full lock.
- ROS 2 Jazzy documentation supports `ament_cmake_gtest` for CMake GTest integration and `rosdep install --from-paths ... --ignore-src` for package dependencies.
- Nav2 Jazzy custom planners inherit `nav2_core::GlobalPlanner`, implement configure/activate/deactivate/cleanup/createPlan, and export via pluginlib. The guarded adapter remains excluded from Phase 1.1.
- `ros_gz` documents Jazzy ↔ Harmonic as a binary-supported pairing.

These facts are used for build/package structure only; no operational Hybrid A* parity is claimed in v0.5.

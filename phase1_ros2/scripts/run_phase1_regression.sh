#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/regression/out"
mkdir -p "$OUT"
status=0
python3 "$ROOT/regression/run_model_regression.py" > "$OUT/model_regression_console.log" 2>&1 || status=1
python3 "$ROOT/regression/export_trajectory_csv.py" > "$OUT/trajectory_export.log" 2>&1 || status=1
python3 "$ROOT/regression/compare_trajectory_csv.py" > "$OUT/trajectory_compare.log" 2>&1 || status=1
python3 "$ROOT/regression/geodesy_reference.py" > "$OUT/geodesy_reference_report.json" 2>&1 || status=1
if command -v colcon >/dev/null 2>&1 && [ -f /opt/ros/jazzy/setup.bash ]; then
  set +u; source /opt/ros/jazzy/setup.bash; set -u
  cd "$ROOT/ros2_ws"
  colcon build --symlink-install --packages-select usv_model_core usv_geodesy usv_map_core > "$OUT/colcon_build.log" 2>&1 || status=1
  if [ -f install/setup.bash ]; then
    set +u; source install/setup.bash; set -u
    colcon test --packages-select usv_model_core usv_geodesy usv_map_core > "$OUT/colcon_test.log" 2>&1 || status=1
    colcon test-result --verbose > "$OUT/colcon_test_result.log" 2>&1 || status=1
  fi
else
  printf '%s\n' 'SKIP: ROS 2 Jazzy/colcon unavailable; pure regression still executed.' > "$OUT/colcon_skipped.txt"
fi
exit "$status"

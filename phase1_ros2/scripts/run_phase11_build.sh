#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="$ROOT/ros2_ws"
OUT="$ROOT/phase11_out"
mkdir -p "$OUT"
status=0

json_status() {
  python3 - "$1" "$2" "$3" <<'PY'
import json,sys,datetime
path,status,detail=sys.argv[1:]
with open(path,'w') as f:
    json.dump({'status':status,'detail':detail,'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},f,indent=2)
    f.write('\n')
PY
}

{
  echo "ROS_DISTRO=${ROS_DISTRO:-}"
  echo "ROS_VERSION=${ROS_VERSION:-}"
  uname -a
  g++ --version | head -1
  cmake --version | head -1
  colcon version-check 2>/dev/null || true
  dpkg-query -W -f='GeographicLib ${Version}\n' libgeographiclib-dev 2>/dev/null || true
} > "$OUT/environment.txt" 2>&1

set +u
source /opt/ros/jazzy/setup.bash
set -u

python3 "$ROOT/scripts/verify_scaffold.py" "$ROOT" > "$OUT/scaffold_static.json" 2>&1 || status=1
bash "$ROOT/scripts/run_phase1_regression.sh" > "$OUT/pure_regression.log" 2>&1 || status=1

cd "$WS"
if [ "${USV_KEEP_BUILD_TREE:-0}" != "1" ]; then
  rm -rf build install log
fi

rosdep update > "$OUT/rosdep_update.log" 2>&1 || true
rosdep install --from-paths \
  src/usv_model_core src/usv_geodesy src/usv_map_core \
  --ignore-src -r -y > "$OUT/rosdep_install.log" 2>&1
rc=$?; [ $rc -eq 0 ] || status=1
json_status "$OUT/rosdep.json" "$([ $rc -eq 0 ] && echo PASS || echo FAIL)" "rc=$rc"

colcon build --event-handlers console_direct+ \
  --packages-select usv_model_core usv_geodesy usv_map_core \
  --cmake-args -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  > "$OUT/colcon_build.log" 2>&1
rc=$?; [ $rc -eq 0 ] || status=1
json_status "$OUT/build.json" "$([ $rc -eq 0 ] && echo PASS || echo FAIL)" "rc=$rc"

if [ $rc -eq 0 ]; then
  set +u
  source install/setup.bash
  set -u
  colcon test --event-handlers console_direct+ \
    --packages-select usv_model_core usv_geodesy usv_map_core \
    > "$OUT/colcon_test.log" 2>&1
  trc=$?; [ $trc -eq 0 ] || status=1
  colcon test-result --verbose > "$OUT/colcon_test_result.log" 2>&1
  rrc=$?; [ $rrc -eq 0 ] || status=1
  json_status "$OUT/tests.json" "$([ $trc -eq 0 ] && [ $rrc -eq 0 ] && echo PASS || echo FAIL)" "test_rc=$trc test_result_rc=$rrc"
else
  json_status "$OUT/tests.json" SKIP "build failed"
fi

python3 "$ROOT/scripts/make_phase11_report.py" "$OUT" || status=1
exit "$status"

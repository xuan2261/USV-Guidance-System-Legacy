#!/usr/bin/env bash
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS="$ROOT/ros2_ws"
PKG="$WS/src/usv_map_core"
OUT="$ROOT/phase12_out"
mkdir -p "$OUT"
status=0
json_status() {
  python3 - "$1" "$2" "$3" <<'PY'
import datetime, json, sys
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
} > "$OUT/environment.txt" 2>&1
python3 "$ROOT/scripts/verify_phase12_map_core.py" "$ROOT" > "$OUT/static_contract.json" 2>&1
src_rc=$?
[ $src_rc -eq 0 ] || status=1
set +e
g++ -std=c++17 -O1 -g -Wall -Wextra -Wpedantic \
  -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all \
  -I"$PKG/include" "$PKG/src/quadtree.cpp" "$PKG/src/synthetic_map.cpp" \
  "$ROOT/regression/map_core_standalone_smoke.cpp" -o "$OUT/map_core_standalone_smoke" \
  > "$OUT/standalone_compile.log" 2>&1
compile_rc=$?
if [ $compile_rc -eq 0 ]; then
  ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1 \
    "$OUT/map_core_standalone_smoke" > "$OUT/standalone_run.log" 2>&1
  run_rc=$?
else
  run_rc=99
fi
set -e
if [ $compile_rc -eq 0 ] && [ $run_rc -eq 0 ]; then
  json_status "$OUT/standalone_sanitizer.json" PASS "compile_rc=$compile_rc run_rc=$run_rc"
else
  json_status "$OUT/standalone_sanitizer.json" FAIL "compile_rc=$compile_rc run_rc=$run_rc"
  status=1
fi
set +u
source /opt/ros/jazzy/setup.bash
set -u
cd "$WS"
rm -rf build install log
rosdep update > "$OUT/rosdep_update.log" 2>&1 || true
rosdep install --from-paths src/usv_map_core --ignore-src -r -y > "$OUT/rosdep_install.log" 2>&1
rc=$?; [ $rc -eq 0 ] || status=1
json_status "$OUT/rosdep.json" "$([ $rc -eq 0 ] && echo PASS || echo FAIL)" "rc=$rc"
colcon build --event-handlers console_direct+ --packages-select usv_map_core \
  --cmake-args -DBUILD_TESTING=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo > "$OUT/colcon_build.log" 2>&1
rc=$?; [ $rc -eq 0 ] || status=1
json_status "$OUT/build.json" "$([ $rc -eq 0 ] && echo PASS || echo FAIL)" "rc=$rc"
if [ $rc -eq 0 ]; then
  set +u; source install/setup.bash; set -u
  colcon test --event-handlers console_direct+ --packages-select usv_map_core > "$OUT/colcon_test.log" 2>&1
  trc=$?
  colcon test-result --verbose > "$OUT/colcon_test_result.log" 2>&1
  rrc=$?
  [ $trc -eq 0 ] && [ $rrc -eq 0 ] || status=1
  json_status "$OUT/tests.json" "$([ $trc -eq 0 ] && [ $rrc -eq 0 ] && echo PASS || echo FAIL)" "test_rc=$trc test_result_rc=$rrc"
else
  json_status "$OUT/tests.json" SKIP "build failed"
fi
python3 "$ROOT/scripts/make_phase12_report.py" "$OUT" || status=1
exit "$status"

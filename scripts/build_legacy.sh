#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"
mkdir -p "$RET/logs"; source /opt/ros/noetic/setup.bash; cd "$WS"

# Debian/Ubuntu GeographicLib development packages may install
# FindGeographicLib.cmake outside CMake's default module search path. Discover
# the module from the package database and pass it workspace-wide instead of
# modifying the pinned upstream source tree.
GEO_FIND="$(dpkg -L libgeographic-dev libgeographiclib-dev 2>/dev/null | grep '/FindGeographicLib\.cmake$' | head -n1 || true)"
GEO_MODULE_DIR=""
if [[ -n "$GEO_FIND" ]]; then GEO_MODULE_DIR="$(dirname "$GEO_FIND")"; fi
python3 - "$RET/geographiclib_discovery.json" "$GEO_FIND" "$GEO_MODULE_DIR" <<'PY'
import json,sys
find_path,module_dir=sys.argv[2:]
with open(sys.argv[1],'w') as f:
    json.dump({'status':'PASS' if find_path and module_dir else 'FAIL',
               'find_module':find_path or None,
               'cmake_module_path':module_dir or None},f,indent=2); f.write('\n')
PY

set +e
rosdep install --from-paths src --ignore-src -r -y 2>&1 | tee "$RET/logs/rosdep.log"; ROSDEP_RC=${PIPESTATUS[0]}
CMAKE_ARGS=(-DCMAKE_BUILD_TYPE=RelWithDebInfo)
if [[ -n "$GEO_MODULE_DIR" ]]; then CMAKE_ARGS+=("-DCMAKE_MODULE_PATH=$GEO_MODULE_DIR"); fi
catkin config --extend /opt/ros/noetic --cmake-args "${CMAKE_ARGS[@]}" 2>&1 | tee "$RET/logs/catkin-config.log"; CONFIG_RC=${PIPESTATUS[0]}
catkin build --no-status 2>&1 | tee "$RET/logs/catkin-build.log"; BUILD_RC=${PIPESTATUS[0]}
set -e
python3 - "$RET/build.json" "$ROSDEP_RC" "$CONFIG_RC" "$BUILD_RC" "$GEO_MODULE_DIR" <<'PY'
import json,sys
out=sys.argv[1]; rr,cr,br=map(int,sys.argv[2:5]); geo=sys.argv[5]
with open(out,'w') as f:
    json.dump({'status':'PASS' if br==0 and cr==0 else 'FAIL',
               'rosdep_rc':rr,'catkin_config_rc':cr,'catkin_build_rc':br,
               'geographiclib_module_path':geo or None},f,indent=2); f.write('\n')
PY
exit "$BUILD_RC"

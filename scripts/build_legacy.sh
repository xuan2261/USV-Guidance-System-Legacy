#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"
mkdir -p "$RET/logs"; source /opt/ros/noetic/setup.bash; cd "$WS"
set +e
rosdep install --from-paths src --ignore-src -r -y 2>&1 | tee "$RET/logs/rosdep.log"; ROSDEP_RC=${PIPESTATUS[0]}
catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=RelWithDebInfo 2>&1 | tee "$RET/logs/catkin-config.log"; CONFIG_RC=${PIPESTATUS[0]}
catkin build --no-status 2>&1 | tee "$RET/logs/catkin-build.log"; BUILD_RC=${PIPESTATUS[0]}
set -e
python3 - "$RET/build.json" "$ROSDEP_RC" "$CONFIG_RC" "$BUILD_RC" <<'PY'
import json,sys
out=sys.argv[1]; rr,cr,br=map(int,sys.argv[2:]); status='PASS' if br==0 and cr==0 else 'FAIL'
with open(out,'w') as f: json.dump({'status':status,'rosdep_rc':rr,'catkin_config_rc':cr,'catkin_build_rc':br},f,indent=2); f.write('\n')
PY
exit "$BUILD_RC"

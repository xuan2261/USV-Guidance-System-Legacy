#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"; MODE="${3:-${RUNTIME_MODE:-smoke}}"
mkdir -p "$RET/scenarios" "$RET/logs"; source /opt/ros/noetic/setup.bash; [[ -f "$WS/devel/setup.bash" ]] && source "$WS/devel/setup.bash"
case "$MODE" in
  none) exit 0 ;;
  smoke) scenarios=("full_mission_test.launch") ;;
  all) scenarios=("full_mission_test.launch" "ny_mission.launch" "ryfylke_mission.launch" "tss_mission.launch" "test_dubin.launch" "test_quadtree.launch") ;;
  *) echo "Invalid runtime mode: $MODE" >&2; exit 2 ;;
esac
for file in "${scenarios[@]}"; do
  id="${file%.launch}"; log="$RET/scenarios/${id}.log"; js="$RET/scenarios/${id}.json"; start=$(date +%s)
  set +e
  timeout --signal=INT --kill-after=10s 180s roslaunch usv_mission_planner "$file" >"$log" 2>&1; rc=$?
  set -e
  end=$(date +%s); elapsed=$((end-start))
  if [[ $rc -eq 0 ]]; then status=PASS; elif [[ $rc -eq 124 || $rc -eq 137 ]]; then status=TIMEOUT; else status=FAIL; fi
  python3 - "$js" "$id" "$status" "$rc" "$elapsed" <<'PY'
import json,sys
out,i,s,r,e=sys.argv[1:]
with open(out,'w') as f: json.dump({'scenario':i,'status':s,'rc':int(r),'elapsed_s':int(e)},f,indent=2); f.write('\n')
PY
done

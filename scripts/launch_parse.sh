#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"
mkdir -p "$RET/logs"; source /opt/ros/noetic/setup.bash; [[ -f "$WS/devel/setup.bash" ]] && source "$WS/devel/setup.bash"
scenarios=(
  "usv_mission_planner full_mission_test.launch"
  "usv_mission_planner ny_mission.launch"
  "usv_mission_planner ryfylke_mission.launch"
  "usv_mission_planner tss_mission.launch"
  "usv_mission_planner test_dubin.launch"
  "usv_mission_planner test_quadtree.launch"
)
TMP="$RET/.launch_parse.tsv"; : > "$TMP"
for spec in "${scenarios[@]}"; do
  pkg="${spec%% *}"; file="${spec#* }"; id="${file%.launch}"
  set +e
  timeout 20s roslaunch --nodes "$pkg" "$file" >"$RET/logs/launch-${id}.log" 2>&1; rc=$?
  set -e
  [[ $rc -eq 0 ]] && status=PASS || status=FAIL
  printf '%s\t%s\t%s\n' "$id" "$status" "$rc" >> "$TMP"
done
python3 - "$TMP" "$RET/launch_parse.json" <<'PY'
import json,sys
rows=[]
for line in open(sys.argv[1]):
    i,s,r=line.rstrip('\n').split('\t'); rows.append({'scenario':i,'status':s,'rc':int(r)})
with open(sys.argv[2],'w') as f: json.dump({'status':'PASS' if all(x['status']=='PASS' for x in rows) else 'FAIL','scenarios':rows},f,indent=2); f.write('\n')
PY

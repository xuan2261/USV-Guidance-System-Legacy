#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"; MODE="${3:-${RUNTIME_MODE:-smoke}}"; HARNESS="${HARNESS_ROOT:-/harness}"
mkdir -p "$RET/scenarios" "$RET/logs"; source /opt/ros/noetic/setup.bash; [[ -f "$WS/devel/setup.bash" ]] && source "$WS/devel/setup.bash"
case "$MODE" in
  none) exit 0 ;;
  smoke) scenarios=("full_mission_test.launch") ;;
  all) scenarios=("full_mission_test.launch" "ny_mission.launch" "ryfylke_mission.launch" "tss_mission.launch" "test_dubin.launch" "test_quadtree.launch") ;;
  *) echo "Invalid runtime mode: $MODE" >&2; exit 2 ;;
esac
for file in "${scenarios[@]}"; do
  id="${file%.launch}"; log="$RET/scenarios/${id}.log"; js="$RET/scenarios/${id}.json"; start=$(date +%s)

  # Resolve launch parameters before runtime so missing non-versioned map assets
  # are reported explicitly instead of surfacing later as a planner SIGSEGV/time-out.
  params_file="$(mktemp)"
  set +e
  roslaunch --dump-params usv_mission_planner "$file" >"$params_file" 2>"$RET/logs/${id}_dump_params.log"
  dump_rc=$?
  set -e
  map_info="$(python3 - "$params_file" <<'PY'
import sys, yaml
p=sys.argv[1]
try:
    data=yaml.safe_load(open(p).read()) or {}
except Exception:
    data={}
name=''
preprocessed=''
for k,v in data.items():
    key=str(k).rstrip('/')
    if key.endswith('/map_name') or key=='map_name':
        name=str(v)
    elif key.endswith('/preprocessed_map') or key=='preprocessed_map':
        preprocessed=str(v).lower()
print(name+'\t'+preprocessed)
PY
)"
  rm -f "$params_file"
  IFS=$'\t' read -r map_name preprocessed_map <<<"$map_info"

  if [[ $dump_rc -eq 0 && -n "$map_name" && "$preprocessed_map" == "true" ]]; then
    asset_json="$RET/scenarios/${id}_assets.json"
    set +e
    python3 "$HARNESS/scripts/validate_runtime_assets.py" \
      --workspace "$WS" --scenario "$id" --map-name "$map_name" --out "$asset_json"
    asset_rc=$?
    set -e
    if [[ $asset_rc -eq 42 ]]; then
      python3 - "$js" "$id" "$asset_json" <<'PY'
import json,sys,os
out,i,asset=sys.argv[1:]
with open(out,'w') as f:
    json.dump({'scenario':i,'status':'BLOCKED_DATA_MISSING','rc':42,'elapsed_s':0,'asset_evidence':os.path.basename(asset)},f,indent=2)
    f.write('\n')
PY
      continue
    elif [[ $asset_rc -ne 0 ]]; then
      python3 - "$js" "$id" "$asset_rc" <<'PY'
import json,sys
out,i,r=sys.argv[1:]
with open(out,'w') as f:
    json.dump({'scenario':i,'status':'PREFLIGHT_ERROR','rc':int(r),'elapsed_s':0},f,indent=2)
    f.write('\n')
PY
      continue
    fi
  fi

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

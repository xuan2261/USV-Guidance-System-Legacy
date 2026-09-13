#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"
mkdir -p "$RET/logs"; source /opt/ros/noetic/setup.bash; [[ -f "$WS/devel/setup.bash" ]] && source "$WS/devel/setup.bash"; cd "$WS"
set +e
catkin run_tests 2>&1 | tee "$RET/logs/catkin-run-tests.log"; TEST_RC=${PIPESTATUS[0]}
catkin_test_results --verbose 2>&1 | tee "$RET/logs/catkin-test-results.log"; RESULT_RC=${PIPESTATUS[0]}
set -e
python3 - "$RET/tests.json" "$TEST_RC" "$RESULT_RC" <<'PY'
import json,sys
out=sys.argv[1]; tr=int(sys.argv[2]); rr=int(sys.argv[3])
with open(out,'w') as f: json.dump({'status':'PASS' if tr==0 and rr==0 else 'FAIL','catkin_run_tests_rc':tr,'catkin_test_results_rc':rr},f,indent=2); f.write('\n')
PY
exit "$RESULT_RC"

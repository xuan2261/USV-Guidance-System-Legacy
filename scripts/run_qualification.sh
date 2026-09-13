#!/usr/bin/env bash
set -uo pipefail
WS="${1:-/workspace}"; RET="${2:-/return}"; MODE="${RUNTIME_MODE:-smoke}"
export HARNESS_ROOT=/harness RETURN_DIR="$RET"
mkdir -p "$WS" "$RET/logs" "$RET/scenarios"; exec > >(tee "$RET/logs/qualification.log") 2>&1
echo "Qualification started: $(date -u +%FT%TZ)"; echo "Runtime mode: $MODE"
FETCH_RC=0; STATIC_RC=0; BUILD_RC=0; TEST_RC=0; PARSE_RC=0; SCENARIO_RC=0
bash /harness/scripts/fetch_legacy.sh "$WS" || FETCH_RC=$?
if [[ $FETCH_RC -eq 0 ]]; then
  python3 /harness/scripts/qualify_static.py "$WS/src/usv_guidance_system" --out "$RET/static_audit.json" || STATIC_RC=$?
  bash /harness/scripts/build_legacy.sh "$WS" "$RET" || BUILD_RC=$?
fi
if [[ $BUILD_RC -eq 0 && $FETCH_RC -eq 0 ]]; then
  bash /harness/scripts/run_tests.sh "$WS" "$RET" || TEST_RC=$?
  bash /harness/scripts/launch_parse.sh "$WS" "$RET" || PARSE_RC=$?
  bash /harness/scripts/run_scenarios.sh "$WS" "$RET" "$MODE" || SCENARIO_RC=$?
fi
python3 /harness/scripts/make_report.py "$RET"; REPORT_RC=$?
echo "Qualification finished: $(date -u +%FT%TZ)"; echo "Stage RCs fetch=$FETCH_RC static=$STATIC_RC build=$BUILD_RC tests=$TEST_RC parse=$PARSE_RC scenarios=$SCENARIO_RC report=$REPORT_RC"; exit "$REPORT_RC"

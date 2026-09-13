#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
validator = root / 'scripts' / 'validate_runtime_assets.py'
checks = []

def add(name, ok, detail=''):
    checks.append({'name': name, 'status': 'PASS' if ok else 'FAIL', 'detail': detail})

with tempfile.TemporaryDirectory() as td:
    ws = Path(td) / 'workspace'
    out = Path(td) / 'missing.json'
    cmd = [sys.executable, str(validator), '--workspace', str(ws), '--scenario', 'full_mission_test', '--map-name', 'outside_ny_updated', '--out', str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(out.read_text()) if out.exists() else {}
    add('missing_assets_blocked', r.returncode == 42 and data.get('status') == 'BLOCKED_DATA_MISSING' and len(data.get('missing', [])) == 2, (r.stdout + r.stderr)[-500:])

    mission = ws / 'src' / 'usv_guidance_system' / 'usv_map' / 'data' / 'mission_regions' / 'outside_ny_updated'
    mission.mkdir(parents=True, exist_ok=True)
    (mission / 'region.sqlite').write_bytes(b'fixture')
    (mission / 'region_detailed.sqlite').write_bytes(b'fixture')
    out2 = Path(td) / 'present.json'
    cmd[-1] = str(out2)
    r2 = subprocess.run(cmd, capture_output=True, text=True)
    data2 = json.loads(out2.read_text()) if out2.exists() else {}
    add('present_assets_pass', r2.returncode == 0 and data2.get('status') == 'PASS' and not data2.get('missing'), (r2.stdout + r2.stderr)[-500:])

run_scenarios = (root / 'scripts' / 'run_scenarios.sh').read_text()
add('scenario_runner_uses_preflight', 'validate_runtime_assets.py' in run_scenarios and 'BLOCKED_DATA_MISSING' in run_scenarios)

ok = all(x['status'] == 'PASS' for x in checks)
print(json.dumps({'status': 'PASS' if ok else 'FAIL', 'checks': checks}, indent=2))
raise SystemExit(0 if ok else 1)

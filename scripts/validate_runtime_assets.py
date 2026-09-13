#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--workspace', required=True)
p.add_argument('--scenario', required=True)
p.add_argument('--map-name', required=True)
p.add_argument('--out', required=True)
a = p.parse_args()

root = Path(a.workspace) / 'src' / 'usv_guidance_system' / 'usv_map' / 'data' / 'mission_regions' / a.map_name
required = [root / 'region.sqlite', root / 'region_detailed.sqlite']
missing = [str(x) for x in required if not x.is_file()]
status = 'PASS' if not missing else 'BLOCKED_DATA_MISSING'
result = {
    'scenario': a.scenario,
    'map_name': a.map_name,
    'status': status,
    'mission_region_dir': str(root),
    'required': [str(x) for x in required],
    'missing': missing,
    'note': 'Legacy upstream ignores generated data/ assets; qualification must not treat a missing mission-region dataset as an algorithm timeout.'
}
Path(a.out).parent.mkdir(parents=True, exist_ok=True)
Path(a.out).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
raise SystemExit(0 if status == 'PASS' else 42)

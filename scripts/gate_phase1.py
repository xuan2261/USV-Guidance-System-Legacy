#!/usr/bin/env python3
from pathlib import Path
import json, sys
p=Path(sys.argv[1] if len(sys.argv)>1 else 'qualification_return/gates.json')
try: g=json.loads(p.read_text())
except Exception as e:
    print(f'BLOCKED: cannot read {p}: {e}',file=sys.stderr); sys.exit(2)
if not g.get('ros2_migration_ready'):
    print('BLOCKED: Q10 is not PASS. Do not claim semantic ROS 2 migration validation yet.',file=sys.stderr); sys.exit(3)
print('PASS: Q10 is PASS; Phase 1 implementation may be compared against the golden baseline.')

#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, json, hashlib, tempfile, zipfile, shutil, sys

ap=argparse.ArgumentParser(description='Validate and triage a QUALIFICATION_RETURN bundle.')
ap.add_argument('input',help='QUALIFICATION_RETURN.zip or extracted qualification_return directory')
ap.add_argument('--out',default='',help='Optional output JSON path')
a=ap.parse_args(); src=Path(a.input).resolve(); tmp=None
if src.is_file():
    tmp=Path(tempfile.mkdtemp(prefix='usv_return_'))
    with zipfile.ZipFile(src) as z: z.extractall(tmp)
    root=tmp
else: root=src

def load(name):
    p=root/name
    try: return json.loads(p.read_text())
    except Exception: return None
required=['preflight.json','environment.json','docker_build.json']
checks=[]
for name in required: checks.append({'name':f'present:{name}','status':'PASS' if (root/name).exists() else 'FAIL'})
gates=load('gates.json')
if gates:
    checks.append({'name':'gates_parse','status':'PASS'})
    ready=bool(gates.get('ros2_migration_ready'))
    overall=gates.get('overall','UNKNOWN')
else:
    checks.append({'name':'gates_parse','status':'WARN'})
    ready=False; overall='NO_GATES'
err=load('harness_error.json')
if ready: next_action='PHASE1_ROS2_CORE_EXTRACTION'
elif err: next_action='FIX_HOST_OR_WRAPPER'
elif (root/'build.json').exists() and (load('build.json') or {}).get('status')!='PASS': next_action='FIX_LEGACY_BUILD'
elif (root/'source_identity.json').exists(): next_action='CLOSE_RUNTIME_GOLDEN_BASELINE'
else: next_action='FIX_FETCH_OR_ENVIRONMENT'
status='PASS' if all(x['status']!='FAIL' for x in checks) else 'FAIL'
result={'schema':'usv-qualification-return-audit/v1','status':status,'qualification_overall':overall,'ros2_migration_ready':ready,'next_action':next_action,'checks':checks}
out=Path(a.out) if a.out else (src.parent/'RETURN_AUDIT.json' if src.is_file() else src/'RETURN_AUDIT.json')
out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
if tmp: shutil.rmtree(tmp,ignore_errors=True)
sys.exit(0 if status=='PASS' else 2)

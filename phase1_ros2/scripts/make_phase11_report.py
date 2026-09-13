#!/usr/bin/env python3
from pathlib import Path
import json, sys, re
out=Path(sys.argv[1])
def load(name, default=None):
    p=out/name
    if not p.exists(): return default
    try: return json.loads(p.read_text())
    except Exception: return default
build=load('build.json',{}) or {}
tests=load('tests.json',{}) or {}
rosdep=load('rosdep.json',{}) or {}
model=load('../regression/out/MODEL_DIFFERENTIAL_REPORT.json',{}) or {}
geo=load('../regression/out/geodesy_reference_report.json',{}) or {}
# Regression reports live outside phase11_out; resolve from script root if absent.
root=Path(__file__).resolve().parents[1]
for key,path in [('model',root/'regression/out/MODEL_DIFFERENTIAL_REPORT.json'),('geo',root/'regression/out/geodesy_reference_report.json')]:
    try:
        data=json.loads(path.read_text())
    except Exception:
        data={}
    if key=='model': model=data
    else: geo=data
checks={
 'rosdep': rosdep.get('status','MISSING'),
 'colcon_build': build.get('status','MISSING'),
 'colcon_test': tests.get('status','MISSING'),
 'model_differential': model.get('status','MISSING'),
 'geodesy_reference': geo.get('status','MISSING'),
}
all_pass=all(v=='PASS' for v in checks.values())
report={
 'schema':'usv-phase11-report/v1',
 'status':'PASS' if all_pass else 'FAIL',
 'packages':['usv_model_core','usv_geodesy','usv_map_core'],
 'checks':checks,
 'parity_claim':'BLOCKED_PENDING_LEGACY_Q10',
 'next_action':'RUN_LEGACY_QUALIFICATION_AND_COMPARE' if all_pass else 'DEBUG_PHASE11_BUILD_OR_TEST'
}
(out/'PHASE11_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
md=['# Phase 1.1 Build/Test Report','',f"Overall: **{report['status']}**",'', '| Check | Status |','|---|---|']
md += [f'| {k} | {v} |' for k,v in checks.items()]
md += ['',f"Parity claim: **{report['parity_claim']}**",'',f"Next action: **{report['next_action']}**",'']
(out/'PHASE11_REPORT.md').write_text('\n'.join(md))
print(json.dumps(report,indent=2))
sys.exit(0 if all_pass else 2)

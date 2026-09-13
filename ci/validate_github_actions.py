#!/usr/bin/env python3
from pathlib import Path
import json, sys, yaml
root=Path(__file__).resolve().parents[1]
wf=root/'.github/workflows'
checks=[]
def add(name, ok, detail=''):
    checks.append({'name':name,'status':'PASS' if ok else 'FAIL','detail':detail})
files=sorted(wf.glob('*.yml'))
add('workflow_count', len(files)==3, ','.join(p.name for p in files))
for p in files:
    try:
        data=yaml.safe_load(p.read_text())
        add(f'yaml:{p.name}', isinstance(data,dict), '')
        txt=p.read_text()
        add(f'permissions_read:{p.name}', 'contents: read' in txt)
        add(f'no_pull_request_target:{p.name}', 'pull_request_target' not in txt)
        add(f'pinned_checkout:{p.name}', 'actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1' in txt)
        add(f'pinned_upload:{p.name}', 'actions/upload-artifact@bbbca2ddaa5d8feaa63e36b76fdaad77386f024f' in txt)
    except Exception as e:
        add(f'yaml:{p.name}',False,str(e))
legacy=(wf/'legacy-qualification.yml').read_text()
p11=(wf/'phase11-ros2.yml').read_text()
add('legacy_evidence_always_uploaded', 'if: always()' in legacy and 'QUALIFICATION_RETURN.zip' in legacy)
add('phase11_evidence_always_uploaded', 'if: always()' in p11 and 'PHASE11_RETURN.zip' in p11)
add('explicit_vm_runner', all('runs-on: ubuntu-24.04' in p.read_text() for p in files))
add('no_secrets_reference', all('secrets.' not in p.read_text() for p in files))
ok=all(c['status']=='PASS' for c in checks)
out={'schema':'usv-github-actions-validation/v1','status':'PASS' if ok else 'FAIL','checks':checks}
print(json.dumps(out,indent=2))
sys.exit(0 if ok else 2)

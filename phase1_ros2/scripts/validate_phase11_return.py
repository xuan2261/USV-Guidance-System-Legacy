#!/usr/bin/env python3
from pathlib import Path
import json,sys,zipfile,tempfile
src=Path(sys.argv[1])
tmp=None
if src.is_file() and src.suffix.lower()=='.zip':
    tmp=tempfile.TemporaryDirectory(); root=Path(tmp.name)
    with zipfile.ZipFile(src) as z: z.extractall(root)
else: root=src
p=root/'PHASE11_REPORT.json'
if not p.exists():
    print(json.dumps({'status':'FAIL','next_action':'FIX_PHASE11_WRAPPER','reason':'PHASE11_REPORT.json missing'},indent=2)); sys.exit(2)
r=json.loads(p.read_text())
print(json.dumps(r,indent=2))
sys.exit(0 if r.get('status')=='PASS' else 1)

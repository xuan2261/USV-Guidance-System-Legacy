#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
import yaml
def git(args): return subprocess.check_output(['git',*args], text=True).strip()
p=argparse.ArgumentParser(); p.add_argument('--workspace',required=True); p.add_argument('--upstream',required=True); p.add_argument('--deps-lock',required=True); p.add_argument('--source-out',required=True); p.add_argument('--deps-out',required=True); a=p.parse_args()
up=Path(a.upstream)
source={'status':'PASS','path':str(up),'head':git(['-C',str(up),'rev-parse','HEAD']),'describe':git(['-C',str(up),'describe','--always','--dirty'])}
Path(a.source_out).write_text(json.dumps(source,indent=2)+'\n')
lock=yaml.safe_load(Path(a.deps_lock).read_text())['repositories']; items=[]; ok=True
for name,spec in lock.items():
    rp=Path(a.workspace)/'src'/name; actual=git(['-C',str(rp),'rev-parse','HEAD']); match=(actual==spec['version']); ok &= match
    items.append({'name':name,'expected':spec['version'],'actual':actual,'match':match,'url':spec['url']})
Path(a.deps_out).write_text(json.dumps({'status':'PASS' if ok else 'FAIL','dependencies':items},indent=2)+'\n')

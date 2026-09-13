#!/usr/bin/env python3
import argparse, json, subprocess
from pathlib import Path
import yaml

def git(args):
    return subprocess.check_output(['git', *args], text=True).strip()

p=argparse.ArgumentParser()
p.add_argument('--workspace',required=True)
p.add_argument('--upstream',required=True)
p.add_argument('--deps-lock',required=True)
p.add_argument('--source-out',required=True)
p.add_argument('--deps-out',required=True)
a=p.parse_args()

up=Path(a.upstream)
source={
    'status':'PASS',
    'path':str(up),
    'head':git(['-C',str(up),'rev-parse','HEAD']),
    'describe':git(['-C',str(up),'describe','--always','--dirty'])
}
Path(a.source_out).write_text(json.dumps(source,indent=2)+'\n')

lock=yaml.safe_load(Path(a.deps_lock).read_text())['repositories']
items=[]
ok=True
for name,spec in lock.items():
    rp=Path(a.workspace)/'src'/name
    actual=git(['-C',str(rp),'rev-parse','HEAD'])
    match=(actual==spec['version'])
    ok &= match
    entry={
        'name':name,
        'expected':spec['version'],
        'actual':actual,
        'match':match,
        'url':spec['url'],
        'submodules':[]
    }
    for sm_path,sm_spec in (spec.get('submodules') or {}).items():
        full=rp/sm_path
        expected=sm_spec['version']
        try:
            actual_sm=git(['-C',str(full),'rev-parse','HEAD'])
            tree=git(['-C',str(rp),'ls-tree','HEAD','--',sm_path]).split()
            indexed=tree[2] if len(tree)>=3 and tree[1]=='commit' else None
            sm_match=(actual_sm==expected and indexed==expected)
        except Exception:
            actual_sm=None; indexed=None; sm_match=False
        ok &= sm_match
        entry['submodules'].append({
            'path':sm_path,
            'url':sm_spec.get('url'),
            'expected':expected,
            'superproject_gitlink':indexed,
            'actual':actual_sm,
            'match':sm_match
        })
    items.append(entry)

Path(a.deps_out).write_text(json.dumps({
    'status':'PASS' if ok else 'FAIL',
    'dependencies':items
},indent=2)+'\n')

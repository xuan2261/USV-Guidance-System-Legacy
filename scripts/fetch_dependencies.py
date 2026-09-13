#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
import yaml
lock = Path(sys.argv[1]); dst = Path(sys.argv[2])
data = yaml.safe_load(lock.read_text())['repositories']; dst.mkdir(parents=True, exist_ok=True)
for name, spec in data.items():
    url, sha = spec['url'], spec['version']; path = dst / name
    if not (path / '.git').exists(): subprocess.run(['git','clone','--filter=blob:none',url,str(path)],check=True)
    subprocess.run(['git','-C',str(path),'fetch','--tags','--force','origin',sha],check=True)
    subprocess.run(['git','-C',str(path),'checkout','--detach',sha],check=True)
    actual = subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
    if actual != sha: raise SystemExit(f'{name}: expected {sha}, got {actual}')
    print(f'PIN OK {name} {actual}')

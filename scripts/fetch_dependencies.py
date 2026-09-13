#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
import yaml

lock = Path(sys.argv[1])
dst = Path(sys.argv[2])
data = yaml.safe_load(lock.read_text())['repositories']
dst.mkdir(parents=True, exist_ok=True)

def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def out(args):
    return subprocess.check_output(args, text=True).strip()

def norm_url(url: str) -> str:
    return url.rstrip('/').removesuffix('.git')

for name, spec in data.items():
    url, sha = spec['url'], spec['version']
    path = dst / name
    if not (path / '.git').exists():
        run(['git', 'clone', '--filter=blob:none', url, str(path)])
    run(['git', '-C', str(path), 'fetch', '--tags', '--force', 'origin', sha])
    run(['git', '-C', str(path), 'checkout', '--detach', sha])
    actual = out(['git', '-C', str(path), 'rev-parse', 'HEAD'])
    if actual != sha:
        raise SystemExit(f'{name}: expected {sha}, got {actual}')
    print(f'PIN OK {name} {actual}')

    submodules = spec.get('submodules') or {}
    if submodules:
        # The pinned superproject commit is authoritative for which gitlink SHA
        # must be checked out. Initialize recursively, then verify both the
        # lockfile and superproject index agree with the checked-out revision.
        run(['git', '-C', str(path), 'submodule', 'sync', '--recursive'])
        run(['git', '-C', str(path), 'submodule', 'update', '--init', '--recursive', '--checkout'])
        for sm_path, sm_spec in submodules.items():
            expected = sm_spec['version']
            full = path / sm_path
            if not full.exists():
                raise SystemExit(f'{name}:{sm_path}: submodule worktree missing')
            tree = out(['git', '-C', str(path), 'ls-tree', 'HEAD', '--', sm_path]).split()
            if len(tree) < 3 or tree[1] != 'commit':
                raise SystemExit(f'{name}:{sm_path}: not a gitlink in pinned superproject')
            indexed = tree[2]
            actual_sm = out(['git', '-C', str(full), 'rev-parse', 'HEAD'])
            if indexed != expected:
                raise SystemExit(f'{name}:{sm_path}: lock {expected} disagrees with superproject gitlink {indexed}')
            if actual_sm != expected:
                raise SystemExit(f'{name}:{sm_path}: expected {expected}, got {actual_sm}')
            expected_url = sm_spec.get('url')
            if expected_url:
                actual_url = out(['git', '-C', str(full), 'config', '--get', 'remote.origin.url'])
                if norm_url(actual_url) != norm_url(expected_url):
                    raise SystemExit(f'{name}:{sm_path}: expected URL {expected_url}, got {actual_url}')
            print(f'SUBMODULE PIN OK {name}:{sm_path} {actual_sm}')

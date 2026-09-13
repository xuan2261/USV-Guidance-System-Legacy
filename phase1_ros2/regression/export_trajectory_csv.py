#!/usr/bin/env python3
from pathlib import Path
import csv,json,subprocess,sys
from legacy_model_reference import trajectory
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out/trajectories'; (OUT/'legacy').mkdir(parents=True,exist_ok=True); (OUT/'core').mkdir(parents=True,exist_ok=True)
sc=json.loads((ROOT/'model_scenarios.json').read_text()); dt=float(sc['integration']['dt_s'])
bin_path=ROOT/'out/core_model_runner'
if not bin_path.exists():
    print('core_model_runner missing; run run_model_regression.py first',file=sys.stderr); sys.exit(2)
for item in sc['scenarios']:
    rows=trajectory(item['state'],item['command'],item['duration_s'],dt)
    with (OUT/'legacy'/f"{item['id']}.csv").open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['t','x','y','yaw','u','v','r']);
        for t,s in rows:w.writerow([t,*s])
    args=[str(bin_path),str(item['duration_s']),str(dt),*map(str,item['state']),*map(str,item['command'])]
    rp=subprocess.run(args,text=True,capture_output=True,check=True)
    (OUT/'core'/f"{item['id']}.csv").write_text(rp.stdout)
print(f'PASS exported {len(sc["scenarios"])} paired trajectories to {OUT}')
